import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase._async.client import AsyncClient

from app.core.auth import get_current_coach
from app.core.supabase import get_async_supabase
from app.repositories.run_repository import RunRepository
from app.schemas.coach_schemas import Coach
from app.schemas.feedback_schemas import FeedbackResponse
from app.services.feedback_service import FeedbackService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["Feedback"])


async def get_feedback_service(
    coach: Coach = Depends(get_current_coach),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> FeedbackService:
    repository = RunRepository(supabase)
    return FeedbackService(repository, coach_id=coach.coach_id)


@router.get("/{run_id}/feedback", response_model=FeedbackResponse)
async def get_run_feedback(
    run_id: UUID,
    service: FeedbackService = Depends(get_feedback_service),
) -> FeedbackResponse:
    """Generate AI coach feedback for a completed run."""
    logger.info(f"Route: GET /runs/{run_id}/feedback")
    feedback = await service.get_feedback(run_id)
    return FeedbackResponse(feedback=feedback)
