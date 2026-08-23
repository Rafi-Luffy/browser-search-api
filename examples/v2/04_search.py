import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# Search is the same one-call pattern as the v1 example.
demo("POST /v2/search", lambda: api.post(
    "/v2/search", {"query": "Indian Space Research Organisation achievements", "limit": 2}
))
