"""Public social feed and authenticated contribution/report routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.identity import CurrentUser, require_trusted_origin
from app.domains.social.content import (
    BlankPostError,
    BlankReportReasonError,
    DuplicatePostReportError,
    PostUnavailableForReportError,
    list_public_feed,
    publish_post,
    report_post as create_post_report,
)
from app.infrastructure.database import get_db
from app.models import SocialPost
from app.schemas.social import (
    SocialPostCreate,
    SocialPostReportCreate,
    SocialPostReportResponse,
    SocialPostResponse,
)

router = APIRouter(tags=["social-feed"])


def post_response(post: SocialPost) -> SocialPostResponse:
    return SocialPostResponse(
        id=post.id,
        author_id=post.author_id,
        author_display_name=post.author.display_name,
        kind=post.kind,
        body=post.body,
        created_at=post.created_at,
    )


@router.get("/feed", response_model=list[SocialPostResponse])
def list_feed(
    db: Session = Depends(get_db),
    limit: int = Query(default=30, ge=1, le=100),
) -> list[SocialPostResponse]:
    return [post_response(post) for post in list_public_feed(db, limit)]


@router.post("/posts", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    body: SocialPostCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    require_trusted_origin(request)
    try:
        post = publish_post(db, user, body.kind, body.body)
    except BlankPostError as exc:
        raise HTTPException(status_code=422, detail="Post cannot be blank") from exc
    return post_response(post)


@router.post(
    "/posts/{post_id}/reports",
    response_model=SocialPostReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def report_post(
    post_id: str,
    body: SocialPostReportCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> SocialPostReportResponse:
    require_trusted_origin(request)
    try:
        report = create_post_report(db, user, post_id, body.reason)
    except PostUnavailableForReportError as exc:
        raise HTTPException(status_code=404, detail="Post not found") from exc
    except BlankReportReasonError as exc:
        raise HTTPException(status_code=422, detail="Report reason cannot be blank") from exc
    except DuplicatePostReportError as exc:
        raise HTTPException(status_code=409, detail="You have already reported this post") from exc
    return SocialPostReportResponse(
        id=report.id,
        post_id=report.post_id,
        status="pending",
        created_at=report.created_at,
    )
