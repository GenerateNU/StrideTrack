import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class LongJumpRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_long_jump_metrics(self, run_id: UUID) -> list[dict]:
        logger.info(f"Repository: Fetching long jump metrics for run: {run_id}")

        response = (
            await self.supabase.table("run_metrics")
            .select(
                "stride_num, ic_time, to_time, gct_ms, flight_ms, step_time_ms, foot"
            )
            .eq("run_id", str(run_id))
            .order("ic_time")
            .execute()
        )

        if not response.data:
            logger.warning(
                f"Repository: Long jump metrics not found for run_id {run_id}"
            )
            raise NotFoundException("Long jump metrics", str(run_id))

        logger.info(f"Repository: Found {len(response.data)} rows for run {run_id}")
        return response.data
