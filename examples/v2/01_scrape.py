import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# v2 keeps a Firecrawl-compatible scrape request shape.
demo("POST /v2/scrape", lambda: api.post(
    "/v2/scrape", {"url": "https://en.wikipedia.org/wiki/ISRO", "formats": ["markdown"]}
))
