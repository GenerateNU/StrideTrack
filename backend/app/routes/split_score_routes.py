import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.core.supabase import get_async_supabase
from app.repositories.split_score_repository import SplitScoreRepository
from app.schemas.split_score_schemas import SplitScoreResponse
from app.services.split_score_service import SplitScoreService, UnsupportedEventError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run", tags=["Run"])


async def get_split_score_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> SplitScoreService:
    return SplitScoreService(SplitScoreRepository(supabase))


@router.get(
    "/athletes/{run_id}/metrics/split-score",
    response_model=SplitScoreResponse,
    summary="Get split score percentiles for a run",
)
async def get_split_score(
    run_id: UUID,
    service: SplitScoreService = Depends(get_split_score_service),
) -> SplitScoreResponse:
    """
    Return a percentile for each race segment normalized by total race time.

    Tells the coach whether the athlete went out too fast, faded late, or
    underperformed on specific hurdles relative to the elite population.

    Percentile interpretation: a **high** percentile for a segment means the
    athlete spent a greater share of their total race time there — i.e., they
    were relatively slower in that segment compared to the population.

    - **404** — run_id not found, or no stride metrics recorded for this run.
    - **422** — event type is not supported for split score analysis.
    """
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/split-score")
    try:
        return await service.get_split_score(run_id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except UnsupportedEventError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
