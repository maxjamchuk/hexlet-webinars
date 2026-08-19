from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Incident
from app.schemas import (
    Category,
    IncidentCreate,
    IncidentRead,
    IncidentStatus,
    IncidentUpdate,
)

app = FastAPI(title="Anomaly Registry API")
SessionDependency = Annotated[Session, Depends(get_session)]


def find_incident(session: Session, incident_id: int) -> Incident:
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Происшествие не найдено")
    return incident


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "service": "Anomaly Registry API",
        "message": "Бюро аномалий принимает сообщения",
    }


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/incidents", response_model=IncidentRead, status_code=status.HTTP_201_CREATED
)
def create_incident(payload: IncidentCreate, session: SessionDependency) -> Incident:
    incident = Incident(**payload.model_dump())
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


@app.get("/incidents", response_model=list[IncidentRead])
def read_incidents(
    session: SessionDependency,
    status_filter: Annotated[IncidentStatus | None, Query(alias="status")] = None,
    category: Category | None = None,
    danger_level: int | None = Query(default=None, ge=1, le=5),
) -> list[Incident]:
    statement = select(Incident)
    if status_filter is not None:
        statement = statement.where(Incident.status == status_filter)
    if category is not None:
        statement = statement.where(Incident.category == category)
    if danger_level is not None:
        statement = statement.where(Incident.danger_level == danger_level)
    return list(session.scalars(statement).all())


@app.get("/incidents/{incident_id}", response_model=IncidentRead)
def read_incident(incident_id: int, session: SessionDependency) -> Incident:
    return find_incident(session, incident_id)


@app.patch("/incidents/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    session: SessionDependency,
) -> Incident:
    incident = find_incident(session, incident_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)
    session.commit()
    session.refresh(incident)
    return incident


@app.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, session: SessionDependency) -> Response:
    incident = find_incident(session, incident_id)
    session.delete(incident)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
