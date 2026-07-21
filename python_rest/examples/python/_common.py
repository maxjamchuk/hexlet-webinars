"""Small display helpers; HTTP calls stay visible in every example."""

from __future__ import annotations

import json
import os
import sys

import requests


TIMEOUT = 10


def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8080").rstrip("/")


def print_exchange(response: requests.Response) -> None:
    print(f"{response.request.method} {response.url}")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', '<missing>')}")


def print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def print_request_error(error: requests.RequestException) -> None:
    print(f"Request failed: {error}", file=sys.stderr)
