import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# A list makes it easy to add more pages to the batch.
urls = ["https://en.wikipedia.org/wiki/ISRO", "https://en.wikipedia.org/wiki/Chandrayaan-3"]
demo("POST /v2/batch/scrape", lambda: api.post("/v2/batch/scrape", {"urls": urls, "formats": ["markdown"]}))
