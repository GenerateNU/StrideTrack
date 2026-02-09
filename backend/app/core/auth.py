import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import (
    DevUserNotAllowedException,
)
from app.schemas.user_schema import User

security = HTTPBearer()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = credentials.credentials

    # --- DEV TOKEN BYPASS ---
    if token == "dev-token":
        if ENVIRONMENT == "development":
            return User(
                id="dev-user-id",
                email="dev@stridetrack.local",
            )
        else:
            raise DevUserNotAllowedException()

    # --- NORMAL JWT FLOW ---
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )

        return User(
            id=payload["sub"],
            email=payload.get("email", ""),
        )

    except jwt.ExpiredSignatureError as err:
        raise HTTPException(status_code=401, detail="Token expired") from err
    except jwt.InvalidTokenError as err:
        raise HTTPException(status_code=401, detail="Invalid token") from err
