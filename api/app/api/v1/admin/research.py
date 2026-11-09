"""Administrative researcher, organization, entitlement, event, and audit endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.identity import PlatformAdmin, require_trusted_origin
from app.domains.admin.research import (
    AdminResourceConflict,
    AdminResourceNotFound,
    cancel_research_event,
    decide_organization_request,
    decide_researcher_application,
    grant_user_entitlement,
    has_active_entitlement,
    list_admin_audit_events,
    list_organizations,
    list_pending_organization_requests,
    list_pending_researcher_applications,
    list_research_events,
    list_user_entitlements,
    list_users,
    revoke_user_entitlement,
    set_user_verification,
)
from app.infrastructure.database import get_db
from app.models import ResearchEventRegistration
from app.schemas.admin_research import (
    AdminAuditEventResponse,
    AdminEntitlementResponse,
    AdminOrganizationResponse,
    AdminResearchEventResponse,
    OrganizationRequestDecision,
    OrganizationRequestResponse,
    OrganizationDecisionResponse,
    PlatformUserResponse,
    ResearcherApplicationDecision,
    ResearcherApplicationResponse,
    ResearchEventDecision,
    UserVerificationUpdate,
    EntitlementGrant,
)

router = APIRouter(tags=["admin-research"])


def _raise_admin_error(error: ValueError) -> None:
    if isinstance(error, AdminResourceNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, AdminResourceConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise error


@router.get("/users", response_model=list[PlatformUserResponse])
def platform_users(
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[PlatformUserResponse]:
    return [
        PlatformUserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            email_verified=user.email_verified_at is not None,
            researcher_approved=user.researcher_approved_at is not None,
            organization_creation_entitled=has_active_entitlement(
                db, user.id, "organization_create"
            ),
            created_at=user.created_at,
        )
        for user in list_users(db, limit)
    ]


@router.put("/users/{user_id}/verification", response_model=PlatformUserResponse)
def update_user_verification(
    user_id: str,
    body: UserVerificationUpdate,
    request: Request,
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> PlatformUserResponse:
    require_trusted_origin(request)
    try:
        user = set_user_verification(db, admin, user_id, body.verified)
    except ValueError as error:
        _raise_admin_error(error)
    return PlatformUserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        email_verified=user.email_verified_at is not None,
        researcher_approved=user.researcher_approved_at is not None,
        organization_creation_entitled=has_active_entitlement(
            db, user.id, "organization_create"
        ),
        created_at=user.created_at,
    )


@router.get(
    "/researcher/applications",
    response_model=list[ResearcherApplicationResponse],
)
def researcher_applications(
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> list[ResearcherApplicationResponse]:
    return [
        ResearcherApplicationResponse(
            id=application.id,
            user_id=application.user_id,
            display_name=application.applicant.display_name,
            email=application.applicant.email,
            biography=application.biography,
            research_interests=application.research_interests,
            affiliation=application.affiliation,
            status=application.status,
            created_at=application.created_at,
        )
        for application in list_pending_researcher_applications(db)
    ]


@router.post(
    "/researcher/applications/{application_id}/decision",
    response_model=ResearcherApplicationResponse,
)
def review_researcher_application(
    application_id: str,
    body: ResearcherApplicationDecision,
    request: Request,
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> ResearcherApplicationResponse:
    require_trusted_origin(request)
    try:
        application = decide_researcher_application(db, admin, application_id, body.decision)
    except ValueError as error:
        _raise_admin_error(error)
    return ResearcherApplicationResponse(
        id=application.id,
        user_id=application.user_id,
        display_name=application.applicant.display_name,
        email=application.applicant.email,
        biography=application.biography,
        research_interests=application.research_interests,
        affiliation=application.affiliation,
        status=application.status,
        created_at=application.created_at,
    )


@router.get(
    "/organizations/requests",
    response_model=list[OrganizationRequestResponse],
)
def organization_requests(
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> list[OrganizationRequestResponse]:
    return [
        OrganizationRequestResponse(
            id=request.id,
            requester_id=request.requester_id,
            requester_display_name=request.requester.display_name,
            requester_email=request.requester.email,
            slug=request.slug,
            name=request.name,
            description=request.description,
            website=request.website,
            created_at=request.created_at,
        )
        for request in list_pending_organization_requests(db)
    ]


@router.post(
    "/organizations/requests/{request_id}/decision",
    response_model=OrganizationDecisionResponse,
)
def review_organization_request(
    request_id: str,
    body: OrganizationRequestDecision,
    request: Request,
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> OrganizationDecisionResponse:
    require_trusted_origin(request)
    try:
        creation_request, organization = decide_organization_request(
            db, admin, request_id, body.decision
        )
    except ValueError as error:
        _raise_admin_error(error)
    return OrganizationDecisionResponse(
        id=creation_request.id,
        status=creation_request.status,
        organization_id=organization.id if organization else None,
        reviewed_at=creation_request.reviewed_at,
    )


@router.get("/organizations", response_model=list[AdminOrganizationResponse])
def platform_organizations(
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[AdminOrganizationResponse]:
    return [
        AdminOrganizationResponse(
            id=organization.id,
            slug=organization.slug,
            name=organization.name,
            website=organization.website,
            verification_status=organization.verification_status,
            created_by_id=organization.created_by_id,
            verified_by_id=organization.verified_by_id,
            created_at=organization.created_at,
        )
        for organization in list_organizations(db, limit)
    ]


@router.get("/users/{user_id}/entitlements", response_model=list[AdminEntitlementResponse])
def user_entitlements(
    user_id: str,
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> list[AdminEntitlementResponse]:
    return [
        AdminEntitlementResponse.model_validate(entitlement)
        for entitlement in list_user_entitlements(db, user_id)
    ]


@router.post(
    "/users/{user_id}/entitlements",
    response_model=AdminEntitlementResponse,
    status_code=201,
)
def grant_entitlement(
    user_id: str,
    body: EntitlementGrant,
    request: Request,
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> AdminEntitlementResponse:
    require_trusted_origin(request)
    try:
        entitlement = grant_user_entitlement(
            db, admin, user_id, body.key, body.expires_at
        )
    except ValueError as error:
        _raise_admin_error(error)
    return AdminEntitlementResponse.model_validate(entitlement)


@router.post(
    "/entitlements/{entitlement_id}/revoke",
    response_model=AdminEntitlementResponse,
)
def revoke_entitlement(
    entitlement_id: str,
    request: Request,
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> AdminEntitlementResponse:
    require_trusted_origin(request)
    try:
        entitlement = revoke_user_entitlement(db, admin, entitlement_id)
    except ValueError as error:
        _raise_admin_error(error)
    return AdminEntitlementResponse.model_validate(entitlement)


@router.get("/events", response_model=list[AdminResearchEventResponse])
def administration_research_events(
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[AdminResearchEventResponse]:
    result: list[AdminResearchEventResponse] = []
    for event in list_research_events(db, limit):
        registration_count = db.scalar(
            select(func.count(ResearchEventRegistration.id)).where(
                ResearchEventRegistration.event_id == event.id
            )
        ) or 0
        result.append(
            AdminResearchEventResponse(
                id=event.id,
                organization_id=event.organization_id,
                organization_name=event.organization.name if event.organization else None,
                created_by_id=event.created_by_id,
                title=event.title,
                starts_at=event.starts_at,
                ends_at=event.ends_at,
                status=event.status,
                registration_count=registration_count,
            )
        )
    return result


@router.post(
    "/events/{event_id}/decision",
    response_model=AdminResearchEventResponse,
)
def administer_research_event(
    event_id: str,
    body: ResearchEventDecision,
    request: Request,
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
) -> AdminResearchEventResponse:
    require_trusted_origin(request)
    try:
        event = cancel_research_event(db, admin, event_id)
    except ValueError as error:
        _raise_admin_error(error)
    return AdminResearchEventResponse(
        id=event.id,
        organization_id=event.organization_id,
        organization_name=event.organization.name if event.organization else None,
        created_by_id=event.created_by_id,
        title=event.title,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        status=event.status,
        registration_count=db.scalar(
            select(func.count(ResearchEventRegistration.id)).where(
                ResearchEventRegistration.event_id == event.id
            )
        ) or 0,
    )


@router.get("/audit/events", response_model=list[AdminAuditEventResponse])
def audit_events(
    admin: PlatformAdmin,
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[AdminAuditEventResponse]:
    return [
        AdminAuditEventResponse(
            id=event.id,
            actor_id=event.actor_id,
            actor_email=event.actor.email,
            action=event.action,
            target_type=event.target_type,
            target_id=event.target_id,
            summary=event.summary,
            created_at=event.created_at,
        )
        for event in list_admin_audit_events(db, limit)
    ]
