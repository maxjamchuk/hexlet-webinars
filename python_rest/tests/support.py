from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def seed_movie(
    tmdb_id: int | None,
    title: str,
    release_date: str | None,
    *,
    original_title: str | None = None,
    overview: str | None = None,
    vote_average: float = 7.0,
    vote_count: int = 350,
    poster_path: str | None = None,
    genres: list[str] | None = None,
    original_language: str | None = "en",
) -> dict:
    return {
        "tmdb_id": tmdb_id,
        "title": title,
        "original_title": original_title,
        "overview": overview,
        "release_date": release_date,
        "vote_average": vote_average,
        "vote_count": vote_count,
        "poster_path": poster_path,
        "genres": genres or [],
        "original_language": original_language,
    }


def sample_seed() -> list[dict]:
    return [
        seed_movie(
            11477,
            "Common Wealth",
            "2000-09-29",
            original_title="La comunidad",
            genres=["Comedy", "Thriller", "Crime"],
            original_language="es",
        ),
        seed_movie(
            12502,
            "Silkwood",
            "1983-12-14",
            genres=["Drama"],
        ),
        seed_movie(
            14522,
            "Black Beauty",
            "1994-07-29",
            genres=["Family", "Adventure", "Drama"],
        ),
    ]


def write_seed(path: Path, movies: list[dict]) -> None:
    path.write_text(
        json.dumps(movies, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.resolve().as_posix()}"


class ApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        directory = Path(self.temporary_directory.name)
        self.seed_path = directory / "movies.json"
        self.database_path = directory / "movies.db"
        write_seed(self.seed_path, sample_seed())
        self.settings = Settings(
            database_url=sqlite_url(self.database_path),
            seed_path=self.seed_path,
        )
        self.client_context = TestClient(create_app(self.settings))
        self.client = self.client_context.__enter__()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.temporary_directory.cleanup()
