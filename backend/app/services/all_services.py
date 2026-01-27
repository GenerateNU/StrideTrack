import logging
from uuid import UUID

from app.repositories.all_repositories import CoachesRepo, AthletesRepo, TrianingRunsRepo

logger = logging.getLogger(__name__)

class CoachesService:
    """Service layer for coaches business logic."""
    
    def __init__(self, repository: CoachesRepo):
        self.repository = repository
    
    async def get_all_coaches(self) -> list[dict]:
        """Get all coaches."""
        logger.info("Service: Getting all coaches")
        coaches = await self.repository.get_all()
        logger.info(f"Service: Retrieved {len(coaches)} coaches")
        return coaches

    async def get_coach_by_id(self, coach_id: UUID) -> dict:
        """Get a coach by ID."""
        logger.info(f"Service: Getting athlete {coach_id}")
        coach = await self.repository.get_by_id(coach_id)
        logger.info(f"Service: Found coach {coach_id}")
        return coach
    
    async def get_coach_by_name(self, coach_name: str) -> dict:
        """Get an coach by name."""
        logger.info(f"Service: Getting coach {athlete_name}")
        coach = await self.repository.get_by_name(coach_name)
        logger.info(f"Service: Found coach {coach_name}")
        return coach

    async def update_coach(self, coach_id: UUID, data: dict) -> dict:
        """Update a coach."""
        logger.info(f"Service: Updating coach {coach_id}")
        coach = await self.repository.update(coach_id, data)
        logger.info(f"Service: Updated coach {coach_id}")
        return coach

class AthletesService:
    """Service layer for athletes business logic."""
    def __init__(self, repository: AthletesRepo):
        self.repository = repository
    
    async def get_all_athletes(self) -> list[dict]:
        """Get all athletes."""
        logger.info("Service: Getting all athletes")
        athletes = await self.repository.get_all()
        logger.info(f"Service: Retrieved {len(athletes)} athletes")
        return athletes

    async def get_athlete_by_id(self, athlete_id: UUID) -> dict:
        """Get an athlete by ID."""
        logger.info(f"Service: Getting athlete {athlete_id}")
        athlete = await self.repository.get_by_id(athlete_id)
        logger.info(f"Service: Found athlete {athlete_id}")
        return athlete
    
    async def get_athlete_by_name(self, athlete_name: str) -> dict:
        """Get an athlete by name."""
        logger.info(f"Service: Getting athlete {athlete_name}")
        athlete = await self.repository.get_by_name(athlete_id)
        logger.info(f"Service: Found athlete {athlete_name}")
        return athlete
    
    async def get_athletes_by_coach(self, coach_id: UUID) -> dict:
        """Get all athletes of a coach"""
        logger.info(f"Service: Getting athletes for coach {coach_id}")
        athletes = await self.repository.get_by_coach(coach_id)
        logger.info(f"Service: Found athletes for coach {caoch_id}")
        return athletes

    async def create_athlete(self, data: dict) -> dict:
        """Create a new athlete."""
        logger.info(f"Service: Creating athlete for coach {data.get('coach_id')}")
        athlete = await self.repository.create(data)
        logger.info(f"Service: Created athlete {athlete['id']}")
        return athlete

    async def update_athlete(self, athlete_id: UUID, data: dict) -> dict:
        """Update an athlete."""
        logger.info(f"Service: Updating athlete {athlete_id}")
        athlete = await self.repository.update(athlete_id, data)
        logger.info(f"Service: Updated athlete {athlete_id}")
        return athlete

    async def delete_athlete(self, athlete_id: UUID) -> None:
        """Delete an athlete."""
        logger.info(f"Service: Deleting athlete {athlete_id}")
        await self.repository.delete(athlete_id)
        logger.info(f"Service: Deleted athlete {athlete_id}")

class TrainingRunsService:
    """Service layer for training runs business logic."""

    def __init__(self, repository: TrianingRunsRepo):
        self.repository = repository

    async def get_all_runs(self) -> list[dict]:
        """Get all training runs."""
        logger.info("Service: Getting all training runs")
        runs = await self.repository.get_all()
        logger.info(f"Service: Retrieved {len(runs)} training runs")
        return runs

    async def get_run_by_id(self, run_id: UUID) -> dict:
        """Get a training run by ID."""
        logger.info(f"Service: Getting training run {run_id}")
        run = await self.repository.get_by_id(run_id)
        logger.info(f"Service: Found training run {run_id}")
        return run

    async def create_run(self, data: dict) -> dict:
        """Create a new training run."""
        logger.info(f"Service: Creating training run for {data.get('athlete_name')}")
        run = await self.repository.create(data)
        logger.info(f"Service: Created training run {run['id']}")
        return run

    async def update_run(self, run_id: UUID, data: dict) -> dict:
        """Update a training run."""
        logger.info(f"Service: Updating training run {run_id}")
        run = await self.repository.update(run_id, data)
        logger.info(f"Service: Updated training run {run_id}")
        return run

    async def delete_run(self, run_id: UUID) -> None:
        """Delete a training run."""
        logger.info(f"Service: Deleting training run {run_id}")
        await self.repository.delete(run_id)
        logger.info(f"Service: Deleted training run {run_id}")
