import logging
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from supabase._async.client import AsyncClient

from app.core.supabase import get_async_supabase
from app.repositories.csv_repository import CSVRepository
from app.schemas.csv_schemas import CSVUploadResponse
from app.services.csv_service import CSVService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/csv", tags=["CSV"])


async def get_csv_service(
    supabase: AsyncClient = Depends(get_async_supabase),
) -> CSVService:
    repository = CSVRepository(supabase)
    return CSVService(repository)


@router.post(
    "/upload-run", response_model=CSVUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_run_csv(
    file: UploadFile = File(...),
    athlete_id: str = Form(...),
    event_type: str = Form(...),
    run_name: str = Form(None),
    service: CSVService = Depends(get_csv_service),
) -> CSVUploadResponse:
    logger.info(
        f"Route: POST /upload-run filename={file.filename}, "
        f"athlete_id={athlete_id}, event_type={event_type}"
    )

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Run data must be in .csv format")

    valid_events = [
        "sprint_60m",
        "sprint_100m",
        "sprint_200m",
        "sprint_400m",
        "hurdles_60m",
        "hurdles_110m",
        "hurdles_100m",
        "hurdles_400m",
        "long_jump",
        "triple_jump",
        "high_jump",
        "bosco_test",
        "reaction_time_test",
    ]
    if event_type not in valid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type. Must be one of: {', '.join(valid_events)}",
        )

    try:
        content = await file.read()
        raw_df = pd.read_csv(BytesIO(content))
    except Exception as e:
        logger.exception("Failed to read run data CSV")
        raise HTTPException(
            status_code=400, detail=f"Failed to read run data CSV: {str(e)}"
        ) from e

    try:
        result = await service.ingest_stride_csv(
            raw_df, athlete_id, event_type, run_name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to ingest run data frame")
        raise HTTPException(
            status_code=500, detail=f"Failed to ingest run data frame: {str(e)}"
        ) from e

    return result
