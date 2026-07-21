import unittest

from scripts.export_movies_from_mongo import (
    ExportError,
    FIELD_ORDER,
    normalize_document,
    validate_movie,
    validate_movies,
)


def source_document(**overrides):
    document = {
        "id": 11477,
        "title": "Common Wealth",
        "original_title": "La comunidad",
        "overview": "After finding an enormous amount of money...",
        "release_date": "2000-09-29",
        "vote_average": 6.907,
        "vote_count": 350,
        "poster_path": "/witJ36VoxVAu62lpcyBhiKtAMAn.jpg",
        "genre_ids": [35, 53, 80],
        "original_language": "es",
    }
    document.update(overrides)
    return document


def normalized_movie(**overrides):
    movie = normalize_document(source_document())
    movie.update(overrides)
    return movie


class NormalizeDocumentTest(unittest.TestCase):
    def test_converts_mongo_document_to_seed_model(self):
        movie = normalize_document(source_document())

        self.assertEqual(tuple(movie), FIELD_ORDER)
        self.assertEqual(movie["tmdb_id"], 11477)
        self.assertEqual(movie["title"], "Common Wealth")
        self.assertEqual(movie["original_title"], "La comunidad")
        self.assertNotIn("id", movie)
        self.assertNotIn("year", movie)
        self.assertNotIn("_id", movie)

    def test_converts_genre_ids_to_names_in_source_order(self):
        movie = normalize_document(source_document(genre_ids=[35, 53, 80]))

        self.assertEqual(movie["genres"], ["Comedy", "Thriller", "Crime"])

    def test_missing_genres_become_empty_array(self):
        movie = normalize_document(source_document(genre_ids=None))

        self.assertEqual(movie["genres"], [])

    def test_rejects_unknown_genre_id(self):
        with self.assertRaisesRegex(ExportError, "unknown TMDB movie genre ID: 123"):
            normalize_document(source_document(genre_ids=[35, 123]))

    def test_rejects_empty_title(self):
        with self.assertRaisesRegex(ExportError, "title must be a non-empty string"):
            normalize_document(source_document(title="  \t"))


class ValidateMoviesTest(unittest.TestCase):
    def test_rejects_duplicate_tmdb_id(self):
        movies = [
            normalized_movie(tmdb_id=1),
            normalized_movie(tmdb_id=2),
            normalized_movie(tmdb_id=2),
        ]

        with self.assertRaisesRegex(ExportError, "duplicate tmdb_id: 2"):
            validate_movies(movies, expected_count=3)

    def test_rejects_wrong_sort_order(self):
        movies = [
            normalized_movie(tmdb_id=2, vote_count=351),
            normalized_movie(tmdb_id=1, vote_count=350),
        ]

        with self.assertRaisesRegex(ExportError, "not sorted"):
            validate_movies(movies, expected_count=2)

    def test_accepts_vote_count_then_tmdb_id_sort_order(self):
        movies = [
            normalized_movie(tmdb_id=1, vote_count=350),
            normalized_movie(tmdb_id=2, vote_count=350),
            normalized_movie(tmdb_id=3, vote_count=351),
        ]

        validate_movies(movies, expected_count=3)

    def test_rejects_invalid_release_date_format(self):
        movie = normalized_movie(release_date="29-09-2000")

        with self.assertRaisesRegex(ExportError, "YYYY-MM-DD"):
            validate_movie(movie)

    def test_rejects_invalid_calendar_date(self):
        movie = normalized_movie(release_date="2000-02-30")

        with self.assertRaisesRegex(ExportError, "YYYY-MM-DD"):
            validate_movie(movie)


if __name__ == "__main__":
    unittest.main()
