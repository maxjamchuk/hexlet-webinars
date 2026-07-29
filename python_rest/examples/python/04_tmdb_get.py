from __future__ import annotations

import os
import sys
from collections.abc import Callable
from typing import Any

import requests

from _common import TIMEOUT, print_json


TMDB_BASE_URL = "https://api.themoviedb.org/3"


def run_tmdb_example(
    tmdb_api_key: str,
    request_get: Callable[..., requests.Response] = requests.get,
) -> int:
    headers = {"Accept": "application/json"}
    search_params = {
        "api_key": tmdb_api_key,
        "query": "Interstellar",
        "language": "en-US",
        "page": 1,
    }

    try:
        search_response = request_get(
            f"{TMDB_BASE_URL}/search/movie",
            headers=headers,
            params=search_params,
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        print("TMDB search request failed.", file=sys.stderr)
        return 1

    print("GET /search/movie")
    print(f"Status: {search_response.status_code}")
    if search_response.status_code == 401:
        print("TMDB rejected the API Key v3 (401 Unauthorized).", file=sys.stderr)
        return 1
    if search_response.status_code != 200:
        print(f"Unexpected TMDB status: {search_response.status_code}", file=sys.stderr)
        return 1

    search_data: dict[str, Any] = search_response.json()
    results = search_data.get("results", [])
    print(f"Total results: {search_data.get('total_results', len(results))}")
    print("First results:")
    print_json(
        [
            {"id": movie.get("id"), "title": movie.get("title"), "release_date": movie.get("release_date")}
            for movie in results[:3]
        ]
    )
    if not results:
        print("TMDB returned no movies for this query.")
        return 0

    movie_id = results[0]["id"]
    try:
        details_response = request_get(
            f"{TMDB_BASE_URL}/movie/{movie_id}",
            headers=headers,
            params={"api_key": tmdb_api_key, "language": "en-US"},
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        print("TMDB details request failed.", file=sys.stderr)
        return 1

    print(f"GET /movie/{movie_id}")
    print(f"Status: {details_response.status_code}")
    if details_response.status_code == 401:
        print("TMDB rejected the API Key v3 (401 Unauthorized).", file=sys.stderr)
        return 1
    if details_response.status_code != 200:
        print(f"Unexpected TMDB status: {details_response.status_code}", file=sys.stderr)
        return 1

    details = details_response.json()
    print_json(
        {
            "title": details.get("title"),
            "release_date": details.get("release_date"),
            "vote_average": details.get("vote_average"),
            "genres": [genre.get("name") for genre in details.get("genres", [])],
        }
    )
    return 0


def main() -> int:
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    if not tmdb_api_key:
        print(
            "TMDB_API_KEY is not set. Export a TMDB API Key v3 first.",
            file=sys.stderr,
        )
        return 1
    return run_tmdb_example(tmdb_api_key)


if __name__ == "__main__":
    raise SystemExit(main())
