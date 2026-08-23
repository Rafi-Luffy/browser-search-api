import json
import os
import time
from datetime import datetime
from main import api

VAGUE_QUERIES = [
    {"query": "apple", "category": "brand_vs_fruit", "note": "Ambiguous: Apple Inc. vs fruit vs music"},
    {"query": "jaguar", "category": "car_vs_animal", "note": "Ambiguous: Jaguar cars vs Jaguar animal vs Jacksonville Jaguars"},
    {"query": "mercury", "category": "multi_meaning", "note": "Ambiguous: Planet vs chemical element vs Roman god vs car"},
    {"query": "crane", "category": "multi_meaning", "note": "Ambiguous: Construction machine vs bird species"},
    {"query": "delta", "category": "multi_meaning", "note": "Ambiguous: Delta Air Lines vs river delta vs mathematical symbol"},
    {"query": "matrix", "category": "popculture_vs_math", "note": "Ambiguous: The Matrix movie vs mathematical matrix vs Matrix protocol"},
    {"query": "python", "category": "programming_vs_snake", "note": "Ambiguous: Python programming language vs Python snake"},
    {"query": "how to fix it", "category": "extremely_vague_question", "note": "No context provided on what needs fixing"},
    {"query": "something went wrong", "category": "error_phrase", "note": "Common error string without context"},
    {"query": "best way", "category": "incomplete_phrase", "note": "Incomplete query with no subject"},
]

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "vague_search_test_results.json")


def test_search_query(query, limit=4):
    endpoint = "/v1/search"
    payload = {"query": query, "limit": limit}

    start_time = time.time()
    try:
        res = api.post(endpoint, payload)
        duration = round(time.time() - start_time, 2)
        data = res.get("data", {})
        results = data.get("results", [])

        return {
            "status": "success",
            "duration_seconds": duration,
            "result_count": len(results),
            "results": [
                {
                    "position": r.get("position"),
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "snippet": r.get("snippet"),
                }
                for r in results
            ],
            "raw_response": res,
        }
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        return {
            "status": "error",
            "error_message": str(e),
            "duration_seconds": duration,
            "result_count": 0,
            "raw_response": None,
        }


def run_tests():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Starting Vague & Ambiguous Search Query Tests (/v1/search)...", flush=True)
    print(f"Total vague queries: {len(VAGUE_QUERIES)}", flush=True)
    print("=" * 75, flush=True)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(VAGUE_QUERIES),
        "stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "queries": {},
    }

    latencies = []

    for i, item in enumerate(VAGUE_QUERIES, 1):
        q = item["query"]
        note = item["note"]
        print(f"\n[{i}/{len(VAGUE_QUERIES)}] Query: '{q}' ({note})", flush=True)

        res = test_search_query(q, limit=4)
        if res["status"] == "success":
            summary["stats"]["success"] += 1
            latencies.append(res["duration_seconds"])
            print(f"  /v1/search: SUCCESS ({res['duration_seconds']}s) - {res['result_count']} results", flush=True)
            for r in res["results"][:3]:
                print(f"     [Pos {r['position']}] {r['title']} ({r['url']})", flush=True)
        else:
            summary["stats"]["error"] += 1
            print(f"  /v1/search: ERROR ({res['duration_seconds']}s) - {res['error_message']}", flush=True)

        summary["queries"][q] = res

    if latencies:
        summary["stats"]["avg_latency_s"] = round(sum(latencies) / len(latencies), 2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 75, flush=True)
    print("VAGUE SEARCH TEST SUMMARY", flush=True)
    print("=" * 75, flush=True)
    print(f"Success: {summary['stats']['success']}/{len(VAGUE_QUERIES)} | Avg Latency: {summary['stats']['avg_latency_s']}s", flush=True)
    print(f"Full details saved to: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    run_tests()
