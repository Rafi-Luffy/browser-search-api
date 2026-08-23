import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CRW_API_URL", os.getenv("API_URL", "http://localhost:8000")).rstrip("/")


class BrowserAPI:
    # Keep authentication in one reusable object; the public API URL is code configuration.
    def __init__(self, key=None):
        self.key = key or os.getenv("CRW_API_KEY", "")

    # Send JSON, raise HTTP errors, and return the decoded response.
    def request(self, path, data=None, method="GET", timeout=30, headers=None):
        headers = headers or ({} if path == "/health" else {
            "Authorization": f"Bearer {self.key}",
        })
        response = requests.request(
            method, f"{API_URL}{path}", json=data, headers=headers, timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    # Send a GET request without making examples repeat request details.
    def get(self, path, timeout=30):
        return self.request(path, timeout=timeout)

    # Send a JSON POST request with the shared authentication headers.
    def post(self, path, data, timeout=30):
        return self.request(path, data, "POST", timeout)

    # Send a DELETE request for cancellable jobs such as crawls.
    def delete(self, path, timeout=30):
        return self.request(path, method="DELETE", timeout=timeout)

    # Let requests build the multipart body for PDF uploads.
    def parse_pdf(self, pdf, filename="document.pdf", timeout=30):
        response = requests.post(
            f"{API_URL}/v2/parse",
            files={"file": (filename, pdf, "application/pdf")},
            headers={"Authorization": f"Bearer {self.key}"},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()


# One shared object is imported by smoke_test.py and every example.
api = BrowserAPI()


# Keep output formatting in one place instead of repeating print/json code.
def show(title, result):
    print(f"\n=== {title} ===\n{json.dumps(result, indent=2, ensure_ascii=False)}")


# Run a demonstration and show its error without hiding which endpoint failed.
def demo(title, action):
    try:
        show(title, action())
    except Exception as error:
        print(f"\n=== {title} ===\nError: {error}")
