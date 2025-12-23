"""Exception handlers for converting domain exceptions to HTTP responses."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import NotFoundException


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
