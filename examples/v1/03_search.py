import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# The request helper handles auth, JSON encoding, and response parsing.
demo("POST /v1/search", lambda: api.post(
    "/v1/search", {"query": "Reserve Bank of India interest rate updates", "limit": 3}
))
