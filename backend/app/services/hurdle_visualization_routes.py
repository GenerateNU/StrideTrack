import logging
from uuid import UUID

from app.repositories.example_repository import ExampleRepository
from app.schemas.example_schemas import (
    ExampleRunCreate,
    ExampleRunResponse,
    ExampleRunUpdate,
)

logger = logging.getLogger(__name__)


class ExampleService:
    """Service layer for training runs business logic."""

    def __init__(self, repository: ExampleRepository) -> None:
        self.repository = repository

    async def get_all_runs(self) -> list[ExampleRunResponse]:
        """Get all training runs."""
        logger.info("Service: Getting all training runs")
        runs = await self.repository.get_all()
        logger.info(f"Service: Retrieved {len(runs)} training runs")
        return runs

    async def get_run_by_id(self, run_id: UUID) -> ExampleRunResponse:
        """Get a training run by ID."""
        logger.info(f"Service: Getting training run {run_id}")
        run = await self.repository.get_by_id(run_id)
        logger.info(f"Service: Found training run {run_id}")
        return run

    async def create_run(self, data: ExampleRunCreate) -> ExampleRunResponse:
        """Create a new training run."""
        logger.info(f"Service: Creating training run for {data.athlete_name}")
        run = await self.repository.create(data)
        logger.info(f"Service: Created training run {run.id}")
        return run

    async def update_run(
        self, run_id: UUID, data: ExampleRunUpdate
    ) -> ExampleRunResponse:
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
