"""SQLAlchemy persistence models."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tmdb_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, unique=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    original_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    vote_average: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    vote_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    poster_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    genres: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    original_language: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )
