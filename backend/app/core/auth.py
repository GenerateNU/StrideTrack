import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel

security = HTTPBearer()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

class CurrentUser(BaseModel):
    id: str
    email: str

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return CurrentUser(id=payload["sub"], email=payload.get("email", ""))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")