import logging
from uuid import UUID

from app.repositories.run_repository import RunRepository
from app.schemas.hurdle_schemas import HurdleMetricRow

logger = logging.getLogger(__name__)


class HurdleService:
    """Service for hurdle-metric related business logic."""

    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository

    async def get_hurdle_metrics_by_run_id(self, run_id: UUID) -> list[HurdleMetricRow]:
        """
        Fetch raw step rows for a run and transform them into per-hurdle metrics.
        """
        logger.info(f"Service: Getting hurdle metrics for run {run_id}")

        # IMPORTANT: hurdle transform requires at least foot, ic_time, to_time, gct_ms.
        # So the repository method used here must SELECT to_time.
        steps = await self.repository.get_run_metrics_for_hurdles(run_id)

        # TODO: Replace this placeholder with your real transform call.
        # Example:
        # transformed_rows = transform_stride_cycles_to_hurdle_metrics(steps)
        transformed_rows: list[dict] = []

        # Pydantic will coerce/validate and also ensures consistent response shape.
        result = [HurdleMetricRow(**row) for row in transformed_rows]

        logger.info(f"Service: Returning {len(result)} hurdle rows for run {run_id}")
        return result