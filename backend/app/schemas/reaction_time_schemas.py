from pydantic import BaseModel


class ReactionTimeRunMetric(BaseModel):
    ic_time: float
    to_time: float
    gct_ms: float


class ReactionTimeResponse(BaseModel):
    run_id: str
    reaction_time_ms: float
    onset_timestamp_ms: float
    zone: str
    zone_description: str


class AverageReactionTimeResponse(BaseModel):
    athlete_id: str
    average_reaction_time_ms: float
    run_count: int
    zone: str
    zone_description: str
