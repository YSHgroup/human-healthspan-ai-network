from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.health import router as health_router
from app.api.v1 import router as v1_router
from app.db.session import initialize_database, seed_communities


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.app_env.lower() in {"development", "dev", "test"}:
        initialize_database()
    else:
        seed_communities()
    yield


app = FastAPI(
    title="Human Healthspan Network API",
    version="0.3.0",
    description="Phase 1 modular monolith API foundation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router)
app.include_router(v1_router, prefix="/api/v1")
