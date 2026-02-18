import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient
from typing import Literal

from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.run_schemas import RunResponse, LROverlayData, StackedBarData
from app.services.run_service import RunService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run", tags=["Run"])


# Dependency injection
async def get_run_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> RunService:
    repository = RunRepository(supabase)
    return RunService(repository)


@router.get("/athletes/{run_id}/metrics", response_model=list[RunResponse])
async def get_run_metric_record(
    run_id: UUID, service: RunService = Depends(get_run_service)
) -> list[RunResponse]:
    """Get all run metrics for a specific run."""
    logger.info(f"Route: GET /athletes/{run_id}/metrics")
    metrics = await service.get_metrics_by_run_id(run_id)
    logger.info(
        f"Route: Returning a 