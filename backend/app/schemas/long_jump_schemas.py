from typing import Literal

from pydantic import BaseModel, Field


class LongJumpMetricRow(BaseModel):
    takeoff_foot: Literal["left", "right"] | None = None
    takeoff_gct_ms: int | None = Field(default=None, ge=0)
    penultimate_foot: Literal["left", "right"] | None = None
    penultimate_gct_ms: int | None = Field(default=None, ge=0)
    jump_ft_ms: int | None = Field(default=None, ge=0)
    clearance_start_ms: int | None = Field(default=None, ge=0)
    clearance_end_ms: int | None = Field(default=None, ge=0)
    approach_mean_gct_ms: float | None = None
    approach_mean_ft_ms: float | None = None
    approach_cv_pct: float | None = None
    approach_rsi: float | None = None


class ApproachProfileData(BaseModel):
    stride_num: int
    foot: Literal["left", "right"]
    ic_time: int = Field(..., ge=0)
    gct_ms: int = Field(..., ge=0)
    phase: str


class LjTakeoffData(BaseModel):
    takeoff_foot: Literal["left", "right"] | None = None
    takeoff_gct_ms: int | None = None
    penultimate_foot: Literal["left", "right"] | None = None
    penultimate_gct_ms: int | None = None
    jump_ft_ms: int | None = None
