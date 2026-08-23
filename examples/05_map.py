import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo

# Discover and map internal/external links from a site
demo("POST /v1/map", lambda: api.post(
    "/v1/map", {"url": "https://news.ycombinator.com", "limit": 10}
))
