import logging
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase  # ✅ CORRECT IMPORT
from app.repositories.csv_repository import CSVRepository
from app.schemas.csv_schemas import CSVUploadResponse
from app.services.csv_service import CSVService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/csv", tags=["CSV"])


# Dependency injection
async def get_csv_service(
    supabase: AsyncClient = Depends(get_async_supabase),  # ✅ CORRECT PATTERN
) -> CSVService:
    repository = CSVRepository(supabase)
    return CSVService(repository)


@router.post(
    "/upload-run", response_model=CSVUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_data_csv(
    file: UploadFile = File(...),
    athlete_id: str = Form(...),
    event_type: str = Form(...),
    name: str = Form(None),
    service: CSVService = Depends(get_csv_service),
) -> CSVUploadResponse:
    logger.info(f"Route: POST /upload-run filename={file.filename}")

    # Basic file validation
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Run data must be in .csv format")

    try:
        content = await file.read()
        raw_df = pd.read_csv(BytesIO(content))
    except Exception as e:
        logger.exception("Failed to read CSV file")
        raise HTTPException(
            status_code=400, detail=f"Failed to read CSV file: {str(e)}"
        ) from e

    try:
        result = await service.ingest_stride_csv(
            raw_df, athlete_id=athlete_id, event_type=event_type, name=name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to ingest run data frame")
        raise HTTPException(
            status_code=500, detail=f"Failed to ingest run data frame: {str(e)}"
        ) from e

    return result
