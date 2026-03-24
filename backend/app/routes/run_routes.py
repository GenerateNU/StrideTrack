import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunCreate, RunCreateResponse, RunRepository
from app.schemas.run_schemas import (
    LROverlayData,
    RunResponse,
    SprintDriftData,
    StackedBarData,
    StepFrequencyData,
    RunMeta
)
from app.services.run_service import RunService

from app.schemas.coach_schemas import Coach
from app.core.auth import get_current_coach

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run", tags=["Run"])


async def get_run_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> RunService:
    repository = RunRepository(supabase)
    return RunService(repository, coach_id=coach.coach_id)


@router.get("", response_model=list[RunCreateResponse])
async def list_runs(
    service: RunService = Depends(get_run_service),
) -> list[RunCreateResponse]:
    """Get all runs, ordered by most recent first."""
    logger.info("Route: GET /run")
    runs = await service.get_all_runs()
    logger.info(f"Route: Returning {len(runs)} runs")
    return runs


@router.get("/athlete/{athlete_id}", response_model=list[RunCreateResponse])
async def list_runs_by_athlete(
    athlete_id: UUID,
    service: RunService = Depends(get_run_service),
) -> list[RunCreateResponse]:
    """Get all runs for a specific athlete."""
    logger.info(f"Route: GET /run/athlete/{athlete_id}")
    runs = await service.get_runs_by_athlete_id(athlete_id)
    logger.info(f"Route: Returning {len(runs)} runs for athlete {athlete_id}")
    return runs


@router.get("/athletes/{run_id}/metrics", response_model=list[RunResponse])
async def get_run_metric_record(
    run_id: UUID, service: RunService = Depends(get_run_service)
) -> list[RunResponse]:
    """Get all run metrics for a specific run."""
    logger.info(f"Route: GET /athletes/{run_id}/metrics")
    metrics = await service.get_metrics_by_run_id(run_id)
    logger.info(f"Route: Returning a metric record for run: {run_id}")
    return metrics

@router.get("/athletes/{run_id}/metadata", response_model=RunMeta)
async def get_run_metadata(
    run_id: UUID, service: RunService = Depends(get_run_service)
) -> RunMeta:
    """Get a specific run's metadata'."""
    logger.info(f"Route: GET /athletes/{run_id}/metadata")
    meta = await service.get_meta_by_run_id(run_id)
    logger.info(f"Route: Returning metadata for run: {run_id}")
    return meta

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
    return await service.transform_step_frequency(run_id)


@router.post("", response_model=RunCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    data: RunCreate, service: RunService = Depends(get_run_service)
) -> RunCreateResponse:
    """Create a new run."""
    logger.info(f"Route: POST /run for athlete {data.athlete_id}")
    run = await service.create_run(data)
    logger.info(f"Route: Created run {run.run_id}")
    return run
