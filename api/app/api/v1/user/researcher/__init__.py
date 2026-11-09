"""Researcher applications, organizations, projects, tasks, documents, and events."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.identity import CurrentUser, require_trusted_origin
from app.domains.organizations.workflows import (
    OrganizationAccessDenied,
    OrganizationConflict,
    OrganizationNotFound,
    accept_organization_invitation,
    decline_organization_invitation,
    invite_organization_member,
    list_member_organizations,
    list_organization_members,
    list_organization_requests,
    list_pending_invitations,
    organization_invitation_response,
    organization_summary,
    submit_organization_request,
)
from app.domains.researcher.workflows import (
    ResearchAccessDenied,
    ResearchApplicationConflict,
    ResearchResourceConflict,
    ResearchResourceDenied,
    ResearchResourceNotFound,
    can_view_project,
    create_project,
    create_project_document,
    create_project_task,
    create_research_event,
    event_response_data,
    get_project,
    get_researcher_application,
    invite_project_member,
    list_project_activity,
    list_project_documents,
    list_project_members,
    list_project_tasks,
    list_projects,
    list_research_events,
    list_researcher_profiles,
    register_for_research_event,
    require_researcher_access,
    submit_researcher_application,
    update_project_task,
    update_researcher_profile,
)
from app.infrastructure.database import get_db
from app.models import OrganizationInvitation, ResearchEvent, ResearchProject, ResearchTask
from app.schemas.researcher import (
    OrganizationInvitationCreate,
    OrganizationInvitationResponse,
    OrganizationMemberResponse,
    OrganizationRequestCreate,
    OrganizationRequestResponse,
    OrganizationResponse,
    ResearchActivityResponse,
    ResearchDocumentCreate,
    ResearchDocumentResponse,
    ResearchEventCreate,
    ResearchEventResponse,
    ResearcherApplicationCreate,
    ResearcherProfileResponse,
    ResearcherProfileUpdate,
    ResearcherStatusResponse,
    ResearchProjectCreate,
    ResearchProjectMemberCreate,
    ResearchProjectMemberResponse,
    ResearchProjectResponse,
    ResearchTaskCreate,
    ResearchTaskResponse,
    ResearchTaskUpdate,
)

router = APIRouter(prefix="/researcher", tags=["user-researcher"])


def _raise_research_error(error: ValueError) -> None:
    if isinstance(error, (ResearchAccessDenied, ResearchResourceDenied, OrganizationAccessDenied)):
        raise HTTPException(status_code=403, detail=str(error) or "Research access required") from error
    if isinstance(error, (ResearchResourceNotFound, OrganizationNotFound)):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, (ResearchApplicationConflict, ResearchResourceConflict, OrganizationConflict)):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise error


def _project_response(project: ResearchProject) -> ResearchProjectResponse:
    return ResearchProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        community_id=project.community_id,
        owner_id=project.owner_id,
        owner_display_name=project.owner.display_name,
        title=project.title,
        description=project.description,
        objectives=project.objectives,
        research_questions=project.research_questions,
        visibility=project.visibility,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _task_response(task: ResearchTask) -> ResearchTaskResponse:
    return ResearchTaskResponse(
        id=task.id,
        project_id=task.project_id,
        created_by_id=task.created_by_id,
        assignee_id=task.assignee_id,
        assignee_display_name=task.assignee.display_name if task.assignee else None,
        title=task.title,
        description=task.description,
        status=task.status,
        due_at=task.due_at,
        created_at=task.created_at,
    )


@router.get("/me", response_model=ResearcherStatusResponse)
def researcher_status(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearcherStatusResponse:
    application = get_researcher_application(db, user)
    return ResearcherStatusResponse(
        email_verified=user.email_verified_at is not None,
        approved=user.researcher_approved_at is not None,
        application_status=application.status if application else "none",
    )


@router.post(
    "/applications",
    response_model=ResearcherStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def apply_for_researcher_access(
    body: ResearcherApplicationCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearcherStatusResponse:
    require_trusted_origin(request)
    try:
        application = submit_researcher_application(
            db,
            user,
            body.biography,
            body.research_interests,
            body.affiliation,
            body.profile_public,
        )
    except ValueError as error:
        _raise_research_error(error)
    return ResearcherStatusResponse(
        email_verified=user.email_verified_at is not None,
        approved=False,
        application_status=application.status,
    )


@router.put("/profile", response_model=ResearcherStatusResponse)
def edit_researcher_profile(
    body: ResearcherProfileUpdate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearcherStatusResponse:
    require_trusted_origin(request)
    try:
        application = update_researcher_profile(
            db,
            user,
            body.biography,
            body.research_interests,
            body.affiliation,
            body.profile_public,
        )
    except ValueError as error:
        _raise_research_error(error)
    return ResearcherStatusResponse(
        email_verified=True,
        approved=True,
        application_status=application.status,
    )


@router.get("/profile", response_model=ResearcherProfileResponse)
def own_researcher_profile(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearcherProfileResponse:
    application = get_researcher_application(db, user)
    if application is None or application.status != "approved" or user.researcher_approved_at is None:
        raise HTTPException(status_code=403, detail="Approved researcher profile required")
    return ResearcherProfileResponse(
        user_id=user.id,
        display_name=user.display_name,
        biography=application.biography,
        research_interests=application.research_interests,
        affiliation=application.affiliation,
        profile_public=application.profile_public,
    )


@router.get("/profiles", response_model=list[ResearcherProfileResponse])
def researcher_profiles(
    user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ResearcherProfileResponse]:
    try:
        require_researcher_access(user)
    except ValueError as error:
        _raise_research_error(error)
    return [
        ResearcherProfileResponse(
            user_id=profile.id,
            display_name=profile.display_name,
            biography=application.biography,
            research_interests=application.research_interests,
            affiliation=application.affiliation,
            profile_public=application.profile_public,
        )
        for profile, application in list_researcher_profiles(db, limit)
    ]


@router.post(
    "/organizations/requests",
    response_model=OrganizationRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_organization(
    body: OrganizationRequestCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> OrganizationRequestResponse:
    require_trusted_origin(request)
    try:
        result = submit_organization_request(
            db,
            user,
            slug=body.slug,
            name=body.name,
            description=body.description,
            website=body.website,
        )
    except ValueError as error:
        _raise_research_error(error)
    return OrganizationRequestResponse.model_validate(result)


@router.get("/organizations/requests/me", response_model=list[OrganizationRequestResponse])
def my_organization_requests(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[OrganizationRequestResponse]:
    return [OrganizationRequestResponse.model_validate(item) for item in list_organization_requests(db, user)]


@router.get("/organizations", response_model=list[OrganizationResponse])
def my_organizations(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[OrganizationResponse]:
    return [OrganizationResponse(**organization_summary(item)) for item in list_member_organizations(db, user)]


@router.get("/organizations/invitations", response_model=list[OrganizationInvitationResponse])
def my_organization_invitations(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[OrganizationInvitationResponse]:
    return [
        OrganizationInvitationResponse(**organization_invitation_response(invitation))
        for invitation in list_pending_invitations(db, user)
    ]


@router.post("/organizations/invitations/{invitation_id}/accept", status_code=status.HTTP_204_NO_CONTENT)
def accept_organization_invite(
    invitation_id: str,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> None:
    require_trusted_origin(request)
    try:
        accept_organization_invitation(db, user, invitation_id)
    except ValueError as error:
        _raise_research_error(error)


@router.post("/organizations/invitations/{invitation_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
def decline_organization_invite(
    invitation_id: str,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> None:
    require_trusted_origin(request)
    try:
        decline_organization_invitation(db, user, invitation_id)
    except ValueError as error:
        _raise_research_error(error)


@router.post(
    "/organizations/{organization_id}/invitations",
    response_model=OrganizationInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def invite_organization_user(
    organization_id: str,
    body: OrganizationInvitationCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> OrganizationInvitationResponse:
    require_trusted_origin(request)
    try:
        invitation = invite_organization_member(
            db, user, organization_id, body.email, body.role
        )
    except ValueError as error:
        _raise_research_error(error)
    invitation = db.query(OrganizationInvitation).filter_by(id=invitation.id).one()
    return OrganizationInvitationResponse(**organization_invitation_response(invitation))


@router.get(
    "/organizations/{organization_id}/members",
    response_model=list[OrganizationMemberResponse],
)
def organization_members(
    organization_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[OrganizationMemberResponse]:
    try:
        members = list_organization_members(db, user, organization_id)
    except ValueError as error:
        _raise_research_error(error)
    return [
        OrganizationMemberResponse(
            user_id=membership.user.id,
            display_name=membership.user.display_name,
            email=membership.user.email,
            role=membership.role,
            joined_at=membership.joined_at,
        )
        for membership in members
    ]


@router.get("/projects", response_model=list[ResearchProjectResponse])
def researcher_projects(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ResearchProjectResponse]:
    try:
        projects = list_projects(db, user)
    except ValueError as error:
        _raise_research_error(error)
    return [_project_response(project) for project in projects]


@router.post(
    "/projects",
    response_model=ResearchProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research_project(
    body: ResearchProjectCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearchProjectResponse:
    require_trusted_origin(request)
    try:
        project = create_project(
            db,
            user,
            organization_id=body.organization_id,
            community_id=body.community_id,
            title=body.title,
            description=body.description,
            objectives=body.objectives,
            research_questions=body.research_questions,
            visibility=body.visibility,
        )
    except ValueError as error:
        _raise_research_error(error)
    return _project_response(project)


@router.get("/projects/{project_id}", response_model=ResearchProjectResponse)
def researcher_project(
    project_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearchProjectResponse:
    try:
        project = get_project(db, project_id)
        if not can_view_project(db, project, user):
            raise ResearchResourceDenied
    except ValueError as error:
        _raise_research_error(error)
    return _project_response(project)


@router.post(
    "/projects/{project_id}/members",
    response_model=ResearchProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_research_project_member(
    project_id: str,
    body: ResearchProjectMemberCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearchProjectMemberResponse:
    require_trusted_origin(request)
    try:
        membership = invite_project_member(db, project_id, user, body.email)
    except ValueError as error:
        _raise_research_error(error)
    return ResearchProjectMemberResponse(
        user_id=membership.user.id,
        display_name=membership.user.display_name,
        role=membership.role,
        joined_at=membership.joined_at,
    )


@router.get(
    "/projects/{project_id}/members",
    response_model=list[ResearchProjectMemberResponse],
)
def research_project_members(
    project_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ResearchProjectMemberResponse]:
    try:
        members = list_project_members(db, project_id, user)
    except ValueError as error:
        _raise_research_error(error)
    return [
        ResearchProjectMemberResponse(
            user_id=member.user.id,
            display_name=member.user.display_name,
            role=member.role,
            joined_at=member.joined_at,
        )
        for member in members
    ]


@router.get("/projects/{project_id}/tasks", response_model=list[ResearchTaskResponse])
def project_tasks(
    project_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ResearchTaskResponse]:
    try:
        tasks = list_project_tasks(db, project_id, user)
    except ValueError as error:
        _raise_research_error(error)
    return [_task_response(task) for task in tasks]


@router.post(
    "/projects/{project_id}/tasks",
    response_model=ResearchTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_task(
    project_id: str,
    body: ResearchTaskCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearchTaskResponse:
    require_trusted_origin(request)
    try:
        task = create_project_task(
            db,
            project_id,
            user,
            body.title,
            body.description,
            body.assignee_email,
            body.due_at,
        )
    except ValueError as error:
        _raise_research_error(error)
    return _task_response(task)


@router.patch(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=ResearchTaskResponse,
)
def change_project_task_status(
    project_id: str,
    task_id: str,
    body: ResearchTaskUpdate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearchTaskResponse:
    require_trusted_origin(request)
    try:
        task = update_project_task(db, project_id, task_id, user, body.status)
    except ValueError as error:
        _raise_research_error(error)
    return _task_response(task)


@router.get("/projects/{project_id}/documents", response_model=list[ResearchDocumentResponse])
def project_documents(
    project_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ResearchDocumentResponse]:
    try:
        documents = list_project_documents(db, project_id, user)
    except ValueError as error:
        _raise_research_error(error)
    return [ResearchDocumentResponse.model_validate(document) for document in documents]


@router.post(
    "/projects/{project_id}/documents",
    response_model=ResearchDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def attach_project_document(
    project_id: str,
    body: ResearchDocumentCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearchDocumentResponse:
    require_trusted_origin(request)
    try:
        document = create_project_document(
            db,
            project_id,
            user,
            body.title,
            body.filename,
            body.content,
            body.access_scope,
        )
    except ValueError as error:
        _raise_research_error(error)
    return ResearchDocumentResponse.model_validate(document)


@router.get(
    "/projects/{project_id}/activity",
    response_model=list[ResearchActivityResponse],
)
def project_activity(
    project_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ResearchActivityResponse]:
    try:
        activities = list_project_activity(db, project_id, user, limit)
    except ValueError as error:
        _raise_research_error(error)
    return [
        ResearchActivityResponse(
            id=activity.id,
            actor_id=activity.actor_id,
            actor_display_name=activity.actor.display_name,
            action=activity.action,
            summary=activity.summary,
            occurred_at=activity.occurred_at,
        )
        for activity in activities
    ]


@router.get("/events", response_model=list[ResearchEventResponse])
def research_events(
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[ResearchEventResponse]:
    try:
        events = list_research_events(db, user)
    except ValueError as error:
        _raise_research_error(error)
    return [
        ResearchEventResponse(**event_response_data(db, event, user))
        for event in events
    ]


@router.post(
    "/events",
    response_model=ResearchEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    body: ResearchEventCreate,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> ResearchEventResponse:
    require_trusted_origin(request)
    try:
        event = create_research_event(
            db,
            user,
            organization_id=body.organization_id,
            title=body.title,
            description=body.description,
            location=body.location,
            starts_at=body.starts_at,
            ends_at=body.ends_at,
        )
    except ValueError as error:
        _raise_research_error(error)
    event = db.query(ResearchEvent).filter_by(id=event.id).first()
    if event is None:
        raise HTTPException(status_code=500, detail="Created event could not be loaded")
    return ResearchEventResponse(**event_response_data(db, event, user))


@router.post("/events/{event_id}/registration", status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: str,
    request: Request,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    require_trusted_origin(request)
    try:
        registration = register_for_research_event(db, event_id, user)
    except ValueError as error:
        _raise_research_error(error)
    return {"event_id": registration.event_id, "status": "registered"}
