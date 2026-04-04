from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.event_type import EventType


class HurdleStepRow(BaseModel):
    stride_num: int
    ic_time: int
    to_time: int
    gct_ms: int
    flight_ms: int
    step_time_ms: int
    foot: str


class HurdleMetricRow(BaseModel):
    hurdle_num: int = Field(..., gt=0)

    clearance_start_ms: int = Field(..., ge=0)
    clearance_end_ms: int = Field(..., ge=0)

    takeoff_ft_ms: int = Field(..., ge=0)

    # Last hurdle has no next hurdle, so these may be missing
    hurdle_split_ms: int | None = Field(default=None, ge=0)
    steps_between_hurdles: int | None = Field(default=None, ge=0)

    takeoff_foot: Literal["left", "right"] | None = None
    takeoff_gct_ms: int | None = Field(default=None, ge=0)

    landing_foot: Literal["left", "right"] | None = None
    landing_gct_ms: int | None = Field(default=None, ge=0)

    gct_increase_hurdle_to_hurdle_pct: float | None = None


class HurdleSplitBarData(BaseModel):
    hurdle_num: int
    hurdle_split_ms: int | None = None


class StepsBetweenHurdlesData(BaseModel):
    hurdle_num: int
    steps_between_hurdles: int | None = None


class TakeoffGctBarData(BaseModel):
    hurdle_num: int
    takeoff_foot: Literal["left", "right"] | None = None
    takeoff_gct_ms: int | None = None


class LandingGctBarData(BaseModel):
    hurdle_num: int
    landing_foot: Literal["left", "right"] | None = None
    landing_gct_ms: int | None = None


class TakeoffFtBarData(BaseModel):
    hurdle_num: int
    takeoff_ft_ms: int


class GctIncreaseData(BaseModel):
    hurdle_num: int
    takeoff_gct_ms: int | None = None
    gct_increase_hurdle_to_hurdle_pct: float | None = None


class ProjectedSplit(BaseModel):
    hurdle_num: int
    split_ms: int


class HurdleProjectionResponse(BaseModel):
    completed_splits: list[ProjectedSplit]
    projected_splits: list[ProjectedSplit]
    projected_final_segment_ms: int
    projected_total_ms: int | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    target_event: EventType
    total_hurdles: int


class HurdleTimelinePoint(BaseModel):
    time_s: float
    foot: Literal["left", "right"]
    phase: Literal["ground", "air"]
    gct_ms: int | None = None
    ft_ms: int | None = None


class HurdleMarker(BaseModel):
    time_s: float
    hurdle_num: int


class HurdleTimelineResponse(BaseModel):
    points: list[HurdleTimelinePoint]
    hurdle_markers: list[HurdleMarker]
