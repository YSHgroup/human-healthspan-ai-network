from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.domain import Evidence, Literature, User
from app.services.authorization import AuthorizationService


class RetrievalService:
    """Fetch only literature/evidence within the requester's project access scope."""

    def __init__(self, db: Session):
        self.db = db

    def retrieve(
        self,
        query: str,
        authorization_scope: dict[str, str | int],
    ) -> list[dict[str, str | None]]:
        if not query.strip():
            return []
        principal_id = UUID(str(authorization_scope["principal_id"]))
        principal = self.db.get(User, principal_id)
        if principal is None or not principal.is_active:
            return []

        accessible_project_ids = AuthorizationService(self.db).readable_project_ids(principal)

        pattern = f"%{query.strip()}%"
        limit = min(max(int(authorization_scope.get("limit", 10)), 1), 50)
        literature = self.db.scalars(
            select(Literature)
            .where(
                Literature.project_id.in_(accessible_project_ids),
                or_(Literature.title.ilike(pattern), Literature.authors.ilike(pattern)),
            )
            .limit(limit)
        )
        evidence = self.db.scalars(
            select(Evidence)
            .where(
                Evidence.project_id.in_(accessible_project_ids),
                Evidence.summary.ilike(pattern),
            )
            .limit(limit)
        )
        results: list[dict[str, str | None]] = [
            {
                "id": str(item.id),
                "project_id": str(item.project_id),
                "kind": "literature",
                "title": item.title,
                "content": item.authors,
                "source_url": item.source_url,
                "evidence_type": item.source_type,
            }
            for item in literature
        ]
        results.extend(
            {
                "id": str(item.id),
                "project_id": str(item.project_id),
                "kind": "evidence",
                "title": item.label,
                "content": item.summary,
                "source_url": item.source_url,
                "evidence_type": item.label,
            }
            for item in evidence
        )
        return results[:limit]
