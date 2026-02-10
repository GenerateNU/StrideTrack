from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.user_schema import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "email": user.email}

