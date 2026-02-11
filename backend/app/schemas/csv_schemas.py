from pydantic import BaseModel, Field


class ResponseData(BaseModel):
    stride_num: int = Field(..., gt=0)
    foot: str = Field(..., min_length=1, max_length=255)
    ic_time: int = Field(..., gt=0)
    to_time: int = Field(..., gt=0)
    next_ic_time: int = Field(..., gt=0)
    gct_ms: int = Field(..., gt=0)
    flight_ms: int = Field(..., gt=0)
    step_time_ms: int = Field(..., gt=0)

class CSVUploadResponse(BaseModel):
    message: str = Field(..., min_length=1, max_length=255)
