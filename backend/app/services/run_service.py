import logging
from typing import Literal
from app.core.exceptions import NotFoundException
from uuid import UUID

from app.repositories.run_repository import RunCreate, RunCreateResponse, RunRepository
from app.schemas.run_schemas import LROverlayData, RunResponse, StackedBarData
from app.utils.chart_transformations import (
    transform_data_for_lr_overlay,
    transform_data_for_stacked_bar,
)

logger = logging.getLogger(__name__)


class RunService:
    """Service for run metric related business logic."""

    def __init__(self, repository: RunRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def get_metrics_by_run_id(self, run_id: UUID) -> list[RunResponse]:
        """Get all run metrics for a specific run."""

        # Verify run belongs to an athlete under this coach
        run_check = await self.repository.supabase.table("run") \
            .select("run_id, athletes!inner(coach_id)") \
            .eq("run_id", str(run_id)) \
            .eq("athletes.coach_id", str(self.coach_id)) \
            .execute()

        if not run_check.data:
            raise NotFoundException("Run", str(run_id))

        logger.info(f"Service: Getting metrics for run {run_id}")

        # Convert UUID to string for Supabase query
        metric = await self.repository.get_run_metrics(run_id)

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

    async def create_run(self, data: RunCreate) -> RunCreateResponse:
        """Create a new run."""

        athlete_check = await self.repository.supabase.table("athletes") \
            .select("athlete_id") \
            .eq("athlete_id", str(data.athlete_id)) \
            .eq("coach_id", str(self.coach_id)) \
            .execute()

        if not athlete_check.data:
            raise NotFoundException("Athlete", str(data.athlete_id))

        logger.info(f"Service: Creating run for athlete {data.athlete_id}")
        run = await self.repository.create(data)
        logger.info(f"Service: Created run {run.run_id}")
        return run
