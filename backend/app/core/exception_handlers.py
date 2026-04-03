"""Exception handlers for converting domain exceptions to HTTP responses."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DevUserNotAllowedException,
    ExpiredTokenException,
    InvalidTokenException,
    NotACoachException,
    NotFoundException,
    UnsupportedEventError,
)


async def not_found_exception_handler(
    request: Request, exc: NotFoundException
) -> JSONResponse:
    """Handle NotFoundException and return 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def value_error_exception_handler(
    request: Request, exc: ValueError
) -> JSONResponse:
    """Handle ValueError and return 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


async def invalid_token_handler(_: Request, __: InvalidTokenException) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Invalid token"})


async def expired_token_handler(_: Request, __: ExpiredTokenException) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Token expired"})


async def dev_user_not_allowed_handler(
    _: Request, __: DevUserNotAllowedException
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "Dev user not allowed"})


async def not_a_coach_handler(_: Request, __: NotACoachException) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "User is not a coach"})


async def unsupported_event_handler(
    _: Request, exc: UnsupportedEventError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )
