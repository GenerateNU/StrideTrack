import logging
from uuid import UUID

from supabase._async.client import AsyncClient

from app.core.exceptions import NotFoundException
from app.schemas.example_schemas import ExampleRunResponse, ExampleRunCreate, ExampleRunUpdate

logger = logging.getLogger(__name__)


class ExampleRepository:
    """Repository for training_runs table operations."""

    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase
        self.table = "training_runs"

    async def get_all(self) -> list[ExampleRunResponse]:
        """Get all training runs."""
        logger.info("Repository: Fetching all training runs")
        response = (
            await self.supabase.table(self.table)
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        logger.info(f"Repository: Found {len(response.data)} training runs")
        return [ExampleRunResponse(**run) for run in response.data]

    async def get_by_id(self, run_id: UUID) -> ExampleRunResponse:
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
        return ExampleRunResponse(**response.data[0])

    async def create(self, data: ExampleRunCreate) -> ExampleRunResponse:
        """Create a new training run."""
        create_data = data.model_dump(exclude_unset=True)
        logger.info(f"Repository: Creating training run for {create_data.get('athlete_name')}")
        response = await self.supabase.table(self.table).insert(create_data).execute()
        created = response.data[0]
        logger.info(f"Repository: Created training run {created['id']}")
        return ExampleRunResponse(**created)

    async def update(self, run_id: UUID, data: ExampleRunUpdate) -> ExampleRunResponse:
        """Update a training run."""
        update_data = data.model_dump(exclude_unset=True)

        logger.info(f"Repository: Updating training run {run_id}")
        response = (
            await self.supabase.table(self.table)
            .update(update_data)
            .eq("id", str(run_id))
            .execute()
        )

        if not response.data:
            logger.warning(f"Repository: Training run not found for update {run_id}")
            raise NotFoundException("Training run", str(run_id))

        updated = response.data[0]
        logger.info(f"Repository: Updated training run {run_id}")
        return ExampleRunResponse(**updated)

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
