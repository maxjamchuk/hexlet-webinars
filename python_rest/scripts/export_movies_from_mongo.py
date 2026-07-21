"""Export a deterministic, validated movie seed from Kadracoon MongoDB."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_MONGODB_URI = "mongodb://localhost:27017"
DEFAULT_DATABASE = "tmdb"
DEFAULT_COLLECTION = "movies"
DEFAULT_OUTPUT_PATH = "data/movies.json"
DEFAULT_LIMIT = 1000

FIELD_ORDER = (
    "tmdb_id",
    "title",
    "original_title",
    "overview",
    "release_date",
    "vote_average",
    "vote_count",
    "poster_path",
    "genres",
    "original_language",
)

TMDB_MOVIE_GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

MONGO_FILTER = {
    "vote_count": {"$gt": 0},
    "id": {"$exists": True, "$type": "int", "$gt": 0},
    "title": {"$exists": True, "$type": "string", "$regex": r"\S"},
}

MONGO_PROJECTION = {
    "_id": 0,
    "id": 1,
    "title": 1,
    "original_title": 1,
    "overview": 1,
    "release_date": 1,
    "vote_average": 1,
    "vote_count": 1,
    "poster_path": 1,
    "genre_ids": 1,
    "original_language": 1,
}


class ExportError(ValueError):
    """Raised when source or normalized seed data violates the contract."""


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_integer(value: object, field: str) -> int:
    if not _is_integer(value):
        raise ExportError(f"{field} must be an integer, got {type(value).__name__}")
    return int(value)


def _require_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ExportError(f"{field} must be a number, got {type(value).__name__}")
    number = float(value)
    if not math.isfinite(number):
        raise ExportError(f"{field} must be finite")
    return number


def _nullable_string(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ExportError(f"{field} must be a string or null")
    if not value.strip():
        return None
    return value


def _normalize_genres(genre_ids: object) -> list[str]:
    if genre_ids is None:
        return []
    if not isinstance(genre_ids, list):
        raise ExportError("genre_ids must be an array or null")

    genres: list[str] = []
    for genre_id in genre_ids:
        normalized_id = _require_integer(genre_id, "genre_id")
        try:
            genres.append(TMDB_MOVIE_GENRES[normalized_id])
        except KeyError as error:
            raise ExportError(
                f"unknown TMDB movie genre ID: {normalized_id}"
            ) from error
    return genres


def normalize_document(document: Mapping[str, Any]) -> dict[str, Any]:
    """Convert one MongoDB movie document to the stable seed representation."""
    tmdb_id = _require_integer(document.get("id"), "id")

    title = document.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ExportError("title must be a non-empty string")

    movie = {
        "tmdb_id": tmdb_id,
        "title": title.strip(),
        "original_title": _nullable_string(
            document.get("original_title"), "original_title"
        ),
        "overview": _nullable_string(document.get("overview"), "overview"),
        "release_date": _nullable_string(
            document.get("release_date"), "release_date"
        ),
        "vote_average": _require_number(
            document.get("vote_average"), "vote_average"
        ),
        "vote_count": _require_integer(document.get("vote_count"), "vote_count"),
        "poster_path": _nullable_string(
            document.get("poster_path"), "poster_path"
        ),
        "genres": _normalize_genres(document.get("genre_ids")),
        "original_language": _nullable_string(
            document.get("original_language"), "original_language"
        ),
    }
    validate_movie(movie)
    return movie


def validate_movie(movie: Mapping[str, Any]) -> None:
    """Validate one normalized movie and its stable field order."""
    if tuple(movie) != FIELD_ORDER:
        raise ExportError(
            "movie fields must be exactly in this order: " + ", ".join(FIELD_ORDER)
        )

    tmdb_id = movie["tmdb_id"]
    if not _is_integer(tmdb_id) or tmdb_id <= 0:
        raise ExportError("tmdb_id must be a positive integer")

    title = movie["title"]
    if not isinstance(title, str) or not title.strip():
        raise ExportError("title must be a non-empty string")

    for field in (
        "original_title",
        "overview",
        "release_date",
        "poster_path",
        "original_language",
    ):
        value = movie[field]
        if value is not None and not isinstance(value, str):
            raise ExportError(f"{field} must be a string or null")

    release_date = movie["release_date"]
    if release_date is not None:
        try:
            parsed_date = datetime.strptime(release_date, "%Y-%m-%d")
        except ValueError as error:
            raise ExportError(
                "release_date must be null or a valid date in YYYY-MM-DD format"
            ) from error
        if parsed_date.strftime("%Y-%m-%d") != release_date:
            raise ExportError(
                "release_date must be null or a valid date in YYYY-MM-DD format"
            )

    vote_count = movie["vote_count"]
    if not _is_integer(vote_count) or vote_count < 0:
        raise ExportError("vote_count must be a non-negative integer")

    vote_average = movie["vote_average"]
    if (
        isinstance(vote_average, bool)
        or not isinstance(vote_average, (int, float))
        or not math.isfinite(float(vote_average))
        or not 0 <= vote_average <= 10
    ):
        raise ExportError("vote_average must be a finite number from 0 to 10")

    genres = movie["genres"]
    if not isinstance(genres, list) or any(
        not isinstance(genre, str) or not genre for genre in genres
    ):
        raise ExportError("genres must be an array of non-empty strings")


def validate_movies(
    movies: Sequence[Mapping[str, Any]], expected_count: int = DEFAULT_LIMIT
) -> None:
    """Validate the complete export, including uniqueness and sort order."""
    if len(movies) != expected_count:
        raise ExportError(
            f"expected {expected_count} movies, got {len(movies)}"
        )

    for index, movie in enumerate(movies):
        try:
            validate_movie(movie)
        except ExportError as error:
            raise ExportError(f"movie #{index + 1}: {error}") from error

    tmdb_ids = [movie["tmdb_id"] for movie in movies]
    if len(tmdb_ids) != len(set(tmdb_ids)):
        seen: set[int] = set()
        duplicate: int | None = None
        for tmdb_id in tmdb_ids:
            if tmdb_id in seen:
                duplicate = tmdb_id
                break
            seen.add(tmdb_id)
        raise ExportError(f"duplicate tmdb_id: {duplicate}")

    actual_order = [
        (movie["vote_count"], movie["tmdb_id"]) for movie in movies
    ]
    expected_order = sorted(actual_order)
    if actual_order != expected_order:
        mismatch = next(
            index
            for index, pair in enumerate(actual_order)
            if pair != expected_order[index]
        )
        raise ExportError(
            "movies are not sorted by vote_count ASC, tmdb_id ASC "
            f"at position {mismatch + 1}"
        )

    if movies:
        vote_counts = [movie["vote_count"] for movie in movies]
        if movies[0]["vote_count"] != min(vote_counts):
            raise ExportError("the first movie does not have the minimum vote_count")
        if movies[-1]["vote_count"] != max(vote_counts):
            raise ExportError("the last movie does not have the maximum vote_count")


def fetch_documents(
    mongodb_uri: str,
    database_name: str,
    collection_name: str,
    limit: int,
) -> list[dict[str, Any]]:
    """Read the source documents with one deterministic MongoDB find query."""
    try:
        from pymongo import ASCENDING, MongoClient
        from pymongo.errors import PyMongoError
    except ImportError as error:
        raise ExportError(
            "pymongo is required; install dependencies from requirements.txt"
        ) from error

    try:
        with MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000) as client:
            collection = client[database_name][collection_name]
            cursor = (
                collection.find(MONGO_FILTER, MONGO_PROJECTION)
                .sort([("vote_count", ASCENDING), ("id", ASCENDING)])
                .limit(limit)
            )
            return list(cursor)
    except PyMongoError as error:
        raise ExportError(
            f"failed to read MongoDB collection "
            f"{database_name}.{collection_name}: {error}"
        ) from error


def write_json(movies: Sequence[Mapping[str, Any]], output_path: Path) -> None:
    """Atomically write UTF-8 JSON with deterministic formatting."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(movies, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
        os.replace(temporary_path, output_path)
    except OSError as error:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise ExportError(f"failed to write {output_path}: {error}") from error


