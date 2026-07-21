from __future__ import annotations

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_json, print_request_error


def main() -> int:
    base_url = api_base_url()
    try:
        found = requests.get(f"{base_url}/movies/1", timeout=TIMEOUT)
        missing = requests.get(f"{base_url}/movies/999999", timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1

    print_exchange(found)
    if found.status_code != 200:
        print(found.text)
        return 1
    print_json(found.json())

    print()
    print_exchange(missing)
    detail = missing.json().get("detail", missing.text)
    print(f"Expected 404 detail: {detail}")
    return 0 if missing.status_code == 404 else 1


if __name__ == "__main__":
    raise SystemExit(main())
