from fastapi import FastAPI, HTTPException, Query, Response
from fastapi import status as http_status

from app.schemas import (
    Category,
    IncidentCreate,
    IncidentRead,
    IncidentStatus,
    IncidentUpdate,
)

app = FastAPI(title="Anomaly Registry API")
incidents: dict[int, IncidentRead] = {}
next_id = 1


def find_incident(incident_id: int) -> IncidentRead:
    incident = incidents.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Происшествие не найдено")
    return incident


@app.get("/")
def read_root() -> dict[str, str]:
    return {"service": "Anomaly Registry API"}


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/incidents",
    response_model=IncidentRead,
    status_code=http_status.HTTP_201_CREATED,
)
def create_incident(payload: IncidentCreate) -> IncidentRead:
    global next_id
    incident = IncidentRead(id=next_id, **payload.model_dump())
    incidents[next_id] = incident
    next_id += 1
    return incident


@app.get("/incidents", response_model=list[IncidentRead])
def read_incidents(
    status: IncidentStatus | None = None,
    category: Category | None = None,
    danger_level: int | None = Query(default=None, ge=1, le=5),
) -> list[IncidentRead]:
    result = list(incidents.values())
    if status is not None:
        result = [item for item in result if item.status == status]
    if category is not None:
        result = [item for item in result if item.category == category]
    if danger_level is not None:
        result = [item for item in result if item.danger_level == danger_level]
    return result


@app.get("/incidents/{incident_id}", response_model=IncidentRead)
def read_incident(incident_id: int) -> IncidentRead:
    return find_incident(incident_id)


@app.patch("/incidents/{incident_id}", response_model=IncidentRead)
def update_incident(incident_id: int, payload: IncidentUpdate) -> IncidentRead:
    incident = find_incident(incident_id)
    updated = incident.model_copy(update=payload.model_dump(exclude_unset=True))
    incidents[incident_id] = updated
    return updated


@app.delete(
    "/incidents/{incident_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def delete_incident(incident_id: int) -> Response:
    find_incident(incident_id)
    del incidents[incident_id]
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
