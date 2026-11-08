"""Community access, discussions, reactions, and moderation rules."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Community,
    CommunityCreationRequest,
    CommunityMembership,
    CommunityPostingSuspension,
    ModerationAction,
    ModerationAppeal,
    SocialPost,
    SocialPostComment,
    SocialPostReaction,
    SocialPostReport,
    User,
)


class SocialDomainError(ValueError):
    pass


class CommunityNotFound(SocialDomainError):
    pass


class CommunitySlugUnavailable(SocialDomainError):
    pass


class MembershipConflict(SocialDomainError):
    pass


class MembershipNotFound(SocialDomainError):
    pass


class CommunityAccessDenied(SocialDomainError):
    pass


class ModeratorAccessDenied(SocialDomainError):
    pass


class ContentNotFound(SocialDomainError):
    pass


class ContentUnavailable(SocialDomainError):
    pass


class PostingSuspended(SocialDomainError):
    pass


class InvalidModerationAction(SocialDomainError):
    pass


class AppealNotAllowed(SocialDomainError):
    pass


class DuplicateContentReport(SocialDomainError):
    pass


def get_community(db: Session, community_id: str) -> Community:
    community = db.get(Community, community_id)
    if community is None:
        raise CommunityNotFound
    return community


def membership_for(db: Session, community_id: str, user_id: str) -> CommunityMembership | None:
    return db.scalar(
        select(CommunityMembership).where(
            CommunityMembership.community_id == community_id,
            CommunityMembership.user_id == user_id,
        )
    )


def is_community_moderator(db: Session, community_id: str, user_id: str) -> bool:
    membership = membership_for(db, community_id, user_id)
    return bool(
        membership
        and membership.status == "active"
        and membership.role in {"owner", "moderator"}
    )


def require_community_member(db: Session, community: Community, user_id: str) -> CommunityMembership:
    membership = membership_for(db, community.id, user_id)
    if not membership or membership.status != "active":
        raise CommunityAccessDenied
    return membership


def require_community_access(db: Session, community: Community, user_id: str | None) -> None:
    if community.access_type == "open":
        return
    if user_id is None:
        raise CommunityAccessDenied
    require_community_member(db, community, user_id)


def list_communities(db: Session, user: User) -> list[tuple[Community, CommunityMembership | None]]:
    communities = db.scalars(select(Community).order_by(Community.name, Community.id)).all()
    return [(community, membership_for(db, community.id, user.id)) for community in communities]


def submit_community_creation_request(
    db: Session,
    user: User,
    slug: str,
    name: str,
    description: str,
    access_type: str,
) -> CommunityCreationRequest:
    normalized_slug = slug.strip().lower()
    if db.scalar(select(Community.id).where(Community.slug == normalized_slug)) or db.scalar(
        select(CommunityCreationRequest.id).where(CommunityCreationRequest.slug == normalized_slug)
    ):
        raise CommunitySlugUnavailable
    request = CommunityCreationRequest(
        requester_id=user.id,
        slug=normalized_slug,
        name=name.strip(),
        description=description.strip(),
        access_type=access_type,
        status="pending",
    )
    db.add(request)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CommunitySlugUnavailable from exc
    db.refresh(request)
    return request


def join_community(
    db: Session,
    user: User,
    community_id: str,
    application_message: str | None,
) -> CommunityMembership:
    community = get_community(db, community_id)
    existing = membership_for(db, community.id, user.id)
    if existing and existing.status in {"active", "pending"}:
        raise MembershipConflict
    status = "active" if community.access_type == "open" else "pending"
    membership = existing or CommunityMembership(community_id=community.id, user_id=user.id)
    membership.role = "member"
    membership.status = status
    membership.application_message = application_message.strip() if application_message else None
    membership.joined_at = datetime.now(timezone.utc)
    membership.reviewed_at = None
    membership.reviewed_by_id = None
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def list_pending_memberships(db: Session, community_id: str, moderator: User) -> list[CommunityMembership]:
    if not is_community_moderator(db, community_id, moderator.id):
        raise ModeratorAccessDenied
    return list(
        db.scalars(
            select(CommunityMembership)
            .options(joinedload(CommunityMembership.user))
            .where(
                CommunityMembership.community_id == community_id,
                CommunityMembership.status == "pending",
            )
            .order_by(CommunityMembership.joined_at, CommunityMembership.id)
        ).all()
    )


def decide_membership(
    db: Session,
    community_id: str,
    membership_id: str,
    moderator: User,
    decision: str,
) -> CommunityMembership:
    if not is_community_moderator(db, community_id, moderator.id):
        raise ModeratorAccessDenied
    membership = db.scalar(
        select(CommunityMembership).where(
            CommunityMembership.id == membership_id,
            CommunityMembership.community_id == community_id,
        )
    )
    if membership is None or membership.status != "pending":
        raise MembershipNotFound
    membership.status = "active" if decision == "approve" else "rejected"
    membership.reviewed_at = datetime.now(timezone.utc)
    membership.reviewed_by_id = moderator.id
    db.commit()
    db.refresh(membership)
    return membership


def list_community_posts(db: Session, community_id: str, user: User, limit: int) -> list[SocialPost]:
    community = get_community(db, community_id)
    require_community_access(db, community, user.id)
    return list(
        db.scalars(
            select(SocialPost)
            .options(joinedload(SocialPost.author))
            .where(
                SocialPost.community_id == community.id,
                SocialPost.moderation_status == "published",
            )
            .order_by(SocialPost.created_at.desc(), SocialPost.id.desc())
            .limit(limit)
        ).all()
    )


def publish_community_post(
    db: Session,
    community_id: str,
    user: User,
    kind: str,
    body: str,
) -> SocialPost:
    community = get_community(db, community_id)
    require_community_member(db, community, user.id)
    normalized = body.strip()
    if not normalized:
        raise ContentUnavailable
    ensure_can_post(db, community.id, user.id)
    post = SocialPost(
        author_id=user.id,
        community_id=community.id,
        kind=kind,
        body=normalized,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def ensure_can_post(db: Session, community_id: str | None, user_id: str) -> None:
    if community_id is None:
        return
    now = datetime.now(timezone.utc)
    suspension = db.scalar(
        select(CommunityPostingSuspension.id).where(
            CommunityPostingSuspension.community_id == community_id,
            CommunityPostingSuspension.user_id == user_id,
            CommunityPostingSuspension.revoked_at.is_(None),
            CommunityPostingSuspension.expires_at > now,
        )
    )
    if suspension:
        raise PostingSuspended


def get_post_with_access(db: Session, post_id: str, user_id: str | None) -> SocialPost:
    post = db.scalar(
        select(SocialPost)
        .options(joinedload(SocialPost.community))
        .where(
            SocialPost.id == post_id,
            SocialPost.moderation_status == "published",
        )
    )
    if post is None:
        raise ContentNotFound
    if post.community is not None:
        require_community_access(db, post.community, user_id)
    return post


def list_comments(db: Session, post_id: str, user_id: str | None) -> list[SocialPostComment]:
    post = get_post_with_access(db, post_id, user_id)
    return list(
        db.scalars(
            select(SocialPostComment)
            .options(joinedload(SocialPostComment.author))
            .where(
                SocialPostComment.post_id == post.id,
                SocialPostComment.moderation_status == "published",
            )
            .order_by(SocialPostComment.created_at, SocialPostComment.id)
        ).all()
    )


def add_comment(db: Session, post_id: str, user: User, body: str) -> SocialPostComment:
    post = get_post_with_access(db, post_id, user.id)
    if post.community_id is not None:
        require_community_member(db, post.community, user.id)
    normalized = body.strip()
    if not normalized:
        raise ContentUnavailable
    ensure_can_post(db, post.community_id, user.id)
    comment = SocialPostComment(post_id=post.id, author_id=user.id, body=normalized)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def set_reaction(
    db: Session,
    post_id: str,
    user: User,
    kind: str | None,
) -> tuple[int, str | None]:
    post = get_post_with_access(db, post_id, user.id)
    if post.community_id is not None:
        require_community_member(db, post.community, user.id)
        if kind is not None:
            ensure_can_post(db, post.community_id, user.id)
    reaction = db.scalar(
        select(SocialPostReaction).where(
            SocialPostReaction.post_id == post.id,
            SocialPostReaction.user_id == user.id,
        )
    )
    if kind is None:
        if reaction:
            db.delete(reaction)
            db.commit()
        current_kind = None
    elif reaction:
        reaction.kind = kind
        db.commit()
        current_kind = kind
    else:
        db.add(SocialPostReaction(post_id=post.id, user_id=user.id, kind=kind))
        db.commit()
        current_kind = kind
    count = db.scalar(
        select(func.count()).select_from(SocialPostReaction).where(SocialPostReaction.post_id == post.id)
    )
    return int(count or 0), current_kind


def get_reactions(
    db: Session,
    post_id: str,
    user_id: str | None,
) -> tuple[int, str | None]:
    post = get_post_with_access(db, post_id, user_id)
    if post.community_id is not None and user_id is not None:
        require_community_member(db, post.community, user_id)
    current = None
    if user_id is not None:
        current = db.scalar(
            select(SocialPostReaction.kind).where(
                SocialPostReaction.post_id == post.id,
                SocialPostReaction.user_id == user_id,
            )
        )
    count = db.scalar(
        select(func.count()).select_from(SocialPostReaction).where(
            SocialPostReaction.post_id == post.id
        )
    )
    return int(count or 0), current


def submit_content_report(
    db: Session,
    user: User,
    reason: str,
    post_id: str | None = None,
    comment_id: str | None = None,
) -> SocialPostReport:
    normalized_reason = reason.strip()
    if not normalized_reason:
        raise ContentUnavailable
    if (post_id is None) == (comment_id is None):
        raise ContentNotFound
    if post_id is not None:
        post = get_post_with_access(db, post_id, user.id)
        author_id = post.author_id
    else:
        comment = db.scalar(
            select(SocialPostComment)
            .options(joinedload(SocialPostComment.post).joinedload(SocialPost.community))
            .where(
                SocialPostComment.id == comment_id,
                SocialPostComment.moderation_status == "published",
            )
        )
        if comment is None:
            raise ContentNotFound
        if comment.post.moderation_status != "published":
            raise ContentNotFound
        if comment.post.community is not None:
            require_community_access(db, comment.post.community, user.id)
        author_id = comment.author_id
    if author_id == user.id:
        raise ContentNotFound
    report = SocialPostReport(
        reporter_id=user.id,
        reason=normalized_reason,
        status="pending",
        post_id=post_id,
        comment_id=comment_id,
    )
    db.add(report)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateContentReport from exc
    db.refresh(report)
    return report


def report_community_id(db: Session, report: SocialPostReport) -> str | None:
    if report.post_id:
        post = db.get(SocialPost, report.post_id)
        return post.community_id if post else None
    if report.comment_id:
        comment = db.get(SocialPostComment, report.comment_id)
        post = db.get(SocialPost, comment.post_id) if comment else None
        return post.community_id if post else None
    return None


def list_moderation_reports(
    db: Session,
    community_id: str,
    moderator: User,
) -> list[SocialPostReport]:
    if not is_community_moderator(db, community_id, moderator.id):
        raise ModeratorAccessDenied
    post_reports = (
        select(SocialPostReport.id)
        .join(SocialPost, SocialPost.id == SocialPostReport.post_id)
        .where(SocialPost.community_id == community_id)
    )
    comment_reports = (
        select(SocialPostReport.id)
        .join(SocialPostComment, SocialPostComment.id == SocialPostReport.comment_id)
        .join(SocialPost, SocialPost.id == SocialPostComment.post_id)
        .where(SocialPost.community_id == community_id)
    )
    return list(
        db.scalars(
            select(SocialPostReport)
            .options(joinedload(SocialPostReport.reporter))
            .where(
                SocialPostReport.status == "pending",
                SocialPostReport.id.in_(post_reports.union(comment_reports)),
            )
            .order_by(SocialPostReport.created_at, SocialPostReport.id)
        ).all()
    )


def review_report(
    db: Session,
    community_id: str,
    report_id: str,
    moderator: User,
    action: str,
    reason: str,
    duration_hours: int | None,
) -> ModerationAction:
    if not is_community_moderator(db, community_id, moderator.id):
        raise ModeratorAccessDenied
    report = db.get(SocialPostReport, report_id)
    if report is None or report.status != "pending" or report_community_id(db, report) != community_id:
        raise ContentNotFound
    if action == "suspend" and duration_hours is None:
        raise InvalidModerationAction
    if action != "suspend" and duration_hours is not None:
        raise InvalidModerationAction
    if report.post_id:
        target = db.get(SocialPost, report.post_id)
        if target is None:
            raise ContentNotFound
        target_user_id = target.author_id
    else:
        target_comment = db.get(SocialPostComment, report.comment_id)
        if target_comment is None:
            raise ContentNotFound
        target_user_id = target_comment.author_id
    if target_user_id == moderator.id:
        raise ModeratorAccessDenied
    if action == "suspend":
        target_membership = membership_for(db, community_id, target_user_id)
        if target_membership is None or target_membership.status != "active" or target_membership.role != "member":
            raise ModeratorAccessDenied
    expires_at = (
        datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        if duration_hours is not None
        else None
    )
    moderation_action = ModerationAction(
        community_id=community_id,
        report_id=report.id,
        moderator_id=moderator.id,
        target_user_id=target_user_id,
        action=action,
        reason=reason.strip(),
        expires_at=expires_at,
    )
    if action in {"hide", "remove"}:
        if report.post_id:
            target.moderation_status = "hidden" if action == "hide" else "removed"
        else:
            target_comment.moderation_status = "hidden" if action == "hide" else "removed"
    db.add(moderation_action)
    if action == "suspend":
        db.flush()
        db.add(
            CommunityPostingSuspension(
                community_id=community_id,
                user_id=target_user_id,
                issued_by_id=moderator.id,
                moderation_action_id=moderation_action.id,
                reason=reason.strip(),
                expires_at=expires_at,
            )
        )
    report.status = "escalated" if action == "escalate" else "reviewed"
    db.commit()
    db.refresh(moderation_action)
    return moderation_action


def list_user_moderation_actions(db: Session, user: User) -> list[ModerationAction]:
    return list(
        db.scalars(
            select(ModerationAction)
            .where(ModerationAction.target_user_id == user.id)
            .order_by(ModerationAction.created_at.desc(), ModerationAction.id)
        ).all()
    )


def submit_appeal(
    db: Session,
    action_id: str,
    user: User,
    reason: str,
) -> ModerationAppeal:
    action = db.get(ModerationAction, action_id)
    if (
        action is None
        or action.target_user_id != user.id
        or action.action not in {"hide", "remove", "warn", "suspend"}
        or action.appeal_status is not None
    ):
        raise AppealNotAllowed
    appeal = ModerationAppeal(
        action_id=action.id,
        appellant_id=user.id,
        reason=reason.strip(),
        status="pending",
    )
    action.appeal_status = "pending"
    db.add(appeal)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppealNotAllowed from exc
    db.refresh(appeal)
    return appeal


def list_pending_appeals(
    db: Session,
    community_id: str,
    moderator: User,
) -> list[ModerationAppeal]:
    if not is_community_moderator(db, community_id, moderator.id):
        raise ModeratorAccessDenied
    return list(
        db.scalars(
            select(ModerationAppeal)
            .join(ModerationAction, ModerationAction.id == ModerationAppeal.action_id)
            .where(
                ModerationAction.community_id == community_id,
                ModerationAppeal.status == "pending",
            )
            .order_by(ModerationAppeal.created_at, ModerationAppeal.id)
        ).all()
    )


def decide_appeal(
    db: Session,
    community_id: str,
    appeal_id: str,
    moderator: User,
    decision: str,
) -> ModerationAppeal:
    if not is_community_moderator(db, community_id, moderator.id):
        raise ModeratorAccessDenied
    appeal = db.get(ModerationAppeal, appeal_id)
    action = db.get(ModerationAction, appeal.action_id) if appeal else None
    if (
        appeal is None
        or action is None
        or action.community_id != community_id
        or appeal.status != "pending"
    ):
        raise AppealNotAllowed
    now = datetime.now(timezone.utc)
    appeal.status = decision
    appeal.reviewed_by_id = moderator.id
    appeal.reviewed_at = now
    action.appeal_status = decision
    if decision == "overturned":
        report = db.get(SocialPostReport, action.report_id)
        if report and report.post_id:
            post = db.get(SocialPost, report.post_id)
            if post:
                post.moderation_status = "published"
        elif report and report.comment_id:
            comment = db.get(SocialPostComment, report.comment_id)
            if comment:
                comment.moderation_status = "published"
        suspension = db.scalar(
            select(CommunityPostingSuspension).where(
                CommunityPostingSuspension.moderation_action_id == action.id,
                CommunityPostingSuspension.revoked_at.is_(None),
            )
        )
        if suspension:
            suspension.revoked_at = now
    db.commit()
    db.refresh(appeal)
    return appeal


def is_posting_suspended(db: Session, community_id: str, user_id: str) -> bool:
    now = datetime.now(timezone.utc)
    return db.scalar(
        select(CommunityPostingSuspension.id).where(
            CommunityPostingSuspension.community_id == community_id,
            CommunityPostingSuspension.user_id == user_id,
            CommunityPostingSuspension.revoked_at.is_(None),
            CommunityPostingSuspension.expires_at > now,
        )
    ) is not None