def export_movies(
    mongodb_uri: str,
    database_name: str,
    collection_name: str,
    output_path: Path,
    limit: int,
) -> list[dict[str, Any]]:
    documents = fetch_documents(
        mongodb_uri, database_name, collection_name, limit
    )
    movies: list[dict[str, Any]] = []
    for index, document in enumerate(documents):
        try:
            movies.append(normalize_document(document))
        except ExportError as error:
            source_id = document.get("id", "missing")
            raise ExportError(
                f"source document #{index + 1} (id={source_id}): {error}"
            ) from error

    validate_movies(movies, expected_count=limit)
    write_json(movies, output_path)
    return movies


def _positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a deterministic Kadracoon movie seed from MongoDB."
    )
    parser.add_argument(
        "--mongodb-uri",
        default=os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI),
        help="MongoDB URI (env: MONGODB_URI)",
    )
    parser.add_argument(
        "--database",
        default=os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE),
        help="database name (env: MONGODB_DATABASE)",
    )
    parser.add_argument(
        "--collection",
        default=os.getenv("MONGODB_COLLECTION", DEFAULT_COLLECTION),
        help="collection name (env: MONGODB_COLLECTION)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.getenv("MOVIES_OUTPUT_PATH", DEFAULT_OUTPUT_PATH)),
        help="output JSON path (env: MOVIES_OUTPUT_PATH)",
    )
    parser.add_argument(
        "--limit",
        type=_positive_integer,
        default=os.getenv("MOVIES_EXPORT_LIMIT", str(DEFAULT_LIMIT)),
        help="number of movies (env: MOVIES_EXPORT_LIMIT)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.database.strip():
        print("Export failed: database name must not be empty", file=sys.stderr)
        return 1
    if not args.collection.strip():
        print("Export failed: collection name must not be empty", file=sys.stderr)
        return 1

    try:
        movies = export_movies(
            mongodb_uri=args.mongodb_uri,
            database_name=args.database,
            collection_name=args.collection,
            output_path=args.output,
            limit=args.limit,
        )
    except ExportError as error:
        print(f"Export failed: {error}", file=sys.stderr)
        return 1

    print(
        f"Exported {len(movies)} movies to {args.output} "
        f"(vote_count {movies[0]['vote_count']}..{movies[-1]['vote_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
