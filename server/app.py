from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.config import settings
from server.routers import (
    capabilities,
    crawl,
    diff,
    health,
    map as map_router,
    mcp,
    parse,
    scrape,
    search,
)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Universal Web Search, Scraping, Crawling, PDF Parsing, and MCP API for unlimited AI and agent usage.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    public_paths = [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
    ]

    path = request.url.path
    if path in public_paths or request.method == "OPTIONS":
        return await call_next(request)

    if settings.REQUIRE_AUTH and settings.API_KEY:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "error": "Missing Authorization header"},
            )

        token = auth_header.replace("Bearer ", "").strip()
        if token != settings.API_KEY:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"success": False, "error": "Invalid API Key"},
            )

    return await call_next(request)


@app.get("/")
async def root():
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "online",
        "endpoints": {
            "health": "/health",
            "capabilities": "/v1/capabilities",
            "search_v1": "/v1/search",
            "search_v2": "/v2/search",
            "scrape_v1": "/v1/scrape",
            "scrape_v2": "/v2/scrape",
            "batch_scrape": "/v2/batch/scrape",
            "map_v1": "/v1/map",
            "map_v2": "/v2/map",
            "crawl_v1": "/v1/crawl",
            "crawl_v2": "/v2/crawl",
            "change_diff": "/v1/change-tracking/diff",
            "pdf_parse": "/v2/parse",
            "mcp": "/mcp",
            "docs": "/docs",
        },
    }


app.include_router(health.router)
app.include_router(capabilities.router)
app.include_router(search.router)
app.include_router(scrape.router)
app.include_router(map_router.router)
app.include_router(crawl.router)
app.include_router(diff.router)
app.include_router(parse.router)
app.include_router(mcp.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
    )
