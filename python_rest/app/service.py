"""Movie application services."""

from __future__ import annotations

from .models import Movie
from .repository import MovieRepository
from .schemas import MovieCreate, MovieListQuery, MoviePatch, MovieReplace


class MovieNotFoundError(LookupError):
    def __init__(self, movie_id: int):
        self.movie_id = movie_id
        super().__init__(f"Movie {movie_id} not found")


class MovieService:
    def __init__(self, repository: MovieRepository):
        self.repository = repository

    def list(self, query: MovieListQuery) -> tuple[list[Movie], int]:
        return self.repository.list(
            title=query.title,
            year=query.year,
            limit=query.limit,
            offset=query.offset,
        )

    def get(self, movie_id: int) -> Movie:
        movie = self.repository.get(movie_id)
        if movie is None:
            raise MovieNotFoundError(movie_id)
        return movie

    def create(self, payload: MovieCreate) -> Movie:
        return self.repository.create(payload.model_dump())

    def replace(self, movie_id: int, payload: MovieReplace) -> Movie:
        movie = self.get(movie_id)
        return self.repository.update(movie, payload.model_dump())

    def patch(self, movie_id: int, payload: MoviePatch) -> Movie:
        movie = self.get(movie_id)
        return self.repository.update(movie, payload.model_dump(exclude_unset=True))

    def delete(self, movie_id: int) -> None:
        movie = self.get(movie_id)
        self.repository.delete(movie)
