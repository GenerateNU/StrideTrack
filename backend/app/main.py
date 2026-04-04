from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.exception_handlers import (
    dev_user_not_allowed_handler,
    expired_token_handler,
    invalid_token_handler,
    not_a_coach_handler,
    not_found_exception_handler,
    unsupported_event_handler,
    value_error_exception_handler,
)
from app.core.exceptions import (
    DevUserNotAllowedException,
    ExpiredTokenException,
    InvalidTokenException,
    NotACoachException,
    NotFoundException,
    UnsupportedEventError,
)
from app.core.observability import setup_observability
from app.schemas.health_schemas import RootResponse

FastAPIInstrumentor, HTTPXInstrumentor = setup_observability()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title="StrideTrack API",
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
    },
)

FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(ValueError, value_error_exception_handler)
app.add_exception_handler(InvalidTokenException, invalid_token_handler)
app.add_exception_handler(ExpiredTokenException, expired_token_handler)
app.add_exception_handler(DevUserNotAllowedException, dev_user_not_allowed_handler)
app.add_exception_handler(NotACoachException, not_a_coach_handler)
app.add_exception_handler(UnsupportedEventError, unsupported_event_handler)


@app.get("/")
def read_root() -> RootResponse:
    return RootResponse(message="StrideTrack API")


app.include_router(api_router)
