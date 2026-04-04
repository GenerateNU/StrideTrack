import logging
from collections import defaultdict
from typing import Literal
from uuid import UUID

from app.repositories.run_repository import RunRepository
from app.schemas.run_schemas import (
    AsymmetryData,
    GCTRangeData,
    LROverlayData,
    RunResponse,
    StackedBarData,
)
from app.utils.chart_transformations import (
    transform_data_for_lr_overlay,
    transform_data_for_stacked_bar,
)

logger = logging.getLogger(__name__)


class UniversalMetricService:
    """Service for universal metric transformations (applicable to all event types)."""

    def __init__(self, repository: RunRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def get_metrics_by_run_id(self, run_id: UUID) -> list[RunResponse]:
        """Get all run metrics for a specific run."""
        await self.repository.verify_run_belongs_to_coach(run_id, self.coach_id)
        logger.info(f"Service: Getting metrics for run {run_id}")
        return await self.repository.get_run_metrics(run_id)

    async def transform_lr_overlay(
        self, run_id: UUID, metric: Literal["gct_ms", "flight_ms"]
    ) -> list[LROverlayData]:
        """Transform run data for FT and GCT visualizations."""
        logger.info(f"Service: Transforming run {run_id} for {metric} visualization")
        data = await self.repository.get_run_metrics(run_id)
        return transform_data_for_lr_overlay(data, metric)

    async def transform_stacked_bar(self, run_id: UUID) -> list[StackedBarData]:
        """Transform run data for step time visualization."""
        logger.info(f"Service: Transforming run {run_id} for stacked bar chart")
        data = await self.repository.get_run_metrics(run_id)
        return transform_data_for_stacked_bar(data)

    async def get_asymmetry(self, run_id: UUID) -> AsymmetryData:
        """Calculate GCT and FT asymmetry % between left and right foot."""
        logger.info(f"Service: Calculating asymmetry for run {run_id}")
        data = await self.repository.get_run_metrics(run_id)

        strides: dict = defaultdict(dict)
        for m in data:
            strides[m.stride_num][m.foot.lower()] = m

        gct_asym_list = []
        ft_asym_list = []

        for stride in strides.values():
            left = stride.get("left")
            right = stride.get("right")
            if left and right:
                gct_avg = (left.gct_ms + right.gct_ms) / 2
                ft_avg = (left.flight_ms + right.flight_ms) / 2
                if gct_avg > 0:
                    gct_asym_list.append(
                        abs(left.gct_ms - right.gct_ms) / gct_avg * 100
                    )
                if ft_avg > 0:
                    ft_asym_list.append(
                        abs(left.flight_ms - right.flight_ms) / ft_avg * 100
                    )

        gct_asym = sum(gct_asym_list) / len(gct_asym_list) if gct_asym_list else 0.0
        ft_asym = sum(ft_asym_list) / len(ft_asym_list) if ft_asym_list else 0.0

        return AsymmetryData(gct_asymmetry_pct=gct_asym, ft_asymmetry_pct=ft_asym)

    async def get_gct_range(
        self, run_id: UUID, min_ms: float, max_ms: float
    ) -> GCTRangeData:
        """Bucket steps by GCT into below / in / above a user-defined range."""
        logger.info(f"Service: Calculating GCT range for run {run_id}")
        data = await self.repository.get_run_metrics(run_id)

        below = sum(1 for m in data if m.gct_ms < min_ms)
        in_range = sum(1 for m in data if min_ms <= m.gct_ms <= max_ms)
        above = sum(1 for m in data if m.gct_ms > max_ms)

        return GCTRangeData(
            below=below, in_range=in_range, above=above, min_ms=min_ms, max_ms=max_ms
        )
