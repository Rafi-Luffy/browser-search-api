from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from server.services.scraper_service import scraper_service

router = APIRouter(tags=["Scrape"])


class ScrapeRequest(BaseModel):
    url: str
    formats: Optional[List[str]] = Field(default_factory=lambda: ["markdown"])
    onlyMainContent: Optional[bool] = True
    jsonSchema: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = 30.0


class BatchScrapeRequest(BaseModel):
    urls: List[str]
    formats: Optional[List[str]] = Field(default_factory=lambda: ["markdown"])
    onlyMainContent: Optional[bool] = True
    timeout: Optional[float] = 30.0


@router.post("/v1/scrape")
@router.post("/scrape")
@router.post("/v2/scrape")
async def scrape_endpoint(req: ScrapeRequest):
    return await scraper_service.scrape(
        url=req.url,
        formats=req.formats,
        only_main_content=req.onlyMainContent if req.onlyMainContent is not None else True,
        json_schema=req.jsonSchema,
        timeout=req.timeout or 30.0,
    )


@router.post("/v1/batch/scrape")
@router.post("/v1/batch-scrape")
@router.post("/batch/scrape")
@router.post("/batch-scrape")
@router.post("/v2/batch/scrape")
async def batch_scrape_endpoint(req: BatchScrapeRequest):
    return await scraper_service.batch_scrape(
        urls=req.urls,
        formats=req.formats,
        only_main_content=req.onlyMainContent if req.onlyMainContent is not None else True,
        timeout=req.timeout or 30.0,
    )
