"""HTTP routes for the Movie API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from .models import Movie
from .repository import MovieRepository
from .schemas import (
    MovieCreate,
    MovieList,
    MovieListQuery,
    MoviePatch,
    MovieRead,
    MovieReplace,
)
from .service import MovieService


router = APIRouter()


def get_session(request: Request):
    yield from request.app.state.database.session()


def get_service(session: Annotated[Session, Depends(get_session)]) -> MovieService:
    return MovieService(MovieRepository(session))


ListQuery = Annotated[MovieListQuery, Query()]
Service = Annotated[MovieService, Depends(get_service)]


@router.get("/movies", response_model=MovieList)
def list_movies(query: ListQuery, service: Service) -> MovieList:
    movies, total = service.list(query)
    return MovieList(
        items=[MovieRead.model_validate(movie) for movie in movies],
        total=total,
        limit=query.limit,
        offset=query.offset,
    )


@router.head("/movies")
def head_movies(query: ListQuery, service: Service) -> Response:
    _, total = service.list(query)
    return Response(
        status_code=status.HTTP_200_OK,
        headers={
            "X-Total-Count": str(total),
            "X-Limit": str(query.limit),
            "X-Offset": str(query.offset),
        },
    )


@router.options("/movies", status_code=status.HTTP_204_NO_CONTENT)
def options_movies() -> Response:
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"Allow": "GET, HEAD, POST, OPTIONS"},
    )


@router.post(
    "/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED
)
def create_movie(
    payload: MovieCreate, response: Response, service: Service
) -> Movie:
    movie = service.create(payload)
    response.headers["Location"] = f"/movies/{movie.id}"
    return movie


@router.get("/movies/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int, service: Service) -> Movie:
    return service.get(movie_id)


@router.put("/movies/{movie_id}", response_model=MovieRead)
def replace_movie(
    movie_id: int, payload: MovieReplace, service: Service
) -> Movie:
    return service.replace(movie_id, payload)


@router.patch("/movies/{movie_id}", response_model=MovieRead)
def patch_movie(movie_id: int, payload: MoviePatch, service: Service) -> Movie:
    return service.patch(movie_id, payload)


@router.delete(
    "/movies/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_movie(movie_id: int, service: Service) -> Response:
    service.delete(movie_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.options(
    "/movies/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def options_movie(movie_id: int) -> Response:
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"Allow": "GET, PUT, PATCH, DELETE, OPTIONS"},
    )
