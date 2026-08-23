import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

demo("POST /v1/scrape (Markdown)", lambda: api.post(
    "/v1/scrape", {"url": url, "formats": ["markdown"]}
))

demo("POST /v1/scrape (Links & HTML)", lambda: api.post(
    "/v1/scrape", {"url": url, "formats": ["links"]}
))
