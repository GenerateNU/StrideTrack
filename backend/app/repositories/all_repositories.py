import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)

class CoachesRepo:
    def __init__(seld, supabase: AsyncClient):
        self.supabase = supabase
        self.table = "coaches"

    async def get_all(self) -> list[dict]:
        """Get all coaches"""
        logger.info("Repository: Fetching all coaches")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        logger.info(f"Repository: Found {len(response.data)} coaches")
        return response.data

    async def get_by_id(self, coach_id: UUID) -> dict:
        """Get a coach by ID."""
        logger.info(f"Repository: Fetching coach {coach_id}")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .eq("id", str(coach_id))
            .execute()
        )
        if not response.data:
            logger.warning(f"Repository: Coach not found {coach_id}")
            raise NotFoundException("Coach", str(coach_id))

        logger.info(f"Repository: Found coach {coach_id}")
        return response.data[0]
    
    async def get_by_name(self, coach_name: str) -> dict:
        """Get a coach by name."""
        logger.info(f"Repository: Fetching coach {coach_name}")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .eq("coach_name", coach_name)
            .execute()
        )
        if not response.data:
            logger.warning(f"Repository: Coach not found {coach_name}")
            raise NotFoundException("Coach", str(coach_name))

        logger.info(f"Repository: Found coach {coach_name}")
        return response.data[0]
    
    async def update(self, coach_id: UUID, data: dict) -> dict:
        """Update a coach."""
        logger.info(f"Repository: Updating coach {coach_id}")
        response = (
            await self.supabase.table(self.table)
            .update(data)
            .eq("id", str(coach_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Coach not found for update {coach_id}")
            raise NotFoundException("Coach", str(coach_id))

        updated = response.data[0]
        logger.info(f"Repository: Updated coach {coach_id}")
        return updated

class AthletesRepo:
    """Repository for athletes table operations"""

    def __init__(seld, supabase: AsyncClient):
        self.supabase = supabase
        self.table = "athletes"
    
    async def get_all(self) -> list[dict]:
        """Get all athletes"""
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
            .eq("id", str(athlete_id))
            .execute()
        )
        if not response.data:
            logger.warning(f"Repository: Athlete not found {athlete_id}")
            raise NotFoundException("Athlete", str(athlete_id))

        logger.info(f"Repository: Found athlete {run_id}")
        return response.data[0]

    async def get_by_name(self, athlete_name: str) -> dict:
        """Get an athlete by name."""
        logger.info(f"Repository: Fetching athlete {athlete_name}")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .eq("athlete_name", athlete_name)
            .execute()
        )
        if not response.data:
            logger.warning(f"Repository: Athlete not found {athlete_name}")
            raise NotFoundException("Athlete", str(athlete_name))

        logger.info(f"Repository: Found athlete {athlete_name}")
        return response.data[0]
    
    async def get_by_coach(self, coach_id: UUID) -> list[dict]:
        """Gets all athletes by coach."""
        logger.info(f"Repository: Fetching athletes for coach {coach_id}")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .eq("coach_id", str(coach_id))
            .execute()
        )
        logger.info(f"Repository: Found {len(response.data)} athletes for coach {coach_id}")
        return response.data

    async def create(self, data: dict) -> dict:
        """Create a new athlete."""
        logger.info(f"Repository: Creating athlete for coach {data.get('coach_id')}")
        response = await self.supabase.table(self.table).insert(data).execute()
        created = response.data[0]
        logger.info(f"Repository: Created athlete {created['id']}")
        return created

    async def update(self, athlete_id: UUID, data: dict) -> dict:
        """Update an athlete."""
        logger.info(f"Repository: Updating athlete {athlete_id}")
        response = (
            await self.supabase.table(self.table)
            .update(data)
            .eq("id", str(athlete_id))
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
            .eq("id", str(athlete_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Athlete not found for deletion {athlete_id}")
            raise NotFoundException("Athlete", str(athlete_id))

        logger.info(f"Repository: Deleted athlete {athlete_id}")

class TrianingRunsRepo:
    """Repository for training_runs table operations."""

    def __init__(self, supabase: AsyncClient):
        self.supabase = supabase
        self.table = "training_runs"

    async def get_all(self) -> list[dict]:
        """Get all training runs."""
        logger.info("Repository: Fetching all training runs")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        logger.info(f"Repository: Found {len(response.data)} training runs")
        return response.data

    async def get_by_id(self, run_id: UUID) -> dict:
        """Get a training run by ID."""
        logger.info(f"Repository: Fetching training run {run_id}")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .eq("id", str(run_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Training run not found {run_id}")
            raise NotFoundException("Training run", str(run_id))

        logger.info(f"Repository: Found training run {run_id}")
        return response.data[0]

    async def create(self, data: dict) -> dict:
        """Create a new training run."""
        logger.info(f"Repository: Creating training run for {data.get('athlete_name')}")
        response = await self.supabase.table(self.table).insert(data).execute()
        created = response.data[0]
        logger.info(f"Repository: Created training run {created['id']}")
        return created

    async def update(self, run_id: UUID, data: dict) -> dict:
        """Update a training run."""
        logger.info(f"Repository: Updating training run {run_id}")
        response = (
            await self.supabase.table(self.table)
            .update(data)
            .eq("id", str(run_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Training run not found for update {run_id}")
            raise NotFoundException("Training run", str(run_id))

        updated = response.data[0]
        logger.info(f"Repository: Updated training run {run_id}")
        return updated

    async def delete(self, run_id: UUID) -> None:
        """Delete a training run."""
        logger.info(f"Repository: Deleting training run {run_id}")
        response = (
            await self.supabase.table(self.table)
            .delete()
            .eq("id", str(run_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Training run not found for deletion {run_id}")
            raise NotFoundException("Training run", str(run_id))

        logger.info(f"Repository: Deleted training run {run_id}")

 