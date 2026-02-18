from pydantic import BaseModel, Field
from typing import Optional, Literal


class RunResponse(BaseModel):
    stride_num: int = Field(..., gt=0)
    foot: str = Field(..., min_length=1, max_length=255)
    ic_time: int = Field(..., ge=0)
    gct_ms: int = Field(..., gt=0)
    flight_ms: int = Field(..., gt=0)
    step_time_ms: int = Field(..., gt=0)

class LROverlayData(BaseModel):
    stride_num: int
    left: Optional[float] = None
    right: Optional[float] = None

class StackedBarData(BaseModel):
    stride_num: int
    foot: Literal["left", "right"]
    label: str
    gct_ms: float
    flight_ms: float
