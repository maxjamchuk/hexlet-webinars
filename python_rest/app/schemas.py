"""Pydantic request, response, query, and seed schemas."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


def _strip_non_empty(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must not be empty or whitespace")
    return value


NonEmptyString = Annotated[str, AfterValidator(_strip_non_empty)]
VoteAverage = Annotated[float, Field(ge=0, le=10)]
VoteCount = Annotated[int, Field(ge=0, strict=True)]


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class MovieCreate(StrictSchema):
    title: NonEmptyString
    original_title: str | None = None
    overview: str | None = None
    release_date: date | None = None
    vote_average: VoteAverage = 0
    vote_count: VoteCount = 0
    poster_path: str | None = None
    genres: list[NonEmptyString] = Field(default_factory=list)
    original_language: str | None = None


class MovieReplace(StrictSchema):
    title: NonEmptyString
    original_title: str | None
    overview: str | None
    release_date: date | None
    vote_average: VoteAverage
    vote_count: VoteCount
    poster_path: str | None
    genres: list[NonEmptyString]
    original_language: str | None


class MoviePatch(StrictSchema):
    title: NonEmptyString | None = None
    original_title: str | None = None
    overview: str | None = None
    release_date: date | None = None
    vote_average: VoteAverage | None = None
    vote_count: VoteCount | None = None
    poster_path: str | None = None
    genres: list[NonEmptyString] | None = None
    original_language: str | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "MoviePatch":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        non_nullable_fields = {"title", "vote_average", "vote_count", "genres"}
        null_fields = [
            field
            for field in non_nullable_fields & self.model_fields_set
            if getattr(self, field) is None
        ]
        if null_fields:
            raise ValueError(
                "fields must not be null: " + ", ".join(sorted(null_fields))
            )
        return self


class MovieSeed(StrictSchema):
    tmdb_id: Annotated[int, Field(gt=0, strict=True)] | None
    title: NonEmptyString
    original_title: str | None
    overview: str | None
    release_date: date | None
    vote_average: VoteAverage
    vote_count: VoteCount
    poster_path: str | None
    genres: list[NonEmptyString]
    original_language: str | None


class MovieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int | None
    title: str
    original_title: str | None
    overview: str | None
    release_date: date | None
    vote_average: float
    vote_count: int
    poster_path: str | None
    genres: list[str]
    original_language: str | None


class MovieList(BaseModel):
    items: list[MovieRead]
    total: int
    limit: int
    offset: int


class MovieListQuery(BaseModel):
    title: str | None = None
    year: int | None = Field(default=None, ge=1800, le=2100)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("title filter must not be empty or whitespace")
        return value
