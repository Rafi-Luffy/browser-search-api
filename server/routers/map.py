from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from server.services.scraper_service import scraper_service

router = APIRouter(tags=["Map"])


class MapRequest(BaseModel):
    url: str
    search: Optional[str] = None
    limit: Optional[int] = 100


@router.post("/v1/map")
async def v1_map(req: MapRequest):
    links = await scraper_service.map_links(url=req.url, search=req.search, limit=req.limit or 100)
    return {
        "success": True,
        "data": {
            "links": links,
            "total": len(links),
        },
    }


@router.post("/v2/map")
async def v2_map(req: MapRequest):
    links = await scraper_service.map_links(url=req.url, search=req.search, limit=req.limit or 100)
    return {
        "success": True,
        "data": {
            "links": links,
            "total": len(links),
        },
    }
