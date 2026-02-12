from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Profile(BaseModel):
    """Profile model returned from auth dependency."""

    profile_id: UUID
    auth_user_id: UUID
    email: EmailStr
    name: str
    role: Literal["coach", "athlete"]
    created_at: datetime

    class Config:
        from_attributes = True
