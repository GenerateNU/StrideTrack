import logging

import pandas as pd
from fastapi import HTTPException

from app.repositories.csv_repository import CSVRepository
from app.schemas.csv_schemas import CSVUploadResponse
from app.utils.transform_run import transform_feet_to_stride_cycles

logger = logging.getLogger(__name__)


class CSVService:
    def __init__(self, repository: CSVRepository) -> None:
        self.repository = repository

    async def ingest_stride_csv(
        self,
        raw_df: pd.DataFrame,
        athlete_id: str,
        event_type: str,
        run_name: str | None = None,
    ) -> CSVUploadResponse:

        if not athlete_id:
            raise HTTPException(status_code=400, detail="athlete_id is required")
        if not event_type:
            raise HTTPException(status_code=400, detail="event_type is required")

        # Transform
        try:
            transformed_df = transform_feet_to_stride_cycles(raw_df)
        except Exception as e:
            logger.exception("Service: Run data transform failed")
            raise HTTPException(
                status_code=500, detail=f"Run data transform failed: {str(e)}"
            ) from e

        # Load
        try:
            run_record = await self.repository.insert_transformed_stride_rows(
                transformed_df, athlete_id, event_type, run_name
            )
        except Exception as e:
            logger.exception("Service: Transformed run data insert failed")
            raise HTTPException(
                status_code=500, detail=f"Transformed run data insert failed: {str(e)}"
            ) from e

        logger.info(
            f"Service: ingest_stride_csv rows_in={len(raw_df)} rows_out={len(transformed_df)}"
        )

        return CSVUploadResponse(
            message=f"CSV uploaded successfully. Created {len(transformed_df)} stride metrics.",
            run_id=run_record["run_id"],
            strides_count=len(transformed_df),
        )
