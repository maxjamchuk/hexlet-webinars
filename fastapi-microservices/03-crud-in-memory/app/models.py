from enum import Enum

from pydantic import BaseModel, Field, field_validator


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


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    category: Category | None = None
    danger_level: int | None = Field(default=None, ge=1, le=5)
    status: IncidentStatus | None = None

    @field_validator("title", "category", "danger_level", "status")
    @classmethod
    def required_values_cannot_be_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("поле нельзя обнулить")
        return value


class IncidentRead(IncidentCreate):
    id: int
