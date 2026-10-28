from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.models.domain import ResearchMember, ResearchProject, User


class AuthorizationService:
    """Central policy boundary for user/team/project/document access."""

    def __init__(self, db: Session):
        self.db = db

    def readable_project_ids(self, principal: User) -> Select[tuple[UUID]]:
        project_ids = select(ResearchProject.id)
        member_project_ids = select(ResearchMember.project_id).where(
            ResearchMember.user_id == principal.id
        )
        return project_ids.where(
            or_(
                ResearchProject.owner_id == principal.id,
                ResearchProject.visibility == "public",
                and_(
                    ResearchProject.visibility == "team",
                    ResearchProject.id.in_(member_project_ids),
                ),
            )
        )

    def can_read_project(self, principal: User, project: ResearchProject) -> bool:
        if project.owner_id == principal.id:
            return True
        if project.visibility == "public":
            return True
        if project.visibility != "team":
            return False
        return self.db.scalar(
            select(ResearchMember.id).where(
                ResearchMember.project_id == project.id,
                ResearchMember.user_id == principal.id,
            )
        ) is not None

    def can_write_project(self, principal: User, project: ResearchProject) -> bool:
        if project.owner_id == principal.id:
            return True
        if project.visibility != "team":
            return False
        membership = self.db.scalar(
            select(ResearchMember).where(
                ResearchMember.project_id == project.id,
                ResearchMember.user_id == principal.id,
            )
        )
        return membership is not None and membership.role == "member"

    def can_read(self, principal_id: UUID, resource: dict) -> bool:
        project_id = resource.get("project_id")
        principal = self.db.get(User, principal_id)
        project = self.db.get(ResearchProject, project_id) if project_id else None
        return principal is not None and project is not None and self.can_read_project(principal, project)

    def can_write(self, principal_id: UUID, resource: dict) -> bool:
        project_id = resource.get("project_id")
        principal = self.db.get(User, principal_id)
        project = self.db.get(ResearchProject, project_id) if project_id else None
        return principal is not None and project is not None and self.can_write_project(principal, project)
