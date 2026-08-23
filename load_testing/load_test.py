# Measure request throughput and latency against a lightweight API endpoint.
# Threads run until the duration or maximum-request limit is reached.

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import median

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests
from main import API_URL, api

# ==============================================================================
# Load Test Configuration
# ==============================================================================
# API_URL is imported from main.py (respects CRW_API_URL / .env)

# API endpoint to test (default to lightweight route)
ENDPOINT = "/v1/capabilities"

# Number of concurrent threads sending requests
CONCURRENCY = 2

# Duration limit in seconds
DURATION_SECONDS = 10

# Maximum number of total requests allowed across all threads
MAX_REQUESTS = 200
# ==============================================================================


# Return the value at a percentile, or zero when no requests succeeded.
def calculate_percentile(values, fraction):
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


# Run the concurrent load test and print a compact result summary.
def run():
    if not api.key:
        raise RuntimeError("Set CRW_API_KEY in .env before running load test.")

    lock = threading.Lock()
    latencies = []
    failures = {}
    completed = 0
    deadline = time.monotonic() + DURATION_SECONDS

    # Reserve request slots and record either latency or a failure category.
    def send_request():
        nonlocal completed
        while time.monotonic() < deadline:
            with lock:
                if completed >= MAX_REQUESTS:
                    return
                completed += 1
            started = time.monotonic()
            try:
                response = requests.get(
                    f"{API_URL}{ENDPOINT}",
                    headers={"Authorization": f"Bearer {api.key}"},
                    timeout=30,
                )
                response.raise_for_status()
                with lock:
                    latencies.append(time.monotonic() - started)
            except requests.HTTPError as error:
                name = str(error.response.status_code) if error.response is not None else type(error).__name__
                with lock:
                    failures[name] = failures.get(name, 0) + 1
            except requests.RequestException as error:
                name = type(error).__name__
                with lock:
                    failures[name] = failures.get(name, 0) + 1

    started = time.monotonic()
    deadline = started + DURATION_SECONDS
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_request) for _ in range(CONCURRENCY)]
        for f in futures:
            f.result()
    elapsed = max(time.monotonic() - started, 0.001)

    succeeded = len(latencies)
    failed = sum(failures.values())

    # A dictionary makes the report easy to print, save, or send elsewhere.
    summary = {
        "endpoint": ENDPOINT,
        "concurrency": CONCURRENCY,
        "elapsed_seconds": round(elapsed, 2),
        "succeeded": succeeded,
        "failed": failed,
        "successful_rps": round(succeeded / elapsed, 2),
    }
    if latencies:
        summary["latency_ms"] = {
            "p50": round(median(latencies) * 1_000, 1),
            "p95": round(calculate_percentile(latencies, 0.95) * 1_000, 1),
            "max": round(max(latencies) * 1_000, 1),
        }
    if failures:
        summary["failures_by_type"] = failures
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
