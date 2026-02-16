import logging

from app.utils.event_display_names import get_all_events
from fastapi import APIRouter

from app.schemas.event_schemas import EventListResponse, EventOption

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/types", response_model=EventListResponse)
async def get_event_types() -> EventListResponse:
    logger.info("Route: GET /events/types")
    events = get_all_events()
    event_options = [EventOption(value=e["value"], label=e["label"]) for e in events]
    logger.info(f"Route: Returning {len(event_options)} event types")
    return EventListResponse(events=event_options)
