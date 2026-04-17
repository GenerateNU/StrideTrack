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
    flight_ms: int = Field(..., ge=0)
    step_time_ms: int = Field(..., gt=0)


class RunUpdate(BaseModel):
    event_type: EventType | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    target_event: str | None = None
    hurdles_completed: int | None = Field(default=None, ge=1, le=10)


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
    hurdles_completed: int | None = Field(default=None, ge=1, le=10)


class RunCreateResponse(BaseModel):
    run_id: UUID
    athlete_id: UUID
    event_type: EventType
    target_event: str | None = None
    hurdles_completed: int | None = Field(default=None, ge=1, le=10)
    elapsed_ms: int
    created_at: str
    name: str | None = None


class RunMeta(BaseModel):
    run_id: UUID
    athlete_id: UUID
    event_type: EventType
    created_at: datetime
    name: str | None = None
    elapsed_ms: int
    hurdles_completed: int | None = None
    target_event: str | None = None
    elapsed_ms: int | None = None


class StepSeriesPoint(BaseModel):
    stride_num: int
    foot: Literal["left", "right"]
    ic_time: int = Field(..., ge=0)
    to_time: int | None = Field(default=None, ge=0)
    gct_ms: int = Field(..., ge=0)
    flight_ms: int | None = Field(default=None, ge=0)
    step_time_ms: int | None = Field(default=None, ge=0)
    rsi: float | None = None
    duty_factor: float | None = None
    contact_flight_index: float | None = None
    step_frequency_hz: float | None = None


class StrideSeriesPoint(BaseModel):
    stride_num: int
    stride_time_ms: int = Field(..., ge=0)


class GctRangeBucket(BaseModel):
    label: str
    count: int = Field(..., ge=0)
    lower_bound_ms: int | None = Field(default=None, ge=0)
    upper_bound_ms: int | None = Field(default=None, ge=0)


class UniversalKpis(BaseModel):
    total_steps: int
    mean_gct_ms: float
    mean_ft_ms: float | None = None
    mean_rsi: float | None = None
    mean_step_frequency_hz: float | None = None
    gct_asymmetry_pct: float | None = None
    ft_asymmetry_pct: float | None = None
    delta_gct_lr_ms: float | None = None
    delta_ft_lr_ms: float | None = None
    gct_drift_pct: float | None = None
    ft_drift_pct: float | None = None
    mean_duty_factor: float | None = None
    mean_contact_flight_index: float | None = None
