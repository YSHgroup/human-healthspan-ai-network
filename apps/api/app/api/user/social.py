from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_optional_current_user
from app.api.user.aliases import alias_routes
from app.api.v1_routes import _feed_posts
from app.db.session import get_db
from app.domains.events.router import router as events_router
from app.domains.messaging.router import router as messaging_router
from app.domains.notifications.router import router as notifications_router
from app.domains.organizations.router import invitations_router
from app.models.domain import Follow, Profile, User
from app.schemas.content import FeedPostOut

router = APIRouter()

_SOCIAL_PATHS = {
    "/feed": "/feed",
    "/posts": "/posts",
    "/posts/{post_id}": "/posts/{post_id}",
    "/posts/{post_id}/comments": "/posts/{post_id}/comments",
    "/posts/{post_id}/reactions": "/posts/{post_id}/reactions",
    "/posts/{post_id}/bookmark": "/posts/{post_id}/bookmark",
    "/communities": "/communities",
    "/communities/{community_id}": "/communities/{community_id}",
    "/communities/{community_id}/feed": "/communities/{community_id}/feed",
    "/communities/{community_id}/join": "/communities/{community_id}/join",
    "/users/{user_id}": "/members/{user_id}",
    "/users/{user_id}/follow": "/members/{user_id}/follow",
    "/search": "/search",
    "/reports": "/reports",
    "/dashboard/summary": "/dashboard/summary",
}
_created = alias_routes(router, lambda path: _SOCIAL_PATHS.get(path), "social")
assert set(_created) == set(_SOCIAL_PATHS.values()), "social alias mapping drifted from the MVP routes"


@router.get("/discussions", response_model=list[FeedPostOut], tags=["social"])
def discussions(
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
    community_id: UUID | None = None,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> list[FeedPostOut]:
    """Question-style threads; ordinary posts stay in /feed."""
    return _feed_posts(db, limit, offset, community_id, user, content_type="question")


@router.get("/connections", tags=["social"])
def connections(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """Following / followers with a 'mutual' flag; mutual follows are treated as connections."""
    def load(user_column, other_column):
        rows = db.execute(
            select(other_column, Profile.display_name, Profile.is_public)
            .outerjoin(Profile, Profile.user_id == other_column)
            .join(User, User.id == other_column)
            .where(user_column == user.id, User.is_active.is_(True))
        ).all()
        return {row[0]: (row[1] if row[2] and row[1] else "Member") for row in rows}

    following = load(Follow.follower_id, Follow.followed_id)
    followers = load(Follow.followed_id, Follow.follower_id)
    mutual = set(following) & set(followers)
    as_list = lambda data: [{"user_id": str(uid), "display_name": name, "mutual": uid in mutual} for uid, name in data.items()]  # noqa: E731
    return {"following": as_list(following), "followers": as_list(followers), "connection_count": len(mutual)}


router.include_router(events_router, prefix="/events")
router.include_router(notifications_router, prefix="/notifications")
router.include_router(messaging_router, prefix="/messages")
router.include_router(invitations_router, prefix="/invitations")
