import json
import os
import time
from datetime import datetime
from main import api

SEARCH_QUERIES = [
    "Quantum computing algorithms and applications 2026",
    "Best James Webb Space Telescope discoveries",
    "How to make authentic Italian Carbonara recipe",
    "Global economic outlook inflation interest rates",
    "Machine learning transformer architecture explained",
    "History of the Ancient Library of Alexandria",
    "Python 3.12 performance vs CPython free threading",
    "C++ vs Rust memory safety concurrency",
    "What is the capital of France?",
    "Next.js vs Remix fullstack web development",
    "Climate change renewable energy transition statistics"
]

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "random_search_test_results.json")


def test_search_query(query, limit=3):
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
            "status_code": 200,
            "duration_seconds": duration,
            "result_count": len(results),
            "results_sample": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "snippet": r.get("snippet")[:120] + "..." if r.get("snippet") else None,
                }
                for r in results[:2]
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

    print(f"Starting Universal Web Search Tests...")
    print(f"Total queries to test: {len(SEARCH_QUERIES)}")
    print("=" * 70)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(SEARCH_QUERIES),
        "stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "queries": {},
    }

    latencies = []

    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] Query: '{query}'", flush=True)

        res = test_search_query(query, limit=3)
        if res["status"] == "success":
            summary["stats"]["success"] += 1
            latencies.append(res["duration_seconds"])
            print(f"  /v1/search: SUCCESS ({res['duration_seconds']}s) - {res['result_count']} results returned", flush=True)
            for sample in res.get("results_sample", []):
                print(f"    -> {sample['title']}: {sample['url']}", flush=True)
        else:
            summary["stats"]["error"] += 1
            print(f"  /v1/search: ERROR ({res['duration_seconds']}s) - {res['error_message']}", flush=True)

        summary["queries"][query] = res

    if latencies:
        summary["stats"]["avg_latency_s"] = round(sum(latencies) / len(latencies), 2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"Universal Search -> Success: {summary['stats']['success']}/{len(SEARCH_QUERIES)} | Avg Latency: {summary['stats']['avg_latency_s']}s")
    print(f"Full outputs saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_tests()
