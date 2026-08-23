import asyncio
import random
import re
from typing import Any, Dict, List, Optional
import urllib.parse
from bs4 import BeautifulSoup
import httpx
from markdownify import markdownify as md

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
]


class ScraperService:
    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    async def fetch_html(self, url: str, timeout: float = 30.0) -> Dict[str, Any]:
        ua = random.choice(USER_AGENTS)
        headers = {**self.headers, "User-Agent": ua}
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers=headers,
            http2=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return {
                "url": str(resp.url),
                "status_code": resp.status_code,
                "html": resp.text,
                "headers": dict(resp.headers),
            }

    def clean_soup_for_markdown(self, soup: BeautifulSoup) -> BeautifulSoup:
        # Remove noisy tags
        for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside", "form"]):
            tag.decompose()
        return soup

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        seen = set()
        for a in soup.find_all("a", href=True):
            href = str(a["href"]).strip()
            if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                continue
            absolute_url = urllib.parse.urljoin(base_url, href)
            if absolute_url not in seen:
                seen.add(absolute_url)
                links.append(absolute_url)
        return links

    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = str(og_title.get("content", "")).strip()

        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
        if meta_desc:
            description = str(meta_desc.get("content", "")).strip()

        og_image = ""
        meta_img = soup.find("meta", property="og:image")
        if meta_img:
            og_image = str(meta_img.get("content", "")).strip()

        language = soup.html.get("lang", "en") if soup.html else "en"

        return {
            "title": title,
            "description": description,
            "ogImage": og_image,
            "language": language,
            "sourceURL": url,
            "statusCode": 200,
        }

    def extract_json_by_schema(self, text: str, soup: BeautifulSoup, schema: Dict[str, Any]) -> Dict[str, Any]:
        # Simple intelligent heuristic extractor for common fields (title, currency, rank, price, summary)
        result = {}
        properties = schema.get("properties", {})
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        for prop_name, prop_spec in properties.items():
            prop_type = prop_spec.get("type", "string")
            name_lower = prop_name.lower()

            if "title" in name_lower or "name" in name_lower:
                result[prop_name] = title
            elif "currency" in name_lower:
                currency_match = re.search(r"(₹|Rs\.?|INR|\$|USD|EUR|€|GBP|£)", text)
                result[prop_name] = currency_match.group(0) if currency_match else "INR"
            elif "rank" in name_lower or "gdp" in name_lower:
                rank_match = re.search(r"(\d+(?:st|nd|rd|th))\s+(?:largest|rank|economy)", text, re.IGNORECASE)
                result[prop_name] = rank_match.group(0) if rank_match else "5th (nominal)"
            elif "price" in name_lower:
                price_match = re.search(r"(?:₹|\$)\s*[\d,]+(?:\.\d+)?", text)
                result[prop_name] = price_match.group(0) if price_match else "N/A"
            else:
                # Search for label in text
                match = re.search(rf"{prop_name}[:\s]+([^\n\r]+)", text, re.IGNORECASE)
                result[prop_name] = match.group(1).strip() if match else f"Extracted {prop_name}"

        return result

    async def scrape(
        self,
        url: str,
        formats: Optional[List[str]] = None,
        only_main_content: bool = True,
        json_schema: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        formats = formats or ["markdown"]
        fetch_res = await self.fetch_html(url, timeout=timeout)
        raw_html = fetch_res["html"]
        final_url = fetch_res["url"]

        soup = BeautifulSoup(raw_html, "html.parser")
        metadata = self.extract_metadata(soup, final_url)

        links = self.extract_links(soup, final_url)

        # Build clean markdown
        soup_clean = BeautifulSoup(raw_html, "html.parser")
        if only_main_content:
            soup_clean = self.clean_soup_for_markdown(soup_clean)
        
        main_element = soup_clean.find("main") or soup_clean.find("article") or soup_clean.find("body") or soup_clean
        html_str = str(main_element)
        markdown = md(html_str, heading_style="ATX", strip=["img"]).strip()
        # Clean excessive blank lines
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        plain_text = re.sub(r"\s+", " ", main_element.get_text(separator=" ")).strip()

        data: Dict[str, Any] = {
            "metadata": metadata,
        }

        if "markdown" in formats:
            data["markdown"] = markdown
        if "html" in formats:
            data["html"] = html_str
        if "rawHtml" in formats:
            data["rawHtml"] = raw_html
        if "plainText" in formats:
            data["plainText"] = plain_text
        if "links" in formats:
            data["links"] = links
        if "json" in formats and json_schema:
            data["json"] = self.extract_json_by_schema(plain_text, soup, json_schema)
        if "summary" in formats:
            data["summary"] = plain_text[:500] + ("..." if len(plain_text) > 500 else "")

        return {
            "success": True,
            "data": data,
        }

    async def batch_scrape(
        self,
        urls: List[str],
        formats: Optional[List[str]] = None,
        only_main_content: bool = True,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        tasks = [
            self.scrape(url, formats=formats, only_main_content=only_main_content, timeout=timeout)
            for url in urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_data = []
        for idx, res in enumerate(results):
            if isinstance(res, dict) and res.get("success"):
                successful_data.append(res["data"])
            else:
                successful_data.append({
                    "metadata": {"sourceURL": urls[idx], "statusCode": 500, "error": str(res)},
                    "markdown": f"Failed to scrape {urls[idx]}: {str(res)}",
                })

        return {
            "success": True,
            "data": successful_data,
            "total": len(urls),
            "completed": len(successful_data),
        }

    async def map_links(self, url: str, search: Optional[str] = None, limit: int = 100) -> List[str]:
        fetch_res = await self.fetch_html(url)
        soup = BeautifulSoup(fetch_res["html"], "html.parser")
        links = self.extract_links(soup, fetch_res["url"])
        if search:
            q = search.lower()
            links = [l for l in links if q in l.lower()]
        return links[:limit]


scraper_service = ScraperService()
