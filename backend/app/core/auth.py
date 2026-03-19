import logging
import os
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from supabase._async.client import AsyncClient

from app.core.exceptions import (
    DevUserNotAllowedException,
    ExpiredTokenException,
    InvalidTokenException,
    NotACoachException,
    NotFoundException,
)
from app.core.supabase import get_async_supabase
from app.schemas.coach_schemas import Coach
from app.schemas.profile_schemas import Profile

logger = logging.getLogger(__name__)

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# JWKS client for verifying Supabase JWTs (works for both HS256 and ES256)
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
jwks_client = PyJWKClient(JWKS_URL)

# Dev user UUID - matches seed.sql
DEV_AUTH_USER_ID = UUID("00000000-0000-0000-0000-000000000099")


async def get_current_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> Profile:
    """Decode JWT and return profile. Creates profile if first login."""
    token = credentials.credentials

    # --- DEV TOKEN BYPASS ---
    if token == "dev-token":
        if ENVIRONMENT != "development":
            raise DevUserNotAllowedException()

        auth_user_id = DEV_AUTH_USER_ID
        email = "dev@stridetrack.local"
        name = "Dev User"
    else:
        # --- NORMAL JWT FLOW ---
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "HS256"],
                audience="authenticated",
            )
            auth_user_id = UUID(payload["sub"])
            email = payload.get("email", "")
            user_metadata = payload.get("user_metadata", {})
            name = user_metadata.get("full_name") or user_metadata.get("name") or email

        except jwt.ExpiredSignatureError as err:
            raise ExpiredTokenException() from err
        except jwt.InvalidTokenError as err:
            raise InvalidTokenException() from err

    # --- GET OR CREATE PROFILE ---
    profile = await _get_or_create_profile(supabase, auth_user_id, email, name)
    return profile


async def get_current_coach(
    profile: Profile = Depends(get_current_profile),
    supabase: AsyncClient = Depends(get_async_supabase),
) -> Coach:
    """Get coach for current profile. Raises if user is not a coach."""
    if profile.role != "coach":
        raise NotACoachException()

    response = (
        await supabase.table("coaches")
        .select("*")
        .eq("profile_id", str(profile.profile_id))
        .execute()
    )

    if not response.data:
        logger.error(f"Coach not found for profile {profile.profile_id}")
        raise NotFoundException("Coach", str(profile.profile_id))

    coach_data = response.data[0]
    return Coach(
        coach_id=coach_data["coach_id"],
        profile=profile,
        created_at=coach_data["created_at"],
    )


async def _get_or_create_profile(
    supabase: AsyncClient,
    auth_user_id: UUID,
    email: str,
    name: str,
) -> Profile:
    """Find existing profile or create new one."""
    # Try to find existing profile
    response = (
        await supabase.table("profiles")
        .select("*")
        .eq("auth_user_id", str(auth_user_id))
        .execute()
    )

    if response.data:
        return Profile(**response.data[0])

    # Create new profile (default role: coach for now)
    logger.info(f"Creating new profile for auth_user_id={auth_user_id}")
    create_response = (
        await supabase.table("profiles")
        .insert(
            {
                "auth_user_id": str(auth_user_id),
                "email": email,
                "name": name,
                "role": "coach",
            }
        )
        .execute()
    )

    profile = Profile(**create_response.data[0])

    # Also create coach entry for new users
    # Might change later if we make athletes users
    await (
        supabase.table("coaches")
        .insert(
            {
                "profile_id": str(profile.profile_id),
            }
        )
        .execute()
    )

    logger.info(f"Created profile and coach for {email}")
    return profile
