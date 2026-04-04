import logging
from uuid import UUID

from app.repositories.run_repository import RunRepository
from app.schemas.run_schemas import RunCreate, RunCreateResponse, RunMeta

logger = logging.getLogger(__name__)


class RunService:
    """Service for run CRUD operations."""

    def __init__(self, repository: RunRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def create_run(self, data: RunCreate) -> RunCreateResponse:
        """Create a new run."""
        await self.repository.verify_athlete_belongs_to_coach(data.athlete_id, self.coach_id)
        logger.info(f"Service: Creating run for athlete {data.athlete_id}")
        run = await self.repository.create(data)
        logger.info(f"Service: Created run {run.run_id}")
        return run

    async def get_all_runs(self) -> list[RunCreateResponse]:
        """Get all runs for the current coach's athletes."""
        logger.info("Service: Getting all runs for coach")
        runs = await self.repository.get_all(self.coach_id)
        logger.info(f"Service: Retrieved {len(runs)} runs")
        return runs

    async def get_runs_by_athlete_id(self, athlete_id: UUID) -> list[RunCreateResponse]:
        """Get all runs for a specific athlete."""
        await self.repository.verify_athlete_belongs_to_coach(athlete_id, self.coach_id)
        logger.info(f"Service: Getting runs for athlete {athlete_id}")
        runs = await self.repository.get_by_athlete_id(athlete_id)
        logger.info(f"Service: Retrieved {len(runs)} runs for athlete {athlete_id}")
        return runs

    async def get_meta_by_run_id(self, run_id: UUID) -> RunMeta:
        """Get metadata for a specific run."""
        await self.repository.verify_run_belongs_to_coach(run_id, self.coach_id)
        logger.info(f"Service: Getting metadata for run {run_id}")
        meta = await self.repository.get_run_meta(run_id)
        logger.info(f"Service: Retrieved metadata for run {run_id}")
        return meta
