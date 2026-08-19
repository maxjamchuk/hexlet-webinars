from fastapi import FastAPI

app = FastAPI(title="Anomaly Registry API")


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": "Anomaly Registry API",
        "message": "Бюро аномалий принимает сообщения",
    }
