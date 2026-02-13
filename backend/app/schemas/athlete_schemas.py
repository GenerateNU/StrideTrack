from uuid import UUID

from pydantic import BaseModel, Field


class AthleteCreate(BaseModel):
    coach_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    height_in: float | None = Field(None, gt=0)
    weight_lbs: float | None = Field(None, gt=0)


class AthleteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    height_in: float | None = Field(None, gt=0)
    weight_lbs: float | None = Field(None, gt=0)


class AthleteResponse(BaseModel):
    athlete_id: UUID
    coach_id: UUID
    name: str
    height_in: float | None
    weight_lbs: float | None
    created_at: str
