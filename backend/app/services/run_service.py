import logging
from uuid import UUID
from typing import Literal
from app.schemas.run_schemas import RunResponse, LROverlayData, StackedBarData
from app.utils.chart_transformations import transform_data_for_lr_overlay, transform_data_for_stacked_bar
from app.repositories.run_repository import RunRepository

logger = logging.getLogger(__name__)


class RunService:
    """Service for run metric related business logic."""

    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    async def get_metrics_by_run_id(self, run_id: UUID) -> list[RunResponse]:
        """Get all run metrics for a specific run."""
        logger.info(f"Service: Getting metrics for run {run_id}")

        # Convert UUID to string for Supabase qu