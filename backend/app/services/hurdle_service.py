import logging
from uuid import UUID

import numpy as np
import pandas as pd

from app.core.exceptions import NotFoundException
from app.repositories.hurdle_repository import HurdleRepository
from app.schemas.hurdle_schemas import (
    GctIncreaseData,
    HurdleMetricRow,
    HurdleSplitBarData,
    LandingGctBarData,
    StepsBetweenHurdlesData,
    TakeoffFtBarData,
    TakeoffGctBarData,
)
from app.utils.hurdle_chart_transformations import (
    transform_gct_increase,
    transform_hurdle_splits,
    transform_landing_gct,
    transform_steps_between_hurdles,
    transform_takeoff_ft,
    transform_takeoff_gct,
)
from app.utils.hurdle_metrics import transform_stride_cycles_to_hurdle_metrics

logger = logging.getLogger(__name__)


class HurdleService:
    """Service for hurdle-metric related business logic."""

    def __init__(self, repository: HurdleRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def _get_hurdle_metric_rows(self, run_id: UUID) -> list[HurdleMetricRow]:
        """Fetch raw steps, run the hurdle transform, and return validated HurdleMetricRow objects."""
        run_check = (
            await self.repository.supabase.table("run")
            .select("run_id, athletes!inner(coach_id)")
            .eq("run_id", str(run_id))
            .eq("athletes.coach_id", str(self.coach_id))
            .execute()
        )

        if not run_check.data:
            raise NotFoundException("Run", str(run_id))

        steps = await self.repository.get_hurdle_metrics(run_id)

        df = pd.DataFrame(steps)
        hurdle_df = transform_stride_cycles_to_hurdle_metrics(df)
        rows = hurdle_df.to_dict(orient="records")

        # Sanitize at the dict level so Pydantic sees Python None, not nan.
        sanitized = [
            {
                k: (None if isinstance(v, float) and np.isnan(v) else v)
                for k, v in row.items()
            }
            for row in rows
        ]

        return [HurdleMetricRow(**row) for row in sanitized]

    async def get_hurdle_metrics_by_run_id(self, run_id: UUID) -> list[HurdleMetricRow]:
        """Get all per-hurdle metrics for a run."""
        logger.info(f"Service: Getting hurdle metrics for run {run_id}")
        result = await self._get_hurdle_metric_rows(run_id)
        logger.info(f"Service: Returning {len(result)} hurdle rows for run {run_id}")
        return result

    async def get_hurdle_splits(self, run_id: UUID) -> list[HurdleSplitBarData]:
        """Transform hurdle data for split bar chart."""
        logger.info(f"Service: Getting hurdle splits for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_hurdle_splits(data)

    async def get_steps_between_hurdles(
        self, run_id: UUID
    ) -> list[StepsBetweenHurdlesData]:
        """Transform hurdle data for steps-between display."""
        logger.info(f"Service: Getting steps between hurdles for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_steps_between_hurdles(data)

    async def get_takeoff_gct(self, run_id: UUID) -> list[TakeoffGctBarData]:
        """Transform hurdle data for takeoff GCT bar chart."""
        logger.info(f"Service: Getting takeoff GCT for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_takeoff_gct(data)

    async def get_landing_gct(self, run_id: UUID) -> list[LandingGctBarData]:
        """Transform hurdle data for landing GCT bar chart."""
        logger.info(f"Service: Getting landing GCT for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_landing_gct(data)

    async def get_takeoff_ft(self, run_id: UUID) -> list[TakeoffFtBarData]:
        """Transform hurdle data for takeoff FT bar chart."""
        logger.info(f"Service: Getting takeoff FT for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_takeoff_ft(data)

    async def get_gct_increase(self, run_id: UUID) -> list[GctIncreaseData]:
        """Transform hurdle data for GCT increase KPI."""
        logger.info(f"Service: Getting GCT increase for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_gct_increase(data)
