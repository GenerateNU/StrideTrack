import logging
from uuid import UUID

import pandas as pd

from app.core.observability import get_tracer
from app.repositories.csv_repository import CSVRepository
from app.schemas.csv_schemas import CSVUploadResponse
from app.utils.transform_run import transform_feet_to_stride_cycles

logger = logging.getLogger(__name__)


class CSVService:
    """Service for CSV-based run ingestion."""

    def __init__(self, repository: CSVRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def ingest_stride_csv(
        self,
        raw_df: pd.DataFrame,
        athlete_id: str,
        event_type: str,
        name: str | None = None,
        elapsed_ms: int | None = None,
    ) -> CSVUploadResponse:
        """Transform raw CSV data into stride cycles and persist a complete run."""
        await self.repository.verify_athlete_belongs_to_coach(athlete_id, self.coach_id)

        tracer = get_tracer()
        with tracer.start_as_current_span("csv.ingest") as span:
            span.set_attribute("csv.rows_in", len(raw_df))

            if elapsed_ms is None and "Time" in raw_df.columns and len(raw_df) > 0:
                elapsed_ms = int(raw_df["Time"].max() - raw_df["Time"].min())

            transformed_df = transform_feet_to_stride_cycles(raw_df)
            span.set_attribute("csv.rows_transformed", len(transformed_df))

            result = await self.repository.insert_complete_run(
                df=transformed_df,
                athlete_id=athlete_id,
                event_type=event_type,
                name=name,
                elapsed_ms=elapsed_ms,
            )
            span.set_attribute("csv.run_id", result.run_id)
            span.set_attribute("csv.rows_inserted", result.rows_inserted)

            logger.info(
                f"Service: ingest_stride_csv rows_in={len(raw_df)} rows_out={len(transformed_df)} run_id={result.run_id}"
            )

            return CSVUploadResponse(
                message=f"CSV uploaded successfully. Run ID: {result.run_id}, Rows inserted: {result.rows_inserted}",
                run_id=str(result.run_id),
                rows_inserted=result.rows_inserted,
            )
