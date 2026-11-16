"""Researcher access, project collaboration, and research-event workflows."""

from datetime import datetime, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.domains.organizations.workflows import get_active_organization_membership
from app.models import (
    CommunityMembership,
    OrganizationMembership,
    ResearchActivity,
    ResearchDocument,
    ResearchEvent,
    ResearchEventRegistration,
    ResearchProject,
    ResearchProjectMember,
    ResearchTask,
    ResearcherApplication,
    User,
)


class ResearcherWorkflowError(ValueError):
    pass


class ResearchAccessDenied(ResearcherWorkflowError):
    pass


class ResearchApplicationConflict(ResearcherWorkflowError):
    pass


class ResearchResourceNotFound(ResearcherWorkflowError):
    pass


class ResearchResourceDenied(ResearcherWorkflowError):
    pass


class ResearchResourceConflict(ResearcherWorkflowError):
    pass


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def has_researcher_access(user: User) -> bool:
    return user.email_verified_at is not None and user.researcher_approved_at is not None


def require_researcher_access(user: User) -> None:
    if not has_researcher_access(user):
        raise ResearchAccessDenied


def get_researcher_application(db: Session, user: User) -> ResearcherApplication | None:
    return db.scalar(
        select(ResearcherApplication).where(ResearcherApplication.user_id == user.id)
    )


def submit_researcher_application(
    db: Session,
    user: User,
    biography: str,
    research_interests: str,
    affiliation: str | None,
    profile_public: bool,
) -> ResearcherApplication:
    if user.email_verified_at is None:
        raise ResearchAccessDenied("Verified email is required to apply")
    if user.researcher_approved_at is not None:
        raise ResearchApplicationConflict("Researcher access has already been approved")

    application = get_researcher_application(db, user)
    if application is not None and application.status == "pending":
        raise ResearchApplicationConflict("A researcher application is already pending")
    if application is None:
        application = ResearcherApplication(
            user_id=user.id,
            biography=biography.strip(),
            research_interests=research_interests.strip(),
            affiliation=affiliation.strip() if affiliation else None,
            profile_public=profile_public,
        )
        db.add(application)
    else:
        application.biography = biography.strip()
        application.research_interests = research_interests.strip()
        application.affiliation = affiliation.strip() if affiliation else None
        application.profile_public = profile_public
        application.status = "pending"
        application.created_at = datetime.now(timezone.utc)
        application.reviewed_at = None
        application.reviewed_by_id = None
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ResearchApplicationConflict("A researcher application is already pending") from exc
    db.refresh(application)
    return application


def list_researcher_profiles(db: Session, limit: int) -> list[tuple[User, ResearcherApplication]]:
    return list(
        db.execute(
            select(User, ResearcherApplication)
            .join(ResearcherApplication, ResearcherApplication.user_id == User.id)
            .where(
                ResearcherApplication.status == "approved",
                ResearcherApplication.profile_public.is_(True),
                User.email_verified_at.is_not(None),
                User.researcher_approved_at.is_not(None),
            )
            .order_by(User.display_name, User.id)
            .limit(limit)
        ).all()
    )


def update_researcher_profile(
    db: Session,
    user: User,
    biography: str,
    research_interests: str,
    affiliation: str | None,
    profile_public: bool,
) -> ResearcherApplication:
    require_researcher_access(user)
    application = get_researcher_application(db, user)
    if application is None or application.status != "approved":
        raise ResearchAccessDenied("Approved researcher profile not found")
    application.biography = biography.strip()
    application.research_interests = research_interests.strip()
    application.affiliation = affiliation.strip() if affiliation else None
    application.profile_public = profile_public
    db.commit()
    db.refresh(application)
    return application


def create_project(
    db: Session,
    owner: User,
    *,
    organization_id: str | None,
    community_id: str | None,
    title: str,
    description: str,
    objectives: str,
    research_questions: str,
    visibility: str,
) -> ResearchProject:
    require_researcher_access(owner)
    if organization_id is not None and get_active_organization_membership(
        db, organization_id, owner.id
    ) is None:
        raise ResearchResourceDenied("Active organization membership is required")
    if visibility == "community":
        if community_id is None:
            raise ResearchResourceConflict("Community visibility requires a community")
        community_membership = db.scalar(
            select(CommunityMembership).where(
                CommunityMembership.community_id == community_id,
                CommunityMembership.user_id == owner.id,
                CommunityMembership.status == "active",
            )
        )
        if community_membership is None:
            raise ResearchResourceDenied("Active community membership is required")
    elif community_id is not None:
        raise ResearchResourceConflict("A community can only be set for community visibility")

    project = ResearchProject(
        organization_id=organization_id,
        community_id=community_id,
        owner_id=owner.id,
        title=title.strip(),
        description=description.strip(),
        objectives=objectives.strip(),
        research_questions=research_questions.strip(),
        visibility=visibility,
    )
    db.add(project)
    db.flush()
    db.add(
        ResearchProjectMember(
            project_id=project.id,
            user_id=owner.id,
            role="owner",
            status="active",
            invited_by_id=owner.id,
        )
    )
    _record_activity(db, project.id, owner.id, "project_created", f"Created project {project.title}")
    db.commit()
    db.refresh(project)
    return project


