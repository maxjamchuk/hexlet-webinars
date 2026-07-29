from __future__ import annotations

import importlib.util
import io
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests


EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples" / "python"
sys.path.insert(0, str(EXAMPLES_DIR))
SPEC = importlib.util.spec_from_file_location(
    "tmdb_example", EXAMPLES_DIR / "04_tmdb_get.py"
)
tmdb_example = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(tmdb_example)


class FakeResponse:
    def __init__(self, status_code: int, url: str, body: dict):
        self.status_code = status_code
        self.url = url
        self._body = body

    def json(self) -> dict:
        return self._body


class FakeGet:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = iter(responses)
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, url: str, **kwargs):
        self.calls.append((url, kwargs))
        return next(self.responses)


class TmdbExampleTest(unittest.TestCase):
    def test_search_uses_api_key_params_and_requests_first_movie_details(self):
        api_key = "test-api-key"
        fake_get = FakeGet(
            [
                FakeResponse(
                    200,
                    f"https://api.themoviedb.org/3/search/movie?api_key={api_key}",
                    {
                        "total_results": 1,
                        "results": [
                            {
                                "id": 157336,
                                "title": "Interstellar",
                                "release_date": "2014-11-05",
                            }
                        ],
                    },
                ),
                FakeResponse(
                    200,
                    f"https://api.themoviedb.org/3/movie/157336?api_key={api_key}",
                    {
                        "title": "Interstellar",
                        "release_date": "2014-11-05",
                        "vote_average": 8.5,
                        "genres": [{"id": 878, "name": "Science Fiction"}],
                    },
                ),
            ]
        )
        output = io.StringIO()

        with redirect_stdout(output):
            result = tmdb_example.run_tmdb_example(api_key, request_get=fake_get)

        self.assertEqual(result, 0)
        self.assertEqual(len(fake_get.calls), 2)
        search_url, search_kwargs = fake_get.calls[0]
        self.assertEqual(
            search_url, "https://api.themoviedb.org/3/search/movie"
        )
        self.assertNotIn("Authorization", search_kwargs["headers"])
        self.assertEqual(search_kwargs["headers"]["Accept"], "application/json")
        self.assertEqual(
            search_kwargs["params"],
            {
                "api_key": api_key,
                "query": "Interstellar",
                "language": "en-US",
                "page": 1,
            },
        )
        details_url, details_kwargs = fake_get.calls[1]
        self.assertEqual(
            details_url, "https://api.themoviedb.org/3/movie/157336"
        )
        self.assertNotIn("Authorization", details_kwargs["headers"])
        self.assertEqual(
            details_kwargs["params"],
            {"api_key": api_key, "language": "en-US"},
        )
        self.assertNotIn(api_key, output.getvalue())

    def test_missing_api_key_has_clear_message(self):
        errors = io.StringIO()

        with patch.dict(os.environ, {}, clear=True), redirect_stderr(errors):
            result = tmdb_example.main()

        self.assertEqual(result, 1)
        self.assertIn("TMDB_API_KEY is not set", errors.getvalue())

    def test_empty_search_result_stops_without_details_request(self):
        fake_get = FakeGet(
            [
                FakeResponse(
                    200,
                    "https://api.themoviedb.org/3/search/movie?query=Interstellar",
                    {"total_results": 0, "results": []},
                )
            ]
        )

        with redirect_stdout(io.StringIO()):
            result = tmdb_example.run_tmdb_example(
                "test-api-key", request_get=fake_get
            )

        self.assertEqual(result, 0)
        self.assertEqual(len(fake_get.calls), 1)

    def test_401_is_handled_without_details_request(self):
        fake_get = FakeGet(
            [
                FakeResponse(
                    401,
                    "https://api.themoviedb.org/3/search/movie?query=Interstellar",
                    {"status_message": "Invalid API key"},
                )
            ]
        )

        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            result = tmdb_example.run_tmdb_example(
                "test-api-key", request_get=fake_get
            )

        self.assertEqual(result, 1)
        self.assertEqual(len(fake_get.calls), 1)

    def test_request_error_does_not_print_api_key(self):
        api_key = "test-api-key"
        errors = io.StringIO()

        def failing_get(*args, **kwargs):
            raise requests.RequestException(
                f"request failed for ?api_key={api_key}"
            )

        with redirect_stderr(errors):
            result = tmdb_example.run_tmdb_example(
                api_key,
                request_get=failing_get,
            )

        self.assertEqual(result, 1)
        self.assertNotIn(api_key, errors.getvalue())


if __name__ == "__main__":
    unittest.main()
