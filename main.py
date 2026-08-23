import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CRW_API_URL", os.getenv("API_URL", "http://localhost:8000")).rstrip("/")


class BrowserAPI:
    def __init__(self, key=None):
        self.key = key or os.getenv("CRW_API_KEY", "")

    def request(self, path, data=None, method="GET", timeout=30, headers=None):
        headers = headers or ({} if path == "/health" else {
            "Authorization": f"Bearer {self.key}",
        })
        response = requests.request(
            method, f"{API_URL}{path}", json=data, headers=headers, timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    def get(self, path, timeout=30):
        return self.request(path, timeout=timeout)

    def post(self, path, data, timeout=30):
        return self.request(path, data, "POST", timeout)

    def delete(self, path, timeout=30):
        return self.request(path, method="DELETE", timeout=timeout)

    def parse_pdf(self, pdf, filename="document.pdf", timeout=30):
        response = requests.post(
            f"{API_URL}/v1/parse",
            files={"file": (filename, pdf, "application/pdf")},
            headers={"Authorization": f"Bearer {self.key}"},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()


api = BrowserAPI()


def show(title, result):
    print(f"\n=== {title} ===\n{json.dumps(result, indent=2, ensure_ascii=False)}")


def demo(title, action):
    try:
        show(title, action())
    except Exception as error:
        print(f"\n=== {title} ===\nError: {error}")
