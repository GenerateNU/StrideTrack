import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.run_schemas import RunResponse

logger = logging.getLogger(__name__)


class RunRepository:
    """Repository for run_metrics and run table operations."""

    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

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
        return response.data
    
    async def get_step_frequency(self, run_id: UUID) -> list[RunResponse]:
        """Fetch run metrics needed for step frequency chart. """
        logger.info(f"Repository: Fetching step frequency for run: {run_id}")
        response = (
            await self.supabase.table("run_metrics")
            .select("stride_num, ic_time, step_time_ms, foot")
            .eq("run_id", run_id)
            .order("ic_time")
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Run metric not found for id {run_id}")
            raise NotFoundException("Run metric", str(run_id))

        logger.info(f"Repository: Found step frequency data for run: {run_id}")
        return response.data
