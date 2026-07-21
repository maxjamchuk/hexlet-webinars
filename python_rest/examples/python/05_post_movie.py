from __future__ import annotations

import argparse

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_json, print_request_error


MINIMAL_PAYLOAD = {"title": "Workshop Movie"}
FULL_PAYLOAD = {
    "title": "Workshop Movie",
    "original_title": "Workshop Movie",
    "overview": "A movie created during the REST API workshop.",
    "release_date": "2026-07-19",
    "vote_average": 7.5,
    "vote_count": 1,
    "poster_path": None,
    "genres": ["Comedy"],
    "original_language": "en",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full", action="store_true", help="send the complete example payload"
    )
    args = parser.parse_args()
    payload = FULL_PAYLOAD if args.full else MINIMAL_PAYLOAD
    url = f"{api_base_url()}/movies"

    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1

    print_exchange(response)
    print(f"Location: {response.headers.get('location', '<missing>')}")
    if response.status_code != 201:
        print(response.text)
        return 1
    movie = response.json()
    print_json(movie)
    print(f"Created local id: {movie['id']}; tmdb_id: {movie['tmdb_id']}")

    try:
        invalid = requests.post(url, json={"title": "   "}, timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1
    print()
    print_exchange(invalid)
    print("Empty title is expected to return 422.")
    return 0 if invalid.status_code == 422 else 1


if __name__ == "__main__":
    raise SystemExit(main())
