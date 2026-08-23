import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo

urls = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Quantum_computing",
]

demo("POST /v1/batch/scrape", lambda: api.post(
    "/v1/batch/scrape", {"urls": urls, "formats": ["markdown"]}
))
