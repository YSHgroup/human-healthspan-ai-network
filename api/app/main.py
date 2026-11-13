from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.middleware import install_middleware
from app.api.v1.router import api_router
from app.config import get_settings
from app.infrastructure.database import engine

settings = get_settings()

app = FastAPI(
    title="Human Healthspan Scientific AI Network API",
    version="0.1.0",
    description="Modular-monolith backend for the Human Healthspan Scientific AI Network.",
)

install_middleware(app)
app.include_router(api_router)


@app.get("/healthz", tags=["operations"])
async def health_check() -> dict[str, str]:
    """Report that the API process is responding."""
    return {"status": "ok"}


@app.get("/readyz", tags=["operations"])
def readiness_check() -> dict[str, str]:
    """Report readiness only when the configured database accepts queries."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Configured database is unavailable") from exc
    return {"status": "ready"}


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = {
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        503: "service_unavailable",
    }.get(exc.status_code, "request_error")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": code,
            "message": exc.detail if isinstance(exc.detail, str) else "Request failed",
            "requestId": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "code": "validation_error",
            "message": "Request validation failed",
            "requestId": getattr(request.state, "request_id", None),
        },
    )


# Wrap the complete application so CORS headers are present on unhandled error responses too.
asgi_app = CORSMiddleware(
    app=app,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "X-Request-ID"],
)
asgi_app.state = app.state
