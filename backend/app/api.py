from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.routes import athletes, coaches, training_runs 

api_router = APIRouter(prefix="/api")


@api_router.get("/health")
async def health_check(supabase: AsyncClient = Depends(get_async_supabase)):
    try:
        await supabase.table("training_runs").select("count", count="exact").execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


api_router.include_router(athletes.router)
api_router.include_router(coaches.router)
api_router.include_router(training_runs.router)
