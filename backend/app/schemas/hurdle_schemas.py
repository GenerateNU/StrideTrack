from typing import Literal

from pydantic import BaseModel, Field


class HurdleMetricRow(BaseModel):
    """Full per-hurdle metric row returned by the base /hurdles endpoint."""
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

# --- Visualization-specific schemas ---


class HurdleSplitBarData(BaseModel):
    """Bar chart data: one bar per hurdle interval showing split time."""

    hurdle_num: int
    hurdle_split_ms: int | None = None


class StepsBetweenHurdlesData(BaseModel):
    """Integer display per hurdle interval."""

    hurdle_num: int
    steps_between_hurdles: int | None = None


class TakeoffGctBarData(BaseModel):
    """Bar chart data: takeoff GCT per hurdle."""

    hurdle_num: int
    takeoff_foot: Literal["left", "right"] | None = None
    takeoff_gct_ms: int | None = None


class LandingGctBarData(BaseModel):
    """Bar chart data: landing GCT per hurdle."""

    hurdle_num: int
    landing_foot: Literal["left", "right"] | None = None
    landing_gct_ms: int | None = None


class TakeoffFtBarData(BaseModel):
    """Bar chart data: flight time during hurdle clearance."""

    hurdle_num: int
    takeoff_ft_ms: int


class GctIncreaseData(BaseModel):
    """KPI data: GCT increase relative to first hurdle."""

    hurdle_num: int
    takeoff_gct_ms: int | None = None
    gct_increase_hurdle_to_hurdle_pct: float | None = None