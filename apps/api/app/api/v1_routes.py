from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.auth import router as auth_router
from app.api.dependencies import get_current_user, require_roles
from app.db.base import utc_now
from app.db.session import get_db
from app.models.domain import (
    AuditEvent,
    Bookmark,
    Comment,
    Community,
    CommunityMember,
    Evidence,
    Follow,
    Hypothesis,
    Literature,
    Post,
    Profile,
    Reaction,
    Report,
    ResearchMember,
    ResearchProject,
    ResearchQuestion,
    User,
)
from app.schemas.auth import AdminUserOut, ProfileOut, PublicUserOut, UserOut, UserProfileUpdate
from app.schemas.content import CommentCreate, CommentOut, PostCreate, PostOut, ReactionCreate
from app.schemas.governance import (
    AdminUserUpdate,
    CommunityOut,
    ModerationDecision,
    ReportCreate,
    ReportOut,
)
from app.schemas.research import (
    EvidenceCreate,
    EvidenceOut,
    HypothesisCreate,
    HypothesisOut,
    LiteratureCreate,
    LiteratureOut,
    ResearchMemberCreate,
    ResearchMemberOut,
    ResearchProjectCreate,
    ResearchProjectOut,
    ResearchProjectUpdate,
    ResearchQuestionCreate,
    ResearchQuestionOut,
)
from app.services.audit import record_audit_event
from app.services.authorization import AuthorizationService
from app.services.search import SearchService

router = APIRouter()
router.include_router(auth_router)


@router.get("/me", response_model=UserOut)
@router.get("/users/me", response_model=UserOut)
def get_me_alias(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    return UserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        profile=ProfileOut.model_validate(profile) if profile else None,
    )


@router.patch("/me", response_model=UserOut)
@router.patch("/users/me", response_model=UserOut)
def update_me_alias(
    payload: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return UserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        profile=ProfileOut.model_validate(profile),
    )


