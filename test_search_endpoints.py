import json
import os
import random
import time
from datetime import datetime
from main import api

# List of varied random search queries across different domains
SEARCH_QUERIES = [
    "Kerala Ayurveda Panchakarma wellness treatments",
    "Quantum computing algorithms and applications 2025",
    "Best James Webb Space Telescope discoveries",
    "How to make authentic Italian Carbonara recipe",
    "Global economic outlook inflation interest rates 2025",
    "Machine learning transformer architecture explained",
    "History of the Ancient Library of Alexandria",
    "Python 3.12 performance vs CPython 3.13 free threading",
    "c++ vs rust memory safety concurrency",
    "What is the capital of France?",
    "Supercalifragilisticexpialidocious",
    "Climate change renewable energy transition statistics"
]

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "random_search_test_results.json")

def test_search_query(query, version="v1", limit=3):
    endpoint = f"/{version}/search"
    payload = {"query": query, "limit": limit}
    
    start_time = time.time()
    try:
        res = api.post(endpoint, payload)
        duration = round(time.time() - start_time, 2)
        
        # Check result key based on endpoint version
        data = res.get("data", {})
        if version == "v1":
            results = data.get("results", [])
        else:
            results = data.get("web", [])
            
        return {
            "status": "success",
            "status_code": 200,
            "duration_seconds": duration,
            "result_count": len(results),
            "results_sample": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "snippet": r.get("snippet")[:120] + "..." if r.get("snippet") else None
                } for r in results[:2]
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
    
    print(f"Starting Random Search Query Tests for v1 and v2 endpoints...")
    print(f"Total queries to test: {len(SEARCH_QUERIES)}")
    print("=" * 70)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(SEARCH_QUERIES),
        "v1_stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "v2_stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "queries": {}
    }
    
    v1_latencies = []
    v2_latencies = []
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] Query: '{query}'")
        
        # Test V1
        v1_res = test_search_query(query, version="v1", limit=3)
        if v1_res["status"] == "success":
            summary["v1_stats"]["success"] += 1
            v1_latencies.append(v1_res["duration_seconds"])
            print(f"  v1/search: SUCCESS ({v1_res['duration_seconds']}s) - {v1_res['result_count']} results returned")
        else:
            summary["v1_stats"]["error"] += 1
            print(f"  v1/search: ERROR ({v1_res['duration_seconds']}s) - {v1_res['error_message']}")
            
        # Test V2
        v2_res = test_search_query(query, version="v2", limit=3)
        if v2_res["status"] == "success":
            summary["v2_stats"]["success"] += 1
            v2_latencies.append(v2_res["duration_seconds"])
            print(f"  v2/search: SUCCESS ({v2_res['duration_seconds']}s) - {v2_res['result_count']} results returned")
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
        
    # Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"v1 Search Endpoint -> Success: {summary['v1_stats']['success']}/{len(SEARCH_QUERIES)} | Avg Latency: {summary['v1_stats']['avg_latency_s']}s")
    print(f"v2 Search Endpoint -> Success: {summary['v2_stats']['success']}/{len(SEARCH_QUERIES)} | Avg Latency: {summary['v2_stats']['avg_latency_s']}s")
    print(f"Full outputs saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_tests()
