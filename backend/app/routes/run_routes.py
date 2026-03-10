import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.run_schemas import (
    LROverlayData,
    RunResponse,
    SprintDriftData,
    StackedBarData,
    StepFrequencyData,
)
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
    logger.info(f"Route: Returning a metric record for run: {run_id}")
    return metrics


@router.get("/athletes/{run_id}/metrics/lr-overlay", response_model=list[LROverlayData])
async def get_lr_overlay(
    run_id: UUID,
    metric: Literal["gct_ms", "flight_ms"],
    service: RunService = Depends(get_run_service),
) -> list[LROverlayData]:
    """Get left/right overlay chart data for a specific run."""
    logger.info(f"Route: GET /athletes/{run_id}/metrics/lr-overlay?metric={metric}")
    return await service.transform_lr_overlay(run_id, metric)


@router.get(
    "/athletes/{run_id}/metrics/stacked-bar", response_model=list[StackedBarData]
)
async def get_stacked_bar(
    run_id: UUID,
    service: RunService = Depends(get_run_service),
) -> list[StackedBarData]:
    """Get stacked bar chart data for a specific run."""
    logger.info(f"Route: GET /athletes/{run_id}/metrics/stacked-bar")
    return await service.transform_stacked_bar(run_id)


@router.get("/athletes/{run_id}/metrics/sprint-drift", response_model=SprintDriftData)
async def get_sprint_drift(
    run_id: UUID,
    service: RunService = Depends(get_run_service),
) -> SprintDriftData:
    """Get GCT and FT drift percentages for sprint fatigue tracking."""
    logger.info(f"Route: GET /athletes/{run_id}/metrics/sprint-drift")
    return await service.get_sprint_drift(run_id)


@router.get(
    "/athletes/{run_id}/metrics/step-frequency", response_model=list[StepFrequencyData]
)
async def get_step_frequency(
    run_id: UUID,
    service: RunService = Depends(get_run_service),
) -> list[StepFrequencyData]:
    """Get step frequency data for a specific run."""
    logger.info(f"Route: GET /athletes/{run_id}/metrics/step-frequency")
    return await service.get_step_frequency(run_id)
