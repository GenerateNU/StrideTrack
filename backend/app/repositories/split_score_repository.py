import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.split_score_schemas import RunMetric, SplitScoreRunMeta

logger = logging.getLogger(__name__)


class SplitScoreRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_run_meta(self, run_id: UUID) -> SplitScoreRunMeta:
        logger.info(f"Repository: Fetching run meta for {run_id}")
        response = (
            await self.supabase.table("run")
            .select("run_id, event_type, elapsed_ms")
            .eq("run_id", str(run_id))
            .execute()
        )
        if not response.data or len(response.data) == 0:
            logger.warning(f"Repository: Run not found for id {run_id}")
            raise NotFoundException("Run", str(run_id))
        logger.info(f"Repository: Found run meta for {run_id}")
        return SplitScoreRunMeta(**response.data[0])

    async def get_athlete_gender(self, run_id: UUID) -> str:
        logger.info(f"Repository: Fetching athlete gender for run {run_id}")
        response = (
            await self.supabase.table("run")
            .select("athletes(gender)")
            .eq("run_id", str(run_id))
            .execute()
        )
        if not response.data or len(response.data) == 0:
            logger.warning(f"Repository: Run not found for id {run_id}")
            raise NotFoundException("Run", str(run_id))
        gender = response.data[0].get("athletes", {}).get("gender")
        logger.info(f"Repository: Found gender '{gender}' for run {run_id}")
        return gender or "male"  # default to male if not set

    async def get_run_metrics(self, run_id: UUID) -> list[RunMetric]:
        logger.info(f"Repository: Fetching stride metrics for {run_id}")
        response = (
            await self.supabase.table("run_metrics")
            .select("ic_time, to_time, gct_ms, foot")
            .eq("run_id", str(run_id))
            .order("ic_time")
            .execute()
        )
        if not response.data:
            logger.warning(f"Repository: Stride metrics not found for run {run_id}")
            raise NotFoundException("Run metrics", str(run_id))
        logger.info(f"Repository: Found {len(response.data)} metric rows for {run_id}")
        return [RunMetric(**row) for row in response.data]
