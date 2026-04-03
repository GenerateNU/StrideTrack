import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.reaction_time_schemas import ReactionTimeRunMetric

logger = logging.getLogger(__name__)


class ReactionTimeRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_run_metrics(self, run_id: UUID) -> list[ReactionTimeRunMetric]:
        logger.info(f"Repository: Fetching reaction time metrics for run {run_id}")
        response = (
            await self.supabase.table("run_metrics")
            .select("ic_time, gct_ms")
            .eq("run_id", str(run_id))
            .order("ic_time")
            .execute()
        )
        if not response.data:
            raise NotFoundException("Run metrics", str(run_id))
        logger.info(f"Repository: Found {len(response.data)} rows for run {run_id}")
        return [ReactionTimeRunMetric(**row) for row in response.data]
