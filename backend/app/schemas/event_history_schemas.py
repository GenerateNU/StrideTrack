from pydantic import BaseModel

from app.schemas.event_type import EventType


class EventHistoryPoint(BaseModel):
    run_number: int
    run_id: str
    run_name: str
    date: str
    total_time_seconds: float


class EventHistoryResponse(BaseModel):
    event_type: EventType
    athlete_id: str
    data_points: list[EventHistoryPoint]
    best_time_seconds: float | None = None
    total_runs: int


class EventHistoryRun(BaseModel):
    run_id: str
    name: str | None = None
    event_type: EventType
    elapsed_ms: int
    created_at: str


__all__ = [
    "EventHistoryPoint",
    "EventHistoryResponse",
    "EventHistoryRun",
    "EventType",
]
