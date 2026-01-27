import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.all_repositories import TrianingRunsRepo
from app.schemas.all_schemas import (
    TrainingRunCreate,
    TrainingRunUpdate,
    TrainingRunResponse,
)

from app.services.all_services import TrainingRunsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training-runs", tags=["Training Runs"])


# Dependency injection
async def get_training_runs_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> TrainingRunsService:
    repository = TrainingRunsRepo(supabase)
    return TrainingRunsService(repository)


@router.get("/", response_model=list[TrainingRunResponse])
async def list_training_runs(service: TrainingRunsService = Depends(get_training_runs_service)):
    """Get all training runs."""
    logger.info("Route: GET /training-runs")
    runs = await service.get_all_runs()
    logger.info(f"Route: Returning {len(runs)} training runs")
    return runs


@router.get("/{run_id}", response_model=TrainingRunResponse)
async def get_training_run(
    run_id: UUID, service: TrainingRunsService = Depends(get_training_runs_service)
):
    """Get a training run by ID."""
    logger.info(f"Route: GET /training-runs/{run_id}")
    run = await service.get_run_by_id(run_id)
    logger.info(f"Route: Returning training run {run_id}")
    return run


@router.post(
    "/",
    response_model=TrainingRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_training_run(
    data: TrainingRunCreate, service: TrainingRunsService = Depends(get_training_runs_service)
):
    """Create a new training run."""
    logger.info(f"Route: POST /training-runs for athlete {data.athlete_name}")
    run = await service.create_run(data.model_dump(exclude_unset=True))
    logger.info(f"Route: Created training run {run['id']}")
    return run


@router.patch("/{run_id}", response_model=TrainingRunResponse)
async def update_training_run(
    run_id: UUID,
    data: TrainingRunUpdate,
    service: TrainingRunsService = Depends(get_training_runs_service),
):
    """Update a training run."""
    logger.info(f"Route: PATCH /training-runs/{run_id}")
    run = await service.update_run(run_id, data.model_dump(exclude_unset=True))
    logger.info(f"Route: Updated training run {run_id}")
    return run


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_run(
    run_id: UUID, service: TrainingRunsService = Depends(get_training_runs_service)
):
    """Delete a training run."""
    logger.info(f"Route: DELETE /training-runs/{run_id}")
    await service.delete_run(run_id)
    logger.info(f"Route: Deleted training run {run_id}")


