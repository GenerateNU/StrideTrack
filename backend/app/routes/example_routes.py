import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.example_repository import ExampleRepository
from app.schemas.example_schemas import (
    ExampleRunCreate,
    ExampleRunResponse,
    ExampleRunUpdate,
)
from app.services.example_service import ExampleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/example", tags=["Example"])


# Dependency injection
async def get_example_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> ExampleService:
    repository = ExampleRepository(supabase)
    return ExampleService(repository)


@router.get("/training-runs", response_model=list[ExampleRunResponse])
async def list_training_runs(
    service: ExampleService = Depends(get_example_service),
) -> list[ExampleRunResponse]:
    """Get all training runs."""
    logger.info("Route: GET /training-runs")
    runs = await service.get_all_runs()
    logger.info(f"Route: Returning {len(runs)} training runs")
    return runs


@router.get("/training-runs/{run_id}", response_model=ExampleRunResponse)
async def get_training_run(
    run_id: UUID, service: ExampleService = Depends(get_example_service)
) -> ExampleRunResponse:
    """Get a training run by ID."""
    logger.info(f"Route: GET /training-runs/{run_id}")
    run = await service.get_run_by_id(run_id)
    logger.info(f"Route: Returning training run {run_id}")
    return run


@router.post(
    "/training-runs",
    response_model=ExampleRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_training_run(
    data: ExampleRunCreate, service: ExampleService = Depends(get_example_service)
) -> ExampleRunResponse:
    """Create a new training run."""
    logger.info(f"Route: POST /training-runs for athlete {data.athlete_name}")
    run = await service.create_run(data.model_dump(exclude_unset=True))
    logger.info(f"Route: Created training run {run['id']}")
    return run


@router.patch("/training-runs/{run_id}", response_model=ExampleRunResponse)
async def update_training_run(
    run_id: UUID,
    data: ExampleRunUpdate,
    service: ExampleService = Depends(get_example_service),
) -> ExampleRunResponse:
    """Update a training run."""
    logger.info(f"Route: PATCH /training-runs/{run_id}")
    run = await service.update_run(run_id, data.model_dump(exclude_unset=True))
    logger.info(f"Route: Updated training run {run_id}")
    return run


@router.delete("/training-runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_run(
    run_id: UUID, service: ExampleService = Depends(get_example_service)
) -> None:
    """Delete a training run."""
    logger.info(f"Route: DELETE /training-runs/{run_id}")
    await service.delete_run(run_id)
    logger.info(f"Route: Deleted training run {run_