from __future__ import annotations

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_json, print_request_error


def main() -> int:
    try:
        response = requests.get(
            f"{api_base_url()}/movies", params={"limit": 3}, timeout=TIMEOUT
        )
    except requests.RequestException as error:
        print_request_error(error)
        return 1

    print_exchange(response)
    if response.status_code != 200:
        print(response.text)
        return 1

    body = response.json()
    print("First items:")
    print_json(body["items"][:3])
    print(f"total={body['total']}, limit={body['limit']}, offset={body['offset']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
