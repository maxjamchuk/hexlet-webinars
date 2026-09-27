from fastapi import FastAPI

app = FastAPI()


@app.get("/message")
def message():
    return {"message": "Hello from api"}


@app.get("/health")
def health():
    return {"status": "ok"}
