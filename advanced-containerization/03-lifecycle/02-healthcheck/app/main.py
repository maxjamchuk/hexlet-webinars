from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app):
    print("APP startup", flush=True)
    yield
    print("APP shutdown: cleanup complete", flush=True)


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello, Docker!"}


@app.get("/health")
def health():
    if Path("/tmp/unhealthy").exists():
        return JSONResponse({"status": "unhealthy"}, status_code=503)
    return {"status": "ok"}
