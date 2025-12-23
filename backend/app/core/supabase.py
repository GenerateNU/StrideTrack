from supabase._async.client import AsyncClient
from supabase._async.client import create_client as acreate_client

from app.core.config import settings

supabase: AsyncClient | None = None


async def get_async_supabase() -> AsyncClient:
    global supabase
    if supabase is None:
        supabase = await acreate_client(
            settings.supabase_url, settings.supabase_service_role_key
        )
        print("Supabase Initialized")
    return supabase
