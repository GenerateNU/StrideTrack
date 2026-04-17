from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.bosco_repository import BoscoRepository
from app.schemas.bosco_schemas import BoscoMetricsResponse
from app.services.bosco_service import BoscoService

router = APIRouter(prefix="/runs", tags=["Bosco Metrics"])


async def get_bosco_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> BoscoService:
    repository = BoscoRepository(supabase)
    return BoscoService(repository)


@router.get("/{run_id}/metrics/bosco", response_model=BoscoMetricsResponse)
async def get_bosco_metrics(
    run_id: str,
    service: BoscoService = Depends(get_bosco_service),
) -> BoscoMetricsResponse:
    """Returns computed Bosco test metrics for a given run."""
    return await service.get_bosco_metrics(run_id)
