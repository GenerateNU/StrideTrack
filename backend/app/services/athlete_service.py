import logging
from uuid import UUID

from app.repositories.athlete_repository import AthleteRepository
from app.schemas.athlete_schemas import AthleteCreate, AthleteResponse, AthleteUpdate

logger = logging.getLogger(__name__)


class AthleteService:
    """Service layer for athletes business logic."""

    def __init__(self, repository: AthleteRepository) -> None:
        self.repository = repository

    async def get_all_athletes(self) -> list[AthleteResponse]:
        """Get all athletes."""
        logger.info("Service: Getting all athletes")
        athletes = await self.repository.get_all()
        logger.info(f"Service: Retrieved {len(athletes)} athletes")
        return [AthleteResponse(**athlete) for athlete in athletes]

    async def get_athlete_by_id(self, athlete_id: UUID) -> AthleteResponse:
        """Get an athlete by ID."""
        logger.info(f"Service: Getting athlete {athlete_id}")
        athlete = await self.repository.get_by_id(athlete_id)
        logger.info(f"Service: Found athlete {athlete_id}")
        return AthleteResponse(**athlete)

    async def create_athlete(self, athlete_create: AthleteCreate) -> AthleteResponse:
        """Create a new athlete."""
        logger.info(f"Service: Creating athlete {athlete_create.name}")
        data = athlete_create.model_dump()
        data["coach_id"] = str(data["coach_id"])
        athlete = await self.repository.create(data)
        logger.info(f"Service: Created athlete {athlete['athlete_id']}")
        return AthleteResponse(**athlete)

    async def update_athlete(
        self, athlete_id: UUID, athlete_update: AthleteUpdate
    ) -> AthleteResponse:
        """Update an athlete."""
        logger.info(f"Service: Updating athlete {athlete_id}")
        athlete = await self.repository.update(
            athlete_id, athlete_update.model_dump(exclude_unset=True)
        )
        logger.info(f"Service: Updated athlete {athlete_id}")
        return AthleteResponse(**athlete)

    async def delete_athlete(self, athlete_id: UUID) -> None:
        """Delete an athlete."""
        logger.info(f"Service: Deleting athlete {athlete_id}")
        await self.repository.delete(athlete_id)
        logger.info(f"Service: Deleted athlete {athlete_id}")
