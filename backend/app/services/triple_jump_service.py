import logging
from uuid import UUID

import numpy as np
import pandas as pd

from app.repositories.triple_jump_repository import TripleJumpRepository
from app.schemas.run_schemas import (
    GctRangeBucket,
    StepSeriesPoint,
    StrideSeriesPoint,
    UniversalKpis,
)
from app.schemas.triple_jump_schemas import (
    PhaseRatioData,
    TjContactEfficiencyData,
    TripleJumpMetricRow,
)
from app.utils.triple_jump_chart_transformations import (
    transform_tj_contact_efficiency,
    transform_tj_phase_ratio,
)
from app.utils.triple_jump_metrics import transform_stride_cycles_to_triple_jump_metrics
from app.utils.universal_metrics import (
    compute_gct_range_buckets,
    compute_step_series,
    compute_stride_series,
    compute_universal_kpis,
)

logger = logging.getLogger(__name__)


def _sanitize(rows: list[dict]) -> list[dict]:
    return [
        {
            k: (None if isinstance(v, float) and np.isnan(v) else v)
            for k, v in row.items()
        }
        for row in rows
    ]


class TripleJumpService:
    def __init__(self, repository: TripleJumpRepository) -> None:
        self.repository = repository

    async def _fetch_and_transform(
        self, run_id: UUID
    ) -> tuple[pd.DataFrame, TripleJumpMetricRow]:
        raw_steps = await self.repository.get_triple_jump_metrics(run_id)
        df = pd.DataFrame(raw_steps)
        tj_df = transform_stride_cycles_to_triple_jump_metrics(df)
        rows = _sanitize(tj_df.to_dict(orient="records"))
        tj_row = TripleJumpMetricRow(**rows[0])
        return df, tj_row

    async def get_triple_jump_metrics(self, run_id: UUID) -> TripleJumpMetricRow:
        logger.info(f"Service: Getting triple jump metrics for run {run_id}")
        _, tj_row = await self._fetch_and_transform(run_id)
        return tj_row

    async def get_universal_kpis(self, run_id: UUID) -> UniversalKpis:
        logger.info(f"Service: Getting universal KPIs for triple jump run {run_id}")
        df, tj_row = await self._fetch_and_transform(run_id)
        return UniversalKpis(
            **compute_universal_kpis(df, approach_end_ms=tj_row.hop_clearance_start_ms)
        )

    async def get_step_series(self, run_id: UUID) -> list[StepSeriesPoint]:
        logger.info(f"Service: Getting step series for triple jump run {run_id}")
        df, tj_row = await self._fetch_and_transform(run_id)
        return [
            StepSeriesPoint(**d)
            for d in compute_step_series(
                df, approach_end_ms=tj_row.hop_clearance_start_ms
            )
        ]

    async def get_stride_series(self, run_id: UUID) -> list[StrideSeriesPoint]:
        logger.info(f"Service: Getting stride series for triple jump run {run_id}")
        df, tj_row = await self._fetch_and_transform(run_id)
        return [
            StrideSeriesPoint(**d)
            for d in compute_stride_series(
                df, approach_end_ms=tj_row.hop_clearance_start_ms
            )
        ]

    async def get_gct_ranges(self, run_id: UUID) -> list[GctRangeBucket]:
        logger.info(f"Service: Getting GCT ranges for triple jump run {run_id}")
        df, tj_row = await self._fetch_and_transform(run_id)
        return [
            GctRangeBucket(**d)
            for d in compute_gct_range_buckets(
                df, approach_end_ms=tj_row.hop_clearance_start_ms
            )
        ]

    async def get_phase_ratio(self, run_id: UUID) -> list[PhaseRatioData]:
        logger.info(f"Service: Getting phase ratio for run {run_id}")
        _, tj_row = await self._fetch_and_transform(run_id)
        return transform_tj_phase_ratio(tj_row)

    async def get_contact_efficiency(self, run_id: UUID) -> TjContactEfficiencyData:
        logger.info(f"Service: Getting contact efficiency for run {run_id}")
        _, tj_row = await self._fetch_and_transform(run_id)
        return transform_tj_contact_efficiency(tj_row)
