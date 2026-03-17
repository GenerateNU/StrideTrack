from typing import Literal

from pydantic import BaseModel, Field


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
