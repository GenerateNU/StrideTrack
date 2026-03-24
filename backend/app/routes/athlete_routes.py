import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.athlete_repository import AthleteRepository
from app.schemas.athlete_schemas import (
    AthleteCreate,
    AthleteResponse,
    AthleteUpdate,
)
from app.schemas.coach_schemas import Coach
from app.services.athlete_service import AthleteService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/athletes", tags=["Athletes"])


async def get_athlete_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> AthleteService:
    repository = AthleteRepository(supabase)
    return AthleteService(repository, coach_id=coach.coach_id)


@router.get("", response_model=list[AthleteResponse])
async def list_athletes(
    service: AthleteService = Depends(get_athlete_service),
) -> list[AthleteResponse]:
    """Get all athletes."""
    logger.info("Route: GET /athletes")
    athletes = await service.get_all_athletes()
    logger.info(f"Route: Returning {len(athletes)} athletes")
    return athletes


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete(
    athlete_id: UUID, service: AthleteService = Depends(get_athlete_service)
) -> AthleteResponse:
    """Get an athlete by ID."""
    logger.info(f"Route: GET /athletes/{athlete_id}")
    athlete = await service.get_athlete_by_id(athlete_id)
    logger.info(f"Route: Returning athlete {athlete_id}")
    return athlete


@router.post(
    "",
    response_model=AthleteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_athlete(
    data: AthleteCreate, service: AthleteService = Depends(get_athlete_service)
) -> AthleteResponse:
    """Create a new athlete."""
    logger.info(f"Route: POST /athletes for {data.name}")
    athlete = await service.create_athlete(data)
    logger.info(f"Route: Created athlete {athlete.athlete_id}")
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