from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.routes.athlete_routes import router as athlete_router
from app.routes.auth_routes import router as auth_router
from app.routes.bosco_routes import router as bosco_router
from app.routes.csv_routes import router as csv_router
from app.routes.example_routes import router as example_router
from app.routes.hurdle_routes import router as hurdle_router
from app.routes.run_routes import router as run_router
from app.routes.split_score_routes import router as split_score_router
from app.schemas.health_schemas import HealthResponse

api_router = APIRouter(prefix="/api")


@api_router.get("/health")
async def health_check(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> HealthResponse:
    try:
        await supabase.table("training_runs").select("count", count="exact").execute()
        return HealthResponse(status="healthy", database="connected")
    except Exception as e:
        return HealthResponse(status="unhealthy", database="disconnected", error=str(e))


api_router.include_router(example_router)
api_router.include_router(csv_router)
api_router.include_router(auth_router)
api_router.include_router(athlete_router)
api_router.include_router(run_router)
api_router.include_router(bosco_router)
api_router.include_router(hurdle_router)
api_router.include_router(split_score_router)
