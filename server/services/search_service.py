import asyncio
import html
import re
import urllib.parse
from typing import Any, Dict, List, Optional
import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS

from server.config import settings

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
]


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = html.unescape(clean)
    return re.sub(r"\s+", " ", clean).strip()


def unwrap_redirect_url(url: str) -> str:
    if not url:
        return ""
    try:
        if "uddg=" in url:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "uddg" in qs:
                return urllib.parse.unquote(qs["uddg"][0])
        if url.startswith("//"):
            return "https:" + url
    except Exception:
        pass
    return url


class SearchService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={
                "User-Agent": USER_AGENTS[0],
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

    async def search_ddgs_library(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()

        def _fetch():
            ddgs = DDGS()
            return list(ddgs.text(query, max_results=max(limit, 5)))

        items = await loop.run_in_executor(None, _fetch)
        results = []
        for item in items:
            raw_url = item.get("href") or item.get("url") or ""
            actual_url = unwrap_redirect_url(raw_url)
            title = item.get("title") or ""
            body = item.get("body") or item.get("snippet") or ""
            if actual_url and actual_url.startswith("http"):
                results.append({
                    "title": title.strip(),
                    "url": actual_url.strip(),
                    "snippet": body.strip(),
                    "engine": "duckduckgo",
                })
        return results

    async def search_duckduckgo_html(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        try:
            resp = await self.client.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query, "b": ""},
                headers={"User-Agent": USER_AGENTS[1]},
            )
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result_div in soup.find_all("div", class_=re.compile(r"result\s|results_links")):
                    a_tag = result_div.find("a", class_="result__a") or result_div.find("a", class_="result__snippet")
                    if not a_tag:
                        continue
                    raw_href = str(a_tag.get("href", ""))
                    url = unwrap_redirect_url(raw_href)
                    if not url or not url.startswith("http"):
                        continue
                    title = a_tag.get_text().strip()
                    snippet_tag = result_div.find("a", class_="result__snippet") or result_div.find("div", class_="result__snippet")
                    snippet = snippet_tag.get_text().strip() if snippet_tag else title
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "engine": "duckduckgo",
                    })
        except Exception:
            pass
        return results

    async def search_duckduckgo_lite(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        try:
            resp = await self.client.post(
                "https://lite.duckduckgo.com/lite/",
                data={"q": query},
                headers={"User-Agent": USER_AGENTS[2]},
            )
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                rows = soup.find_all("tr")
                for i, row in enumerate(rows):
                    link = row.find("a", class_="result-link")
                    if link:
                        raw_href = str(link.get("href", ""))
                        url = unwrap_redirect_url(raw_href)
                        title = link.get_text().strip()
                        snippet = ""
                        if i + 1 < len(rows):
                            snippet_td = rows[i + 1].find("td", class_="result-snippet")
                            if snippet_td:
                                snippet = snippet_td.get_text().strip()
                        if url and url.startswith("http"):
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet or title,
                                "engine": "duckduckgo",
                            })
        except Exception:
            pass
        return results

    async def search_duckduckgo(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Try DDGS first
        try:
            res = await self.search_ddgs_library(query, limit=limit)
            if res:
                return res[:limit]
        except Exception:
            pass

        # Fallback 1: DuckDuckGo HTML
        try:
            res = await self.search_duckduckgo_html(query, limit=limit)
            if res:
                return res[:limit]
        except Exception:
            pass

        # Fallback 2: DuckDuckGo Lite
        try:
            res = await self.search_duckduckgo_lite(query, limit=limit)
            if res:
                return res[:limit]
        except Exception:
            pass

        return []

    async def search_wikipedia(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        try:
            clean_q = re.sub(r"site:\S+", "", query).strip()
            if not clean_q:
                clean_q = query
            api_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": clean_q,
                "format": "json",
                "srlimit": str(max(limit, 5)),
            }
            resp = await self.client.get(api_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("query", {}).get("search", []):
                    title = item.get("title", "")
                    page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                    snippet = clean_html(item.get("snippet", ""))
                    results.append({
                        "title": title,
                        "url": page_url,
                        "snippet": snippet,
                        "engine": "wikipedia",
                    })
        except Exception:
            pass
        return results

    async def search_reddit(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        try:
            clean_q = re.sub(r"site:\S+", "", query).strip()
            api_url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(clean_q)}&limit={max(limit, 5)}"
            resp = await self.client.get(api_url, headers={"User-Agent": "Mozilla/5.0 (UniversalWebSearchAPI/1.0)"})
            if resp.status_code == 200:
                data = resp.json()
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    title = post.get("title", "")
                    permalink = post.get("permalink", "")
                    selftext = post.get("selftext", "")
                    url = f"https://www.reddit.com{permalink}" if permalink else post.get("url", "")
                    snippet = selftext[:300] if selftext else f"Subreddit: r/{post.get('subreddit', '')} | Upvotes: {post.get('score', 0)}"
                    if url and url.startswith("http"):
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "engine": "reddit",
                        })
        except Exception:
            pass
        return results

    async def search_github(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        try:
            clean_q = re.sub(r"site:\S+", "", query).strip()
            api_url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(clean_q)}&per_page={max(limit, 5)}"
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "UniversalWebSearchAPI/1.0"}
            if settings.GITHUB_TOKEN:
                headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
            resp = await self.client.get(api_url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                for repo in data.get("items", []):
                    results.append({
                        "title": repo.get("full_name", ""),
                        "url": repo.get("html_url", ""),
                        "snippet": (repo.get("description") or f"GitHub repository {repo.get('full_name')}") + f" (⭐ {repo.get('stargazers_count', 0)})",
                        "engine": "github",
                    })
        except Exception:
            pass
        return results

    async def search_searxng(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        if not settings.SEARXNG_URL:
            return results
        try:
            endpoint = f"{settings.SEARXNG_URL.rstrip('/')}/search"
            params = {"q": query, "format": "json"}
            resp = await self.client.get(endpoint, params=params)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "engine": "searxng",
                    })
        except Exception:
            pass
        return results

    async def search(
        self,
        query: str,
        limit: int = 5,
        engines: Optional[List[str]] = None,
        lang: str = "en",
        tbs: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        limit = min(max(1, limit), settings.MAX_SEARCH_LIMIT)
        selected_engines = [e.lower() for e in (engines or ["duckduckgo", "searxng", "google", "bing"])]

        tasks = []
        if any(e in selected_engines for e in ["duckduckgo", "google", "bing", "ddg"]):
            tasks.append(self.search_duckduckgo(query, limit=limit * 2))
        if "searxng" in selected_engines and settings.SEARXNG_URL:
            tasks.append(self.search_searxng(query, limit=limit * 2))
        if "wikipedia" in selected_engines:
            tasks.append(self.search_wikipedia(query, limit=limit))
        if "reddit" in selected_engines:
            tasks.append(self.search_reddit(query, limit=limit))
        if "github" in selected_engines:
            tasks.append(self.search_github(query, limit=limit))

        if not tasks:
            tasks.append(self.search_duckduckgo(query, limit=limit * 2))

        engine_results = await asyncio.gather(*tasks, return_exceptions=True)

        merged: List[Dict[str, Any]] = []
        seen_urls = set()

        site_filter = None
        site_match = re.search(r"site:([a-zA-Z0-9.-]+)", query)
        if site_match:
            site_filter = site_match.group(1).lower()

        for res_list in engine_results:
            if isinstance(res_list, list):
                for item in res_list:
                    url = item.get("url", "")
                    if not url or url in seen_urls:
                        continue
                    if site_filter:
                        try:
                            parsed_host = urllib.parse.urlparse(url).netloc.lower()
                            if site_filter not in parsed_host and site_filter not in url.lower():
                                continue
                        except Exception:
                            pass
                    seen_urls.add(url)
                    merged.append(item)

        # Fallback if 0 results
        if not merged:
            # Try Wikipedia fallback
            wiki_res = await self.search_wikipedia(query, limit=limit)
            for item in wiki_res:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    merged.append(item)

        # Format output items with standard schema
        formatted = []
        for idx, item in enumerate(merged[:limit], 1):
            snippet = item.get("snippet", "")
            title = item.get("title", "") or item.get("url", "")
            formatted.append({
                "position": idx,
                "title": title,
                "url": item.get("url", ""),
                "snippet": snippet,
                "description": snippet,
                "score": round(1.0 - (idx - 1) * 0.05, 2),
                "category": item.get("engine", "web"),
            })

        return formatted


search_service = SearchService()
