from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(...)
    database: str = Field(...)
    error: str | None = Field(None)


class RootResponse(BaseModel):
    message: str = Field(...)
