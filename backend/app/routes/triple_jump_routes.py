import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.triple_jump_repository import TripleJumpRepository
from app.schemas.coach_schemas import Coach
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

router = APIRouter(prefix="/runs", tags=["Triple Jump Metrics"])


async def get_triple_jump_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> TripleJumpService:
    repository = TripleJumpRepository(supabase)
    return TripleJumpService(repository, coach_id=coach.coach_id)


@router.get("/{run_id}/metrics/triple-jump", response_model=TripleJumpMetricRow)
async def get_triple_jump_metrics(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> TripleJumpMetricRow:
    """Get triple jump metrics for a run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/triple-jump")
    return await service.get_triple_jump_metrics(run_id)


@router.get("/{run_id}/metrics/triple-jump/kpis", response_model=UniversalKpis)
async def get_tj_universal_kpis(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> UniversalKpis:
    """Get universal KPIs for a triple jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/triple-jump/kpis")
    return await service.get_universal_kpis(run_id)


@router.get(
    "/{run_id}/metrics/triple-jump/steps",
    response_model=list[StepSeriesPoint],
)
async def get_tj_step_series(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[StepSeriesPoint]:
    """Get step series for a triple jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/triple-jump/steps")
    return await service.get_step_series(run_id)


@router.get(
    "/{run_id}/metrics/triple-jump/strides",
    response_model=list[StrideSeriesPoint],
)
async def get_tj_stride_series(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[StrideSeriesPoint]:
    """Get stride series for a triple jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/triple-jump/strides")
    return await service.get_stride_series(run_id)


@router.get(
    "/{run_id}/metrics/triple-jump/gct-ranges",
    response_model=list[GctRangeBucket],
)
async def get_tj_gct_ranges(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[GctRangeBucket]:
    """Get GCT range buckets for a triple jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/triple-jump/gct-ranges")
    return await service.get_gct_ranges(run_id)


@router.get(
    "/{run_id}/metrics/triple-jump/phase-ratio", response_model=list[PhaseRatioData]
)
async def get_tj_phase_ratio(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> list[PhaseRatioData]:
    """Get phase ratio data for a triple jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/triple-jump/phase-ratio")
    return await service.get_phase_ratio(run_id)


@router.get(
    "/{run_id}/metrics/triple-jump/contact-efficiency",
    response_model=TjContactEfficiencyData,
)
async def get_tj_contact_efficiency(
    run_id: UUID,
    service: TripleJumpService = Depends(get_triple_jump_service),
) -> TjContactEfficiencyData:
    """Get contact time efficiency for a triple jump run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/triple-jump/contact-efficiency")
    return await service.get_contact_efficiency(run_id)
