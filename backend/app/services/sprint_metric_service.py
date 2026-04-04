import logging
from uuid import UUID

from app.repositories.run_repository import RunRepository
from app.schemas.run_schemas import SprintDriftData, StepFrequencyData
from app.utils.chart_transformations import transform_data_for_step_frequency
from app.utils.sprint_metrics import calculate_drift

logger = logging.getLogger(__name__)


class SprintMetricService:
    """Service for sprint-specific metric transformations."""

    def __init__(self, repository: RunRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def get_sprint_drift(self, run_id: UUID) -> SprintDriftData:
        """Calculate GCT and FT drift % for sprint fatigue tracking."""
        logger.info(f"Service: Calculating sprint drift for run {run_id}")
        data = await self.repository.get_run_metrics(run_id)
        return calculate_drift(data)

    async def transform_step_frequency(self, run_id: UUID) -> list[StepFrequencyData]:
        """Transform run data for step frequency visualization."""
        logger.info(f"Service: Transforming run {run_id} for step frequency chart")
        data = await self.repository.get_run_metrics(run_id)
        return transform_data_for_step_frequency(data)
