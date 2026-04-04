import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.coach_schemas import Coach
from app.schemas.run_schemas import RunCreate, RunCreateResponse, RunMeta
from app.services.run_service import RunService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Runs"])


async def get_run_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> RunService:
    repository = RunRepository(supabase)
    return RunService(repository, coach_id=coach.coach_id)


@router.get("", response_model=list[RunCreateResponse])
async def list_runs(
    service: RunService = Depends(get_run_service),
) -> list[RunCreateResponse]:
    """Get all runs, ordered by most recent first."""
    logger.info("Route: GET /runs")
    return await service.get_all_runs()


@router.post("", response_model=RunCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    data: RunCreate, service: RunService = Depends(get_run_service)
) -> RunCreateResponse:
    """Create a new run."""
    logger.info(f"Route: POST /runs for athlete {data.athlete_id}")
    return await service.create_run(data)


@router.get("/athlete/{athlete_id}", response_model=list[RunCreateResponse])
async def list_runs_by_athlete(
    athlete_id: UUID,
    service: RunService = Depends(get_run_service),
) -> list[RunCreateResponse]:
    """Get all runs for a specific athlete."""
    logger.info(f"Route: GET /runs/athlete/{athlete_id}")
    return await service.get_runs_by_athlete_id(athlete_id)


@router.get("/{run_id}/metadata", response_model=RunMeta)
async def get_run_metadata(
    run_id: UUID, service: RunService = Depends(get_run_service)
) -> RunMeta:
    """Get a specific run's metadata."""
    logger.info(f"Route: GET /runs/{run_id}/metadata")
    return await service.get_meta_by_run_id(run_id)
