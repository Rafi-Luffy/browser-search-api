import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo

demo("GET /health", lambda: api.get("/health"))

demo("GET /v1/capabilities", lambda: api.get("/v1/capabilities"))
