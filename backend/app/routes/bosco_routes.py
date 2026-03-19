from fastapi import APIRouter, Depends
from supabase import Client

from app.core.supabase import get_async_supabase
from app.repositories.bosco_repository import BoscoRepository
from app.schemas.bosco_schemas import BoscoMetricsResponse
from app.services.bosco_service import BoscoService

router = APIRouter(prefix="/bosco", tags=["bosco"])


def get_bosco_service(
    supabase: Client = Depends(get_async_supabase),
) -> BoscoService:
    repository = BoscoRepository(supabase)
    return BoscoService(repository)


@router.get("/metrics/{run_id}", response_model=BoscoMetricsResponse)
async def get_bosco_metrics(
    run_id: str,
    service: BoscoService = Depends(get_bosco_service),
) -> BoscoMetricsResponse:
    """Returns computed Bosco test metrics for a given run."""
    return service.get_bosco_metrics(run_id)


@router.get("/runs/{athlete_id}")
async def get_bosco_runs(
    athlete_id: str,
    service: BoscoService = Depends(get_bosco_service),
) -> list[dict]:
    """Returns all Bosco test runs for a given athlete."""
    return service.get_bosco_runs_for_athlete(athlete_id)
