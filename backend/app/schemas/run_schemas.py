from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.event_type import EventType


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


class SprintDriftData(BaseModel):
    gct_drift_pct: float
    ft_drift_pct: float


class StepFrequencyData(BaseModel):
    stride_num: int
    foot: Literal["left", "right"]
    label: str
    step_frequency_hz: float


class AsymmetryData(BaseModel):
    gct_asymmetry_pct: float
    ft_asymmetry_pct: float


class GCTRangeData(BaseModel):
    below: int
    in_range: int
    above: int
    min_ms: float
    max_ms: float


class RunCreate(BaseModel):
    athlete_id: UUID
    event_type: EventType
    elapsed_ms: int = Field(..., gt=0)
    target_event: str | None = None


class RunCreateResponse(BaseModel):
    run_id: UUID
    athlete_id: UUID
    event_type: EventType
    target_event: str | None = None
    elapsed_ms: int
    created_at: str


class RunMeta(BaseModel):
    run_id: UUID
    athlete_id: UUID
    event_type: EventType
    created_at: datetime
    name: str | None = None
    elapsed_ms: int
