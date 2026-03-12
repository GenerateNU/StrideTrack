import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class HurdleRepository:
    """Repository for hurdle-specific run_metrics table operations."""

    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_hurdle_metrics(self, run_id: UUID) -> list[dict]:
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
            logger.warning(
                f"Repository: Hurdle metric not found for id {run_id}"
            )
            raise NotFoundException("Hurdle metric", str(run_id))

        logger.info(f"Repository: Found hurdle metric: {run_id}")
        return response.data