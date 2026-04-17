import logging
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.event_history_repository import EventHistoryRepository
from app.schemas.event_history_schemas import EventHistoryResponse, EventType
from app.services.event_history_service import EventHistoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/athletes", tags=["Event History"])


async def get_event_history_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> EventHistoryService:
    repository = EventHistoryRepository(supabase)
    return EventHistoryService(repository)


@router.get("/{athlete_id}/event-history", response_model=EventHistoryResponse)
async def get_event_history_metrics(
    athlete_id: UUID,
    event_type: EventType = Query(...),
    limit: int | None = Query(default=10),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    service: EventHistoryService = Depends(get_event_history_service),
) -> EventHistoryResponse:
    """Get time history for a specific event type and athlete."""
    logger.info(f"Route: GET /athletes/{athlete_id}/event-history")
    return await service.get_event_history(
        athlete_id=athlete_id,
        event_type=event_type,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )
