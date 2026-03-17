import logging
from typing import Literal
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

    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    async def get_metrics_by_run_id(self, run_id: UUID) -> list[RunResponse]:
        """Get all run metrics for a specific run."""
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
        logger.info(f"Service: Creating run for athlete {data.athlete_id}")
        run = await self.repository.create(data)
        logger.info(f"Service: Created run {run.run_id}")
        return run
