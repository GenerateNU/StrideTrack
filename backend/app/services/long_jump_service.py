import logging
from uuid import UUID

import pandas as pd

from app.repositories.long_jump_repository import LongJumpRepository
from app.schemas.long_jump_schemas import (
    ApproachProfileData,
    LjTakeoffData,
    LongJumpMetricRow,
)
from app.schemas.run_schemas import (
    GctRangeBucket,
    StepSeriesPoint,
    StrideSeriesPoint,
    UniversalKpis,
)
from app.utils.long_jump_chart_transformations import (
    transform_lj_approach_profile,
    transform_lj_takeoff,
)
from app.utils.long_jump_metrics import transform_stride_cycles_to_long_jump_metrics
from app.utils.nan_to_none import nan_to_none
from app.utils.universal_metrics import (
    compute_gct_range_buckets,
    compute_step_series,
    compute_stride_series,
    compute_universal_kpis,
)

logger = logging.getLogger(__name__)


class LongJumpService:
    def __init__(self, repository: LongJumpRepository) -> None:
        self.repository = repository

    async def _fetch_and_transform(
        self, run_id: UUID
    ) -> tuple[pd.DataFrame, LongJumpMetricRow, list[StepSeriesPoint]]:
        raw_steps = await self.repository.get_long_jump_metrics(run_id)
        df = pd.DataFrame([s.model_dump() for s in raw_steps])
        lj_df = transform_stride_cycles_to_long_jump_metrics(df)
        rows = nan_to_none(lj_df.to_dict(orient="records"))
        lj_row = LongJumpMetricRow(**rows[0])
        return df, lj_row, raw_steps

    async def get_long_jump_metrics(self, run_id: UUID) -> LongJumpMetricRow:
        logger.info(f"Service: Getting long jump metrics for run {run_id}")
        _, lj_row, _ = await self._fetch_and_transform(run_id)
        return lj_row

    async def get_universal_kpis(self, run_id: UUID) -> UniversalKpis:
        logger.info(f"Service: Getting universal KPIs for long jump run {run_id}")
        df, lj_row, _ = await self._fetch_and_transform(run_id)
        return UniversalKpis(
            **compute_universal_kpis(df, approach_end_ms=lj_row.clearance_start_ms)
        )

    async def get_step_series(self, run_id: UUID) -> list[StepSeriesPoint]:
        logger.info(f"Service: Getting step series for long jump run {run_id}")
        df, lj_row, _ = await self._fetch_and_transform(run_id)
        return [
            StepSeriesPoint(**d)
            for d in compute_step_series(df, approach_end_ms=lj_row.clearance_start_ms)
        ]

    async def get_stride_series(self, run_id: UUID) -> list[StrideSeriesPoint]:
        logger.info(f"Service: Getting stride series for long jump run {run_id}")
        df, lj_row, _ = await self._fetch_and_transform(run_id)
        return [
            StrideSeriesPoint(**d)
            for d in compute_stride_series(
                df, approach_end_ms=lj_row.clearance_start_ms
            )
        ]

    async def get_gct_ranges(self, run_id: UUID) -> list[GctRangeBucket]:
        logger.info(f"Service: Getting GCT ranges for long jump run {run_id}")
        df, lj_row, _ = await self._fetch_and_transform(run_id)
        return [
            GctRangeBucket(**d)
            for d in compute_gct_range_buckets(
                df, approach_end_ms=lj_row.clearance_start_ms
            )
        ]

    async def get_approach_profile(self, run_id: UUID) -> list[ApproachProfileData]:
        logger.info(f"Service: Getting approach profile for long jump run {run_id}")
        df, lj_row, raw_steps = await self._fetch_and_transform(run_id)
        if lj_row.clearance_start_ms is None:
            return []
        return transform_lj_approach_profile(raw_steps, lj_row.clearance_start_ms)

    async def get_takeoff_data(self, run_id: UUID) -> LjTakeoffData:
        logger.info(f"Service: Getting takeoff data for long jump run {run_id}")
        _, lj_row, _ = await self._fetch_and_transform(run_id)
        return transform_lj_takeoff(lj_row)
