import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.run_schemas import (RunResponse)
from app.services.run_service import RunService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run", tags=["Run"])

# Dependency injection
async def get_run_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> RunService:
    repository = RunRepository(supabase)
    return RunService(repository)

@router.get("/athletes/{athlete_id}/metrics", response_model=list[RunResponse])
async def get_athlete_run_metrics(
    athlete_id: UUID,
    service: RunService = Depends(get_run_service)
) -> list[RunResponse]:
    """Get all run metrics for a specific athlete."""
    logger.info(f"Route: GET /athletes/{athlete_id}/metrics")
    metrics = await service.get_run_metrics(athlete_id)
    logger.info(f"Route: Returning {len(metrics)} metric records for athlete {athlete_id}")
    return metrics
