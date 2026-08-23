import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo

# Health endpoint (public)
demo("GET /health", lambda: api.get("/health"))

# Capabilities endpoint (inspect server features, engines, limits)
demo("GET /v1/capabilities", lambda: api.get("/v1/capabilities"))
