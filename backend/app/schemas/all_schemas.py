from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field


class TrainingRunCreate(BaseModel):
    athlete_id: UUID = Field(...)
    athlete_name: str = Field(..., min_length=1, max_length=255)
    distance_meters: int = Field(..., gt=0)
    duration_seconds: float = Field(..., gt=0)
    avg_ground_contact_time_ms: float | None = Field(None, gt=0)
    run_date: date | None = Field(None)


class TrainingRunUpdate(BaseModel):
    athlete_name: str | None = Field(None, min_length=1, max_length=255)
    distance_meters: int | None = Field(None, gt=0)
    duration_seconds: float | None = Field(None, gt=0)
    avg_ground_contact_time_ms: float | None = Field(None, gt=0)


class TrainingRunResponse(BaseModel):
    id: UUID
    athlete_id: UUID
    athlete_name: str
    distance_meters: int
    duration_seconds: float
    avg_ground_contact_time_ms: float | None
    run_date: date # should this be a str or date?
    created_at: datetime # should this be a str or datetime?

class AthleteCreate(BaseModel):
    athlete_name: str = Field(..., min_length=1, max_length=255)
    coach_id: UUID = Field(...)

class AthleteUpdate(BaseModel):    
    athlete_name: str | None = Field(None, min_length=1, max_length=100)

class AthleteResponse(BaseModel):
    id: UUID 
    athlete_name: str
    coach_id: UUID
    created_at: datetime 

class CoachUpdate(BaseModel):
    coach_name: str | None = Field(None, min_length=1, max_length=255)

class CoachResponse(BaseModel):
    id: UUID
    coach_name: str
    created_at: datetime