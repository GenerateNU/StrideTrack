import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.triple_jump_repository import TripleJumpRepository
from app.schemas.run_schemas import (
    GctRangeBucket,
    StepSeriesPoint,
    StrideSeriesPoint,
    UniversalKpis,
)
from app.schemas.triple_jump_schemas import (
    PhaseRatioData,
    TjContactEfficiencyData,
    TripleJumpMetricRow,
)
from app.services.triple_jump_service import TripleJumpService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/run", tags=["Run"])


async def get_triple_jump_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> TripleJumpService:
    repository = TripleJumpRepository(supabase)
    return TripleJumpService(repository)


@router.get(
    "/athletes/{run_id}/metrics/triple-jump",
    response_model=TripleJumpMetricRow,
)
async def get_triple_jump_metrics(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> TripleJumpMetricRow:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/triple-jump")
    return await service.get_triple_jump_metrics(run_id)


@router.get(
    "/athletes/{run_id}/metrics/triple-jump/universal/kpis",
    response_model=UniversalKpis,
)
async def get_tj_universal_kpis(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> UniversalKpis:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/triple-jump/universal/kpis")
    return await service.get_universal_kpis(run_id)


@router.get(
    "/athletes/{run_id}/metrics/triple-jump/universal/steps",
    response_model=list[StepSeriesPoint],
)
async def get_tj_step_series(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[StepSeriesPoint]:
    logger.info(
        f"Route: GET /run/athletes/{run_id}/metrics/triple-jump/universal/steps"
    )
    return await service.get_step_series(run_id)


@router.get(
    "/athletes/{run_id}/metrics/triple-jump/universal/strides",
    response_model=list[StrideSeriesPoint],
)
async def get_tj_stride_series(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[StrideSeriesPoint]:
    logger.info(
        f"Route: GET /run/athletes/{run_id}/metrics/triple-jump/universal/strides"
    )
    return await service.get_stride_series(run_id)


@router.get(
    "/athletes/{run_id}/metrics/triple-jump/universal/gct-ranges",
    response_model=list[GctRangeBucket],
)
async def get_tj_gct_ranges(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[GctRangeBucket]:
    logger.info(
        f"Route: GET /run/athletes/{run_id}/metrics/triple-jump/universal/gct-ranges"
    )
    return await service.get_gct_ranges(run_id)


@router.get(
    "/athletes/{run_id}/metrics/triple-jump/phase-ratio",
    response_model=list[PhaseRatioData],
)
async def get_tj_phase_ratio(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[PhaseRatioData]:
    logger.info(f"Route: GET /run/athletes/{run_id}/metrics/triple-jump/phase-ratio")
    return await service.get_phase_ratio(run_id)


@router.get(
    "/athletes/{run_id}/metrics/triple-jump/contact-efficiency",
    response_model=TjContactEfficiencyData,
)
async def get_tj_contact_efficiency(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> TjContactEfficiencyData:
    logger.info(
        f"Route: GET /run/athletes/{run_id}/metrics/triple-jump/contact-efficiency"
    )
    return await service.get_contact_efficiency(run_id)
