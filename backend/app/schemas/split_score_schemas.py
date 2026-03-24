from pydantic import BaseModel


class SegmentScore(BaseModel):
    """Percentile analysis for a single race segment."""

    label: str
    raw_ms: float
    pct_of_total: float
    percentile: float


class SplitScoreResponse(BaseModel):
    """Full split score report for a single run."""

    run_id: str
    event_type: str
    total_ms: float
    segments: list[SegmentScore]
    coaching_notes: list[str]
