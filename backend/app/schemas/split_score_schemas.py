from uuid import UUID

from pydantic import BaseModel


class RunMeta(BaseModel):
    run_id: UUID
    event_type: str
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
    percentile: float


class SplitScoreResponse(BaseModel):
    run_id: str
    event_type: str
    total_ms: float
    segments: list[SegmentScore]
    coaching_notes: list[str]
