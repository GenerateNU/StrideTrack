# app/routes/hurdle_routes.py

import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.hurdle_schemas import HurdleMetricRow
from app.services.hurdle_service import HurdleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run", tags=["Run"])


# Dependency injection
async def get_hurdle_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> HurdleService:
    repository = RunRepository(supabase)
    return HurdleService(repository)


@router.get(
    "/athletes/{run_id}/metrics/hurdles",
    response_model=list[HurdleMetricRow],
)
async def get_hurdle_metrics(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[HurdleMetricRow]:
    """
    Get per-hurdle derived metrics for a specific run.
    """
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles")
    return await service.get_hurdle_metrics_by_run_id(run_id)

# Future endpoints (placeholders):
# /athletes/{run_id}/metrics/hurdles/splits
# /athletes/{run_id}/metrics/hurdles/takeoff-gct
# /athletes/{run_id}/metrics/hurdles/landing-gct
# /athletes/{run_id}/metrics/hurdles/takeoff-ft