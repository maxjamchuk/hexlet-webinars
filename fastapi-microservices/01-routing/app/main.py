from typing import Any

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Anomaly Registry API")

incidents: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Лифт открывается на несуществующем этаже",
        "category": "space",
        "danger_level": 3,
    },
    {
        "id": 2,
        "title": "Кофейный автомат предсказывает будущее",
        "category": "time",
        "danger_level": 2,
    },
    {
        "id": 3,
        "title": "Капибара телепортируется между переговорками",
        "category": "creature",
        "danger_level": 4,
    },
]


@app.get("/")
def read_root() -> dict[str, str]:
    return {"service": "Anomaly Registry API"}


@app.get("/incidents")
def read_incidents(category: str | None = None) -> list[dict[str, Any]]:
    if category is None:
        return incidents
    return [incident for incident in incidents if incident["category"] == category]


@app.get("/incidents/{incident_id}")
def read_incident(incident_id: int) -> dict[str, Any]:
    for incident in incidents:
        if incident["id"] == incident_id:
            return incident
    raise HTTPException(status_code=404, detail="Происшествие не найдено")
