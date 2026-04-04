import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.reaction_time_repository import ReactionTimeRepository
from app.schemas.reaction_time_schemas import ReactionTimeResponse
from app.services.reaction_time_service import ReactionTimeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reaction-time", tags=["Reaction Time"])


async def get_reaction_time_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> ReactionTimeService:
    return ReactionTimeService(ReactionTimeRepository(supabase))


@router.get(
    "/{run_id}",
    response_model=ReactionTimeResponse,
    summary="Get reaction time for a run",
)
async def get_reaction_time(
    run_id: UUID,
    service: ReactionTimeService = Depends(get_reaction_time_service),
) -> ReactionTimeResponse:
    logger.info(f"Route: GET /reaction-time/{run_id}")
    return await service.get_reaction_time(run_id)
