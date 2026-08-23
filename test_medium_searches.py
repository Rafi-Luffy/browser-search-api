import json
import os
import time
from datetime import datetime
from main import api

MEDIUM_QUERIES = [
    "site:medium.com machine learning system design",
    "site:medium.com python performance optimization",
    "site:medium.com building microservices go vs rust",
    "site:medium.com frontend architecture tailwind react",
    "site:medium.com startup growth engineering strategies",
    "site:medium.com devops kubernetes deployment pipelines",
    "site:medium.com vector database rag architecture",
    "site:medium.com cyber security zero trust architecture",
]

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "medium_search_test_results.json")


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
            "duration_seconds": duration,
            "result_count": len(results),
            "results": [
                {
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

    print("Starting Domain-Restricted Search Tests (site:medium.com)...", flush=True)
    print(f"Total queries: {len(MEDIUM_QUERIES)}", flush=True)
    print("=" * 70, flush=True)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(MEDIUM_QUERIES),
        "stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "queries": {},
    }

    latencies = []

    for i, query in enumerate(MEDIUM_QUERIES, 1):
        print(f"\n[{i}/{len(MEDIUM_QUERIES)}] Query: '{query}'", flush=True)

        res = test_search_query(query, limit=3)
        if res["status"] == "success":
            summary["stats"]["success"] += 1
            latencies.append(res["duration_seconds"])
            print(f"  /v1/search: SUCCESS ({res['duration_seconds']}s) - {res['result_count']} results", flush=True)
            for idx, r in enumerate(res["results"], 1):
                print(f"     {idx}. {r['title']} -> {r['url']}", flush=True)
        else:
            summary["stats"]["error"] += 1
            print(f"  /v1/search: ERROR ({res['duration_seconds']}s) - {res['error_message']}", flush=True)

        summary["queries"][query] = res

    if latencies:
        summary["stats"]["avg_latency_s"] = round(sum(latencies) / len(latencies), 2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70, flush=True)
    print("MEDIUM SEARCH TEST SUMMARY", flush=True)
    print("=" * 70, flush=True)
    print(f"Success: {summary['stats']['success']}/{len(MEDIUM_QUERIES)} | Avg Latency: {summary['stats']['avg_latency_s']}s", flush=True)
    print(f"Saved to: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    run_tests()
