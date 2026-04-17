import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.run_schemas import StepSeriesPoint

logger = logging.getLogger(__name__)


class TripleJumpRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_triple_jump_metrics(self, run_id: UUID) -> list[StepSeriesPoint]:
        logger.info(f"Repository: Fetching triple jump metrics for run: {run_id}")

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
                f"Repository: Triple jump metrics not found for run_id {run_id}"
            )
            raise NotFoundException("Triple jump metrics", str(run_id))

        logger.info(f"Repository: Found {len(response.data)} rows for run {run_id}")
        return [StepSeriesPoint(**row) for row in response.data]
