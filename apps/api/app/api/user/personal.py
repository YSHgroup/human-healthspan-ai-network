from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.user.aliases import alias_routes
from app.db.session import get_db
from app.domains.health.router import consent_router, records_router, sharing_router
from app.domains.messaging.router import router as messaging_router
from app.domains.notifications.router import router as notifications_router
from app.domains.professional.router import professional_router, profile_router
from app.domains.subscriptions.router import router as entitlements_router
from app.models.domain import Comment, Post, ResearchProject, User
from app.models.platform import EventRegistration, WorkHistoryEntry

router = APIRouter()

_PERSONAL_PATHS = {"/me": "/profile", "/dashboard/summary": "/dashboard/summary"}
_created = alias_routes(router, lambda path: _PERSONAL_PATHS.get(path), "personal")
assert set(_created) == set(_PERSONAL_PATHS.values()), "personal alias mapping drifted from the MVP routes"


@router.get("/activity", tags=["personal"])
def my_activity(
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    """A merged, newest-first timeline of the member's own contributions (own data only)."""
    items: list[dict] = []
    for post in db.scalars(select(Post).where(Post.author_id == user.id, Post.deleted_at.is_(None)).order_by(Post.created_at.desc()).limit(limit)):
        items.append({"type": "post", "id": str(post.id), "summary": post.body[:140], "created_at": post.created_at})
    for comment in db.scalars(select(Comment).where(Comment.author_id == user.id, Comment.deleted_at.is_(None)).order_by(Comment.created_at.desc()).limit(limit)):
        items.append({"type": "comment", "id": str(comment.id), "summary": comment.body[:140], "created_at": comment.created_at})
    for project in db.scalars(select(ResearchProject).where(ResearchProject.owner_id == user.id).order_by(ResearchProject.created_at.desc()).limit(limit)):
        items.append({"type": "research_project", "id": str(project.id), "summary": project.title, "created_at": project.created_at})
    for entry in db.scalars(select(WorkHistoryEntry).where(WorkHistoryEntry.user_id == user.id).order_by(WorkHistoryEntry.created_at.desc()).limit(limit)):
        items.append({"type": "work_history", "id": str(entry.id), "summary": entry.summary[:140], "created_at": entry.created_at})
    for registration in db.scalars(select(EventRegistration).where(EventRegistration.user_id == user.id, EventRegistration.status == "registered").order_by(EventRegistration.created_at.desc()).limit(limit)):
        items.append({"type": "event_registration", "id": str(registration.event_id), "summary": "Registered for an event", "created_at": registration.created_at})
    from app.domains.common import as_utc

    items.sort(key=lambda item: as_utc(item["created_at"]), reverse=True)
    return items[:limit]


router.include_router(professional_router, prefix="/professional")
router.include_router(profile_router)
router.include_router(records_router, prefix="/health")
router.include_router(sharing_router, prefix="/sharing")
router.include_router(consent_router, prefix="/consents")
router.include_router(entitlements_router)
router.include_router(messaging_router, prefix="/messages")
router.include_router(notifications_router, prefix="/notifications")
