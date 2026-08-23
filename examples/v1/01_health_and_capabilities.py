import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# A loop keeps the two related GET demonstrations consistent.
for path, title in (("/health", "GET /health"), ("/v1/capabilities", "GET /v1/capabilities")):
    demo(title, lambda path=path: api.get(path))