def _record_activity(db: Session, project_id: str, actor_id: str, action: str, summary: str) -> None:
    db.add(
        ResearchActivity(
            project_id=project_id,
            actor_id=actor_id,
            action=action,
            summary=summary[:500],
        )
    )


def _project_member(db: Session, project_id: str, user_id: str) -> ResearchProjectMember | None:
    return db.scalar(
        select(ResearchProjectMember).where(
            ResearchProjectMember.project_id == project_id,
            ResearchProjectMember.user_id == user_id,
            ResearchProjectMember.status == "active",
        )
    )


def get_project(db: Session, project_id: str) -> ResearchProject:
    project = db.scalar(
        select(ResearchProject)
        .options(joinedload(ResearchProject.owner))
        .where(ResearchProject.id == project_id)
    )
    if project is None:
        raise ResearchResourceNotFound("Project not found")
    return project


def can_view_project(db: Session, project: ResearchProject, user: User) -> bool:
    if not has_researcher_access(user):
        return False
    if project.organization_id is not None and get_active_organization_membership(
        db, project.organization_id, user.id
    ) is None:
        return False
    if _project_member(db, project.id, user.id) is not None:
        return True
    if project.visibility == "public":
        return True
    if project.visibility == "community" and project.community_id:
        return db.scalar(
            select(CommunityMembership.id).where(
                CommunityMembership.community_id == project.community_id,
                CommunityMembership.user_id == user.id,
                CommunityMembership.status == "active",
            )
        ) is not None
    return False


def require_project_member(db: Session, project: ResearchProject, user: User) -> None:
    if not can_view_project(db, project, user) or _project_member(db, project.id, user.id) is None:
        raise ResearchResourceDenied("Active project membership is required")


def list_projects(db: Session, user: User) -> list[ResearchProject]:
    require_researcher_access(user)
    project_ids = select(ResearchProjectMember.project_id).where(
        ResearchProjectMember.user_id == user.id,
        ResearchProjectMember.status == "active",
    )
    organization_ids = select(OrganizationMembership.organization_id).where(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.status == "active",
    )
    community_ids = select(CommunityMembership.community_id).where(
        CommunityMembership.user_id == user.id,
        CommunityMembership.status == "active",
    )
    return list(
        db.scalars(
            select(ResearchProject)
            .options(joinedload(ResearchProject.owner))
            .where(
                or_(
                    and_(
                        ResearchProject.organization_id.is_(None),
                        or_(
                            ResearchProject.owner_id == user.id,
                            ResearchProject.id.in_(project_ids),
                            ResearchProject.visibility == "public",
                            and_(
                                ResearchProject.visibility == "community",
                                ResearchProject.community_id.in_(community_ids),
                            ),
                        ),
                    ),
                    and_(
                        ResearchProject.organization_id.is_not(None),
                        ResearchProject.organization_id.in_(organization_ids),
                        or_(
                            ResearchProject.owner_id == user.id,
                            ResearchProject.id.in_(project_ids),
                        ),
                    ),
                )
            )
            .order_by(ResearchProject.updated_at.desc(), ResearchProject.id)
        ).unique().all()
    )


def invite_project_member(
    db: Session,
    project_id: str,
    inviter: User,
    email: str,
) -> ResearchProjectMember:
    require_researcher_access(inviter)
    project = get_project(db, project_id)
    if project.owner_id != inviter.id:
        raise ResearchResourceDenied("Only the project owner can add project members")
    if project.organization_id is not None and get_active_organization_membership(
        db, project.organization_id, inviter.id
    ) is None:
        raise ResearchResourceDenied("Active organization membership is required")
    normalized_email = email.strip().casefold()
    invitee = db.scalar(select(User).where(func.lower(User.email) == normalized_email))
    if invitee is None or not has_researcher_access(invitee):
        raise ResearchResourceNotFound("Approved researcher account not found")
    if project.organization_id is not None and get_active_organization_membership(
        db, project.organization_id, invitee.id
    ) is None:
        raise ResearchResourceDenied("Invitee must be an active organization member")
    if _project_member(db, project.id, invitee.id) is not None:
        raise ResearchResourceConflict("User is already a project member")
    membership = ResearchProjectMember(
        project_id=project.id,
        user_id=invitee.id,
        role="contributor",
        status="active",
        invited_by_id=inviter.id,
    )
    db.add(membership)
    _record_activity(db, project.id, inviter.id, "member_added", f"Added {invitee.display_name} to the project")
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ResearchResourceConflict("User is already a project member") from exc
    db.refresh(membership)
    return membership


