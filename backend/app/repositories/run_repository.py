import logging

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)

class RunRepository:
    """Repository for run_metrics and run table operations."""

    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_metrics(self, athlete_id: str) -> list[dict]:
        """Get all run metrics for a specific athlete by joining RUN and RUN_METRICS."""
        logger.info(f"Repository: Fetching run metrics for athlete {athlete_id}")
        response = (
            await self.supabase.table("RUN_METRICS")
            .select("stride_num, ic_time, gct_ms, flight_ms, step_time_ms, foot, RUN!inner(run_id, athlete_id)")
            .eq("RUN.athlete_id", athlete_id)
            .order("ic_time")
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Run metrics not found for athlete {athlete_id}")
            raise NotFoundException("Run metrics", str(athlete_id))

        logger.info(f"Repository: Found run metrics for athlete {athlete_id}")
        return response.data

