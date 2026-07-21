from __future__ import annotations

import argparse

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_json, print_request_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("movie_id", type=int, help="actual local ID returned by POST")
    args = parser.parse_args()
    url = f"{api_base_url()}/movies/{args.movie_id}"

    try:
        before = requests.get(url, timeout=TIMEOUT)
        response = requests.patch(
            url,
            json={"vote_average": 9.0, "genres": ["Drama", "Comedy"]},
            timeout=TIMEOUT,
        )
    except requests.RequestException as error:
        print_request_error(error)
        return 1

    print_exchange(response)
    if before.status_code != 200 or response.status_code != 200:
        print(response.text)
        return 1
    movie = response.json()
    print_json(movie)
    print(f"title was preserved: {movie['title'] == before.json()['title']}")

    try:
        cleared = requests.patch(url, json={"overview": None}, timeout=TIMEOUT)
        empty = requests.patch(url, json={}, timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1
    print()
    print_exchange(cleared)
    print(f"overview after explicit null: {cleared.json().get('overview')}")
    print()
    print_exchange(empty)
    print("An empty PATCH body is expected to return 422.")
    return 0 if cleared.status_code == 200 and empty.status_code == 422 else 1


if __name__ == "__main__":
    raise SystemExit(main())
