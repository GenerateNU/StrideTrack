import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.split_score_repository import SplitScoreRepository
from app.schemas.split_score_schemas import SplitScoreResponse
from app.services.split_score_service import SplitScoreService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Split Score"])


async def get_split_score_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> SplitScoreService:
    return SplitScoreService(SplitScoreRepository(supabase))


@router.get(
    "/{run_id}/metrics/split-score",
    response_model=SplitScoreResponse,
    summary="Get split score percentiles for a run",
)
async def get_split_score(
    run_id: UUID,
    service: SplitScoreService = Depends(get_split_score_service),
) -> SplitScoreResponse:
    logger.info(f"Route: GET /runs/{run_id}/metrics/split-score")
    return await service.get_split_score(run_id)