def project_or_404(db: Session, project_id: UUID) -> ResearchProject:
    project = db.get(ResearchProject, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research project not found.")
    return project


def require_project_read(db: Session, user: User, project: ResearchProject) -> None:
    if not AuthorizationService(db).can_read_project(user, project):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research project not found.")


def require_project_write(db: Session, user: User, project: ResearchProject) -> None:
    if not AuthorizationService(db).can_write_project(user, project):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot modify this research project.")


@router.get("/version")
def version() -> dict[str, str]:
    return {"api": "v1", "roadmap_phase": "1"}


@router.get("/users/{user_id}", response_model=PublicUserOut)
def get_public_user(user_id: UUID, db: Session = Depends(get_db)) -> PublicUserOut:
    user = db.get(User, user_id)
    profile = db.scalar(select(Profile).where(Profile.user_id == user_id))
    if user is None or profile is None or not profile.is_public or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return PublicUserOut(
        id=user.id,
        role=user.role,
        profile=ProfileOut.model_validate(profile),
    )


@router.get("/feed", response_model=list[PostOut])
def get_feed(
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
    community_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> list[Post]:
    query = select(Post).join(User, User.id == Post.author_id).where(
        Post.deleted_at.is_(None),
        User.is_active.is_(True),
    )
    if community_id is not None:
        query = query.where(Post.community_id == community_id)
    return list(db.scalars(query.order_by(Post.created_at.desc(), Post.id).limit(limit).offset(offset)))


@router.post("/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Post:
    if payload.community_id is not None:
        community = db.get(Community, payload.community_id)
        if community is None or not community.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found.")
        is_member = db.scalar(
            select(CommunityMember.id).where(
                CommunityMember.community_id == community.id,
                CommunityMember.user_id == user.id,
            )
        )
        if is_member is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Join the community before posting.")
    post = Post(
        author_id=user.id,
        community_id=payload.community_id,
        body=payload.body.strip(),
        content_type=payload.content_type,
        classification=payload.classification,
    )
    db.add(post)
    db.flush()
    record_audit_event(db, user.id, "post.created", "post", post.id)
    db.commit()
    db.refresh(post)
    return post


@router.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: UUID, db: Session = Depends(get_db)) -> Post:
    post = db.get(Post, post_id)
    if post is None or post.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    author = db.get(User, post.author_id)
    if author is None or not author.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post


@router.get("/communities/{community_id}")
def get_community(community_id: UUID, db: Session = Depends(get_db)) -> dict[str, object]:
    community = db.get(Community, community_id)
    if community is None or not community.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found.")
    member_count = db.scalar(
        select(func.count()).select_from(CommunityMember).where(CommunityMember.community_id == community_id)
    )
    return {
        "id": community.id,
        "slug": community.slug,
        "name": community.name,
        "description": community.description,
        "topic": community.topic,
        "member_count": member_count or 0,
    }


@router.get("/communities/{community_id}/feed", response_model=list[PostOut])
def community_feed(
    community_id: UUID,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[Post]:
    community = db.get(Community, community_id)
    if community is None or not community.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found.")
    return list(
        db.scalars(
            select(Post)
            .join(User, User.id == Post.author_id)
            .where(Post.community_id == community_id, Post.deleted_at.is_(None), User.is_active.is_(True))
            .order_by(Post.created_at.desc(), Post.id)
            .limit(limit)
            .offset(offset)
        )
    )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    post = db.get(Post, post_id)
    if post is None or post.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    if post.author_id != user.id and user.role not in {"admin", "moderator"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot remove this post.")
    post.deleted_at = utc_now()
    record_audit_event(db, user.id, "post.removed", "post", post.id)
    db.commit()


@router.get("/posts/{post_id}/comments", response_model=list[CommentOut])
def list_comments(
    post_id: UUID,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[Comment]:
    post = db.get(Post, post_id)
    if post is None or post.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    query = (
        select(Comment)
        .join(User, User.id == Comment.author_id)
        .where(Comment.post_id == post_id, Comment.deleted_at.is_(None), User.is_active.is_(True))
    )
    return list(db.scalars(query.order_by(Comment.created_at.asc()).limit(limit).offset(offset)))


@router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Comment:
    post = db.get(Post, post_id)
    if post is None or post.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    comment = Comment(post_id=post_id, author_id=user.id, body=payload.body.strip())
    db.add(comment)
    db.flush()
    record_audit_event(db, user.id, "comment.created", "comment", comment.id)
    db.commit()
    db.refresh(comment)
    return comment


@router.post("/posts/{post_id}/reactions", status_code=status.HTTP_201_CREATED)
def react_to_post(
    post_id: UUID,
    payload: ReactionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    post = db.get(Post, post_id)
    if post is None or post.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    reaction = db.scalar(
        select(Reaction).where(Reaction.post_id == post_id, Reaction.user_id == user.id)
    )
    if reaction is None:
        db.add(Reaction(post_id=post_id, user_id=user.id, kind=payload.kind))
        record_audit_event(db, user.id, "post.reacted", "post", post_id, {"kind": payload.kind})
    else:
        reaction.kind = payload.kind
        record_audit_event(db, user.id, "post.reaction_updated", "post", post_id, {"kind": payload.kind})
    db.commit()
    return {"status": "recorded", "kind": payload.kind}


@router.delete("/posts/{post_id}/reactions", status_code=status.HTTP_204_NO_CONTENT)
def remove_post_reaction(
    post_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    reaction = db.scalar(
        select(Reaction).where(Reaction.post_id == post_id, Reaction.user_id == user.id)
    )
    if reaction is not None:
        db.delete(reaction)
        record_audit_event(db, user.id, "post.reaction_removed", "post", post_id)
        db.commit()


@router.post("/posts/{post_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
def bookmark_post(
    post_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    post = db.get(Post, post_id)
    if post is None or post.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    existing = db.scalar(
        select(Bookmark).where(Bookmark.post_id == post_id, Bookmark.user_id == user.id)
    )
    if existing is None:
        db.add(Bookmark(post_id=post_id, user_id=user.id))
        record_audit_event(db, user.id, "post.bookmarked", "post", post_id)
        db.commit()


@router.delete("/posts/{post_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
def unbookmark_post(
    post_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    bookmark = db.scalar(
        select(Bookmark).where(Bookmark.post_id == post_id, Bookmark.user_id == user.id)
    )
    if bookmark is not None:
        db.delete(bookmark)
        record_audit_event(db, user.id, "post.unbookmarked", "post", post_id)
        db.commit()


@router.post("/users/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    user_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself.")
    target = db.get(User, user_id)
    if target is None or not target.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    existing = db.scalar(
        select(Follow).where(Follow.follower_id == user.id, Follow.followed_id == user_id)
    )
    if existing is None:
        db.add(Follow(follower_id=user.id, followed_id=user_id))
        record_audit_event(db, user.id, "user.followed", "user", user_id)
        db.commit()


@router.delete("/users/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    follow = db.scalar(
        select(Follow).where(Follow.follower_id == user.id, Follow.followed_id == user_id)
    )
    if follow is not None:
        db.delete(follow)
        record_audit_event(db, user.id, "user.unfollowed", "user", user_id)
        db.commit()


@router.get("/communities", response_model=list[CommunityOut])
def list_communities(db: Session = Depends(get_db)) -> list[Community]:
    return list(
        db.scalars(
            select(Community).where(Community.is_active.is_(True)).order_by(Community.name.asc())
        )
    )


@router.post("/communities/{community_id}/join", status_code=status.HTTP_204_NO_CONTENT)
def join_community(
    community_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    community = db.get(Community, community_id)
    if community is None or not community.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found.")
    member = db.scalar(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == user.id,
        )
    )
    if member is None:
        db.add(CommunityMember(community_id=community_id, user_id=user.id))
        record_audit_event(db, user.id, "community.joined", "community", community_id)
        db.commit()


@router.delete("/communities/{community_id}/join", status_code=status.HTTP_204_NO_CONTENT)
def leave_community(
    community_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    member = db.scalar(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == user.id,
        )
    )
    if member is not None:
        db.delete(member)
        record_audit_event(db, user.id, "community.left", "community", community_id)
        db.commit()


@router.get("/research/projects", response_model=list[ResearchProjectOut])
def list_research_projects(
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResearchProject]:
    readable_project_ids = AuthorizationService(db).readable_project_ids(user)
    query = select(ResearchProject).where(ResearchProject.id.in_(readable_project_ids))
    return list(
        db.scalars(query.order_by(ResearchProject.created_at.desc()).limit(limit).offset(offset))
    )


@router.post(
    "/research/projects",
    response_model=ResearchProjectOut,
    status_code=status.HTTP_201_CREATED,
)
def create_research_project(
    payload: ResearchProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProject:
    project = ResearchProject(
        owner_id=user.id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        visibility=payload.visibility,
    )
    db.add(project)
    db.flush()
    record_audit_event(db, user.id, "research_project.created", "research_project", project.id)
    db.commit()
    db.refresh(project)
    return project


@router.get("/research/projects/{project_id}", response_model=ResearchProjectOut)
def get_research_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProject:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    return project


@router.patch("/research/projects/{project_id}", response_model=ResearchProjectOut)
def update_research_project(
    project_id: UUID,
    payload: ResearchProjectUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProject:
    project = project_or_404(db, project_id)
    require_project_write(db, user, project)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(project, field, value.strip() if isinstance(value, str) else value)
    record_audit_event(db, user.id, "research_project.updated", "research_project", project.id)
    db.commit()
    db.refresh(project)
    return project


@router.post("/research/projects/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_research_member(
    project_id: UUID,
    payload: ResearchMemberCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    project = project_or_404(db, project_id)
    require_project_write(db, user, project)
    if project.visibility != "team":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Set project visibility to 'team' before adding members.",
        )
    target = db.get(User, payload.user_id)
    if target is None or not target.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    existing = db.scalar(
        select(ResearchMember).where(
            ResearchMember.project_id == project_id,
            ResearchMember.user_id == payload.user_id,
        )
    )
    if existing is None:
        db.add(ResearchMember(project_id=project_id, user_id=payload.user_id, role=payload.role))
        record_audit_event(
            db, user.id, "research_member.added", "research_project", project_id,
            {"member_id": str(payload.user_id), "role": payload.role},
        )
        db.commit()
    return {"status": "member_added"}


@router.get(
    "/research/projects/{project_id}/members",
    response_model=list[ResearchMemberOut],
)
def list_research_members(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResearchMember]:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    return list(
        db.scalars(
            select(ResearchMember)
            .where(ResearchMember.project_id == project_id)
            .order_by(ResearchMember.created_at.asc())
        )
    )


@router.post(
    "/research/questions",
    response_model=ResearchQuestionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_research_question(
    payload: ResearchQuestionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchQuestion:
    project = project_or_404(db, payload.project_id)
    require_project_write(db, user, project)
    question = ResearchQuestion(
        project_id=project.id,
        author_id=user.id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        evidence_status="unclassified",
    )
    db.add(question)
    db.flush()
    record_audit_event(db, user.id, "research_question.created", "research_question", question.id)
    db.commit()
    db.refresh(question)
    return question


@router.get("/research/projects/{project_id}/questions", response_model=list[ResearchQuestionOut])
def list_research_questions(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResearchQuestion]:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    return list(
        db.scalars(
            select(ResearchQuestion)
            .where(ResearchQuestion.project_id == project_id)
            .order_by(ResearchQuestion.created_at.desc())
        )
    )


@router.post(
    "/research/projects/{project_id}/hypotheses",
    response_model=HypothesisOut,
    status_code=status.HTTP_201_CREATED,
)
def create_hypothesis(
    project_id: UUID,
    payload: HypothesisCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Hypothesis:
    project = project_or_404(db, project_id)
    require_project_write(db, user, project)
    if payload.research_question_id is not None:
        question = db.get(ResearchQuestion, payload.research_question_id)
        if question is None or question.project_id != project_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research question not found.")
        if payload.research_question_id not in {None, question.id}:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Question ID does not match the route.")
    hypothesis = Hypothesis(
        project_id=project_id,
        research_question_id=payload.research_question_id,
        author_id=user.id,
        title=payload.title,
        description=payload.description,
        origin="human",
    )
    db.add(hypothesis)
    db.flush()
    record_audit_event(db, user.id, "hypothesis.created", "hypothesis", hypothesis.id)
    db.commit()
    db.refresh(hypothesis)
    return hypothesis


@router.post(
    "/research/questions/{question_id}/hypotheses",
    response_model=HypothesisOut,
    status_code=status.HTTP_201_CREATED,
)
def create_question_hypothesis(
    question_id: UUID,
    payload: HypothesisCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Hypothesis:
    question = db.get(ResearchQuestion, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research question not found.")
    project = project_or_404(db, question.project_id)
    require_project_write(db, user, project)
    hypothesis = Hypothesis(
        project_id=project.id,
        research_question_id=question.id,
        author_id=user.id,
        title=payload.title,
        description=payload.description,
        origin="human",
    )
    db.add(hypothesis)
    db.flush()
    record_audit_event(db, user.id, "hypothesis.created", "hypothesis", hypothesis.id)
    db.commit()
    db.refresh(hypothesis)
    return hypothesis


@router.get("/research/projects/{project_id}/hypotheses", response_model=list[HypothesisOut])
def list_hypotheses(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Hypothesis]:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    return list(
        db.scalars(
            select(Hypothesis)
            .where(Hypothesis.project_id == project_id)
            .order_by(Hypothesis.created_at.desc())
        )
    )


@router.post(
    "/research/projects/{project_id}/literature",
    response_model=LiteratureOut,
    status_code=status.HTTP_201_CREATED,
)
def add_literature(
    project_id: UUID,
    payload: LiteratureCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Literature:
    project = project_or_404(db, project_id)
    require_project_write(db, user, project)
    entry = Literature(project_id=project_id, added_by=user.id, **payload.model_dump())
    if payload.doi:
        existing = db.scalar(select(Literature).where(Literature.doi == payload.doi))
        if existing is not None and existing.project_id == project_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This DOI is already in the project.")
    db.add(entry)
    db.flush()
    record_audit_event(db, user.id, "literature.added", "literature", entry.id)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/research/projects/{project_id}/literature", response_model=list[LiteratureOut])
def list_literature(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Literature]:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    return list(
        db.scalars(
            select(Literature)
            .where(Literature.project_id == project_id)
            .order_by(Literature.created_at.desc())
        )
    )


@router.post(
    "/research/projects/{project_id}/evidence",
    response_model=EvidenceOut,
    status_code=status.HTTP_201_CREATED,
)
def add_evidence(
    project_id: UUID,
    payload: EvidenceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Evidence:
    project = project_or_404(db, project_id)
    require_project_write(db, user, project)
    if payload.literature_id is not None:
        literature = db.get(Literature, payload.literature_id)
        if literature is None or literature.project_id != project_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project literature not found.")
    evidence = Evidence(project_id=project_id, created_by=user.id, **payload.model_dump())
    db.add(evidence)
    db.flush()
    record_audit_event(db, user.id, "evidence.created", "evidence", evidence.id)
    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/research/projects/{project_id}/evidence", response_model=list[EvidenceOut])
def list_evidence(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Evidence]:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    return list(
        db.scalars(
            select(Evidence).where(Evidence.project_id == project_id).order_by(Evidence.created_at.desc())
        )
    )


@router.get("/search")
def search(
    q: Annotated[str, Query(min_length=2, max_length=200)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    db: Session = Depends(get_db),
) -> dict[str, list[dict]]:
    return SearchService(db).search(q, limit)


@router.get("/science/search")
def science_search(
    q: Annotated[str, Query(min_length=2, max_length=200)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    pattern = f"%{q.strip()}%"
    public_projects = select(ResearchProject.id).where(ResearchProject.visibility == "public")
    entries = db.scalars(
        select(Literature)
        .where(
            Literature.project_id.in_(public_projects),
            or_(Literature.title.ilike(pattern), Literature.authors.ilike(pattern)),
        )
        .order_by(Literature.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "id": str(entry.id),
            "project_id": str(entry.project_id),
            "title": entry.title,
            "authors": entry.authors,
            "publication_year": entry.publication_year,
            "source_url": entry.source_url,
            "doi": entry.doi,
            "source_type": entry.source_type,
            "provenance": entry.provenance,
        }
        for entry in entries
    ]


@router.post("/reports", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Report:
    target_exists = False
    if payload.target_type == "post":
        target_exists = db.get(Post, payload.target_id) is not None
    elif payload.target_type == "comment":
        target_exists = db.get(Comment, payload.target_id) is not None
    elif payload.target_type == "user":
        target_exists = db.get(User, payload.target_id) is not None
    elif payload.target_type == "evidence":
        evidence = db.get(Evidence, payload.target_id)
        if evidence is not None:
            require_project_read(db, user, project_or_404(db, evidence.project_id))
            target_exists = True
    if not target_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report target not found.")
    report = Report(
        reporter_id=user.id,
        target_type=payload.target_type,
        target_id=str(payload.target_id),
        reason=payload.reason,
        details=payload.details,
    )
    db.add(report)
    db.flush()
    record_audit_event(db, user.id, "report.created", "report", report.id)
    db.commit()
    db.refresh(report)
    return report


@router.get("/moderation/queue", response_model=list[ReportOut])
def moderation_queue(
    _: User = Depends(require_roles("admin", "moderator", "scientific_reviewer", "support_operator")),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: Session = Depends(get_db),
) -> list[Report]:
    return list(
        db.scalars(
            select(Report).where(Report.status == "open").order_by(Report.created_at.asc()).limit(limit)
        )
    )


@router.post("/moderation/reports/{report_id}/decision", response_model=ReportOut)
def decide_report(
    report_id: UUID,
    payload: ModerationDecision,
    user: User = Depends(require_roles("admin", "moderator", "scientific_reviewer")),
    db: Session = Depends(get_db),
) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    if report.status != "open":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Report has already been reviewed.")
    if user.role == "scientific_reviewer" and report.target_type != "evidence":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Scientific reviewers can only review evidence reports.")
    if user.role == "support_operator" and report.target_type == "evidence":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Support operators cannot decide scientific evidence reports.")
    report.status = "resolved" if payload.action != "dismiss" else "dismissed"
    report.reviewed_by = user.id
    report.resolution = payload.reason
    if payload.action == "remove" and report.target_type in {"post", "comment"}:
        target = db.get(Post if report.target_type == "post" else Comment, UUID(report.target_id))
        if target is not None:
            target.deleted_at = utc_now()
    if payload.action == "restrict" and report.target_type == "evidence":
        evidence = db.get(Evidence, UUID(report.target_id))
        if evidence is not None:
            evidence.review_status = "needs_review"
    record_audit_event(
        db,
        user.id,
        "moderation.decision",
        "report",
        report.id,
        {"action": payload.action, "reason": payload.reason},
    )
    db.commit()
    db.refresh(report)
    return report


@router.get("/admin/users", response_model=list[AdminUserOut])
def admin_users(
    user: User = Depends(require_roles("admin", "support_operator")),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    q: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
    db: Session = Depends(get_db),
) -> list[AdminUserOut]:
    query = select(User)
    if q is not None:
        pattern = f"%{q.strip()}%"
        query = query.where(User.email.ilike(pattern))
    users = list(db.scalars(query.order_by(User.created_at.desc()).limit(limit).offset(offset)))
    record_audit_event(db, user.id, "admin.users.read", "user_collection", details={"count": len(users)})
    db.commit()
    profiles = {
        profile.user_id: profile
        for profile in db.scalars(select(Profile).where(Profile.user_id.in_([item.id for item in users])))
    }
    return [
        AdminUserOut(
            id=item.id,
            email=item.email,
            role=item.role,
            is_verified=item.is_verified,
            is_active=item.is_active,
            created_at=item.created_at,
            profile=ProfileOut.model_validate(profiles[item.id]) if item.id in profiles else None,
        )
        for item in users
    ]


@router.patch("/admin/users/{user_id}", response_model=AdminUserOut)
def update_admin_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    admin: User = Depends(require_roles("admin", "support_operator")),
    db: Session = Depends(get_db),
) -> AdminUserOut:
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if admin.role == "support_operator" and payload.role is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Support operators cannot change account roles.")
    if admin.role == "support_operator" and target.role == "admin" and payload.is_active is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Support operators cannot suspend administrator accounts.")
    if target.id == admin.id and (
        payload.is_active is False or (payload.role is not None and payload.role != "admin")
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You cannot remove your own administrator access.")
    removes_admin = target.role == "admin" and (
        payload.is_active is False or (payload.role is not None and payload.role != "admin")
    )
    if removes_admin:
        active_admins = db.scalar(
            select(func.count()).select_from(User).where(User.role == "admin", User.is_active.is_(True))
        )
        if active_admins is not None and active_admins <= 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="At least one active administrator is required.")
    if payload.is_active is not None:
        target.is_active = payload.is_active
    if payload.role is not None:
        target.role = payload.role
    record_audit_event(
        db,
        admin.id,
        "admin.user.updated",
        "user",
        target.id,
        {"reason": payload.reason, "is_active": target.is_active, "role": target.role},
    )
    db.commit()
    db.refresh(target)
    profile = db.scalar(select(Profile).where(Profile.user_id == target.id))
    return AdminUserOut(
        id=target.id,
        email=target.email,
        role=target.role,
        is_verified=target.is_verified,
        is_active=target.is_active,
        created_at=target.created_at,
        profile=ProfileOut.model_validate(profile) if profile else None,
    )


@router.get("/admin/reports", response_model=list[ReportOut])
def admin_reports(
    _: User = Depends(require_roles("admin", "moderator", "scientific_reviewer", "support_operator")),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: Session = Depends(get_db),
) -> list[Report]:
    return list(db.scalars(select(Report).order_by(Report.created_at.desc()).limit(limit)))


@router.get("/admin/audit-logs")
def admin_audit_logs(
    user: User = Depends(require_roles("admin", "read_only_auditor")),
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: Session = Depends(get_db),
) -> list[dict]:
    record_audit_event(db, user.id, "admin.audit_logs.read", "audit_event_collection", details={"limit": limit})
    db.commit()
    events = db.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit))
    return [
        {
            "id": str(event.id),
            "actor_id": str(event.actor_id) if event.actor_id else None,
            "action": event.action,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "details": event.details,
            "created_at": event.created_at,
        }
        for event in events
    ]


@router.get("/admin/ai-monitoring")
def admin_ai_monitoring(
    _: User = Depends(require_roles("admin", "read_only_auditor")),
) -> dict[str, str]:
    return {"status": "not_configured", "detail": "No AI provider or AI-run store is configured."}


@router.post("/ai/chat")
@router.post("/ai/research")
def ai_unavailable(_: User = Depends(get_current_user)) -> Response:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="AI is unavailable because no approved provider is configured.",
    )
