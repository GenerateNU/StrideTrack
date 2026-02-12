from fastapi import APIRouter, Depends

from app.core.auth import get_current_coach, get_current_profile
from app.schemas.coach_schemas import Coach
from app.schemas.profile_schemas import Profile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=Profile)
async def get_me(profile: Profile = Depends(get_current_profile)) -> Profile:
    """Get current user's profile."""
    return profile


@router.get("/me/coach", response_model=Coach)
async def get_me_coach(coach: Coach = Depends(get_current_coach)) -> Coach:
    """Get current user's coach info. Requires coach role."""
    return coach
