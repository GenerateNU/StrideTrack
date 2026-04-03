import logging
from uuid import UUID

import pandas as pd
from fastapi import HTTPException

from app.core.observability import get_tracer
from app.repositories.csv_repository import CSVRepository
from app.schemas.csv_schemas import CSVUploadResponse
from app.utils.transform_run import transform_feet_to_stride_cycles

logger = logging.getLogger(__name__)


class CSVService:
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

        # Athlete Check
        athlete_check = (
            await self.repository.supabase.table("athletes")
            .select("athlete_id")
            .eq("athlete_id", athlete_id)
            .eq("coach_id", str(self.coach_id))
            .execute()
        )
        if not athlete_check.data:
            raise HTTPException(status_code=404, detail="Athlete not found")

        # Transform
        try:
            transformed_df = transform_feet_to_stride_cycles(raw_df)
        except Exception as e:
            logger.exception("Service: Run data transform failed")
            raise HTTPException(
                status_code=500, detail=f"Run data transform failed: {str(e)}"
            ) from e

        tracer = get_tracer()
        with tracer.start_as_current_span("csv.ingest") as span:
            span.set_attribute("csv.rows_in", len(raw_df))

            # Use client-provided elapsed_ms (wall-clock); fall back to CSV Time delta
            if elapsed_ms is None and "Time" in raw_df.columns and len(raw_df) > 0:
                elapsed_ms = int(raw_df["Time"].max() - raw_df["Time"].min())

            # Transform
            try:
                transformed_df = transform_feet_to_stride_cycles(raw_df)
                span.set_attribute("csv.rows_transformed", len(transformed_df))
            except Exception as e:
                logger.exception("Service: Run data transform failed")
                span.set_attribute("error", True)
                raise HTTPException(
                    status_code=500, detail=f"Run data transform failed: {str(e)}"
                ) from e

            # Load
            try:
                result = await self.repository.insert_complete_run(
                    df=transformed_df,
                    athlete_id=athlete_id,
                    event_type=event_type,
                    name=name,
                    elapsed_ms=elapsed_ms,
                )
                span.set_attribute("csv.run_id", result["run_id"])
                span.set_attribute("csv.rows_inserted", result["rows_inserted"])
            except Exception as e:
                logger.exception("Service: Transformed run data insert failed")
                span.set_attribute("error", True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Transformed run data insert failed: {str(e)}",
                ) from e

            logger.info(
                f"Service: ingest_stride_csv rows_in={len(raw_df)} rows_out={len(transformed_df)} run_id={result['run_id']}"
            )

            return CSVUploadResponse(
                message=f"CSV uploaded successfully. Run ID: {result['run_id']}, Rows inserted: {result['rows_inserted']}",
                run_id=str(result["run_id"]),
                rows_inserted=result["rows_inserted"],
            )
