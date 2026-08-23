import asyncio
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from server.services.search_service import search_service
from server.services.scraper_service import scraper_service

router = APIRouter(tags=["Search"])


class ScrapeOptions(BaseModel):
    formats: Optional[List[str]] = Field(default_factory=lambda: ["markdown"])
    onlyMainContent: Optional[bool] = True


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5
    engines: Optional[List[str]] = None
    lang: Optional[str] = "en"
    tbs: Optional[str] = None
    sources: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    scrapeOptions: Optional[ScrapeOptions] = None


async def _perform_search_and_optional_scrape(req: SearchRequest) -> List[Dict[str, Any]]:
    results = await search_service.search(
        query=req.query,
        limit=req.limit or 5,
        engines=req.engines,
        lang=req.lang or "en",
        tbs=req.tbs,
    )

    if req.scrapeOptions and results:
        formats = req.scrapeOptions.formats or ["markdown"]
        only_main = req.scrapeOptions.onlyMainContent if req.scrapeOptions.onlyMainContent is not None else True

        async def _scrape_res(res_item):
            try:
                url = res_item.get("url")
                if url:
                    scrape_res = await scraper_service.scrape(
                        url=url,
                        formats=formats,
                        only_main_content=only_main,
                        timeout=10.0,
                    )
                    if scrape_res.get("success"):
                        if "markdown" in formats and "markdown" in scrape_res["data"]:
                            res_item["markdown"] = scrape_res["data"]["markdown"]
                        if "html" in formats and "html" in scrape_res["data"]:
                            res_item["html"] = scrape_res["data"]["html"]
            except Exception:
                pass

        await asyncio.gather(*[_scrape_res(r) for r in results[:req.limit]], return_exceptions=True)

    return results


def _build_search_response(query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "success": True,
        "data": {
            "query": query,
            "results": results,
            "web": results,
            "totalResults": len(results),
            "total": len(results),
        },
    }


@router.post("/v1/search")
@router.post("/search")
@router.post("/v2/search")
async def search_endpoint(req: SearchRequest):
    results = await _perform_search_and_optional_scrape(req)
    return _build_search_response(req.query, results)
