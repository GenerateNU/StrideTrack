import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.hurdle_repository import HurdleRepository
from app.schemas.hurdle_schemas import (
    GctIncreaseData,
    HurdleMetricRow,
    HurdleSplitBarData,
    LandingGctBarData,
    StepsBetweenHurdlesData,
    TakeoffFtBarData,
    TakeoffGctBarData,
)
from app.services.hurdle_service import HurdleService
from app.schemas.coach_schemas import Coach
from app.core.auth import get_current_coach

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run", tags=["Run"])


# Dependency injection
async def get_hurdle_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> HurdleService:
    repository = HurdleRepository(supabase)
    return HurdleService(repository, coach_id=coach.coach_id)


@router.get(
    "/athletes/{run_id}/metrics/hurdles",
    response_model=list[HurdleMetricRow],
)
async def get_hurdle_metrics(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[HurdleMetricRow]:
    """Get all hurdle metrics for a specific run."""
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles")
    return await service.get_hurdle_metrics_by_run_id(run_id)


@router.get(
    "/athletes/{run_id}/metrics/hurdles/splits",
    response_model=list[HurdleSplitBarData],
)
async def get_hurdle_splits(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[HurdleSplitBarData]:
    """Get hurdle split bar chart data for a specific run."""
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles/splits")
    return await service.get_hurdle_splits(run_id)


@router.get(
    "/athletes/{run_id}/metrics/hurdles/steps-between",
    response_model=list[StepsBetweenHurdlesData],
)
async def get_steps_between_hurdles(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[StepsBetweenHurdlesData]:
    """Get steps between hurdles display data for a specific run."""
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles/steps-between")
    return await service.get_steps_between_hurdles(run_id)


@router.get(
    "/athletes/{run_id}/metrics/hurdles/takeoff-gct",
    response_model=list[TakeoffGctBarData],
)
async def get_takeoff_gct(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[TakeoffGctBarData]:
    """Get takeoff GCT bar chart data for a specific run."""
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles/takeoff-gct")
    return await service.get_takeoff_gct(run_id)


@router.get(
    "/athletes/{run_id}/metrics/hurdles/landing-gct",
    response_model=list[LandingGctBarData],
)
async def get_landing_gct(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[LandingGctBarData]:
    """Get landing GCT bar chart data for a specific run."""
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles/landing-gct")
    return await service.get_landing_gct(run_id)


@router.get(
    "/athletes/{run_id}/metrics/hurdles/takeoff-ft",
    response_model=list[TakeoffFtBarData],
)
async def get_takeoff_ft(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[TakeoffFtBarData]:
    """Get takeoff flight time bar chart data for a specific run."""
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles/takeoff-ft")
    return await service.get_takeoff_ft(run_id)


@router.get(
    "/athletes/{run_id}/metrics/hurdles/gct-increase",
    response_model=list[GctIncreaseData],
)
async def get_gct_increase(
    run_id: UUID,
    service: HurdleService = Depends(get_hurdle_service),
) -> list[GctIncreaseData]:
    """Get GCT increase hurdle-to-hurdle data for a specific run."""
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/hurdles/gct-increase")
    return await service.get_gct_increase(run_id)
