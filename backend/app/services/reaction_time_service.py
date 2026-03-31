import logging

import pandas as pd

from app.schemas.reaction_time_schemas import ReactionTimeRequest, ReactionTimeResponse

logger = logging.getLogger(__name__)


def _classify_zone(reaction_time_ms: float) -> tuple[str, str]:
    if reaction_time_ms < 200:
        return "green", "Excellent (<200ms)"
    elif reaction_time_ms <= 300:
        return "yellow", "Average (200–300ms)"
    else:
        return "red", "Slow (>300ms)"


class ReactionTimeService:
    def compute(self, data: ReactionTimeRequest) -> ReactionTimeResponse:
        logger.info("Service: Computing reaction time")

        df = pd.DataFrame(data.sensor_data)

        # Ensure correct types
        df["timestamp_ms"] = pd.to_numeric(df["timestamp_ms"])
        df["value"] = pd.to_numeric(df["value"])

        # Only look at samples after the stimulus
        post_stimulus = df[df["timestamp_ms"] > data.stimulus_timestamp_ms].copy()

        if post_stimulus.empty:
            raise ValueError("No sensor data found after stimulus timestamp.")

        # First sample where force crosses the GCT onset threshold
        onset_rows = post_stimulus[post_stimulus["value"] >= data.force_threshold_n]

        if onset_rows.empty:
            raise ValueError(
                f"No GCT onset detected above {data.force_threshold_n}N after stimulus."
            )

        onset_timestamp_ms = float(onset_rows.iloc[0]["timestamp_ms"])
        reaction_time_ms = onset_timestamp_ms - data.stimulus_timestamp_ms

        zone, zone_description = _classify_zone(reaction_time_ms)

        logger.info(f"Service: Reaction time = {reaction_time_ms:.2f}ms, zone = {zone}")

        return ReactionTimeResponse(
            reaction_time_ms=round(reaction_time_ms, 2),
            onset_timestamp_ms=onset_timestamp_ms,
            stimulus_timestamp_ms=data.stimulus_timestamp_ms,
            zone=zone,
            zone_description=zone_description,
        )
