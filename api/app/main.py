from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import install_middleware
from app.api.v1.router import api_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Human Healthspan Scientific AI Network API",
    version="0.1.0",
    description=(
        "Modular-monolith backend. Versioned route areas exist (/api/v1/user, /api/v1/admin) "
        "but product workflows are not implemented yet."
    ),
)

# Only trusted application origins may call the API with credentials (shared session cookies).
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "X-Request-ID"],
)
install_middleware(app)
app.include_router(api_router)


@app.get("/healthz", tags=["operations"])
async def health_check() -> dict[str, str]:
    """Report that the API process is responding."""
    return {"status": "ok"}
