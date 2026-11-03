"""Re-expose proven MVP endpoints under the portal API boundaries without duplicating logic.

The original routes keep working (backwards compatible); the aliases give each portal a stable
``/api/v1/user/{social,personal,researcher}`` surface as required by Architecture v1.2 section 7.1.
"""
from collections.abc import Callable

from fastapi import APIRouter
from fastapi.routing import APIRoute

from app.api.v1_routes import router as legacy_router


def alias_routes(target: APIRouter, rename: Callable[[str], str | None], tag: str) -> list[str]:
    """Copy every legacy route whose path ``rename`` maps to a new path. Returns the new paths."""
    created: list[str] = []
    for route in legacy_router.routes:
        if not isinstance(route, APIRoute):
            continue
        new_path = rename(route.path)
        if new_path is None:
            continue
        target.add_api_route(
            new_path,
            route.endpoint,
            methods=sorted(route.methods or []),
            response_model=route.response_model,
            status_code=route.status_code,
            dependencies=route.dependencies,
            tags=[tag],
            name=f"{tag}:{route.name}",
        )
        created.append(new_path)
    return created
