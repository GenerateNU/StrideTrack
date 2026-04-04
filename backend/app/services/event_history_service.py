import logging
from datetime import date
from uuid import UUID

# from supabase._async.client import AsyncClient
from app.repositories.event_history_repository import EventHistoryRepository
from app.schemas.event_history_schemas import EventHistoryPoint, EventHistoryResponse

logger = logging.getLogger(__name__)


class EventHistoryService:
    def __init__(self, repository: EventHistoryRepository) -> None:
        self.repository = repository

    async def get_event_history(
        self,
        athlete_id: UUID,
        event_type: str,
        limit: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> EventHistoryResponse:
        logger.info(f"Service: Getting {event_type} history for athlete {athlete_id}")

        runs = await self.repository.get_runs_by_event_type(
            athlete_id=athlete_id,
            event_type=event_type,
            limit=limit,
            date_from=date_from,
            date_to=date_to,
        )

        if not runs:
            return EventHistoryResponse(
                event_type=event_type,
                athlete_id=str(athlete_id),
                data_points=[],
                best_time_seconds=None,
                total_runs=0,
            )

        data_points = [
            EventHistoryPoint(
                run_number=index + 1,
                run_id=run["run_id"],
                run_name=run["name"] or f"Run {index + 1}",
                date=run["created_at"][:10],
                total_time_seconds=round(run["elapsed_ms"] / 1000, 3),
            )
            for index, run in enumerate(runs)
        ]

        if not data_points:
            return EventHistoryResponse(
                event_type=event_type,
                athlete_id=str(athlete_id),
                data_points=[],
                best_time_seconds=None,
                total_runs=0,
            )

        best_time = min(p.total_time_seconds for p in data_points)

        return EventHistoryResponse(
            event_type=event_type,
            athlete_id=str(athlete_id),
            data_points=data_points,
            best_time_seconds=best_time,
            total_runs=len(data_points),
        )
