import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.split_score_schemas import RunMetric, SplitScoreRunMeta

logger = logging.getLogger(__name__)


class SplitScoreRepository:
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

    async def get_run_meta(self, run_id: UUID) -> SplitScoreRunMeta:
        """Fetch run metadata (event type and elapsed time) for a run."""
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

    async def get_athlete_gender(self, run_id: UUID) -> str | None:
        """Fetch the gender of the athlete who owns the run. Returns None if unset."""
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
        return gender

    async def get_run_metrics(self, run_id: UUID) -> list[RunMetric]:
        """Fetch all stride metrics for a run ordered by initial contact time."""
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
