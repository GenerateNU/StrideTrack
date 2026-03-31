from pydantic import BaseModel, Field


class ReactionTimeRequest(BaseModel):
    stimulus_timestamp_ms: float = Field(
        ..., description="Timestamp (ms) when the start stimulus was triggered"
    )
    sensor_data: list[dict] = Field(
        ...,
        description="Raw force plate rows: [{timestamp_ms, timestamp_iso, sensor_id, value}]",
    )
    force_threshold_n: float = Field(
        default=20.0,
        gt=0,
        description="Force (N) threshold to detect GCT onset. Defaults to 20N.",
    )


class ReactionTimeResponse(BaseModel):
    reaction_time_ms: float = Field(
        ..., description="Time from stimulus to first GCT onset (ms)"
    )
    onset_timestamp_ms: float = Field(
        ..., description="Absolute timestamp of detected GCT onset (ms)"
    )
    stimulus_timestamp_ms: float = Field(
        ..., description="Stimulus timestamp echoed back (ms)"
    )
    zone: str = Field(..., description="Color zone: green / yellow / red")
    zone_description: str = Field(..., description="Human-readable zone label")
