import logging
from fastapi import HTTPException
import pandas as pd
from app.services.transform_run import transform_feet_to_stride_cycles
from app.repositories.data_repository import DataRepository
from app.schemas.csv_schemas import CSVUploadResponse

logger = logging.getLogger(__name__)

class DataService:
  def __init__(self, repository: DataRepository):
      self.repository = repository

  async def ingest_stride_csv(self, raw_df: pd.DataFrame) -> CSVUploadResponse:
      # Transform
      try:
          transformed_df = transform_feet_to_stride_cycles(raw_df)
      except Exception as e:
          logger.exception("Service: Run data transform failed")
          raise HTTPException(status_code=500, detail=f"Run data transform failed: {str(e)}")

      # Load
      try:
          await self.repository.insert_transformed_stride_rows(transformed_df)
      except Exception as e:
          logger.exception("Service: Transformed run data insert failed")
          raise HTTPException(status_code=500, detail=f"Transformed run data insert failed: {str(e)}")

      logger.info(f"Service: ingest_stride_csv rows_in={len(raw_df)} rows_out={len(transformed_df)}")

      return CSVUploadResponse(
          message="CSV uploaded, transformed, and saved successfully"
      )