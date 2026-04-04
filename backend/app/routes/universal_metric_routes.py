import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.coach_schemas import Coach
from app.schemas.run_schemas import (
    AsymmetryData,
    GCTRangeData,
    LROverlayData,
    RunResponse,
    StackedBarData,
)
from app.services.universal_metric_service import UniversalMetricService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Universal Metrics"])


async def get_universal_metric_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> UniversalMetricService:
    repository = RunRepository(supabase)
    return UniversalMetricService(repository, coach_id=coach.coach_id)


@router.get("/{run_id}/metrics", response_model=list[RunResponse])
async def get_run_metrics(
    run_id: UUID,
    service: UniversalMetricService = Depends(get_universal_metric_service),
) -> list[RunResponse]:
    """Get all run metrics for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics")
    return await service.get_metrics_by_run_id(run_id)


@router.get("/{run_id}/metrics/lr-overlay", response_model=list[LROverlayData])
async def get_lr_overlay(
    run_id: UUID,
    metric: Literal["gct_ms", "flight_ms"],
    service: UniversalMetricService = Depends(get_universal_metric_service),
) -> list[LROverlayData]:
    """Get left/right overlay chart data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/lr-overlay?metric={metric}")
    return await service.transform_lr_overlay(run_id, metric)


@router.get("/{run_id}/metrics/stacked-bar", response_model=list[StackedBarData])
async def get_stacked_bar(
    run_id: UUID,
    service: UniversalMetricService = Depends(get_universal_metric_service),
) -> list[StackedBarData]:
    """Get stacked bar chart data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/stacked-bar")
    return await service.transform_stacked_bar(run_id)


@router.get("/{run_id}/metrics/asymmetry", response_model=AsymmetryData)
async def get_asymmetry(
    run_id: UUID,
    service: UniversalMetricService = Depends(get_universal_metric_service),
) -> AsymmetryData:
    """Get GCT and FT asymmetry % between left and right foot."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/asymmetry")
    return await service.get_asymmetry(run_id)


@router.get("/{run_id}/metrics/gct-range", response_model=GCTRangeData)
async def get_gct_range(
    run_id: UUID,
    min_ms: float = Query(default=100.0),
    max_ms: float = Query(default=200.0),
    service: UniversalMetricService = Depends(get_universal_metric_service),
) -> GCTRangeData:
    """Bucket steps by GCT into below / in / above a user-defined range."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/gct-range")
    return await service.get_gct_range(run_id, min_ms, max_ms)