def list_project_members(db: Session, project_id: str, user: User) -> list[ResearchProjectMember]:
    project = get_project(db, project_id)
    require_project_member(db, project, user)
    return list(
        db.scalars(
            select(ResearchProjectMember)
            .options(joinedload(ResearchProjectMember.user))
            .where(
                ResearchProjectMember.project_id == project_id,
                ResearchProjectMember.status == "active",
            )
            .order_by(ResearchProjectMember.joined_at, ResearchProjectMember.id)
        ).unique().all()
    )


def list_project_tasks(db: Session, project_id: str, user: User) -> list[ResearchTask]:
    project = get_project(db, project_id)
    require_project_member(db, project, user)
    return list(
        db.scalars(
            select(ResearchTask)
            .options(joinedload(ResearchTask.assignee))
            .where(ResearchTask.project_id == project_id)
            .order_by(ResearchTask.created_at, ResearchTask.id)
        ).unique().all()
    )


def create_project_task(
    db: Session,
    project_id: str,
    creator: User,
    title: str,
    description: str,
    assignee_email: str | None,
    due_at: datetime | None,
) -> ResearchTask:
    project = get_project(db, project_id)
    require_project_member(db, project, creator)
    assignee = None
    if assignee_email:
        assignee = db.scalar(
            select(User).where(func.lower(User.email) == assignee_email.strip().casefold())
        )
        if assignee is None or _project_member(db, project.id, assignee.id) is None:
            raise ResearchResourceDenied("Task assignee must be an active project member")
    task = ResearchTask(
        project_id=project.id,
        created_by_id=creator.id,
        assignee_id=assignee.id if assignee else None,
        title=title.strip(),
        description=description.strip(),
        due_at=due_at,
    )
    db.add(task)
    db.flush()
    _record_activity(db, project.id, creator.id, "task_created", f"Created task {task.title}")
    db.commit()
    db.refresh(task)
    if task.assignee_id:
        db.refresh(task, attribute_names=["assignee"])
    return task


def update_project_task(
    db: Session,
    project_id: str,
    task_id: str,
    user: User,
    status: str,
) -> ResearchTask:
    project = get_project(db, project_id)
    require_project_member(db, project, user)
    task = db.scalar(
        select(ResearchTask)
        .options(joinedload(ResearchTask.assignee))
        .where(ResearchTask.project_id == project.id, ResearchTask.id == task_id)
    )
    if task is None:
        raise ResearchResourceNotFound("Task not found")
    task.status = status
    _record_activity(db, project.id, user.id, "task_updated", f"Updated task {task.title} to {status}")
    db.commit()
    db.refresh(task)
    return task


def create_project_document(
    db: Session,
    project_id: str,
    uploader: User,
    title: str,
    filename: str,
    content: str,
    access_scope: str,
) -> ResearchDocument:
    project = get_project(db, project_id)
    require_project_member(db, project, uploader)
    document = ResearchDocument(
        project_id=project.id,
        uploaded_by_id=uploader.id,
        title=title.strip(),
        filename=filename.strip(),
        content=content,
        access_scope=access_scope,
    )
    db.add(document)
    db.flush()
    _record_activity(db, project.id, uploader.id, "document_added", f"Added document {document.title}")
    db.commit()
    db.refresh(document)
    return document


