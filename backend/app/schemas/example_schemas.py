from uuid import UUID

from pydantic import BaseModel, Field


class ExampleRunCreate(BaseModel):
    athlete_name: str = Field(..., min_length=1, max_length=255)
    distance_meters: int = Field(..., gt=0)
    duration_seconds: float = Field(..., gt=0)
    avg_ground_contact_time_ms: float | None = Field(None, gt=0)


class ExampleRunUpdate(BaseModel):
    athlete_name: str | None = Field(None, min_length=1, max_length=255)
    distance_meters: int | None = Field(None, gt=0)
    duration_seconds: float | None = Field(None, gt=0)
    avg_ground_contact_time_ms: float | None = Field(None, gt=0)


class ExampleRunResponse(BaseModel):
    id: UUID
    athlete_name: str
    distance_meters: int
    duration_seconds: float
    avg_ground_contact_time_ms: float | None
    created_at: str
