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
    "site:medium.com cyber security zero trust architecture"
]

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "medium_search_test_results.json")

def test_search_query(query, version="v1", limit=3):
    endpoint = f"/{version}/search"
    payload = {"query": query, "limit": limit}
    
    start_time = time.time()
    try:
        res = api.post(endpoint, payload)
        duration = round(time.time() - start_time, 2)
        
        data = res.get("data", {})
        results = data.get("results", []) if version == "v1" else data.get("web", [])
            
        return {
            "status": "success",
            "duration_seconds": duration,
            "result_count": len(results),
            "results": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "snippet": r.get("snippet")
                } for r in results
            ],
            "raw_response": res
        }
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        return {
            "status": "error",
            "error_message": str(e),
            "duration_seconds": duration,
            "result_count": 0,
            "raw_response": None
        }

def run_tests():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Starting Medium.com Search Tests for v1 and v2 endpoints...")
    print(f"Total queries: {len(MEDIUM_QUERIES)}")
    print("=" * 70)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(MEDIUM_QUERIES),
        "v1_stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "v2_stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "queries": {}
    }
    
    v1_latencies = []
    v2_latencies = []
    
    for i, query in enumerate(MEDIUM_QUERIES, 1):
        print(f"\n[{i}/{len(MEDIUM_QUERIES)}] Query: '{query}'")
        
        # Test V1
        v1_res = test_search_query(query, version="v1", limit=3)
        if v1_res["status"] == "success":
            summary["v1_stats"]["success"] += 1
            v1_latencies.append(v1_res["duration_seconds"])
            print(f"  v1/search: SUCCESS ({v1_res['duration_seconds']}s) - {v1_res['result_count']} results")
            for idx, r in enumerate(v1_res["results"], 1):
                print(f"     {idx}. {r['title']} -> {r['url']}")
        else:
            summary["v1_stats"]["error"] += 1
            print(f"  v1/search: ERROR ({v1_res['duration_seconds']}s) - {v1_res['error_message']}")
            
        # Test V2
        v2_res = test_search_query(query, version="v2", limit=3)
        if v2_res["status"] == "success":
            summary["v2_stats"]["success"] += 1
            v2_latencies.append(v2_res["duration_seconds"])
            print(f"  v2/search: SUCCESS ({v2_res['duration_seconds']}s) - {v2_res['result_count']} results")
            for idx, r in enumerate(v2_res["results"], 1):
                print(f"     {idx}. {r['title']} -> {r['url']}")
        else:
            summary["v2_stats"]["error"] += 1
            print(f"  v2/search: ERROR ({v2_res['duration_seconds']}s) - {v2_res['error_message']}")
            
        summary["queries"][query] = {
            "v1": v1_res,
            "v2": v2_res
        }

    if v1_latencies:
        summary["v1_stats"]["avg_latency_s"] = round(sum(v1_latencies) / len(v1_latencies), 2)
    if v2_latencies:
        summary["v2_stats"]["avg_latency_s"] = round(sum(v2_latencies) / len(v2_latencies), 2)
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 70)
    print("MEDIUM SEARCH TEST SUMMARY")
    print("=" * 70)
    print(f"v1 Search Endpoint -> Success: {summary['v1_stats']['success']}/{len(MEDIUM_QUERIES)} | Avg Latency: {summary['v1_stats']['avg_latency_s']}s")
    print(f"v2 Search Endpoint -> Success: {summary['v2_stats']['success']}/{len(MEDIUM_QUERIES)} | Avg Latency: {summary['v2_stats']['avg_latency_s']}s")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_tests()
