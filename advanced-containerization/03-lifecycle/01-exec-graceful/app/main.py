from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app):
    print("APP startup", flush=True)
    yield
    print("APP shutdown: cleanup complete", flush=True)


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello, Docker!"}
