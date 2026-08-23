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
    {"query": "best way", "category": "incomplete_phrase", "note": "Incomplete query with no subject"}
]

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "vague_search_test_results.json")

def test_search_query(query, version="v1", limit=4):
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
                    "position": r.get("position"),
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
    
    print("Starting Vague & Ambiguous Search Query Tests (v1 vs v2)...")
    print(f"Total vague queries: {len(VAGUE_QUERIES)}")
    print("=" * 75)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(VAGUE_QUERIES),
        "v1_stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "v2_stats": {"success": 0, "error": 0, "avg_latency_s": 0.0},
        "queries": {}
    }
    
    v1_latencies = []
    v2_latencies = []
    
    for i, item in enumerate(VAGUE_QUERIES, 1):
        query = item["query"]
        note = item["note"]
        print(f"\n[{i}/{len(VAGUE_QUERIES)}] Query: '{query}' ({note})")
        
        # Test V1
        v1_res = test_search_query(query, version="v1", limit=4)
        if v1_res["status"] == "success":
            summary["v1_stats"]["success"] += 1
            v1_latencies.append(v1_res["duration_seconds"])
            print(f"  v1/search: SUCCESS ({v1_res['duration_seconds']}s) - {v1_res['result_count']} results")
            for r in v1_res["results"]:
                print(f"     [Pos {r['position']}] {r['title']} ({r['url']})")
        else:
            summary["v1_stats"]["error"] += 1
            print(f"  v1/search: ERROR ({v1_res['duration_seconds']}s) - {v1_res['error_message']}")
            
        # Test V2
        v2_res = test_search_query(query, version="v2", limit=4)
        if v2_res["status"] == "success":
            summary["v2_stats"]["success"] += 1
            v2_latencies.append(v2_res["duration_seconds"])
            print(f"  v2/search: SUCCESS ({v2_res['duration_seconds']}s) - {v2_res['result_count']} results")
            for r in v2_res["results"]:
                print(f"     [Pos {r['position']}] {r['title']} ({r['url']})")
        else:
            summary["v2_stats"]["error"] += 1
            print(f"  v2/search: ERROR ({v2_res['duration_seconds']}s) - {v2_res['error_message']}")
            
        summary["queries"][query] = {
            "meta": item,
            "v1": v1_res,
            "v2": v2_res
        }

    if v1_latencies:
        summary["v1_stats"]["avg_latency_s"] = round(sum(v1_latencies) / len(v1_latencies), 2)
    if v2_latencies:
        summary["v2_stats"]["avg_latency_s"] = round(sum(v2_latencies) / len(v2_latencies), 2)
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 75)
    print("VAGUE SEARCH TEST SUMMARY")
    print("=" * 75)
    print(f"v1 Search Endpoint -> Success: {summary['v1_stats']['success']}/{len(VAGUE_QUERIES)} | Avg Latency: {summary['v1_stats']['avg_latency_s']}s")
    print(f"v2 Search Endpoint -> Success: {summary['v2_stats']['success']}/{len(VAGUE_QUERIES)} | Avg Latency: {summary['v2_stats']['avg_latency_s']}s")
    print(f"Full details saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_tests()
