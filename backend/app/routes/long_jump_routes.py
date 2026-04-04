import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.long_jump_repository import LongJumpRepository
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

router = APIRouter(prefix="/run", tags=["Run"])


async def get_long_jump_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> LongJumpService:
    repository = LongJumpRepository(supabase)
    return LongJumpService(repository)


@router.get(
    "/athletes/{run_id}/metrics/long-jump",
    response_model=LongJumpMetricRow,
)
async def get_long_jump_metrics(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> LongJumpMetricRow:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/long-jump")
    return await service.get_long_jump_metrics(run_id)


@router.get(
    "/athletes/{run_id}/metrics/long-jump/universal/kpis",
    response_model=UniversalKpis,
)
async def get_lj_universal_kpis(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> UniversalKpis:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/long-jump/universal/kpis")
    return await service.get_universal_kpis(run_id)


@router.get(
    "/athletes/{run_id}/metrics/long-jump/universal/steps",
    response_model=list[StepSeriesPoint],
)
async def get_lj_step_series(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[StepSeriesPoint]:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/long-jump/universal/steps")
    return await service.get_step_series(run_id)


@router.get(
    "/athletes/{run_id}/metrics/long-jump/universal/strides",
    response_model=list[StrideSeriesPoint],
)
async def get_lj_stride_series(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[StrideSeriesPoint]:
    logger.info(
        f"Route: GET /run/athletes/{run_id}/metrics/long-jump/universal/strides"
    )
    return await service.get_stride_series(run_id)


@router.get(
    "/athletes/{run_id}/metrics/long-jump/universal/gct-ranges",
    response_model=list[GctRangeBucket],
)
async def get_lj_gct_ranges(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[GctRangeBucket]:
    logger.info(
        f"Route: GET /run/athletes/{run_id}/metrics/long-jump/universal/gct-ranges"
    )
    return await service.get_gct_ranges(run_id)


@router.get(
    "/athletes/{run_id}/metrics/long-jump/approach-profile",
    response_model=list[ApproachProfileData],
)
async def get_lj_approach_profile(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> list[ApproachProfileData]:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/long-jump/approach-profile")
    return await service.get_approach_profile(run_id)


@router.get(
    "/athletes/{run_id}/metrics/long-jump/takeoff",
    response_model=LjTakeoffData,
)
async def get_lj_takeoff(
    run_id: UUID,
    service: LongJumpService = Depends(get_long_jump_service),
) -> LjTakeoffData:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/long-jump/takeoff")
    return await service.get_takeoff_data(run_id)
