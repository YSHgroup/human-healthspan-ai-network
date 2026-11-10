"""Platform community approval and global moderation workflows."""

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.domains.admin.audit import record_admin_action
from app.models import (
    Community,
    CommunityCreationRequest,
    CommunityMembership,
    ModerationAction,
    ModerationAppeal,
    SocialPost,
    SocialPostComment,
    SocialPostReport,
    User,
)


class AdminWorkflowError(ValueError):
    pass


class CommunityRequestNotFound(AdminWorkflowError):
    pass


class CommunityRequestAlreadyReviewed(AdminWorkflowError):
    pass


class CommunitySlugUnavailable(AdminWorkflowError):
    pass


class PlatformReportNotFound(AdminWorkflowError):
    pass


class PlatformReportNotReviewable(AdminWorkflowError):
    pass


class PlatformAppealNotFound(AdminWorkflowError):
    pass


def list_pending_community_requests(db: Session) -> list[CommunityCreationRequest]:
    return list(
        db.scalars(
            select(CommunityCreationRequest)
            .options(joinedload(CommunityCreationRequest.requester))
            .where(CommunityCreationRequest.status == "pending")
            .order_by(CommunityCreationRequest.created_at, CommunityCreationRequest.id)
        ).all()
    )


def decide_community_request(
    db: Session,
    request_id: str,
    reviewer: User,
    decision: str,
) -> tuple[CommunityCreationRequest, Community | None]:
    creation_request = db.scalar(
        select(CommunityCreationRequest)
        .options(joinedload(CommunityCreationRequest.requester))
        .where(CommunityCreationRequest.id == request_id)
        .with_for_update()
    )
    if creation_request is None:
        raise CommunityRequestNotFound
    if creation_request.status != "pending":
        raise CommunityRequestAlreadyReviewed

    reviewed_at = datetime.now(timezone.utc)
    community = None
    if decision == "approve":
        if db.scalar(select(Community.id).where(Community.slug == creation_request.slug)):
            raise CommunitySlugUnavailable
    try:
        if decision == "approve":
            community = Community(
                slug=creation_request.slug,
                name=creation_request.name,
                description=creation_request.description,
                access_type=creation_request.access_type,
                created_by_id=creation_request.requester_id,
            )
            db.add(community)
            db.flush()
            db.add(
                CommunityMembership(
                    community_id=community.id,
                    user_id=creation_request.requester_id,
                    role="owner",
                    status="active",
                    joined_at=reviewed_at,
                    reviewed_at=reviewed_at,
                    reviewed_by_id=reviewer.id,
                )
            )
            creation_request.status = "approved"
        else:
            creation_request.status = "rejected"

        creation_request.reviewed_at = reviewed_at
        creation_request.reviewed_by_id = reviewer.id
        record_admin_action(
            db,
            reviewer,
            "community_request_decided",
            "community_request",
            creation_request.id,
            f"{decision.title()} community request for {creation_request.name}",
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CommunitySlugUnavailable from exc
    db.refresh(creation_request)
    if community is not None:
        db.refresh(community)
    return creation_request, community


def list_platform_moderation_reports(
    db: Session,
    limit: int,
) -> list[SocialPostReport]:
    global_post_reports = (
        select(SocialPostReport.id)
        .join(SocialPost, SocialPost.id == SocialPostReport.post_id)
        .where(SocialPost.community_id.is_(None))
    )
    global_comment_reports = (
        select(SocialPostReport.id)
        .join(SocialPostComment, SocialPostComment.id == SocialPostReport.comment_id)
        .join(SocialPost, SocialPost.id == SocialPostComment.post_id)
        .where(SocialPost.community_id.is_(None))
    )
    global_pending = (
        (SocialPostReport.status == "pending")
        & SocialPostReport.id.in_(global_post_reports.union(global_comment_reports))
    )
    return list(
        db.scalars(
            select(SocialPostReport)
            .options(
                joinedload(SocialPostReport.reporter),
                joinedload(SocialPostReport.post).joinedload(SocialPost.author),
                joinedload(SocialPostReport.post).joinedload(SocialPost.community),
                joinedload(SocialPostReport.comment).joinedload(SocialPostComment.author),
                joinedload(SocialPostReport.comment)
                .joinedload(SocialPostComment.post)
                .joinedload(SocialPost.author),
                joinedload(SocialPostReport.comment)
                .joinedload(SocialPostComment.post)
                .joinedload(SocialPost.community),
            )
            .where(or_(global_pending, SocialPostReport.status == "escalated"))
            .order_by(SocialPostReport.created_at, SocialPostReport.id)
            .limit(limit)
        ).all()
    )


def review_platform_report(
    db: Session,
    report_id: str,
    reviewer: User,
    action: str,
    reason: str,
) -> ModerationAction:
    report = db.scalar(
        select(SocialPostReport)
        .options(
            joinedload(SocialPostReport.post).joinedload(SocialPost.author),
            joinedload(SocialPostReport.post).joinedload(SocialPost.community),
            joinedload(SocialPostReport.comment).joinedload(SocialPostComment.author),
            joinedload(SocialPostReport.comment)
            .joinedload(SocialPostComment.post)
            .joinedload(SocialPost.author),
            joinedload(SocialPostReport.comment)
            .joinedload(SocialPostComment.post)
            .joinedload(SocialPost.community),
        )
        .where(SocialPostReport.id == report_id)
        .with_for_update()
    )
    if report is None:
        raise PlatformReportNotFound

    target_author_id: str
    target_post: SocialPost | None = None
    target_comment: SocialPostComment | None = None
    if report.post is not None:
        target_post = report.post
        target_author_id = target_post.author_id
        community_id = target_post.community_id
    elif report.comment is not None and report.comment.post is not None:
        target_comment = report.comment
        target_post = target_comment.post
        target_author_id = target_comment.author_id
        community_id = target_post.community_id
    else:
        raise PlatformReportNotFound

    is_escalated = report.status == "escalated"
    is_global_pending = report.status == "pending" and community_id is None
    if not (is_escalated or is_global_pending):
        raise PlatformReportNotReviewable
    if target_author_id == reviewer.id:
        raise PlatformReportNotReviewable

    moderation_action = ModerationAction(
        community_id=community_id,
        report_id=report.id,
        moderator_id=reviewer.id,
        target_user_id=target_author_id,
        action=action,
        reason=reason.strip(),
    )
    if action in {"hide", "remove"}:
        if target_comment is not None:
            target_comment.moderation_status = "hidden" if action == "hide" else "removed"
        elif target_post is not None:
            target_post.moderation_status = "hidden" if action == "hide" else "removed"
    db.add(moderation_action)
    report.status = "reviewed"
    record_admin_action(
        db,
        reviewer,
        "moderation_report_reviewed",
        "moderation_report",
        report.id,
        f"Applied {action} moderation action to "
        f"{'comment' if target_comment is not None else 'post'} report",
    )
    db.commit()
    db.refresh(moderation_action)
    return moderation_action


def list_platform_appeals(db: Session) -> list[ModerationAppeal]:
    return list(
        db.scalars(
            select(ModerationAppeal)
            .join(ModerationAction, ModerationAction.id == ModerationAppeal.action_id)
            .options(joinedload(ModerationAppeal.action))
            .where(
                ModerationAction.community_id.is_(None),
                ModerationAppeal.status == "pending",
            )
            .order_by(ModerationAppeal.created_at, ModerationAppeal.id)
        ).all()
    )


def decide_platform_appeal(
    db: Session,
    appeal_id: str,
    reviewer: User,
    decision: str,
) -> ModerationAppeal:
    appeal = db.scalar(
        select(ModerationAppeal)
        .options(joinedload(ModerationAppeal.action))
        .where(ModerationAppeal.id == appeal_id)
        .with_for_update()
    )
    if (
        appeal is None
        or appeal.action is None
        or appeal.action.community_id is not None
        or appeal.status != "pending"
    ):
        raise PlatformAppealNotFound

    now = datetime.now(timezone.utc)
    appeal.status = decision
    appeal.reviewed_by_id = reviewer.id
    appeal.reviewed_at = now
    appeal.action.appeal_status = decision
    record_admin_action(
        db,
        reviewer,
        "moderation_appeal_decided",
        "moderation_appeal",
        appeal.id,
        f"{decision.title()} platform moderation appeal",
    )
    if decision == "overturned":
        report = db.get(SocialPostReport, appeal.action.report_id)
        if report and report.post_id:
            post = db.get(SocialPost, report.post_id)
            if post:
                post.moderation_status = "published"
        elif report and report.comment_id:
            comment = db.get(SocialPostComment, report.comment_id)
            if comment:
                comment.moderation_status = "published"
    db.commit()
    db.refresh(appeal)
    return appeal
