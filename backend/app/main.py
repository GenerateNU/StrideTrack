import os
from contextlib import asynccontextmanager

from app.core.seed_data import seed_database
from app.core.supabase import get_async_supabase
from app.utils.preprocess.preprocessing_queue import init_queue
from app.utils.supabase_check import wait_for_supabase
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("LIFESPAN STARTING", flush=True)
    supabase = await get_async_supabase()

    await wait_for_supabase(supabase)

    await init_queue(supabase)

    if os.getenv("ENVIRONMENT") == "development":
        await seed_database(supabase)

    yield
    # Shutdown (if needed)


app = FastAPI(title="StrideTrack API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "StrideTrack API"}
