from pydantic import BaseModel, Field


class CSVInsertResult(BaseModel):
    run_id: str
    rows_inserted: int


class CSVUploadResponse(BaseModel):
    """Response returned after a successful CSV upload and ingestion."""

    message: str = Field(..., min_length=1, max_length=255)
    run_id: str = Field(..., description="ID of the created run")
    rows_inserted: int = Field(..., ge=0, description="Number of metric rows inserted")
