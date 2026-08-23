import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_TITLE: str = "Universal Web Search & Browser API"
    API_VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    API_KEY: str = os.getenv("CRW_API_KEY", os.getenv("API_KEY", ""))
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "false").lower() in ("true", "1", "yes")

    SEARXNG_URL: str = os.getenv("SEARXNG_URL", "")

    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

    MAX_SEARCH_LIMIT: int = 50
    MAX_SCRAPE_CONCURRENCY: int = 20
    MAX_CRAWL_PAGES: int = 100
    MAX_CRAWL_DEPTH: int = 5
    MAX_UPLOAD_BYTES: int = 52428800

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
