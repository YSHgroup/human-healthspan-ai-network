from fastapi import APIRouter

from app.ai.router import organization_ai_router, scientist_router
from app.api.user.aliases import alias_routes
from app.domains.organizations.router import router as organizations_router
from app.domains.research.router import router as research_router

router = APIRouter()


def _researcher_path(path: str) -> str | None:
    if path.startswith("/research/projects"):
        return path.replace("/research/projects", "/projects", 1)
    if path.startswith("/research/"):
        return path
    if path == "/science/search":
        return "/literature/search"
    return None


_created = alias_routes(router, _researcher_path, "researcher")
assert "/projects" in _created and "/literature/search" in _created, "researcher alias mapping drifted"

router.include_router(research_router)
router.include_router(organizations_router, prefix="/organizations")
router.include_router(organization_ai_router, prefix="/organization-ai")
router.include_router(scientist_router, prefix="/ai-scientist")
