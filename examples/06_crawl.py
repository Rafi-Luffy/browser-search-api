import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo, show

job = api.post("/v1/crawl", {
    "url": "https://news.ycombinator.com",
    "maxDepth": 1,
    "maxPages": 2,
    "formats": ["markdown"],
})
show("POST /v1/crawl", job)

crawl_id = job.get("id") or job.get("jobId")
if crawl_id:
    time.sleep(1)
    demo("GET /v1/crawl/{id}", lambda: api.get(f"/v1/crawl/{crawl_id}"))
    demo("GET /v1/crawl/active", lambda: api.get("/v1/crawl/active"))
    demo("DELETE /v1/crawl/{id}", lambda: api.delete(f"/v1/crawl/{crawl_id}"))
