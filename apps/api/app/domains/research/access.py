from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import User
from app.models.platform import ResearchMembership

RESEARCH_ROLES = frozenset({"admin", "scientific_reviewer"})


def has_research_access(db: Session, user: User) -> bool:
    """Approved researcher membership (Blueprint section 5); portal navigation is never authorization."""
    if user.role in RESEARCH_ROLES:
        return True
    status_value = db.scalar(select(ResearchMembership.status).where(ResearchMembership.user_id == user.id))
    return status_value == "approved"


# ---- project helpers shared by legacy and portal routers (moved from v1_routes, behavior unchanged)
from uuid import UUID  # noqa: E402

from fastapi import HTTPException, status  # noqa: E402

from app.models.domain import ResearchProject  # noqa: E402
from app.services.authorization import AuthorizationService  # noqa: E402


def project_or_404(db: Session, project_id: UUID) -> ResearchProject:
    project = db.get(ResearchProject, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research project not found.")
    return project


def require_project_read(db: Session, user: User, project: ResearchProject) -> None:
    if not AuthorizationService(db).can_read_project(user, project):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research project not found.")


def require_project_write(db: Session, user: User, project: ResearchProject) -> None:
    if not AuthorizationService(db).can_write_project(user, project):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot modify this research project.")
