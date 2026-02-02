from fastapi import APIRouter, Depends
from app.core.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me")
async def get_me(user: CurrentUser = Depends(get_current_user)):
    return {"user_id": user.id, "email": user.email}