import logging
from typing import Literal
from uuid import UUID

from app.core.exceptions import NotFoundException
from app.repositories.run_repository import RunCreate, RunCreateResponse, RunRepository
from app.schemas.run_schemas import (
    AsymmetryData,
    GCTRangeData,
    LROverlayData,
    RunMeta,
    RunResponse,
    SprintDriftData,
    StackedBarData,
    StepFrequencyData,
)
from app.utils.chart_transformations import (
    transform_data_for_lr_overlay,
    transform_data_for_stacked_bar,
    transform_data_for_step_frequency,
)
from app.utils.sprint_metrics import calculate_drift

logger = logging.getLogger(__name__)


class RunService:
    """Service for run metric related business logic."""

    def __init__(self, repository: RunRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def get_metrics_by_run_id(self, run_id: UUID) -> list[RunResponse]:
        """Get all run metrics for a specific run."""

        run_check = (
            await self.repository.supabase.table("run")
            .select("run_id, athletes!inner(coach_id)")
            .eq("run_id", str(run_id))
            .eq("athletes.coach_id", str(self.coach_id))
            .execute()
        )

        if not run_check.data:
            raise NotFoundException("Run", str(run_id))

        logger.info(f"Service: Getting metrics for run {run_id}")
        metric = await self.repository.get_run_metrics(run_id)
        logger.info(f"Service: Retrieved metrics for run {run_id}")
        return metric

    async def get_meta_by_run_id(self, run_id: UUID) -> RunMeta:
        """Get metadata for a specific run."""

        run_check = (
            await self.repository.supabase.table("run")
            .select("run_id, athletes!inner(coach_id)")
            .eq("run_id", str(run_id))
            .eq("athletes.coach_id", str(self.coach_id))
            .execute()
        )

        if not run_check.data:
            raise NotFoundException("Run", str(run_id))

        logger.info(f"Service: Getting metrics for run {run_id}")
        metric = await self.repository.get_run_meta(run_id)
        logger.info(f"Service: Retrieved metrics for run {run_id}")
        return metric

    async def transform_lr_overlay(
        self, run_id: UUID, metric: Literal["gct_ms", "flight_ms"]
    ) -> list[LROverlayData]:
        """Transform run data for FT and GCT visualizations"""
        logger.info(f"Service: Transforming run {run_id} for {metric} visualization")
        data = await self.repository.get_run_metrics(run_id)
        transformed = transform_data_for_lr_overlay(data, metric)
        logger.info(f"Service: Transformed run {run_id} for {metric} visualization")
        return transformed

    async def transform_stacked_bar(self, run_id: UUID) -> list[StackedBarData]:
        """Transform run data for step time visualization"""
        logger.info(f"Service: Transforming run {run_id} for stacked bar chart")
        data = await self.repository.get_run_metrics(run_id)
        transformed = transform_data_for_stacked_bar(data)
        logger.info(f"Service: Transformed run {run_id} for stacked bar chart")
        return transformed

    async def get_sprint_drift(self, run_id: UUID) -> SprintDriftData:
        """Calculate GCT and FT drift % for sprint fatigue tracking."""
        logger.info(f"Service: Calculating sprint drift for run {run_id}")
        data = await self.repository.get_run_metrics(run_id)
        result = calculate_drift(data)
        logger.info(f"Service: Calculated sprint drift for run {run_id}")
        return result

    async def transform_step_frequency(self, run_id: UUID) -> list[StepFrequencyData]:
        """Transform run data for step frequency visualization"""
        logger.info(f"Service: Transforming run {run_id} for step frequency chart")
        data = await self.repository.get_run_metrics(run_id)
        transformed = transform_data_for_step_frequency(data)
        logger.info(f"Service: Transformed run {run_id} for step frequency chart")
        return transformed

    async def get_asymmetry(self, run_id: UUID) -> AsymmetryData:
        """Calculate GCT and FT asymmetry % between left and right foot."""
        logger.info(f"Service: Calculating asymmetry for run {run_id}")
        data = await self.repository.get_run_metrics(run_id)

        from collections import defaultdict

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

        logger.info(f"Service: Calculated asymmetry for run {run_id}")
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

        logger.info(f"Service: Calculated GCT range for run {run_id}")
        return GCTRangeData(
            below=below, in_range=in_range, above=above, min_ms=min_ms, max_ms=max_ms
        )

    async def create_run(self, data: RunCreate) -> RunCreateResponse:
        """Create a new run."""

        athlete_check = (
            await self.repository.supabase.table("athletes")
            .select("athlete_id")
            .eq("athlete_id", str(data.athlete_id))
            .eq("coach_id", str(self.coach_id))
            .execute()
        )

        if not athlete_check.data:
            raise NotFoundException("Athlete", str(data.athlete_id))

        logger.info(f"Service: Creating run for athlete {data.athlete_id}")
        run = await self.repository.create(data)
        logger.info(f"Service: Created run {run.run_id}")
        return run

    async def get_all_runs(self) -> list[RunCreateResponse]:
        """Get all runs for the current coach's athletes."""

        logger.info("Service: Getting all runs for coach")
        runs = await self.repository.get_all(self.coach_id)

        if not runs:
            return []

        logger.info(f"Service: Retrieved {len(runs)} runs")
        return runs

    async def get_runs_by_athlete_id(self, athlete_id: UUID) -> list[RunCreateResponse]:
        """Get all runs for a specific athlete."""

        athlete_check = (
            await self.repository.supabase.table("athletes")
            .select("athlete_id")
            .eq("athlete_id", str(athlete_id))
            .eq("coach_id", str(self.coach_id))
            .execute()
        )

        if not athlete_check:
            raise NotFoundException("Athlete", athlete_id)

        logger.info(f"Service: Getting runs for athlete {athlete_id}")
        runs = await self.repository.get_by_athlete_id(athlete_id)
        logger.info(f"Service: Retrieved {len(runs)} runs for athlete {athlete_id}")
        return runs
