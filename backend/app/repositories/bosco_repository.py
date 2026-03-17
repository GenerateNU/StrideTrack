import logging

import pandas as pd
from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.bosco_schemas import Run, RunMetrics

logger = logging.getLogger(__name__)


class Bosco_Repository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase
        self.metrics_table = "run_metrics"
        self.run_table = "run"

    async def get_run_metrics_by_run_id(self, run_id: str) -> RunMetrics:
        """Fetches all run metrics rows for a given Bosco run"""

        logger.info(f"Repository: Fetching all run metrics for bosco run {run_id}")
        response = (
            await self.supabase.table("RUN_METRICS")
            .select(
                "stride_num, ic_time, to_time, next_ic_time, gct_ms, flight_ms, step_time_ms"
            )
            .eq("run_id", run_id)
            .order("stride_num", desc=False)
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: run metrics not found for bosco run {run_id}")
            raise NotFoundException("Run ID", str(run_id))

        logger.info(f"Repository: Fetched all run metrics for bosco run {run_id}")
        return pd.DataFrame(response.data)

    async def get_bosco_runs_by_athlete_id(self, athlete_id: str) -> list[Run]:
        """Fetches all Bosco test runs for a given athlete"""

        logger.info(f"Repository: Fetching all bosco runs for athlete {athlete_id}")
        response = (
            await self.supabase.table("RUN")
            .select("run_id, athlete_id, event_type, name")
            .eq("athlete_id", athlete_id)
            .eq("event_type", "bosco_test")
            .execute()
        )

        if not response.data:
            logger.warning(
                f"Repository: bosco tests not found for athlete {athlete_id}"
            )
            raise NotFoundException("Athlete ID", str(athlete_id))

        logger.info(f"Repository: Fetched all bosco runs for athlete {athlete_id}")

        return response.data
