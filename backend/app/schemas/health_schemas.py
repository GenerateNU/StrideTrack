from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., gt=0)
    database: str = Field(..., gt=0)
    error: str | None = Field(None, gt=0)


class RootResponse(BaseModel):
    message: str = Field(..., gt=