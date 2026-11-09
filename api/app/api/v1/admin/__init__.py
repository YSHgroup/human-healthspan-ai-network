"""Platform administration for community approval and global moderation."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.identity import PlatformAdmin, require_trusted_origin
from app.domains.admin.workflows import (
    CommunityRequestAlreadyReviewed,
    CommunityRequestNotFound,
    CommunitySlugUnavailable,
    PlatformAppealNotFound,
    PlatformReportNotFound,
    PlatformReportNotReviewable,
    decide_community_request,
    decide_platform_appeal,
    list_pending_community_requests,
    list_platform_appeals,
    list_platform_moderation_reports,
    review_platform_report,
)
from app.infrastructure.database import get_db
from app.models import ModerationAction, ModerationAppeal, SocialPostReport
from app.schemas.admin import (
    CommunityRequestDecisionResponse,
    CommunityRequestReview,
    PlatformAppealDecision,
    PlatformCommunityRequestResponse,
    PlatformModerationActionCreate,
    PlatformModerationAppealResponse,
    PlatformModerationReportResponse,
)
from app.schemas.social import ModerationActionResponse


router = APIRouter(prefix="/admin", tags=["admin"])


def report_response(report: SocialPostReport) -> PlatformModerationReportResponse:
    if report.post is not None:
        target_kind = "post"
        target_body = report.post.body
        target_author = report.post.author
        community = report.post.community
    elif report.comment is not None and report.comment.post is not None:
        target_kind = "comment"
        target_body = report.comment.body
        target_author = report.comment.author
        community = report.comment.post.community
    else:
        raise HTTPException(status_code=404, detail="Reported content not found")
    return PlatformModerationReportResponse(
        id=report.id,
        post_id=report.post_id,
        comment_id=report.comment_id,
        reporter_id=report.reporter_id,
        reporter_display_name=report.reporter.display_name,
        reason=report.reason,
        status=report.status,
        created_at=report.created_at,
        target_kind=target_kind,
        target_body=target_body,
        target_author_id=target_author.id,
        target_author_display_name=target_author.display_name,
        community_id=community.id if community else None,
        community_name=community.name if community else None,
    )


def action_response(action: ModerationAction) -> ModerationActionResponse:
    return ModerationActionResponse(
        id=action.id,
        community_id=action.community_id,
        report_id=action.report_id,
        moderator_id=action.moderator_id,
        target_user_id=action.target_user_id,
        action=action.action,
        reason=action.reason,
        created_at=action.created_at,
        expires_at=action.expires_at,
        appeal_status=action.appeal_status,
    )


def appeal_response(appeal: ModerationAppeal) -> PlatformModerationAppealResponse:
    return PlatformModerationAppealResponse(
        id=appeal.id,
        action_id=appeal.action_id,
        appellant_id=appeal.appellant_id,
        reason=appeal.reason,
        status=appeal.status,
        created_at=appeal.created_at,
        action=appeal.action.action,
        action_reason=appeal.action.reason,
        target_user_id=appeal.action.target_user_id,
    )


@router.get(
    "/communities/requests",
    response_model=list[PlatformCommunityRequestResponse],
)
def community_requests(
    user: PlatformAdmin,
    db: Session = Depends(get_db),
) -> list[PlatformCommunityRequestResponse]:
    return [
        PlatformCommunityRequestResponse(
            id=request.id,
            requester_id=request.requester_id,
            requester_display_name=request.requester.display_name,
            slug=request.slug,
            name=request.name,
            description=request.description,
            access_type=request.access_type,
            created_at=request.created_at,
        )
        for request in list_pending_community_requests(db)
    ]


@router.post(
    "/communities/requests/{request_id}/decision",
    response_model=CommunityRequestDecisionResponse,
)
def decide_community_creation_request(
    request_id: str,
    body: CommunityRequestReview,
    request: Request,
    user: PlatformAdmin,
    db: Session = Depends(get_db),
) -> CommunityRequestDecisionResponse:
    require_trusted_origin(request)
    try:
        creation_request, community = decide_community_request(db, request_id, user, body.decision)
    except CommunityRequestNotFound as error:
        raise HTTPException(status_code=404, detail="Community request not found") from error
    except CommunityRequestAlreadyReviewed as error:
        raise HTTPException(status_code=409, detail="Community request has already been reviewed") from error
    except CommunitySlugUnavailable as error:
        raise HTTPException(status_code=409, detail="The requested community slug is no longer available") from error
    return CommunityRequestDecisionResponse(
        id=creation_request.id,
        status=creation_request.status,
        community_id=community.id if community else None,
        reviewed_at=creation_request.reviewed_at,
    )


@router.get(
    "/moderation/reports",
    response_model=list[PlatformModerationReportResponse],
)
def platform_moderation_reports(
    user: PlatformAdmin,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[PlatformModerationReportResponse]:
    return [report_response(report) for report in list_platform_moderation_reports(db, limit)]


@router.post(
    "/moderation/reports/{report_id}/actions",
    response_model=ModerationActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def review_platform_moderation_report(
    report_id: str,
    body: PlatformModerationActionCreate,
    request: Request,
    user: PlatformAdmin,
    db: Session = Depends(get_db),
) -> ModerationActionResponse:
    require_trusted_origin(request)
    try:
        action = review_platform_report(db, report_id, user, body.action, body.reason)
    except PlatformReportNotFound as error:
        raise HTTPException(status_code=404, detail="Report not found") from error
    except PlatformReportNotReviewable as error:
        raise HTTPException(status_code=409, detail="Report is not available for platform review") from error
    return action_response(action)


@router.get(
    "/moderation/appeals",
    response_model=list[PlatformModerationAppealResponse],
)
def platform_moderation_appeals(
    user: PlatformAdmin,
    db: Session = Depends(get_db),
) -> list[PlatformModerationAppealResponse]:
    return [appeal_response(appeal) for appeal in list_platform_appeals(db)]


@router.post(
    "/moderation/appeals/{appeal_id}/decision",
    response_model=PlatformModerationAppealResponse,
)
def decide_platform_moderation_appeal(
    appeal_id: str,
    body: PlatformAppealDecision,
    request: Request,
    user: PlatformAdmin,
    db: Session = Depends(get_db),
) -> PlatformModerationAppealResponse:
    require_trusted_origin(request)
    try:
        appeal = decide_platform_appeal(db, appeal_id, user, body.decision)
    except PlatformAppealNotFound as error:
        raise HTTPException(status_code=404, detail="Platform appeal not found") from error
    return appeal_response(appeal)
