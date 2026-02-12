import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class AthleteRepository:
    """Repository for athletes table operations."""

    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase
        self.table = "athletes"

    async def get_all(self) -> list[dict]:
        """Get all athletes."""
        logger.info("Repository: Fetching all athletes")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        logger.info(f"Repository: Found {len(response.data)} athletes")
        return response.data

    async def get_by_id(self, athlete_id: UUID) -> dict:
        """Get an athlete by ID."""
        logger.info(f"Repository: Fetching athlete {athlete_id}")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .eq("athlete_id", str(athlete_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Athlete not found {athlete_id}")
            raise NotFoundException("Athlete", str(athlete_id))

        logger.info(f"Repository: Found athlete {athlete_id}")
        return response.data[0]

    async def create(self, data: dict) -> dict:
        """Create a new athlete."""
        logger.info(f"Repository: Creating athlete {data.get('name')}")
        response = await self.supabase.table(self.table).insert(data).execute()
        created = response.data[0]
        logger.info(f"Repository: Created athlete {created['athlete_id']}")
        return created

    async def update(self, athlete_id: UUID, data: dict) -> dict:
        """Update an athlete."""
        logger.info(f"Repository: Updating athlete {athlete_id}")
        response = (
            await self.supabase.table(self.table)
            .update(data)
            .eq("athlete_id", str(athlete_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Athlete not found for update {athlete_id}")
            raise NotFoundException("Athlete", str(athlete_id))

        updated = response.data[0]
        logger.info(f"Repository: Updated athlete {athlete_id}")
        return updated

    async def delete(self, athlete_id: UUID) -> None:
        """Delete an athlete."""
        logger.info(f"Repository: Deleting athlete {athlete_id}")
        response = (
            await self.supabase.table(self.table)
            .delete()
            .eq("athlete_id", str(athlete_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Athlete not found for deletion {athlete_id}")
            raise NotFoundException("Athlete", str(athlete_id))

        logger.info(f"Repository: Deleted athlete {athlete_id}")
