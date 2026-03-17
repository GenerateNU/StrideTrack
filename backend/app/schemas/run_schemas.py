from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RunResponse(BaseModel):
    stride_num: int = Field(..., gt=0)
    foot: str = Field(..., min_length=1, max_length=255)
    ic_time: int = Field(..., ge=0)
    gct_ms: int = Field(..., gt=0)
    flight_ms: int = Field(..., gt=0)
    step_time_ms: int = Field(..., gt=0)


class LROverlayData(BaseModel):
    stride_num: int
    left: float | None = None
    right: float | None = None


class StackedBarData(BaseModel):
    stride_num: int
    foot: Literal["left", "right"]
    label: str
    gct_ms: float
    flight_ms: float


class RunCreate(BaseModel):
    athlete_id: UUID
    event_type: str
    elapsed_ms: int = Field(..., gt=0)


class RunCreateResponse(BaseModel):
    run_id: UUID
    athlete_id: UUID
    event_type: str
    elapsed_ms: int
    created_at: str
