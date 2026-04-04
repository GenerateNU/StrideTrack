import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.event_type import EventType
from app.schemas.reaction_time_schemas import ReactionTimeRunMetric

logger = logging.getLogger(__name__)

EXCLUDED_EVENT_TYPES = (EventType.bosco_test,)


class ReactionTimeRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_run_metrics(self, run_id: UUID) -> list[ReactionTimeRunMetric]:
        logger.info(f"Repository: Fetching reaction time metrics for run {run_id}")
        response = (
            await self.supabase.table("run_metrics")
            .select("ic_time, to_time, gct_ms")
            .eq("run_id", str(run_id))
            .order("ic_time")
            .execute()
        )
        if not response.data:
            raise NotFoundException("Run metrics", str(run_id))
        logger.info(f"Repository: Found {len(response.data)} rows for run {run_id}")
        return [ReactionTimeRunMetric(**row) for row in response.data]

    async def get_all_run_metrics_for_athlete(
        self, athlete_id: UUID
    ) -> dict[str, list[ReactionTimeRunMetric]]:
        """
        Fetch run_metrics for all non-bosco runs belonging to an athlete.
        Returns a dict mapping run_id -> list of ReactionTimeRunMetric.
        """
        logger.info(f"Repository: Fetching all runs for athlete {athlete_id}")

        # Get all non-bosco runs for this athlete
        runs_response = (
            await self.supabase.table("run")
            .select("run_id")
            .eq("athlete_id", str(athlete_id))
            .not_.in_("event_type", list(EXCLUDED_EVENT_TYPES))
            .execute()
        )
        if not runs_response.data:
            raise NotFoundException("Runs", str(athlete_id))

        run_ids = [r["run_id"] for r in runs_response.data]

        # Fetch metrics for all those runs
        metrics_response = (
            await self.supabase.table("run_metrics")
            .select("run_id, ic_time, to_time, gct_ms")
            .in_("run_id", run_ids)
            .order("ic_time")
            .execute()
        )

        result: dict[str, list[ReactionTimeRunMetric]] = {rid: [] for rid in run_ids}
        for row in metrics_response.data or []:
            rid = row["run_id"]
            if rid in result:
                result[rid].append(
                    ReactionTimeRunMetric(
                        ic_time=row["ic_time"],
                        to_time=row["to_time"],
                        gct_ms=row["gct_ms"],
                    )
                )
        return result
