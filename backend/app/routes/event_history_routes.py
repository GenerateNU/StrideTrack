import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.event_history_repository import EventHistoryRepository
from app.schemas.event_history_schemas import EventHistoryResponse
from app.services.event_history_service import EventHistoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/event-history", tags=["Event History"])


async def get_event_history_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> EventHistoryService:
    repository = EventHistoryRepository(supabase)
    return EventHistoryService(repository)


@router.get("/metrics", response_model=EventHistoryResponse)
async def get_event_history_metrics(
    athlete_id: UUID = Query(...),
    event_type: str = Query(...),
    limit: int | None = Query(default=10),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    service: EventHistoryService = Depends(get_event_history_service),
) -> EventHistoryResponse:
    """Get time history for a specific event type and athlete."""
    logger.info(f"Route: GET /event-history/metrics for athlete {athlete_id}")
    return await service.get_event_history(
        athlete_id=athlete_id,
        event_type=event_type,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )
