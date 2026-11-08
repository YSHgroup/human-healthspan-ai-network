"""Social feed rules shared by user-facing API routes."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import SocialPost, SocialPostReport, User


class BlankPostError(ValueError):
    pass


class BlankReportReasonError(ValueError):
    pass


class PostUnavailableForReportError(ValueError):
    pass


class DuplicatePostReportError(ValueError):
    pass


def list_public_feed(db: Session, limit: int) -> list[SocialPost]:
    return list(
        db.scalars(
            select(SocialPost)
            .options(joinedload(SocialPost.author))
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


def report_post(db: Session, user: User, post_id: str, reason: str) -> SocialPostReport:
    post = db.get(SocialPost, post_id)
    if post is None or post.author_id == user.id:
        raise PostUnavailableForReportError
    normalized_reason = reason.strip()
    if not normalized_reason:
        raise BlankReportReasonError
    report = SocialPostReport(post_id=post.id, reporter_id=user.id, reason=normalized_reason)
    db.add(report)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicatePostReportError from exc
    db.refresh(report)
    return report
