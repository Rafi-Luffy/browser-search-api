import json
import os
import sys

from main import api

TARGET_URL = "https://en.wikipedia.org/wiki/Ayurveda"
BATCH_URLS = [TARGET_URL, "https://en.wikipedia.org/wiki/Panchakarma"]
SEARCH_QUERY = "Kerala Ayurveda Panchakarma wellness treatments"
OUTPUT_FILE = "outputs/smoke_test_results.json"


# Keep the PDF smoke test self-contained and free from temporary files.
def sample_pdf():
    return (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n"
        b"0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n"
    )


# Smoke tests should continue so one failed endpoint does not hide the others.
def safe(action):
    try:
        return action()
    except Exception as error:
        return {"error": str(error)}


# Convert the command-line argument into the selected test group and URL.
def arguments():
    value = sys.argv[1] if len(sys.argv) > 1 else "all"
    return ("all", value, [value]) if value.startswith("http") else (value.lower(), TARGET_URL, BATCH_URLS)


# Build endpoint checks as data, then run them through one small loop.
def checks(action, target_url, batch_urls):
    groups = {
        "health": [
            ("health", "GET /health", lambda: api.get("/health")),
            ("capabilities", "GET /v1/capabilities", lambda: api.get("/v1/capabilities")),
        ],
        "scrape": [
            ("v1_scrape", "POST /v1/scrape", lambda: api.post("/v1/scrape", {"url": target_url, "formats": ["markdown"]})),
            ("v2_scrape", "POST /v2/scrape", lambda: api.post("/v2/scrape", {"url": target_url, "formats": ["markdown"]})),
            ("v2_batch_scrape", "POST /v2/batch/scrape", lambda: api.post("/v2/batch/scrape", {"urls": batch_urls, "formats": ["markdown"]})),
        ],
        "search": [
            ("v1_search", "POST /v1/search", lambda: api.post("/v1/search", {"query": SEARCH_QUERY, "limit": 2})),
            ("v2_search", "POST /v2/search", lambda: api.post("/v2/search", {"query": SEARCH_QUERY, "limit": 2})),
        ],
        "map": [
            ("v1_map", "POST /v1/map", lambda: api.post("/v1/map", {"url": target_url})),
            ("v2_map", "POST /v2/map", lambda: api.post("/v2/map", {"url": target_url})),
        ],
        "crawl": [
            ("v1_crawl", "POST /v1/crawl", lambda: api.post("/v1/crawl", {"url": target_url, "maxDepth": 1, "maxPages": 2})),
            ("v2_crawl_active", "GET /v2/crawl/active", lambda: api.get("/v2/crawl/active")),
        ],
    }
    selected = [action] if action != "all" else groups
    return [check for group in selected for check in groups.get(group, [])] + (
        [("v1_diff", "POST /v1/change-tracking/diff", lambda: api.post("/v1/change-tracking/diff", {
            "previous": {"markdown": "Panchakarma: ₹15,000"},
            "current": {"markdown": "Panchakarma: ₹18,000"},
            "modes": ["gitDiff"],
        })), ("v2_pdf_parse", "POST /v2/parse", lambda: api.parse_pdf(sample_pdf(), "kerala_ayurveda_guide.pdf"))]
        if action == "all" else []
    )


# Run selected checks, print each result once, and save a machine-readable report.
def main():
    action, target_url, batch_urls = arguments()
    print(f"Running smoke tests on: {target_url}")
    results = {}
    for key, title, action_fn in checks(action, target_url, batch_urls):
        results[key] = safe(action_fn)
        print(f"\n=== {title} ===\n{json.dumps(results[key], indent=2, ensure_ascii=False)}")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as output:
        json.dump(results, output, indent=2, ensure_ascii=False)
    print(f"\nSaved results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
