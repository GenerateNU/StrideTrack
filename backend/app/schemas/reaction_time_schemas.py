from pydantic import BaseModel


class ReactionTimeRunMetric(BaseModel):
    ic_time: float
    gct_ms: float


class ReactionTimeResponse(BaseModel):
    run_id: str
    reaction_time_ms: float
    onset_timestamp_ms: float
    zone: str
    zone_description: str
