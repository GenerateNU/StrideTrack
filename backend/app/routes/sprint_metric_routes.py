import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.coach_schemas import Coach
from app.schemas.run_schemas import SprintDriftData, StepFrequencyData
from app.services.sprint_metric_service import SprintMetricService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Sprint Metrics"])


async def get_sprint_metric_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> SprintMetricService:
    repository = RunRepository(supabase)
    return SprintMetricService(repository, coach_id=coach.coach_id)


@router.get("/{run_id}/metrics/sprint/drift", response_model=SprintDriftData)
async def get_sprint_drift(
    run_id: UUID,
    service: SprintMetricService = Depends(get_sprint_metric_service),
) -> SprintDriftData:
    """Get GCT and FT drift percentages for sprint fatigue tracking."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/sprint/drift")
    return await service.get_sprint_drift(run_id)


@router.get(
    "/{run_id}/metrics/sprint/step-frequency", response_model=list[StepFrequencyData]
)
async def get_step_frequency(
    run_id: UUID,
    service: SprintMetricService = Depends(get_sprint_metric_service),
) -> list[StepFrequencyData]:
    """Get step frequency data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/sprint/step-frequency")
    return await service.transform_step_frequency(run_id)
