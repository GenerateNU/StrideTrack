import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.athlete_repository import AthleteRepository
from app.repositories.bosco_repository import BoscoRepository
from app.repositories.reaction_time_repository import ReactionTimeRepository
from app.repositories.run_repository import RunRepository
from app.schemas.athlete_schemas import (
    AthleteCreate,
    AthleteResponse,
    AthleteUpdate,
)
from app.schemas.bosco_schemas import Run
from app.schemas.coach_schemas import Coach
from app.schemas.reaction_time_schemas import AverageReactionTimeResponse
from app.schemas.run_schemas import RunCreateResponse
from app.services.athlete_service import AthleteService
from app.services.bosco_service import BoscoService
from app.services.reaction_time_service import ReactionTimeService
from app.services.run_service import RunService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/athletes", tags=["Athletes"])


async def get_athlete_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> AthleteService:
    repository = AthleteRepository(supabase)
    return AthleteService(repository, coach_id=coach.coach_id)


async def get_run_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> RunService:
    repository = RunRepository(supabase)
    return RunService(repository, coach_id=coach.coach_id)


async def get_bosco_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> BoscoService:
    repository = BoscoRepository(supabase)
    return BoscoService(repository)


async def get_reaction_time_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> ReactionTimeService:
    return ReactionTimeService(ReactionTimeRepository(supabase))


# ── Athlete CRUD ──


@router.get("", response_model=list[AthleteResponse])
async def list_athletes(
    service: AthleteService = Depends(get_athlete_service),
) -> list[AthleteResponse]:
    """Get all athletes."""
    logger.info("Route: GET /athletes")
    athletes = await service.get_all_athletes()
    logger.info(f"Route: Returning {len(athletes)} athletes")
    return athletes


@router.post("", response_model=AthleteResponse, status_code=status.HTTP_201_CREATED)
async def create_athlete(
    data: AthleteCreate, service: AthleteService = Depends(get_athlete_service)
) -> AthleteResponse:
    """Create a new athlete."""
    logger.info(f"Route: POST /athletes for {data.name}")
    athlete = await service.create_athlete(data)
    logger.info(f"Route: Created athlete {athlete.athlete_id}")
    return athlete


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete(
    athlete_id: UUID, service: AthleteService = Depends(get_athlete_service)
) -> AthleteResponse:
    """Get an athlete by ID."""
    logger.info(f"Route: GET /athletes/{athlete_id}")
    athlete = await service.get_athlete_by_id(athlete_id)
    logger.info(f"Route: Returning athlete {athlete_id}")
    return athlete


@router.patch("/{athlete_id}", response_model=AthleteResponse)
async def update_athlete(
    athlete_id: UUID,
    data: AthleteUpdate,
    service: AthleteService = Depends(get_athlete_service),
) -> AthleteResponse:
    """Update an athlete."""
    logger.info(f"Route: PATCH /athletes/{athlete_id}")
    athlete = await service.update_athlete(athlete_id, data)
    logger.info(f"Route: Updated athlete {athlete_id}")
    return athlete


@router.delete("/{athlete_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_athlete(
    athlete_id: UUID, service: AthleteService = Depends(get_athlete_service)
) -> None:
    """Delete an athlete."""
    logger.info(f"Route: DELETE /athletes/{athlete_id}")
    await service.delete_athlete(athlete_id)
    logger.info(f"Route: Deleted athlete {athlete_id}")


# ── Athlete-scoped resources ──


@router.get("/{athlete_id}/runs", response_model=list[RunCreateResponse])
async def list_runs_by_athlete(
    athlete_id: UUID,
    service: RunService = Depends(get_run_service),
) -> list[RunCreateResponse]:
    """Get all runs for a specific athlete."""
    logger.info(f"Route: GET /athletes/{athlete_id}/runs")
    return await service.get_runs_by_athlete_id(athlete_id)


@router.get("/{athlete_id}/runs/bosco", response_model=list[Run])
async def get_bosco_runs(
    athlete_id: UUID,
    service: BoscoService = Depends(get_bosco_service),
) -> list[Run]:
    """Get all Bosco test runs for a specific athlete."""
    logger.info(f"Route: GET /athletes/{athlete_id}/runs/bosco")
    return await service.get_bosco_runs_for_athlete(str(athlete_id))


@router.get(
    "/{athlete_id}/metrics/reaction-time/average",
    response_model=AverageReactionTimeResponse,
    summary="Get average reaction time for an athlete across all non-bosco runs",
)
async def get_average_reaction_time(
    athlete_id: UUID,
    service: ReactionTimeService = Depends(get_reaction_time_service),
) -> AverageReactionTimeResponse:
    """Get average reaction time for an athlete across all non-bosco runs."""
    logger.info(f"Route: GET /athletes/{athlete_id}/metrics/reaction-time/average")
    return await service.get_average_reaction_time(athlete_id)
