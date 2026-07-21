from __future__ import annotations

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_request_error


def main() -> int:
    base_url = api_base_url()
    try:
        head = requests.head(
            f"{base_url}/movies",
            params={"limit": 5, "offset": 2},
            timeout=TIMEOUT,
        )
        collection_options = requests.options(
            f"{base_url}/movies", timeout=TIMEOUT
        )
        item_options = requests.options(
            f"{base_url}/movies/1", timeout=TIMEOUT
        )
        trace = requests.request("TRACE", f"{base_url}/movies", timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1

    print_exchange(head)
    print(f"Body bytes: {len(head.content)}")
    for header in ("X-Total-Count", "X-Limit", "X-Offset"):
        print(f"{header}: {head.headers.get(header)}")
    print()
    print_exchange(collection_options)
    print(f"Allow: {collection_options.headers.get('allow')}")
    print()
    print_exchange(item_options)
    print(f"Allow: {item_options.headers.get('allow')}")
    print()
    print_exchange(trace)
    print("TRACE is an HTTP method, but this API does not support it.")

    expected = (200, 204, 204, 405)
    actual = (
        head.status_code,
        collection_options.status_code,
        item_options.status_code,
        trace.status_code,
    )
    return 0 if actual == expected and not head.content else 1


if __name__ == "__main__":
    raise SystemExit(main())
