import logging
from uuid import UUID

from app.repositories.reaction_time_repository import ReactionTimeRepository
from app.schemas.reaction_time_schemas import ReactionTimeResponse

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

        # Stimulus is the start of the run (ic_time = 0)
        stimulus_ms = 0.0

        # First metric where gct_ms crosses threshold indicates GCT onset
        onset = next(
            (m for m in metrics if m.gct_ms >= FORCE_THRESHOLD_GCT_MS),
            None,
        )

        if onset is None:
            raise ValueError(
                f"No GCT onset detected above {FORCE_THRESHOLD_GCT_MS}ms threshold."
            )

        onset_timestamp_ms = float(onset.ic_time)
        reaction_time_ms = onset_timestamp_ms - stimulus_ms
        zone, zone_description = _classify_zone(reaction_time_ms)

        logger.info(f"Service: Reaction time = {reaction_time_ms:.2f}ms, zone = {zone}")

        return ReactionTimeResponse(
            run_id=str(run_id),
            reaction_time_ms=round(reaction_time_ms, 2),
            onset_timestamp_ms=onset_timestamp_ms,
            zone=zone,
            zone_description=zone_description,
        )
