import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.all_repositories_repository import AthletesRepo
from app.schemas.all_schemas import (
    AthleteCreate,
    AthleteUpdate,
    AthleteResponse,
)

from app.services.all_services import AthletesService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/athletes", tags=["Athletes"])


# Dependency injection
async def get_athletes_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> AthletesService:
    repository = AthletesRepo(supabase)
    return AthletesService(repository)


@router.get("/", response_model=list[AthleteResponse])
async def list_athletes(service: AthletesService = Depends(get_athletes_service)):
    """Get all athletes."""
    logger.info("Route: GET /athletes")
    athletes = await service.get_all_athletes()
    logger.info(f"Route: Returning {len(athletes)} athletes")
    return athletes


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete_by_id(
    athlete_id: UUID, service: AthletesService = Depends(get_athletes_service)
):
    """Get an athlete by ID."""
    logger.info(f"Route: GET /athletes/{athlete_id}")
    athlete = await service.get_athlete_by_id(athlete_id)
    logger.info(f"Route: Returning athlete {athlete_id}")
    return athlete

@router.get("/{athlete_name}", response_model=AthleteResponse)
async def get_athlete_by_name(
    athlete_name: str, service: AthletesService = Depends(get_athletes_service)
):
    """Get an athlete by name."""
    logger.info(f"Route: GET /athletes/{athlete_name}")
    athlete = await service.get_athlete_by_name(athlete_name)
    logger.info(f"Route: Returning athlete {athlete_name}")
    return athlete

@router.get("/{coach_id}", response_model=list[AthleteResponse])
async def get_athletes_by_coach(
    coach_id: UUID, service: AthletesService = Depends(get_athletes_service)
):
    """Get all athletes for a coach."""
    logger.info(f"Route: GET /athletes/{coach_id}")
    athlete = await service.get_athlete_by_coach(coach_id)
    logger.info(f"Route: Returning athletes for coach {coach_id}")
    return athlete

@router.post(
    "/",
    response_model=AthleteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_athlete(
    data: AthleteCreate, service: AthletesService = Depends(get_athletes_service)
):
    """Create a new athlete."""
    logger.info(f"Route: POST /athletes for athlete {data.athlete_name}")
    athlete = await service.create_athlete(data.model_dump(exclude_unset=True))
    logger.info(f"Route: Created athlete {athlete['id']}")
    return athlete


@router.patch("/{athlete_id}", response_model=TrainingRunResponse)
async def update_athlete(
    athlete_id: UUID,
    data: AthleteUpdate,
    service: AthletesService = Depends(get_athletes_service),
):
    """Update an athlete."""
    logger.info(f"Route: PATCH /athletes/{athlete_id}")
    athlete = await service.update_athlete(athlete_id, data.model_dump(exclude_unset=True))
    logger.info(f"Route: Updated athlete {athlete_id}")
    return athlete


@router.delete("/{athlete_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_athlete(
    athlete_id: UUID, service: AthletesService = Depends(get_athletes_service)
):
    """Delete an athlete."""
    logger.info(f"Route: DELETE /athletes/{athlete_id}")
    await service.delete_athlete(athlete_id)
    logger.info(f"Route: Deleted athlete {athlete_id}")
