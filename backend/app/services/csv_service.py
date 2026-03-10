import logging

import pandas as pd
from fastapi import HTTPException

from app.core.observability import get_tracer
from app.repositories.csv_repository import CSVRepository
from app.schemas.csv_schemas import CSVUploadResponse
from app.utils.transform_run import transform_feet_to_stride_cycles

logger = logging.getLogger(__name__)


class CSVService:
    def __init__(self, repository: CSVRepository) -> None:
        self.repository = repository

    async def ingest_stride_csv(
        self, raw_df: pd.DataFrame, athlete_id: str, event_type: str, name: str = None
    ) -> CSVUploadResponse:
        tracer = get_tracer()
        with tracer.start_as_current_span("csv.ingest") as span:
            span.set_attribute("csv.rows_in", len(raw_df))
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
                message=f"CSV uploaded successfully. Run ID: {result['run_id']}, Rows inserted: {result['rows_inserted']}"
            )
