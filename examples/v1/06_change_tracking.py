import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from main import api, demo

# Compare two snapshots to demonstrate a git-style content diff.
payload = {
    "previous": {"markdown": "# Daily Fuel Rates\n- Petrol: ₹94.72/litre", "contentHash": "v1"},
    "current": {"markdown": "# Daily Fuel Rates\n- Petrol: ₹94.95/litre", "contentHash": "v2"},
    "modes": ["gitDiff"],
}
demo("POST /v1/change-tracking/diff", lambda: api.post("/v1/change-tracking/diff", payload))
