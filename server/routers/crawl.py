from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server.services.crawler_service import crawler_service

router = APIRouter(tags=["Crawl"])


class CrawlRequest(BaseModel):
    url: str
    maxDepth: Optional[int] = 1
    maxPages: Optional[int] = 10
    limit: Optional[int] = None
    formats: Optional[List[str]] = Field(default_factory=lambda: ["markdown"])


@router.post("/v1/crawl")
async def v1_start_crawl(req: CrawlRequest):
    max_pages = req.limit or req.maxPages or 10
    return crawler_service.start_crawl(
        url=req.url,
        max_depth=req.maxDepth or 1,
        max_pages=max_pages,
        formats=req.formats,
    )


@router.get("/v1/crawl/{crawl_id}")
async def v1_get_crawl(crawl_id: str):
    res = crawler_service.get_status(crawl_id)
    if not res:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return res


@router.delete("/v1/crawl/{crawl_id}")
async def v1_delete_crawl(crawl_id: str):
    success = crawler_service.cancel_crawl(crawl_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return {"success": True, "message": "Crawl job cancelled"}


@router.post("/v2/crawl")
async def v2_start_crawl(req: CrawlRequest):
    max_pages = req.limit or req.maxPages or 10
    job = crawler_service.start_crawl(
        url=req.url,
        max_depth=req.maxDepth or 1,
        max_pages=max_pages,
        formats=req.formats,
    )
    return {
        "success": True,
        "id": job["id"],
        "url": f"/v2/crawl/{job['id']}",
    }


@router.get("/v2/crawl/active")
async def v2_get_active():
    return {
        "success": True,
        "data": {
            "crawls": crawler_service.get_active_crawls(),
        },
    }
