from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.profile_schemas import Profile


class Coach(BaseModel):
    """Coach model with embedded profile."""

    coach_id: UUID
    profile: Profile
    created_at: datetime

    class Config:
        from_attributes = True
