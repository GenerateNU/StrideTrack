import logging
from uuid import UUID

from app.repositories.run_repository import RunRepository

logger = logging.getLogger(__name__)


class RunService:
    """Service for run metric related business logic."""

    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    async def get_run_metrics(self, athlete_id: UUID) -> list[dict]:
        """Get all run metrics for a specific athlete."""
        logger.info(f"Service: Getting metrics for athlete {athlete_id}")

        # Convert UUID to string for Supabase query
        metrics = await self.repository.get_metrics(str(athlete_id))

        logger.info(f"Service: Retrieved {len(metrics)} metric records")
        return metrics
