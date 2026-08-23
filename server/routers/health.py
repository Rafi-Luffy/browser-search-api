from fastapi import APIRouter
from server.services.crawler_service import crawler_service
from server.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.API_VERSION,
        "active_crawl_jobs": crawler_service.get_active_count(),
    }
