import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# v2 starts a crawl and exposes a separate active-crawls endpoint.
demo("POST /v2/crawl", lambda: api.post(
    "/v2/crawl", {"url": "https://www.prsindia.org", "maxDepth": 1, "limit": 2}
))
demo("GET /v2/crawl/active", lambda: api.get("/v2/crawl/active"))
