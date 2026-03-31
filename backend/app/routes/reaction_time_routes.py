import logging

from fastapi import APIRouter, HTTPException

from app.schemas.reaction_time_schemas import ReactionTimeRequest, ReactionTimeResponse
from app.services.reaction_time_service import ReactionTimeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reaction-time", tags=["Reaction Time"])


def get_reaction_time_service() -> ReactionTimeService:
    return ReactionTimeService()


@router.post("/analyze", response_model=ReactionTimeResponse)
async def analyze_reaction_time(
    data: ReactionTimeRequest,
) -> ReactionTimeResponse:
    logger.info("Route: POST /reaction-time/analyze")
    try:
        service = get_reaction_time_service()
        result = service.compute(data)
        logger.info(
            f"Route: Reaction time result = {result.reaction_time_ms}ms ({result.zone})"
        )
        return result
    except ValueError as e:
        logger.warning(f"Route: Bad request - {e}")
        raise HTTPException(status_code=422, detail=str(e)) from e
