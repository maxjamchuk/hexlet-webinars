from __future__ import annotations

import argparse

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_json, print_request_error


REPLACEMENT = {
    "title": "Workshop Movie: Updated",
    "original_title": "Workshop Movie: Updated",
    "overview": "The entire editable representation was replaced.",
    "release_date": "2026-07-20",
    "vote_average": 8.0,
    "vote_count": 2,
    "poster_path": None,
    "genres": ["Drama"],
    "original_language": "en",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("movie_id", type=int, help="actual local ID returned by POST")
    args = parser.parse_args()
    url = f"{api_base_url()}/movies/{args.movie_id}"

    try:
        response = requests.put(url, json=REPLACEMENT, timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1

    print_exchange(response)
    if response.status_code != 200:
        print(response.text)
        return 1
    movie = response.json()
    print_json(movie)
    print(f"id stayed {movie['id']}; tmdb_id stayed {movie['tmdb_id']}")

    incomplete = REPLACEMENT.copy()
    incomplete.pop("overview")
    try:
        invalid = requests.put(url, json=incomplete, timeout=TIMEOUT)
    except requests.RequestException as error:
        print_request_error(error)
        return 1
    print()
    print_exchange(invalid)
    print("Missing a required PUT field is expected to return 422.")
    return 0 if invalid.status_code == 422 else 1


if __name__ == "__main__":
    raise SystemExit(main())
