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
