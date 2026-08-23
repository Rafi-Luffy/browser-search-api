import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# v2 map returns the link structure using the compatibility API.
demo("POST /v2/map", lambda: api.post("/v2/map", {"url": "https://www.prsindia.org"}))
