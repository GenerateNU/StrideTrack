from pydantic import BaseModel, Field

from app.schemas.event_type import EventType


class RunMetrics(BaseModel):
    stride_num: int = Field(..., gt=0)
    foot: str | None = Field(None, min_length=1, max_length=255)
    ic_time: int = Field(..., ge=0)
    to_time: int = Field(..., gt=0)
    next_ic_time: int = Field(..., gt=0)
    gct_ms: int = Field(..., gt=0)
    flight_ms: int = Field(..., gt=0)
    step_time_ms: int = Field(..., gt=0)


class Run(BaseModel):
    run_id: str = Field(..., min_length=1, max_length=255)
    athlete_id: str = Field(..., min_length=1, max_length=255)
    event_type: EventType
    name: str | None = None


class BoscoMetricsResponse(BaseModel):
    run_id: str
    jump_heights: list[float]
    mean_jump_height: float
    peak_jump_height: float
    peak_jump_index: int
    jump_frequency: float
    rsi_per_jump: list[float]
    fatigue_index_pct: float
    flight_per_jump: list[float]
