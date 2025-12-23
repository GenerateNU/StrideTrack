from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.exception_handlers import (
    not_found_exception_handler,
    value_error_exception_handler,
)
from app.core.exceptions import NotFoundException
from app.core.observability import setup_observability

# Setup observability before creating FastAPI app
FastAPIInstrumentor, HTTPXInstrumentor = setup_observability()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup

    yield
    # Shutdown (if needed)


app = FastAPI(
    title="StrideTrack API",
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
    },
)

# Instrument FastAPI for automatic request tracing
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

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "StrideTrack API"}
