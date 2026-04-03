import logging
from datetime import date
from uuid import UUID

from supabase._async.client import AsyncClient

from app.schemas.event_history_schemas import EventHistoryRun

logger = logging.getLogger(__name__)


class EventHistoryRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def get_runs_by_event_type(
        self,
        athlete_id: UUID,
        event_type: str,
        limit: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[EventHistoryRun]:
        logger.info(f"Repository: Fetching {event_type} runs for athlete {athlete_id}")

        query = (
            self.supabase.table("run")
            .select("run_id, name, event_type, elapsed_ms, created_at")
            .eq("athlete_id", str(athlete_id))
            .eq("event_type", event_type)
            .order("created_at", desc=False)
        )

        if date_from:
            query = query.gte("created_at", date_from)
        if date_to:
            query = query.lte("created_at", f"{date_to}T23:59:59")
        if limit:
            query = query.limit(limit)

        response = await query.execute()
        logger.info(f"Repository: Found {len(response.data)} runs")
        return response.data
