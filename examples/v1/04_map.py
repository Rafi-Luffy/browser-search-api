import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# Map discovers links from the supplied site.
demo("POST /v1/map", lambda: api.post("/v1/map", {"url": "https://www.prsindia.org"}))
