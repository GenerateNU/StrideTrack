import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.core.supabase import get_async_supabase
from app.repositories.reaction_time_repository import ReactionTimeRepository
from app.schemas.reaction_time_schemas import (
    AverageReactionTimeResponse,
    ReactionTimeResponse,
)
from app.services.reaction_time_service import ReactionTimeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Reaction Time"])


async def get_reaction_time_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> ReactionTimeService:
    return ReactionTimeService(ReactionTimeRepository(supabase))


@router.get(
    "/{run_id}/metrics/reaction-time",
    response_model=ReactionTimeResponse,
    summary="Get reaction time for a run",
)
async def get_reaction_time(
    run_id: UUID,
    service: ReactionTimeService = Depends(get_reaction_time_service),
) -> ReactionTimeResponse:
    logger.info(f"Route: GET /runs/{run_id}/metrics/reaction-time")
    try:
        return await service.get_reaction_time(run_id)
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.get(
    "/athletes/{athlete_id}/metrics/reaction-time/average",
    response_model=AverageReactionTimeResponse,
    summary="Get average reaction time for an athlete across all non-bosco runs",
)
async def get_average_reaction_time(
    athlete_id: UUID,
    service: ReactionTimeService = Depends(get_reaction_time_service),
) -> AverageReactionTimeResponse:
    logger.info(f"Route: GET /runs/athletes/{athlete_id}/metrics/reaction-time/average")
    try:
        return await service.get_average_reaction_time(athlete_id)
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
