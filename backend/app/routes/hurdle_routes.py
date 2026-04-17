import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.hurdle_repository import HurdleRepository
from app.schemas.coach_schemas import Coach
from app.schemas.hurdle_schemas import (
    GctIncreaseData,
    HurdleMetricRow,
    HurdleProjectionResponse,
    HurdleSplitBarData,
    HurdleTimelineResponse,
    LandingGctBarData,
    StepsBetweenHurdlesData,
    TakeoffFtBarData,
    TakeoffGctBarData,
)
from app.services.hurdle_service import HurdleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Hurdle Metrics"])


async def get_hurdle_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> HurdleService:
    repository = HurdleRepository(supabase)
    return HurdleService(repository, coach_id=coach.coach_id)


async def get_hurdle_params(
    run_id: UUID,
    service: HurdleService,
    hurdles_completed: int | None,
    target_event: str | None,
) -> tuple[int | None, str | None]:
    if hurdles_completed is None or target_event is None:
        run = await service.get_run_hurdle_params(run_id)
        if hurdles_completed is None:
            hurdles_completed = run.hurdles_completed
        if target_event is None:
            target_event = run.target_event
    return hurdles_completed, target_event


@router.get("/{run_id}/metrics/hurdles", response_model=list[HurdleMetricRow])
async def get_hurdle_metrics(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> list[HurdleMetricRow]:
    """Get all hurdle metrics for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_hurdle_metrics_by_run_id(
        run_id, hurdles_completed=hurdles_completed
    )


@router.get("/{run_id}/metrics/hurdles/splits", response_model=list[HurdleSplitBarData])
async def get_hurdle_splits(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> list[HurdleSplitBarData]:
    """Get hurdle split bar chart data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/splits")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_hurdle_splits(run_id, hurdles_completed=hurdles_completed)


@router.get(
    "/{run_id}/metrics/hurdles/steps-between",
    response_model=list[StepsBetweenHurdlesData],
)
async def get_steps_between_hurdles(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> list[StepsBetweenHurdlesData]:
    """Get steps between hurdles display data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/steps-between")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_steps_between_hurdles(
        run_id, hurdles_completed=hurdles_completed
    )


@router.get(
    "/{run_id}/metrics/hurdles/takeoff-gct", response_model=list[TakeoffGctBarData]
)
async def get_takeoff_gct(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> list[TakeoffGctBarData]:
    """Get takeoff GCT bar chart data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/takeoff-gct")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_takeoff_gct(run_id, hurdles_completed=hurdles_completed)


@router.get(
    "/{run_id}/metrics/hurdles/landing-gct", response_model=list[LandingGctBarData]
)
async def get_landing_gct(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> list[LandingGctBarData]:
    """Get landing GCT bar chart data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/landing-gct")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_landing_gct(run_id, hurdles_completed=hurdles_completed)


@router.get(
    "/{run_id}/metrics/hurdles/takeoff-ft", response_model=list[TakeoffFtBarData]
)
async def get_takeoff_ft(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> list[TakeoffFtBarData]:
    """Get takeoff flight time bar chart data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/takeoff-ft")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_takeoff_ft(run_id, hurdles_completed=hurdles_completed)


@router.get(
    "/{run_id}/metrics/hurdles/gct-increase", response_model=list[GctIncreaseData]
)
async def get_gct_increase(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> list[GctIncreaseData]:
    """Get GCT increase hurdle-to-hurdle data for a specific run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/gct-increase")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_gct_increase(run_id, hurdles_completed=hurdles_completed)


@router.get(
    "/{run_id}/metrics/hurdles/projection", response_model=HurdleProjectionResponse
)
async def get_hurdle_projection(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> HurdleProjectionResponse:
    """Get projected race time for a partial hurdle run."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/projection")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_hurdle_projection(
        run_id, hurdles_completed=hurdles_completed, target_event=target_event
    )


@router.get("/{run_id}/metrics/hurdles/timeline", response_model=HurdleTimelineResponse)
async def get_hurdle_timeline(
    run_id: UUID,
    hurdles_completed: int | None = Query(default=None, ge=1, le=10),
    target_event: str | None = Query(default=None),
    service: HurdleService = Depends(get_hurdle_service),
) -> HurdleTimelineResponse:
    """Get time-series data for the hurdle timeline chart."""
    logger.info(f"Route: GET /runs/{run_id}/metrics/hurdles/timeline")

    hurdles_completed, target_event = await get_hurdle_params(
        run_id=run_id,
        service=service,
        hurdles_completed=hurdles_completed,
        target_event=target_event,
    )
    return await service.get_hurdle_timeline(
        run_id, hurdles_completed=hurdles_completed
    )
