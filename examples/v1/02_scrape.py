import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

url = "https://en.wikipedia.org/wiki/Economy_of_India"

# Each payload demonstrates one output format supported by v1 scraping.
payloads = [
    ("Markdown scrape", {"url": url, "formats": ["markdown"]}),
    ("HTML and links scrape", {"url": url, "formats": ["html", "links"]}),
    ("Structured JSON extraction", {
        "url": url,
        "formats": ["json"],
        "jsonSchema": {"type": "object", "properties": {
            "title": {"type": "string"},
            "currency": {"type": "string"},
            "gdp_rank": {"type": "string"},
        }},
    }),
]
for title, payload in payloads:
    demo(title, lambda payload=payload: api.post("/v1/scrape", payload))
