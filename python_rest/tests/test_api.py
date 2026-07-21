from __future__ import annotations

import unittest

from tests.support import ApiTestCase


def replacement_payload() -> dict:
    return {
        "title": "Replacement",
        "original_title": None,
        "overview": "Entirely replaced",
        "release_date": "2024-02-29",
        "vote_average": 8.5,
        "vote_count": 12,
        "poster_path": None,
        "genres": ["Drama"],
        "original_language": "en",
    }


class GetMoviesTest(ApiTestCase):
    def test_list_has_pagination_envelope(self):
        response = self.client.get("/movies")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()), {"items", "total", "limit", "offset"}
        )
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["limit"], 20)
        self.assertEqual(response.json()["offset"], 0)
        self.assertEqual(len(response.json()["items"]), 3)

    def test_get_movie_by_local_id(self):
        response = self.client.get("/movies/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 1)
        self.assertEqual(response.json()["tmdb_id"], 11477)

    def test_unknown_movie_returns_404(self):
        response = self.client.get("/movies/999999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Movie 999999 not found"})

    def test_title_filter_is_case_insensitive(self):
        response = self.client.get("/movies", params={"title": "wEaLtH"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["title"], "Common Wealth")

    def test_year_filter_uses_release_date(self):
        response = self.client.get("/movies", params={"year": 1983})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["title"], "Silkwood")

    def test_limit_and_offset(self):
        response = self.client.get("/movies", params={"limit": 1, "offset": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["limit"], 1)
        self.assertEqual(response.json()["offset"], 1)
        self.assertEqual(response.json()["items"][0]["id"], 2)

    def test_invalid_query_parameters_return_422(self):
        invalid_parameters = [
            {"limit": 0},
            {"limit": 101},
            {"offset": -1},
            {"year": 0},
            {"year": 2200},
            {"title": "   "},
        ]
        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters):
                response = self.client.get("/movies", params=parameters)
                self.assertEqual(response.status_code, 422)


class PostMovieTest(ApiTestCase):
    def test_create_returns_defaults_location_and_local_id(self):
        response = self.client.post("/movies", json={"title": "  New Movie  "})

        self.assertEqual(response.status_code, 201)
        movie = response.json()
        self.assertEqual(response.headers["location"], f"/movies/{movie['id']}")
        self.assertEqual(movie["id"], 4)
        self.assertIsNone(movie["tmdb_id"])
        self.assertEqual(movie["title"], "New Movie")
        self.assertIsNone(movie["original_title"])
        self.assertIsNone(movie["overview"])
        self.assertIsNone(movie["release_date"])
        self.assertEqual(movie["vote_average"], 0)
        self.assertEqual(movie["vote_count"], 0)
        self.assertIsNone(movie["poster_path"])
        self.assertEqual(movie["genres"], [])
        self.assertIsNone(movie["original_language"])

    def test_empty_title_is_rejected(self):
        response = self.client.post("/movies", json={"title": " \t "})

        self.assertEqual(response.status_code, 422)

    def test_invalid_vote_average_is_rejected(self):
        response = self.client.post(
            "/movies", json={"title": "Invalid", "vote_average": 10.1}
        )

        self.assertEqual(response.status_code, 422)

    def test_client_cannot_supply_ids(self):
        for read_only_field in ("id", "tmdb_id"):
            with self.subTest(field=read_only_field):
                response = self.client.post(
                    "/movies", json={"title": "Invalid", read_only_field: 10}
                )
                self.assertEqual(response.status_code, 422)

    def test_multiple_movies_can_have_null_tmdb_id(self):
        first = self.client.post("/movies", json={"title": "First local movie"})
        second = self.client.post("/movies", json={"title": "Second local movie"})

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertNotEqual(first.json()["id"], second.json()["id"])
        self.assertIsNone(first.json()["tmdb_id"])
        self.assertIsNone(second.json()["tmdb_id"])


