from enum import StrEnum

from pydantic import BaseModel


class EventHistoryPoint(BaseModel):
    run_number: int
    run_id: str
    run_name: str
    date: str
    total_time_seconds: float


class EventHistoryResponse(BaseModel):
    event_type: str
    athlete_id: str
    data_points: list[EventHistoryPoint]
    best_time_seconds: float | None = None
    total_runs: int


class EventHistoryRun(BaseModel):
    run_id: str
    name: str
    event_type: str
    elapsed_ms: int
    created_at: str


class EventType(StrEnum):
    sprint_60m = "sprint_60m"
    sprint_100m = "sprint_100m"
    sprint_200m = "sprint_200m"
    sprint_400m = "sprint_400m"
    hurdles_60m = "hurdles_60m"
    hurdles_110m = "hurdles_110m"
    hurdles_100m = "hurdles_100m"
    hurdles_400m = "hurdles_400m"
    long_jump = "long_jump"
    triple_jump = "triple_jump"
    high_jump = "high_jump"
    bosco_test = "bosco_test"
    reaction_time_test = "reaction_time_test"
