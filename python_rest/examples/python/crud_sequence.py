"""Smoke test the whole CRUD sequence and remove only its own movie."""

from __future__ import annotations

import requests

from _common import TIMEOUT, api_base_url, print_exchange, print_request_error


CREATE_PAYLOAD = {"title": "Temporary CRUD Smoke Movie"}
REPLACE_PAYLOAD = {
    "title": "Temporary CRUD Smoke Movie: PUT",
    "original_title": None,
    "overview": "Full replacement from the CRUD smoke test.",
    "release_date": "2026-07-19",
    "vote_average": 8.0,
    "vote_count": 2,
    "poster_path": None,
    "genres": ["Drama"],
    "original_language": "en",
}


def main() -> int:
    collection_url = f"{api_base_url()}/movies"
    created_id: int | None = None
    deleted = False

    try:
        created = requests.post(
            collection_url, json=CREATE_PAYLOAD, timeout=TIMEOUT
        )
        print_exchange(created)
        if created.status_code != 201:
            print(created.text)
            return 1
        created_id = created.json()["id"]
        movie_url = f"{collection_url}/{created_id}"
        print(f"Created actual id: {created_id}")

        replaced = requests.put(
            movie_url, json=REPLACE_PAYLOAD, timeout=TIMEOUT
        )
        print_exchange(replaced)
        if replaced.status_code != 200:
            print(replaced.text)
            return 1

        patched = requests.patch(
            movie_url,
            json={"vote_average": 9.0, "genres": ["Drama", "Comedy"]},
            timeout=TIMEOUT,
        )
        print_exchange(patched)
        if patched.status_code != 200:
            print(patched.text)
            return 1

        fetched = requests.get(movie_url, timeout=TIMEOUT)
        print_exchange(fetched)
        if fetched.status_code != 200:
            print(fetched.text)
            return 1

        removed = requests.delete(movie_url, timeout=TIMEOUT)
        print_exchange(removed)
        if removed.status_code != 204 or removed.content:
            print("DELETE did not return an empty 204 response.")
            return 1
        deleted = True

        missing = requests.get(movie_url, timeout=TIMEOUT)
        print_exchange(missing)
        if missing.status_code != 404:
            print("The deleted movie is still available.")
            return 1

        print(f"CRUD smoke test passed; temporary movie {created_id} was removed.")
        return 0
    except requests.RequestException as error:
        print_request_error(error)
        return 1
    finally:
        if created_id is not None and not deleted:
            try:
                cleanup = requests.delete(
                    f"{collection_url}/{created_id}", timeout=TIMEOUT
                )
                print(f"Cleanup DELETE status: {cleanup.status_code}")
            except requests.RequestException as error:
                print_request_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
