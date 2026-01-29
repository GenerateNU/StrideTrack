import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.all_repositories import CoachesRepo
from app.schemas.all_schemas import (
    AthleteResponse,
    CoachUpdate,
    CoachResponse,
    TrainingRunResponse,
)

from app.services.all_services import CoachesService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coaches", tags=["Coaches"])


# Dependency injection
async def get_coaches_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> CoachesService:
    repository = CoachesRepo(supabase)
    return CoachesService(repository)


@router.get("/", response_model=list[AthleteResponse])
async def list_coaches(service: CoachesService = Depends(get_coaches_service)):
    """Get all coaches."""
    logger.info("Route: GET /coaches")
    coaches = await service.get_all_coaches()
    logger.info(f"Route: Returning {len(coaches)} coaches")
    return coaches


@router.get("/{coach_id}", response_model=AthleteResponse)
async def get_coach_by_id(
    coach_id: UUID, service: CoachesService = Depends(get_coaches_service)
):
    """Get an coach by ID."""
    logger.info(f"Route: GET /coaches/{coach_id}")
    coach = await service.get_coach_by_id(coach_id)
    logger.info(f"Route: Returning athlete {coach_id}")
    return coach

@router.get("/{coach_name}", response_model=AthleteResponse)
async def get_coach_by_name(
    coach_name: str, service: CoachesService = Depends(get_coaches_service)
):
    """Get a coach by name."""
    logger.info(f"Route: GET /coaches/{coach_name}")
    coach = await service.get_coach_by_name(coach_name)
    logger.info(f"Route: Returning coach {coach_name}")
    return coach


@router.patch("/{coach_id}", response_model=TrainingRunResponse)
async def update_coach(
    coach_id: UUID,
    data: CoachUpdate,
    service: CoachesService = Depends(get_coaches_service)
):
    """Update a coach."""
    logger.info(f"Route: PATCH /coaches/{coach_id}")
    coach = await service.update_coach(coach_id, data.model_dump(exclude_unset=True))
    logger.info(f"Route: Updated coach {coach_id}")
    return coach
