from fastapi import APIRouter
from server.config import settings

router = APIRouter(tags=["Capabilities"])


@router.get("/v1/capabilities")
async def capabilities():
    return {
        "success": True,
        "server": {
            "name": settings.API_TITLE,
            "version": settings.API_VERSION,
            "serverKeyConfigured": bool(settings.API_KEY),
        },
        "limits": {
            "maxSearchLimit": settings.MAX_SEARCH_LIMIT,
            "maxScrapeConcurrency": settings.MAX_SCRAPE_CONCURRENCY,
            "maxCrawlPages": settings.MAX_CRAWL_PAGES,
            "maxCrawlDepth": settings.MAX_CRAWL_DEPTH,
            "maxBytes": settings.MAX_UPLOAD_BYTES,
        },
        "formats": [
            "markdown",
            "html",
            "rawHtml",
            "plainText",
            "links",
            "json",
            "summary",
            "changeTracking",
        ],
        "diffModes": ["gitDiff", "json"],
        "engines": [
            "duckduckgo",
            "searxng",
            "google",
            "bing",
            "wikipedia",
            "reddit",
            "github",
        ],
        "features": {
            "answer": True,
            "summarizeResults": True,
            "domainFiltering": True,
            "batchScrape": True,
            "pdfParse": True,
            "changeTracking": True,
            "mcp": True,
        },
    }
