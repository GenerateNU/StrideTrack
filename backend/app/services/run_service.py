import logging
from typing import Literal
from uuid import UUID

from app.repositories.run_repository import RunCreate, RunCreateResponse, RunRepository
from app.schemas.run_schemas import (
    LROverlayData,
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

    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    async def get_metrics_by_run_id(self, run_id: UUID) -> list[RunResponse]:
        """Get all run metrics for a specific run."""
        logger.info(f"Service: Getting metrics for run {run_id}")
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

    async def get_sprint_drift(self, run_id: UUID) -> SprintDriftData:
        """Calculate GCT and FT drift % for sprint fatigue tracking."""
        logger.info(f"Service: Calculating sprint drift for run {run_id}")
        data = await self.repository.get_run_metrics(run_id)
        strides = [RunResponse(**row) for row in data]
        result = calculate_drift(strides)
        logger.info(f"Service: Calculated sprint drift for run {run_id}")
        return result

    async def transform_step_frequency(self, run_id: UUID) -> list[StepFrequencyData]:
        """Transform run data for step frequency visualization"""
        logger.info(f"Service: Transforming run {run_id} for step frequency chart")
        data = await self.repository.get_run_metrics(run_id)
        transformed = transform_data_for_step_frequency(data)
        logger.info(f"Service: Transformed run {run_id} for step frequency chart")
        return transformed

    async def create_run(self, data: RunCreate) -> RunCreateResponse:
        """Create a new run."""
        logger.info(f"Service: Creating run for athlete {data.athlete_id}")
        run = await self.repository.create(data)
        logger.info(f"Service: Created run {run.run_id}")
        return run

    async def get_all_runs(self) -> list[RunCreateResponse]:
        """Get all runs."""
        logger.info("Service: Getting all runs")
        runs = await self.repository.get_all()
        logger.info(f"Service: Retrieved {len(runs)} runs")
        return [RunCreateResponse(**run) for run in runs]

    async def get_runs_by_athlete_id(self, athlete_id: UUID) -> list[RunCreateResponse]:
        """Get all runs for a specific athlete."""
        logger.info(f"Service: Getting runs for athlete {athlete_id}")
        runs = await self.repository.get_by_athlete_id(athlete_id)
        logger.info(f"Service: Retrieved {len(runs)} runs for athlete {athlete_id}")
        return [RunCreateResponse(**run) for run in runs]