class PutMovieTest(ApiTestCase):
    def test_full_replacement_preserves_read_only_ids(self):
        response = self.client.put("/movies/1", json=replacement_payload())

        self.assertEqual(response.status_code, 200)
        movie = response.json()
        self.assertEqual(movie["id"], 1)
        self.assertEqual(movie["tmdb_id"], 11477)
        for field, value in replacement_payload().items():
            self.assertEqual(movie[field], value)

    def test_missing_field_is_rejected(self):
        payload = replacement_payload()
        payload.pop("overview")

        response = self.client.put("/movies/1", json=payload)

        self.assertEqual(response.status_code, 422)

    def test_read_only_ids_are_rejected(self):
        for read_only_field in ("id", "tmdb_id"):
            with self.subTest(field=read_only_field):
                payload = replacement_payload() | {read_only_field: 999}
                response = self.client.put("/movies/1", json=payload)
                self.assertEqual(response.status_code, 422)

    def test_unknown_movie_returns_404(self):
        response = self.client.put("/movies/999999", json=replacement_payload())

        self.assertEqual(response.status_code, 404)


class PatchMovieTest(ApiTestCase):
    def test_updates_one_field_and_preserves_others(self):
        before = self.client.get("/movies/1").json()

        response = self.client.patch("/movies/1", json={"title": "Updated"})

        self.assertEqual(response.status_code, 200)
        movie = response.json()
        self.assertEqual(movie["title"], "Updated")
        self.assertEqual(movie["overview"], before["overview"])
        self.assertEqual(movie["genres"], before["genres"])

    def test_updates_multiple_fields(self):
        response = self.client.patch(
            "/movies/1",
            json={"vote_average": 9.1, "vote_count": 500, "genres": [" Drama "]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["vote_average"], 9.1)
        self.assertEqual(response.json()["vote_count"], 500)
        self.assertEqual(response.json()["genres"], ["Drama"])

    def test_null_clears_nullable_field(self):
        self.client.patch("/movies/1", json={"overview": "Temporary"})

        response = self.client.patch("/movies/1", json={"overview": None})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["overview"])

    def test_empty_body_is_rejected(self):
        response = self.client.patch("/movies/1", json={})

        self.assertEqual(response.status_code, 422)

    def test_empty_title_is_rejected(self):
        response = self.client.patch("/movies/1", json={"title": "  "})

        self.assertEqual(response.status_code, 422)

    def test_null_non_nullable_fields_are_rejected(self):
        for field in ("title", "vote_average", "vote_count", "genres"):
            with self.subTest(field=field):
                response = self.client.patch("/movies/1", json={field: None})
                self.assertEqual(response.status_code, 422)

    def test_read_only_id_is_rejected(self):
        response = self.client.patch("/movies/1", json={"id": 10})

        self.assertEqual(response.status_code, 422)

    def test_unknown_movie_returns_404(self):
        response = self.client.patch("/movies/999999", json={"title": "Missing"})

        self.assertEqual(response.status_code, 404)


class DeleteMovieTest(ApiTestCase):
    def test_delete_has_no_body_and_repeated_delete_returns_404(self):
        response = self.client.delete("/movies/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")

        repeated = self.client.delete("/movies/1")
        self.assertEqual(repeated.status_code, 404)


class MetadataMethodsTest(ApiTestCase):
    def test_head_has_empty_body_and_pagination_headers(self):
        response = self.client.head(
            "/movies", params={"year": 2000, "limit": 1, "offset": 0}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.headers["x-total-count"], "1")
        self.assertEqual(response.headers["x-limit"], "1")
        self.assertEqual(response.headers["x-offset"], "0")

    def test_collection_options_has_exact_allow_header(self):
        response = self.client.options("/movies")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.headers["allow"], "GET, HEAD, POST, OPTIONS")

    def test_item_options_has_exact_allow_header(self):
        response = self.client.options("/movies/1")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers["allow"], "GET, PUT, PATCH, DELETE, OPTIONS")

    def test_trace_is_not_implemented(self):
        response = self.client.request("TRACE", "/movies")

        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
