from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sqlalchemy import func, select

from app.database import Database, SeedError
from app.models import Movie
from tests.support import sample_seed, seed_movie, sqlite_url, write_seed


class SeedInitializationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.seed_path = self.directory / "movies.json"
        self.database = Database(sqlite_url(self.directory / "movies.db"))

    def tearDown(self) -> None:
        self.database.dispose()
        self.temporary_directory.cleanup()

    def test_empty_database_is_populated_from_seed(self):
        write_seed(self.seed_path, sample_seed())

        imported = self.database.initialize(self.seed_path)

        self.assertTrue(imported)
        with self.database.session_factory() as session:
            count = session.scalar(select(func.count(Movie.id)))
        self.assertEqual(count, 3)

    def test_repeated_initialization_does_not_duplicate_movies(self):
        write_seed(self.seed_path, sample_seed())

        self.assertTrue(self.database.initialize(self.seed_path))
        self.assertFalse(self.database.initialize(self.seed_path))

        with self.database.session_factory() as session:
            count = session.scalar(select(func.count(Movie.id)))
        self.assertEqual(count, 3)

    def test_repeated_initialization_does_not_overwrite_changes(self):
        write_seed(self.seed_path, sample_seed())
        self.database.initialize(self.seed_path)
        with self.database.session_factory.begin() as session:
            movie = session.get(Movie, 1)
            movie.title = "User edited title"

        self.assertFalse(self.database.initialize(self.seed_path))

        with self.database.session_factory() as session:
            movie = session.get(Movie, 1)
            self.assertEqual(movie.title, "User edited title")

    def test_seed_order_and_tmdb_ids_are_preserved(self):
        write_seed(self.seed_path, sample_seed())

        self.database.initialize(self.seed_path)

        with self.database.session_factory() as session:
            movies = list(session.scalars(select(Movie).order_by(Movie.id)))
        self.assertEqual([movie.id for movie in movies], [1, 2, 3])
        self.assertEqual(
            [movie.tmdb_id for movie in movies], [11477, 12502, 14522]
        )

    def test_invalid_seed_is_rejected_without_partial_import(self):
        movies = sample_seed()
        movies[1]["title"] = "   "
        write_seed(self.seed_path, movies)

        with self.assertRaisesRegex(SeedError, "invalid seed movie #2"):
            self.database.initialize(self.seed_path)

        with self.database.session_factory() as session:
            count = session.scalar(select(func.count(Movie.id)))
        self.assertEqual(count, 0)

    def test_duplicate_tmdb_id_is_rejected(self):
        write_seed(
            self.seed_path,
            [
                seed_movie(42, "First", "2000-01-01"),
                seed_movie(42, "Second", "2001-01-01"),
            ],
        )

        with self.assertRaisesRegex(SeedError, "duplicate tmdb_id 42"):
            self.database.initialize(self.seed_path)

    def test_missing_seed_is_reported_clearly_for_empty_database(self):
        with self.assertRaisesRegex(SeedError, "seed file not found"):
            self.database.initialize(self.seed_path)


if __name__ == "__main__":
    unittest.main()
