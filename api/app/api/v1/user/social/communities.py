"""Community membership, discussions, comments, reactions, and moderation routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.identity import CurrentUser, require_trusted_origin
from app.domains.social.communities import (
    AppealNotAllowed,
    CommunityAccessDenied,
    CommunityNotFound,
    CommunitySlugUnavailable,
    ContentNotFound,
    ContentUnavailable,
    DuplicateContentReport,
    InvalidModerationAction,
    MembershipConflict,
    MembershipNotFound,
    ModeratorAccessDenied,
    PostingSuspended,
    SocialDomainError,
    add_comment,
    decide_appeal,
    decide_membership,
    get_reactions as get_post_reactions,
    join_community,
    list_comments,
    list_communities,
    list_community_posts,
    list_moderation_reports,
    list_pending_appeals,
    list_pending_memberships,
    list_user_moderation_actions,
    publish_community_post,
    review_report,
    set_reaction,
    submit_appeal,
    submit_community_creation_request,
    submit_content_report,
)
from app.infrastructure.database import get_db
from app.models import (
    Community,
    CommunityMembership,
    ModerationAction,
    ModerationAppeal,
    SocialPost,
    SocialPostComment,
    SocialPostReport,
    User,
)
from app.schemas.social import (
    CommunityCreateRequest,
    CommunityCreationRequestResponse,
    CommunityJoinRequest,
    CommunityMembershipResponse,
    CommunityPostCreate,
    CommunityResponse,
    MembershipDecision,
    ModerationActionCreate,
    ModerationActionResponse,
    ModerationAppealCreate,
    ModerationAppealDecision,
    ModerationAppealResponse,
    ModerationReportResponse,
    SocialPostCommentCreate,
    SocialPostCommentResponse,
    SocialPostReactionRequest,
    SocialPostReactionResponse,
    SocialPostResponse,
    SocialPostReportCreate,
    SocialPostReportResponse,
)

router = APIRouter(tags=["social-communities"])


def community_response(
    community: Community,
    membership: CommunityMembership | None,
) -> CommunityResponse:
    return CommunityResponse(
        id=community.id,
        slug=community.slug,
        name=community.name,
        description=community.description,
        rules=community.rules,
        access_type=community.access_type,
        membership_status=membership.status if membership else "none",
        membership_role=membership.role if membership and membership.status == "active" else None,
    )


def post_response(post: SocialPost) -> SocialPostResponse:
    return SocialPostResponse(
        id=post.id,
        author_id=post.author_id,
        author_display_name=post.author.display_name,
        kind=post.kind,
        body=post.body,
        created_at=post.created_at,
    )


def membership_response(membership: CommunityMembership) -> CommunityMembershipResponse:
    return CommunityMembershipResponse(
        id=membership.id,
        community_id=membership.community_id,
        user_id=membership.user_id,
        display_name=membership.user.display_name,
        role=membership.role,
        status=membership.status,
        application_message=membership.application_message,
        joined_at=membership.joined_at,
    )


def comment_response(comment: SocialPostComment) -> SocialPostCommentResponse:
    return SocialPostCommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author_display_name=comment.author.display_name,
        body=comment.body,
        created_at=comment.created_at,
    )


def moderation_report_response(report: SocialPostReport) -> ModerationReportResponse:
    return ModerationReportResponse(
        id=report.id,
        post_id=report.post_id,
        comment_id=report.comment_id,
        reporter_id=report.reporter_id,
        reporter_display_name=report.reporter.display_name,
        reason=report.reason,
        status="pending",
        created_at=report.created_at,
    )


def moderation_action_response(action: ModerationAction) -> ModerationActionResponse:
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


def appeal_response(appeal: ModerationAppeal) -> ModerationAppealResponse:
    return ModerationAppealResponse(
        id=appeal.id,
        action_id=appeal.action_id,
        appellant_id=appeal.appellant_id,
        reason=appeal.reason,
        status=appeal.status,
        created_at=appeal.created_at,
    )


def raise_social_error(error: SocialDomainError) -> None:
    if isinstance(error, (CommunityNotFound, ContentNotFound)):
        raise HTTPException(status_code=404, detail="Resource not found") from error
    if isinstance(error, (ModeratorAccessDenied, CommunityAccessDenied)):
        raise HTTPException(status_code=403, detail="You are not allowed to perform this action") from error
    if isinstance(error, (CommunitySlugUnavailable, MembershipConflict)):
        raise HTTPException(
            status_code=409,
            detail=str(error) or "The resource conflicts with an existing record",
        ) from error
    if isinstance(error, (MembershipNotFound, AppealNotAllowed)):
        raise HTTPException(status_code=404, detail="Request not found") from error
    if isinstance(error, InvalidModerationAction):
        raise HTTPException(status_code=422, detail="Invalid moderation action configuration") from error
    if isinstance(error, PostingSuspended):
        raise HTTPException(status_code=403, detail="Posting is suspended for this community") from error
    if isinstance(error, ContentUnavailable):
        raise HTTPException(status_code=422, detail="Content cannot be blank") from error
    raise error


@router.get("/communities", response_model=list[CommunityResponse])
def get_communities(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[CommunityResponse]:
    return [
        community_response(community, membership)
        for community, membership in list_communities(db, user)
    ]


@router.post(
    "/communities/requests",
    response_model=CommunityCreationRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_community(
    body: CommunityCreateRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> CommunityCreationRequestResponse:
    require_trusted_origin(request)
    try:
        creation_request = submit_community_creation_request(
            db, user, body.slug, body.name, body.description, body.access_type
        )
    except SocialDomainError as error:
        raise_social_error(error)
    return CommunityCreationRequestResponse(
        id=creation_request.id,
        slug=creation_request.slug,
        name=creation_request.name,
        description=creation_request.description,
        access_type=creation_request.access_type,
        status="pending",
        created_at=creation_request.created_at,
    )


@router.post(
    "/communities/{community_id}/join",
    response_model=CommunityMembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def join(
    community_id: str,
    body: CommunityJoinRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> CommunityMembershipResponse:
    require_trusted_origin(request)
    try:
        membership = join_community(db, user, community_id, body.message)
    except SocialDomainError as error:
        raise_social_error(error)
    membership.user = user
    return membership_response(membership)


@router.get(
    "/communities/{community_id}/memberships/pending",
    response_model=list[CommunityMembershipResponse],
)
def pending_memberships(
    community_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[CommunityMembershipResponse]:
    try:
        memberships = list_pending_memberships(db, community_id, user)
    except SocialDomainError as error:
        raise_social_error(error)
    return [membership_response(membership) for membership in memberships]


@router.post(
    "/communities/{community_id}/memberships/{membership_id}/decision",
    response_model=CommunityMembershipResponse,
)
def review_membership(
    community_id: str,
    membership_id: str,
    body: MembershipDecision,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> CommunityMembershipResponse:
    require_trusted_origin(request)
    try:
        membership = decide_membership(db, community_id, membership_id, user, body.decision)
    except SocialDomainError as error:
        raise_social_error(error)
    membership.user = db.get(User, membership.user_id)
    return membership_response(membership)


@router.get(
    "/communities/{community_id}/posts",
    response_model=list[SocialPostResponse],
)
def community_posts(
    community_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(default=30, ge=1, le=100),
) -> list[SocialPostResponse]:
    try:
        posts = list_community_posts(db, community_id, user, limit)
    except SocialDomainError as error:
        raise_social_error(error)
    return [post_response(post) for post in posts]


@router.post(
    "/communities/{community_id}/posts",
    response_model=SocialPostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_community_post(
    community_id: str,
    body: CommunityPostCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    require_trusted_origin(request)
    try:
        post = publish_community_post(db, community_id, user, body.kind, body.body)
    except SocialDomainError as error:
        raise_social_error(error)
    return post_response(post)


@router.get("/posts/{post_id}/comments", response_model=list[SocialPostCommentResponse])
def get_comments(
    post_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[SocialPostCommentResponse]:
    try:
        comments = list_comments(db, post_id, user.id)
    except SocialDomainError as error:
        raise_social_error(error)
    return [comment_response(comment) for comment in comments]


@router.post(
    "/posts/{post_id}/comments",
    response_model=SocialPostCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_comment(
    post_id: str,
    body: SocialPostCommentCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostCommentResponse:
    require_trusted_origin(request)
    try:
        comment = add_comment(db, post_id, user, body.body)
    except SocialDomainError as error:
        raise_social_error(error)
    comment.author = user
    return comment_response(comment)


@router.get("/posts/{post_id}/reactions", response_model=SocialPostReactionResponse)
def get_reactions(
    post_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostReactionResponse:
    try:
        count, current = get_post_reactions(db, post_id, user.id)
    except SocialDomainError as error:
        raise_social_error(error)
    return SocialPostReactionResponse(
        post_id=post_id,
        count=int(count),
        current_user_reaction=current,
    )


@router.put("/posts/{post_id}/reactions", response_model=SocialPostReactionResponse)
def update_reaction(
    post_id: str,
    body: SocialPostReactionRequest,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostReactionResponse:
    require_trusted_origin(request)
    try:
        count, current = set_reaction(db, post_id, user, body.kind)
    except SocialDomainError as error:
        raise_social_error(error)
    return SocialPostReactionResponse(post_id=post_id, count=count, current_user_reaction=current)


@router.delete("/posts/{post_id}/reactions", response_model=SocialPostReactionResponse)
def remove_reaction(
    post_id: str,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostReactionResponse:
    require_trusted_origin(request)
    try:
        count, current = set_reaction(db, post_id, user, None)
    except SocialDomainError as error:
        raise_social_error(error)
    return SocialPostReactionResponse(post_id=post_id, count=count, current_user_reaction=current)


@router.post(
    "/comments/{comment_id}/reports",
    response_model=SocialPostReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_comment(
    comment_id: str,
    body: SocialPostReportCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostReportResponse:
    require_trusted_origin(request)
    try:
        report = submit_content_report(db, user, body.reason, comment_id=comment_id)
    except DuplicateContentReport as error:
        raise HTTPException(status_code=409, detail="You have already reported this comment") from error
    except SocialDomainError as error:
        raise_social_error(error)
    return SocialPostReportResponse(
        id=report.id,
        post_id=report.post_id,
        comment_id=report.comment_id,
        status="pending",
        created_at=report.created_at,
    )


@router.get(
    "/communities/{community_id}/moderation/reports",
    response_model=list[ModerationReportResponse],
)
def moderation_reports(
    community_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ModerationReportResponse]:
    try:
        reports = list_moderation_reports(db, community_id, user)
    except SocialDomainError as error:
        raise_social_error(error)
    return [moderation_report_response(report) for report in reports]


@router.post(
    "/communities/{community_id}/moderation/reports/{report_id}/actions",
    response_model=ModerationActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def take_moderation_action(
    community_id: str,
    report_id: str,
    body: ModerationActionCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ModerationActionResponse:
    require_trusted_origin(request)
    try:
        action = review_report(
            db,
            community_id,
            report_id,
            user,
            body.action,
            body.reason,
            body.duration_hours,
        )
    except SocialDomainError as error:
        raise_social_error(error)
    return moderation_action_response(action)


@router.get("/me/moderation/actions", response_model=list[ModerationActionResponse])
def moderation_actions(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ModerationActionResponse]:
    return [moderation_action_response(action) for action in list_user_moderation_actions(db, user)]


@router.post(
    "/me/moderation/actions/{action_id}/appeals",
    response_model=ModerationAppealResponse,
    status_code=status.HTTP_201_CREATED,
)
def appeal_action(
    action_id: str,
    body: ModerationAppealCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ModerationAppealResponse:
    require_trusted_origin(request)
    try:
        appeal = submit_appeal(db, action_id, user, body.reason)
    except SocialDomainError as error:
        raise_social_error(error)
    return appeal_response(appeal)


@router.post(
    "/communities/{community_id}/moderation/appeals/{appeal_id}/decision",
    response_model=ModerationAppealResponse,
)
def review_appeal(
    community_id: str,
    appeal_id: str,
    body: ModerationAppealDecision,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ModerationAppealResponse:
    require_trusted_origin(request)
    try:
        appeal = decide_appeal(db, community_id, appeal_id, user, body.decision)
    except SocialDomainError as error:
        raise_social_error(error)
    return appeal_response(appeal)


@router.get(
    "/communities/{community_id}/moderation/appeals",
    response_model=list[ModerationAppealResponse],
)
def pending_appeals(
    community_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ModerationAppealResponse]:
    try:
        appeals = list_pending_appeals(db, community_id, user)
    except SocialDomainError as error:
        raise_social_error(error)
    return [appeal_response(appeal) for appeal in appeals]
