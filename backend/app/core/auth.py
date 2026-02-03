import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user_schema import User

security = HTTPBearer()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return User(id=payload["sub"], email=payload.get("email", ""))
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(status_code=401, detail="Token expired") from err
    except jwt.InvalidTokenError as err:
        raise HTTPException(status_code=401, detail="Invalid token") from err
