from __future__ import annotations

import argparse

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_request_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("movie_id", type=int, help="actual local ID returned by POST")
    args = parser.parse_args()
    url = f"{api_base_url()}/movies/{args.movie_id}"

    try:
        deleted = requests.delete(url, timeout=TIMEOUT)
        missing = requests.get(url, timeout=TIMEOUT)
        repeated = requests.delete(url, timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1

    print_exchange(deleted)
    print(f"Body bytes: {len(deleted.content)}")
    print("A successful 204 response has no JSON body, so .json() is not called.")
    print()
    print_exchange(missing)
    print(f"GET detail: {missing.json().get('detail')}")
    print()
    print_exchange(repeated)
    print(f"Repeated DELETE detail: {repeated.json().get('detail')}")
    return 0 if (
        deleted.status_code == 204
        and not deleted.content
        and missing.status_code == 404
        and repeated.status_code == 404
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
