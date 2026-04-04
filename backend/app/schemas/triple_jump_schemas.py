from typing import Literal

from pydantic import BaseModel, Field


class TripleJumpMetricRow(BaseModel):
    hop_gct_ms: int | None = Field(default=None, ge=0)
    step_gct_ms: int | None = Field(default=None, ge=0)
    jump_gct_ms: int | None = Field(default=None, ge=0)
    hop_ft_ms: int | None = Field(default=None, ge=0)
    step_ft_ms: int | None = Field(default=None, ge=0)
    jump_ft_ms: int | None = Field(default=None, ge=0)
    hop_takeoff_foot: Literal["left", "right"] | None = None
    phase_ratio_hop: float | None = None
    phase_ratio_step: float | None = None
    phase_ratio_jump: float | None = None
    contact_time_efficiency: float | None = None
    hop_clearance_start_ms: int | None = Field(default=None, ge=0)
    hop_clearance_end_ms: int | None = Field(default=None, ge=0)
    step_clearance_start_ms: int | None = Field(default=None, ge=0)
    step_clearance_end_ms: int | None = Field(default=None, ge=0)
    jump_clearance_start_ms: int | None = Field(default=None, ge=0)
    jump_clearance_end_ms: int | None = Field(default=None, ge=0)


class PhaseRatioData(BaseModel):
    phase: Literal["hop", "step", "jump"]
    ft_ms: int | None = None
    gct_ms: int | None = None
    ratio_pct: float | None = None


class TjContactEfficiencyData(BaseModel):
    hop_gct_ms: int | None = None
    step_gct_ms: int | None = None
    jump_gct_ms: int | None = None
    hop_ft_ms: int | None = None
    step_ft_ms: int | None = None
    jump_ft_ms: int | None = None
    contact_time_efficiency: float | None = None
