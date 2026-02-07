from io import BytesIO
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

import logging

import pandas as pd

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["Data"])

@router.post("/upload-run", response_model=DataUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_data_csv(file: UploadFile = File(...), service: *SERVICE NAME* = Depends(get_stride_service),):
  logger.info(f"Route: POST /upload-run filename={file.filename}")

  # Basic file validation
  if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Run data must be in .csv format")
  
  # Read CSV into pandas
  try:
      content = await file.read()
      raw_df = pd.read_csv(BytesIO(content))
  except Exception as e:
      logger.exception("Failed to read run data CSV")
      raise HTTPException(status_code=400, detail=f"Failed to read run data CSV: {str(e)}")

  try:
      result = await service.ingest_stride_csv(raw_df)
  except HTTPException:
      raise
  except Exception as e:
      logger.exception("Failed to ingest run data frame")
      raise HTTPException(status_code=500, detail=f"Failed to ingest run data frame: {str(e)}")

  logger.info(
      f"Stride upload complete rows_in={result.rows_in} "
      f"rows_out={result.rows_out} inserted={result.inserted}"
  )

  return result