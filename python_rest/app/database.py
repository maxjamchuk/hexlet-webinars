"""SQLite engine setup and transactional seed initialization."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base, Movie
from .schemas import MovieSeed


class SeedError(RuntimeError):
    """Raised when a fresh database cannot be initialized from its seed."""


def load_seed(seed_path: Path) -> list[MovieSeed]:
    try:
        with seed_path.open(encoding="utf-8") as seed_file:
            raw_movies: Any = json.load(seed_file)
    except FileNotFoundError as error:
        raise SeedError(f"seed file not found: {seed_path}") from error
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SeedError(f"cannot read seed file {seed_path}: {error}") from error

    if not isinstance(raw_movies, list):
        raise SeedError("seed root must be a JSON array")
    if not raw_movies:
        raise SeedError("seed must contain at least one movie")

    movies: list[MovieSeed] = []
    for index, raw_movie in enumerate(raw_movies):
        try:
            movies.append(MovieSeed.model_validate(raw_movie))
        except ValidationError as error:
            raise SeedError(f"invalid seed movie #{index + 1}: {error}") from error

    seen_tmdb_ids: set[int] = set()
    for index, movie in enumerate(movies):
        if movie.tmdb_id is None:
            continue
        if movie.tmdb_id in seen_tmdb_ids:
            raise SeedError(
                f"duplicate tmdb_id {movie.tmdb_id} in seed movie #{index + 1}"
            )
        seen_tmdb_ids.add(movie.tmdb_id)
    return movies


class Database:
    def __init__(self, database_url: str):
        url = make_url(database_url)
        if url.get_backend_name() != "sqlite":
            raise ValueError("only SQLite DATABASE_URL values are supported")

        connect_args = {"check_same_thread": False}
        engine_options: dict[str, Any] = {"connect_args": connect_args}
        if url.database in (None, "", ":memory:"):
            engine_options["poolclass"] = StaticPool
        else:
            Path(url.database).expanduser().resolve().parent.mkdir(
                parents=True, exist_ok=True
            )

        self.engine = create_engine(database_url, **engine_options)
        self.session_factory = sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False
        )

    def initialize(self, seed_path: Path) -> bool:
        """Create tables and seed an empty movie table in one transaction."""
        Base.metadata.create_all(self.engine)
        try:
            with self.session_factory.begin() as session:
                count = session.scalar(select(func.count(Movie.id))) or 0
                if count > 0:
                    return False

                seed_movies = load_seed(seed_path)
                session.add_all(
                    [Movie(**movie.model_dump()) for movie in seed_movies]
                )
        except IntegrityError as error:
            raise SeedError(f"cannot import seed into SQLite: {error.orig}") from error
        return True

    def session(self) -> Iterator[Session]:
        with self.session_factory() as session:
            yield session

    def dispose(self) -> None:
        self.engine.dispose()
