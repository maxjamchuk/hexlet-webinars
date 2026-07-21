"""Database queries for movies."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Movie


class MovieRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(
        self,
        *,
        title: str | None,
        year: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Movie], int]:
        filters = []
        if title is not None:
            filters.append(func.instr(func.lower(Movie.title), title.lower()) > 0)
        if year is not None:
            filters.extend(
                [
                    Movie.release_date >= date(year, 1, 1),
                    Movie.release_date < date(year + 1, 1, 1),
                ]
            )

        total = self.session.scalar(
            select(func.count(Movie.id)).where(*filters)
        ) or 0
        movies = list(
            self.session.scalars(
                select(Movie)
                .where(*filters)
                .order_by(Movie.id.asc())
                .limit(limit)
                .offset(offset)
            )
        )
        return movies, total

    def get(self, movie_id: int) -> Movie | None:
        return self.session.get(Movie, movie_id)

    def create(self, values: dict[str, Any]) -> Movie:
        movie = Movie(tmdb_id=None, **values)
        self.session.add(movie)
        self.session.commit()
        self.session.refresh(movie)
        return movie

    def update(self, movie: Movie, values: dict[str, Any]) -> Movie:
        for field, value in values.items():
            setattr(movie, field, value)
        self.session.commit()
        self.session.refresh(movie)
        return movie

    def delete(self, movie: Movie) -> None:
        self.session.delete(movie)
        self.session.commit()
