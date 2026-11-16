"""Social feed rules shared by user-facing API routes."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import SocialPost, User


class BlankPostError(ValueError):
    pass


def list_public_feed(db: Session, limit: int) -> list[SocialPost]:
    return list(
        db.scalars(
            select(SocialPost)
            .options(joinedload(SocialPost.author))
            .where(
                SocialPost.community_id.is_(None),
                SocialPost.moderation_status == "published",
            )
            .order_by(SocialPost.created_at.desc(), SocialPost.id.desc())
            .limit(limit)
        ).all()
    )


def publish_post(db: Session, user: User, kind: str, body: str) -> SocialPost:
    normalized_body = body.strip()
    if not normalized_body:
        raise BlankPostError
    post = SocialPost(author_id=user.id, kind=kind, body=normalized_body)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
