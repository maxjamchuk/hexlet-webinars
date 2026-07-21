"""Application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "movies.db"
DEFAULT_SEED_PATH = PROJECT_ROOT / "data" / "movies.json"


def _sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.resolve().as_posix()}"


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    seed_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        database_url = os.getenv(
            "DATABASE_URL", _sqlite_url(DEFAULT_DATABASE_PATH)
        )
        seed_path = Path(os.getenv("MOVIES_SEED_PATH", str(DEFAULT_SEED_PATH)))
        if not seed_path.is_absolute():
            seed_path = (Path.cwd() / seed_path).resolve()
        return cls(database_url=database_url, seed_path=seed_path)
