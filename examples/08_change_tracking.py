import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import api, demo

payload = {
    "previous": {"markdown": "# Product Pricing\n- Pro Plan: $49/mo\n- API Requests: 10,000", "contentHash": "v1"},
    "current": {"markdown": "# Product Pricing\n- Pro Plan: $39/mo\n- API Requests: Unlimited", "contentHash": "v2"},
    "modes": ["gitDiff", "json"],
}
demo("POST /v1/change-tracking/diff", lambda: api.post("/v1/change-tracking/diff", payload))
