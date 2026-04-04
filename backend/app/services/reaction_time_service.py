import logging
from uuid import UUID

from app.repositories.reaction_time_repository import ReactionTimeRepository
from app.schemas.reaction_time_schemas import (
    AverageReactionTimeResponse,
    ReactionTimeResponse,
)

logger = logging.getLogger(__name__)

FORCE_THRESHOLD_GCT_MS = 20


def _classify_zone(reaction_time_ms: float) -> tuple[str, str]:
    if reaction_time_ms < 200:
        return "green", "Excellent (<200ms)"
    elif reaction_time_ms <= 300:
        return "yellow", "Average (200–300ms)"
    else:
        return "red", "Slow (>300ms)"


class ReactionTimeService:
    def __init__(self, repository: ReactionTimeRepository) -> None:
        self.repository = repository

    async def get_reaction_time(self, run_id: UUID) -> ReactionTimeResponse:
        logger.info(f"Service: Computing reaction time for run {run_id}")

        metrics = await self.repository.get_run_metrics(run_id)

        if not metrics:
            raise ValueError("No metrics found for this run.")

        # Reaction time = to_time of the first stride (when foot first leaves ground)
        first_stride = metrics[0]
        reaction_time_ms = float(first_stride.to_time)
        zone, zone_description = _classify_zone(reaction_time_ms)

        logger.info(f"Service: Reaction time = {reaction_time_ms:.2f}ms, zone = {zone}")

        return ReactionTimeResponse(
            run_id=str(run_id),
            reaction_time_ms=round(reaction_time_ms, 2),
            onset_timestamp_ms=float(first_stride.to_time),
            zone=zone,
            zone_description=zone_description,
        )

    async def get_average_reaction_time(
        self, athlete_id: UUID
    ) -> AverageReactionTimeResponse:
        logger.info(
            f"Service: Computing average reaction time for athlete {athlete_id}"
        )

        all_metrics = await self.repository.get_all_run_metrics_for_athlete(athlete_id)

        reaction_times: list[float] = []
        for metrics in all_metrics.values():
            if metrics:
                reaction_times.append(float(metrics[0].to_time))

        if not reaction_times:
            raise ValueError("No valid reaction time data found for this athlete.")

        avg_ms = sum(reaction_times) / len(reaction_times)
        zone, zone_description = _classify_zone(avg_ms)

        logger.info(
            f"Service: Average reaction time = {avg_ms:.2f}ms over {len(reaction_times)} runs"
        )

        return AverageReactionTimeResponse(
            athlete_id=str(athlete_id),
            average_reaction_time_ms=round(avg_ms, 2),
            run_count=len(reaction_times),
            zone=zone,
            zone_description=zone_description,
        )
