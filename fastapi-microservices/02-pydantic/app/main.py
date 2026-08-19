from enum import Enum

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class Category(str, Enum):
    SPACE = "space"
    TIME = "time"
    CREATURE = "creature"
    TECHNOLOGY = "technology"
    UNKNOWN = "unknown"


class IncidentStatus(str, Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    category: Category
    danger_level: int = Field(ge=1, le=5)
    status: IncidentStatus = IncidentStatus.NEW


class IncidentRead(IncidentCreate):
    id: int


app = FastAPI(title="Anomaly Registry API")
incidents: dict[int, IncidentRead] = {}
next_id = 1


@app.get("/")
def read_root() -> dict[str, str]:
    return {"service": "Anomaly Registry API"}


@app.post(
    "/incidents",
    response_model=IncidentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(payload: IncidentCreate) -> IncidentRead:
    global next_id
    incident = IncidentRead(id=next_id, **payload.model_dump())
    incidents[next_id] = incident
    next_id += 1
    return incident


@app.get("/incidents", response_model=list[IncidentRead])
def read_incidents() -> list[IncidentRead]:
    return list(incidents.values())


@app.get("/incidents/{incident_id}", response_model=IncidentRead)
def read_incident(incident_id: int) -> IncidentRead:
    incident = incidents.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Происшествие не найдено")
    return incident
