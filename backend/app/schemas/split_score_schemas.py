from uuid import UUID

from pydantic import BaseModel

from app.schemas.event_type import EventType


class SplitScoreRunMeta(BaseModel):
    run_id: UUID
    event_type: EventType
    elapsed_ms: float


class RunMetric(BaseModel):
    ic_time: float
    to_time: float
    gct_ms: float
    foot: str


class SegmentScore(BaseModel):
    label: str
    raw_ms: float
    pct_of_total: float
    diff_s: float
    diff_pct: float


class SplitScoreResponse(BaseModel):
    run_id: str
    event_type: str
    total_ms: float
    segments: list[SegmentScore]
    coaching_notes: list[str]
    population_mean_pcts: list[float]
    population_std_pcts: list[float]
