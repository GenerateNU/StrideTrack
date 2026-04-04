import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.event_type import EventType
from app.schemas.hurdle_schemas import HurdleStepRow

logger = logging.getLogger(__name__)


class HurdleRepository:
    """Repository for hurdle-specific run_metrics table operations."""

    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def verify_run_belongs_to_coach(self, run_id: UUID, coach_id: UUID) -> None:
        """Verify a run belongs to one of the coach's athletes."""
        result = (
            await self.supabase.table("run")
            .select("run_id, athletes!inner(coach_id)")
            .eq("run_id", str(run_id))
            .eq("athletes.coach_id", str(coach_id))
            .execute()
        )
        if not result.data:
            raise NotFoundException("Run", str(run_id))

    async def get_hurdle_metrics(self, run_id: UUID) -> list[HurdleStepRow]:
        """Get a hurdle metric from RUN_METRICS table."""
        logger.info(f"Repository: Fetching hurdle metric: {run_id}")
        response = (
            await self.supabase.table("run_metrics")
            .select(
                "stride_num, ic_time, to_time, gct_ms, flight_ms, step_time_ms, foot"
            )
            .eq("run_id", run_id)
            .order("ic_time")
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Hurdle metric not found for id {run_id}")
            raise NotFoundException("Hurdle metric", str(run_id))

        logger.info(f"Repository: Found hurdle metric: {run_id}")
        return [HurdleStepRow(**row) for row in response.data]

    async def get_run_target_event(self, run_id: UUID) -> str:
        """Get the target_event for a partial hurdle run from the RUN table."""
        logger.info(f"Repository: Fetching target_event for run: {run_id}")
        response = (
            await self.supabase.table("run")
            .select("event_type, target_event")
            .eq("run_id", run_id)
            .single()
            .execute()
        )

        if not response.data:
            raise NotFoundException("Run", str(run_id))

        row = response.data
        if row["event_type"] != EventType.hurdles_partial:
            raise ValueError(
                f"Run {run_id} is not a hurdles_partial run "
                f"(event_type={row['event_type']})"
            )

        if not row["target_event"]:
            raise ValueError(f"Run {run_id} has no target_event")

        logger.info(f"Repository: target_event for {run_id} = {row['target_event']}")
        return row["target_event"]

    async def get_run_event_type(self, run_id: UUID) -> EventType | None:
        """Get the event_type for a run."""
        logger.info(f"Repository: Fetching event_type for run: {run_id}")
        response = (
            await self.supabase.table("run")
            .select("event_type")
            .eq("run_id", str(run_id))
            .single()
            .execute()
        )
        if not response.data:
            return None
        return EventType(response.data["event_type"])
