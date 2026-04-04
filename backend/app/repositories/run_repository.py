import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.run_schemas import (
    RunCreate,
    RunCreateResponse,
    RunMeta,
    RunResponse,
    RunUpdate,
)

logger = logging.getLogger(__name__)


class RunRepository:
    """Repository for run_metrics and run table operations."""

    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def verify_run_belongs_to_coach(self, run_id: UUID, coach_id: UUID) -> None:
        """Verify a run belongs to one of the coach's athletes. Raises NotFoundException if not."""
        result = (
            await self.supabase.table("run")
            .select("run_id, athletes!inner(coach_id)")
            .eq("run_id", str(run_id))
            .eq("athletes.coach_id", str(coach_id))
            .execute()
        )
        if not result.data:
            raise NotFoundException("Run", str(run_id))

    async def verify_athlete_belongs_to_coach(
        self, athlete_id: UUID, coach_id: UUID
    ) -> None:
        """Verify an athlete belongs to the coach. Raises NotFoundException if not."""
        result = (
            await self.supabase.table("athletes")
            .select("athlete_id")
            .eq("athlete_id", str(athlete_id))
            .eq("coach_id", str(coach_id))
            .execute()
        )
        if not result.data:
            raise NotFoundException("Athlete", str(athlete_id))

    async def get_run_metrics(self, run_id: UUID) -> list[RunResponse]:
        """Get a run metric from RUN_METRICS table."""
        logger.info(f"Repository: Fetching run metric: {run_id}")
        response = (
            await self.supabase.table("run_metrics")
            .select("stride_num, ic_time, gct_ms, flight_ms, step_time_ms, foot")
            .eq("run_id", run_id)
            .order("ic_time")
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Run metric not found for id {run_id}")
            raise NotFoundException("Run metric", str(run_id))

        logger.info(f"Repository: Found run metric: {run_id}")
        return [RunResponse(**row) for row in response.data]

    async def get_run_meta(self, run_id: UUID) -> RunMeta:
        """Get a run's metadata from RUN table."""
        logger.info(f"Repository: Fetching run metric: {run_id}")
        response = (
            await self.supabase.table("run").select("*").eq("run_id", run_id).execute()
        )

        if not response.data:
            logger.warning(f"Repository: Run metric not found for id {run_id}")
            raise NotFoundException("Run metric", str(run_id))

        logger.info(f"Repository: Found run metric: {run_id}")
        return RunMeta(**response.data[0])

    async def create(self, run_create: RunCreate) -> RunCreateResponse:
        """Create a new run."""
        logger.info(f"Repository: Creating run for athlete {run_create.athlete_id}")
        data = {
            "athlete_id": str(run_create.athlete_id),
            "event_type": run_create.event_type,
            "elapsed_ms": run_create.elapsed_ms,
        }
        if run_create.target_event is not None:
            data["target_event"] = run_create.target_event

        response = await self.supabase.table("run").insert(data).execute()
        if not response.data:
            raise Exception("Failed to create run")
        logger.info(f"Repository: Created run {response.data[0]['run_id']}")
        return RunCreateResponse(**response.data[0])

    async def get_all(self, coach_id: UUID) -> list[RunCreateResponse]:
        """Get all runs, ordered by most recent first."""
        logger.info("Repository: Fetching all runs")
        response = (
            await self.supabase.table("run")
            .select(
                "run_id, athlete_id, event_type, target_event, elapsed_ms, created_at, name, athletes!inner(coach_id)"
            )
            .eq("athletes.coach_id", str(coach_id))
            .order("created_at", desc=True)
            .execute()
        )

        logger.info(f"Repository: Found {len(response.data)} runs")
        return [RunCreateResponse(**run) for run in response.data]

        logger.info(f"Repository: Found {len(response.data)} runs")
        return [RunCreateResponse(**run) for run in response.data]

    async def get_by_athlete_id(self, athlete_id: UUID) -> list[RunCreateResponse]:
        """Get all runs for a specific athlete, ordered by most recent first."""
        logger.info(f"Repository: Fetching runs for athlete {athlete_id}")
        response = (
            await self.supabase.table("run")
            .select(
                "run_id, athlete_id, event_type, target_event, elapsed_ms, created_at, name"
            )
            .eq("athlete_id", str(athlete_id))
            .order("created_at", desc=True)
            .execute()
        )
        logger.info(
            f"Repository: Found {len(response.data)} runs for athlete {athlete_id}"
        )
        return [RunCreateResponse(**run) for run in response.data]

    async def update(self, run_id: UUID, run_update: RunUpdate) -> RunCreateResponse:
        """Update a run."""
        logger.info(f"Repository: Updating run {run_id}")
        data = run_update.model_dump(exclude_unset=True)
        response = (
            await self.supabase.table("run")
            .update(data)
            .eq("run_id", str(run_id))
            .execute()
        )
        if not response.data:
            logger.warning(f"Repository: Run not found for update {run_id}")
            raise NotFoundException("Run", str(run_id))
        logger.info(f"Repository: Updated run {run_id}")
        return RunCreateResponse(**response.data[0])

    async def delete(self, run_id: UUID) -> None:
        """Delete a run."""
        logger.info(f"Repository: Deleting run {run_id}")
        response = (
            await self.supabase.table("run")
            .delete()
            .eq("run_id", str(run_id))
            .execute()
        )
        if not response.data:
            logger.warning(f"Repository: Run not found for deletion {run_id}")
            raise NotFoundException("Run", str(run_id))
        logger.info(f"Repository: Deleted run {run_id}")
