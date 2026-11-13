"""HTTP middleware: request identifiers and baseline security headers."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.config import get_settings

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store",
}
MAX_RESEARCH_UPLOAD_BODY_SIZE = 10 * 1024 * 1024 + 64 * 1024


def install_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        if request.url.path.endswith("/documents/upload"):
            content_length = request.headers.get("content-length")
            try:
                body_size = int(content_length) if content_length is not None else None
            except ValueError:
                body_size = -1
            if body_size == -1:
                response = JSONResponse(
                    status_code=400,
                    content={
                        "code": "invalid_content_length",
                        "message": "Invalid request Content-Length",
                        "requestId": request_id,
                    },
                )
            elif body_size is not None and body_size > MAX_RESEARCH_UPLOAD_BODY_SIZE:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "code": "request_too_large",
                        "message": "Uploaded request exceeds the 10 MiB file limit",
                        "requestId": request_id,
                    },
                )
            else:
                received = 0
                exceeded = False
                original_receive = request._receive

                async def limited_receive():  # type: ignore[no-untyped-def]
                    nonlocal received, exceeded
                    message = await original_receive()
                    if message["type"] == "http.request":
                        received += len(message.get("body", b""))
                        if received > MAX_RESEARCH_UPLOAD_BODY_SIZE:
                            exceeded = True
                            return {"type": "http.disconnect"}
                    return message

                request._receive = limited_receive
                try:
                    response = await call_next(request)
                except Exception:
                    if not exceeded:
                        raise
                    response = JSONResponse(
                        status_code=413,
                        content={
                            "code": "request_too_large",
                            "message": "Uploaded request exceeds the 10 MiB file limit",
                            "requestId": request_id,
                        },
                    )
                if exceeded:
                    response = JSONResponse(
                        status_code=413,
                        content={
                            "code": "request_too_large",
                            "message": "Uploaded request exceeds the 10 MiB file limit",
                            "requestId": request_id,
                        },
                    )
        else:
            response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        if get_settings().app_env == "production":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        return response
