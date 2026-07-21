"""FastAPI application factory and default ASGI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import router
from .config import Settings
from .database import Database
from .service import MovieNotFoundError


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    database = Database(settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            database.initialize(settings.seed_path)
        except Exception:
            database.dispose()
            raise
        yield
        database.dispose()

    application = FastAPI(title="Hexlet Movie API", lifespan=lifespan)
    application.state.settings = settings
    application.state.database = database

    @application.exception_handler(MovieNotFoundError)
    async def movie_not_found_handler(
        _: Request, error: MovieNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    application.include_router(router)
    return application


app = create_app()
