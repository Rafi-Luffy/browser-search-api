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

ENDPOINT = "/v1/capabilities"
CONCURRENCY = 2
DURATION_SECONDS = 10
MAX_REQUESTS = 200


def calculate_percentile(values, fraction):
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def run():
    if not api.key:
        raise RuntimeError("Set CRW_API_KEY in .env before running load test.")

    lock = threading.Lock()
    latencies = []
    failures = {}
    completed = 0
    deadline = time.monotonic() + DURATION_SECONDS

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
