from __future__ import annotations

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_request_error


CASES = [
    ({"title": "whiplash"}, 200),
    ({"year": 2013}, 200),
    ({"limit": 5, "offset": 10}, 200),
    ({"title": "whiplash", "year": 2013}, 200),
    ({"limit": 0}, 422),
]


def main() -> int:
    for params, expected_status in CASES:
        try:
            response = requests.get(
                f"{api_base_url()}/movies", params=params, timeout=TIMEOUT
            )
        except requests.RequestException as error:
            print_request_error(error)
            return 1

        print_exchange(response)
        body = response.json()
        if response.status_code == 200:
            print(f"items={len(body['items'])}, total={body['total']}")
        else:
            print(f"validation detail entries={len(body.get('detail', []))}")
        print()
        if response.status_code != expected_status:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