def create_project_file_document(
    db: Session,
    project_id: str,
    uploader: User,
    title: str,
    filename: str,
    access_scope: str,
    storage_key: str,
    media_type: str,
    file_size: int,
    sha256: str,
) -> ResearchDocument:
    project = get_project(db, project_id)
    require_project_member(db, project, uploader)
    document = ResearchDocument(
        project_id=project.id,
        uploaded_by_id=uploader.id,
        title=title.strip(),
        filename=filename,
        content="",
        access_scope=access_scope,
        file_storage_key=storage_key,
        media_type=media_type,
        file_size=file_size,
        sha256=sha256,
    )
    db.add(document)
    db.flush()
    _record_activity(db, project.id, uploader.id, "document_added", f"Uploaded document {document.title}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(document)
    return document


def require_project_document_upload_access(
    db: Session,
    project_id: str,
    user: User,
) -> None:
    project = get_project(db, project_id)
    require_project_member(db, project, user)


def get_project_file_document(
    db: Session,
    project_id: str,
    document_id: str,
    user: User,
) -> ResearchDocument:
    project = get_project(db, project_id)
    document = db.scalar(
        select(ResearchDocument).where(
            ResearchDocument.id == document_id,
            ResearchDocument.project_id == project.id,
            ResearchDocument.file_storage_key.is_not(None),
        )
    )
    if document is None:
        raise ResearchResourceNotFound("Document not found")
    if not can_view_project(db, project, user):
        raise ResearchResourceNotFound("Document not found")
    if document.access_scope == "private" and (
        document.uploaded_by_id != user.id and project.owner_id != user.id
    ):
        raise ResearchResourceNotFound("Document not found")
    if document.access_scope == "project" and _project_member(db, project.id, user.id) is None:
        raise ResearchResourceNotFound("Document not found")
    return document


def list_project_documents(
    db: Session,
    project_id: str,
    user: User,
) -> list[ResearchDocument]:
    project = get_project(db, project_id)
    if not can_view_project(db, project, user):
        raise ResearchResourceDenied
    documents = db.scalars(
        select(ResearchDocument)
        .where(ResearchDocument.project_id == project.id)
        .order_by(ResearchDocument.created_at, ResearchDocument.id)
    ).all()
    return [
        document
        for document in documents
        if (
            document.access_scope == "project"
            and _project_member(db, project.id, user.id) is not None
        )
        or document.uploaded_by_id == user.id
        or project.owner_id == user.id
    ]


def list_project_activity(
    db: Session,
    project_id: str,
    user: User,
    limit: int,
) -> list[ResearchActivity]:
    project = get_project(db, project_id)
    if not can_view_project(db, project, user):
        raise ResearchResourceDenied
    return list(
        db.scalars(
            select(ResearchActivity)
            .options(joinedload(ResearchActivity.actor))
            .where(ResearchActivity.project_id == project.id)
            .order_by(ResearchActivity.occurred_at.desc(), ResearchActivity.id)
            .limit(limit)
        ).unique().all()
    )


def create_research_event(
    db: Session,
    creator: User,
    *,
    organization_id: str | None,
    title: str,
    description: str,
    location: str,
    starts_at: datetime,
    ends_at: datetime,
) -> ResearchEvent:
    require_researcher_access(creator)
    if starts_at.tzinfo is None or ends_at.tzinfo is None:
        raise ResearchResourceConflict("Event times must include a timezone")
    now = datetime.now(timezone.utc)
    if starts_at <= now or ends_at <= starts_at:
        raise ResearchResourceConflict("Event must start in the future and end after it starts")
    if organization_id is not None and get_active_organization_membership(
        db, organization_id, creator.id
    ) is None:
        raise ResearchResourceDenied("Active organization membership is required")
    event = ResearchEvent(
        organization_id=organization_id,
        created_by_id=creator.id,
        title=title.strip(),
        description=description.strip(),
        location=location.strip(),
        starts_at=starts_at,
        ends_at=ends_at,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_research_events(db: Session, user: User) -> list[ResearchEvent]:
    statement = select(ResearchEvent).options(joinedload(ResearchEvent.organization)).where(
        ResearchEvent.status == "published"
    )
    if not has_researcher_access(user):
        raise ResearchAccessDenied
    organization_ids = select(OrganizationMembership.organization_id).where(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.status == "active",
    )
    statement = statement.where(
        (ResearchEvent.organization_id.is_(None))
        | ResearchEvent.organization_id.in_(organization_ids)
    )
    return list(db.scalars(statement.order_by(ResearchEvent.starts_at, ResearchEvent.id)).unique().all())


def register_for_research_event(db: Session, event_id: str, user: User) -> ResearchEventRegistration:
    require_researcher_access(user)
    event = db.get(ResearchEvent, event_id)
    if event is None or event.status != "published":
        raise ResearchResourceNotFound("Research event not found")
    if event.organization_id is not None and get_active_organization_membership(
        db, event.organization_id, user.id
    ) is None:
        raise ResearchResourceDenied("Active organization membership is required")
    if _as_utc(event.starts_at) <= datetime.now(timezone.utc):
        raise ResearchResourceConflict("Registration for this event is closed")
    registration = ResearchEventRegistration(event_id=event.id, user_id=user.id)
    db.add(registration)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ResearchResourceConflict("You are already registered for this event") from exc
    db.refresh(registration)
    return registration


def event_response_data(db: Session, event: ResearchEvent, user: User) -> dict[str, object]:
    registration_count = db.scalar(
        select(func.count(ResearchEventRegistration.id)).where(
            ResearchEventRegistration.event_id == event.id
        )
    ) or 0
    registered = db.scalar(
        select(ResearchEventRegistration.id).where(
            ResearchEventRegistration.event_id == event.id,
            ResearchEventRegistration.user_id == user.id,
        )
    ) is not None
    return {
        "id": event.id,
        "organization_id": event.organization_id,
        "organization_name": event.organization.name if event.organization else None,
        "created_by_id": event.created_by_id,
        "title": event.title,
        "description": event.description,
        "location": event.location,
        "starts_at": event.starts_at,
        "ends_at": event.ends_at,
        "status": event.status,
        "registration_count": registration_count,
        "registered": registered,
    }
