import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo

demo("POST /v1/search (General)", lambda: api.post(
    "/v1/search", {"query": "Quantum computing algorithms 2026", "limit": 3}
))

demo("POST /v1/search (Domain Restricted)", lambda: api.post(
    "/v1/search", {"query": "site:github.com rust web scraper", "limit": 2}
))
