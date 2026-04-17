import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.long_jump_repository import LongJumpRepository
from app.schemas.coach_schemas import Coach
from app.schemas.long_jump_schemas import (
    ApproachProfileData,
    LjTakeoffData,
    LongJumpMetricRow,
)
from app.schemas.run_schemas import (
    GctRangeBucket,
    StepSeriesPoint,
    StrideSeriesPoint,
    UniversalKpis,
)
from app.services.long_jump_service import LongJumpService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Long Jump Metrics"])


async def get_long_jump_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> LongJumpService:
    repository = LongJumpRepository(supabase)
    return LongJumpService(repository, coach_id=coach.coach_id)


@router.get("/{run_id}/metrics/long-jump", response_model=LongJumpMetricRow)
async def get_long_jump_metrics(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> LongJumpMetricRow:
    """Get long jump metrics for a run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/long-jump")
    return await service.get_long_jump_metrics(run_id)


@router.get("/{run_id}/metrics/long-jump/kpis", response_model=UniversalKpis)
async def get_lj_universal_kpis(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> UniversalKpis:
    """Get universal KPIs for a long jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/long-jump/kpis")
    return await service.get_universal_kpis(run_id)


@router.get(
    "/{run_id}/metrics/long-jump/steps",
    response_model=list[StepSeriesPoint],
)
async def get_lj_step_series(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[StepSeriesPoint]:
    """Get step series for a long jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/long-jump/steps")
    return await service.get_step_series(run_id)


@router.get(
    "/{run_id}/metrics/long-jump/strides",
    response_model=list[StrideSeriesPoint],
)
async def get_lj_stride_series(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[StrideSeriesPoint]:
    """Get stride series for a long jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/long-jump/strides")
    return await service.get_stride_series(run_id)


@router.get(
    "/{run_id}/metrics/long-jump/gct-ranges",
    response_model=list[GctRangeBucket],
)
async def get_lj_gct_ranges(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[GctRangeBucket]:
    """Get GCT range buckets for a long jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/long-jump/gct-ranges")
    return await service.get_gct_ranges(run_id)


@router.get(
    "/{run_id}/metrics/long-jump/approach-profile",
    response_model=list[ApproachProfileData],
)
async def get_lj_approach_profile(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[ApproachProfileData]:
    """Get approach profile for a long jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/long-jump/approach-profile")
    return await service.get_approach_profile(run_id)


@router.get("/{run_id}/metrics/long-jump/takeoff", response_model=LjTakeoffData)
async def get_lj_takeoff(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> LjTakeoffData:
    """Get takeoff data for a long jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/long-jump/takeoff")
    return await service.get_takeoff_data(run_id)
