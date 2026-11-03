from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_optional_current_user
from app.db.base import utc_now
from app.db.session import get_db
from app.domains.notifications.service import notify
from app.domains.organizations.service import LEAD_ROLES, membership
from app.domains.subscriptions.service import has_feature
from app.models.domain import Community, CommunityMember, Post, User
from app.models.platform import Event, EventInvitation, EventRegistration
from app.schemas.platform import EventCreate, EventInvite, EventOut
from app.services.audit import record_audit_event

router = APIRouter(tags=["events"])


def _visible_filter(user: User | None):
    public = Event.visibility == "public"
    if user is None:
        return public
    member_communities = select(CommunityMember.community_id).where(CommunityMember.user_id == user.id)
    invited = select(EventInvitation.event_id).where(EventInvitation.user_id == user.id)
    return or_(
        public,
        and_(Event.visibility == "community", Event.community_id.in_(member_communities)),
        and_(Event.visibility == "invited", Event.id.in_(invited)),
        Event.organizer_id == user.id,
    )


def _event_out(db: Session, event: Event, user: User | None) -> EventOut:
    registered = db.scalar(
        select(func.count()).select_from(EventRegistration).where(
            EventRegistration.event_id == event.id, EventRegistration.status == "registered"
        )
    ) or 0
    is_registered = user is not None and db.scalar(
        select(EventRegistration.id).where(
            EventRegistration.event_id == event.id,
            EventRegistration.user_id == user.id,
            EventRegistration.status == "registered",
        )
    ) is not None
    out = EventOut.model_validate(event)
    out.registered_count = registered
    out.is_registered = bool(is_registered)
    return out


def _visible_event_or_404(db: Session, user: User | None, event_id: UUID) -> Event:
    event = db.scalar(select(Event).where(Event.id == event_id, _visible_filter(user)))
    if event is None or (event.status == "removed" and (user is None or event.organizer_id != user.id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")
    return event


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EventOut:
    if not has_feature(db, "user", user.id, "event.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creating events is a premium feature. An active plan or entitlement is required.",
        )
    if payload.community_id is not None:
        community = db.get(Community, payload.community_id)
        is_member = db.scalar(
            select(CommunityMember.id).where(
                CommunityMember.community_id == payload.community_id, CommunityMember.user_id == user.id
            )
        )
        if community is None or not community.is_active or is_member is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Join the community before hosting an event in it.")
    if payload.organization_id is not None:
        member = membership(db, payload.organization_id, user.id)
        if member is None or member.role not in LEAD_ROLES:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only organization leaders can host organization events.")
    event = Event(organizer_id=user.id, **payload.model_dump())
    db.add(event)
    db.flush()
    announcement = Post(
        author_id=user.id,
        community_id=payload.community_id,
        body=f"Event: {payload.title}\n\n{payload.description}".strip(),
        content_type="post",
        classification="opinion",
    )
    db.add(announcement)
    db.flush()
    event.discussion_post_id = announcement.id
    record_audit_event(db, user.id, "event.created", "event", event.id)
    db.commit()
    db.refresh(event)
    return _event_out(db, event, user)


@router.get("", response_model=list[EventOut])
def list_events(
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
    include_past: bool = False,
    community_id: UUID | None = None,
    mine: bool = False,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> list[EventOut]:
    query = select(Event).where(_visible_filter(user), Event.status == "scheduled")
    if not include_past:
        query = query.where(Event.starts_at >= utc_now() - timedelta(days=1))
    if community_id is not None:
        query = query.where(Event.community_id == community_id)
    if mine:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required.")
        registered = select(EventRegistration.event_id).where(
            EventRegistration.user_id == user.id, EventRegistration.status == "registered"
        )
        query = query.where(or_(Event.organizer_id == user.id, Event.id.in_(registered)))
    events = db.scalars(query.order_by(Event.starts_at.asc()).limit(limit).offset(offset))
    return [_event_out(db, event, user) for event in events]


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: UUID,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> EventOut:
    return _event_out(db, _visible_event_or_404(db, user, event_id), user)


@router.post("/{event_id}/register", response_model=EventOut)
def register_for_event(
    event_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EventOut:
    event = _visible_event_or_404(db, user, event_id)
    if event.status != "scheduled":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This event is not open for registration.")
    existing = db.scalar(
        select(EventRegistration).where(EventRegistration.event_id == event_id, EventRegistration.user_id == user.id)
    )
    if existing is None or existing.status != "registered":
        registered = db.scalar(
            select(func.count()).select_from(EventRegistration).where(
                EventRegistration.event_id == event_id, EventRegistration.status == "registered"
            )
        ) or 0
        if event.capacity is not None and registered >= event.capacity:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This event is full.")
        if existing is None:
            db.add(EventRegistration(event_id=event_id, user_id=user.id))
        else:
            existing.status = "registered"
        notify(db, event.organizer_id, "event.registration", "New event registration", event.title, "event", event.id, user.id)
        record_audit_event(db, user.id, "event.registered", "event", event.id)
        db.commit()
    return _event_out(db, event, user)


@router.delete("/{event_id}/register", response_model=EventOut)
def cancel_registration(
    event_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EventOut:
    event = _visible_event_or_404(db, user, event_id)
    existing = db.scalar(
        select(EventRegistration).where(EventRegistration.event_id == event_id, EventRegistration.user_id == user.id)
    )
    if existing is not None and existing.status == "registered":
        existing.status = "cancelled"
        record_audit_event(db, user.id, "event.registration_cancelled", "event", event.id)
        db.commit()
    return _event_out(db, event, user)


@router.post("/{event_id}/invitations", status_code=status.HTTP_204_NO_CONTENT)
def invite_to_event(
    event_id: UUID,
    payload: EventInvite,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    event = _visible_event_or_404(db, user, event_id)
    if event.organizer_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the organizer can invite members.")
    target = db.get(User, payload.user_id)
    if target is None or not target.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if db.scalar(
        select(EventInvitation.id).where(EventInvitation.event_id == event_id, EventInvitation.user_id == target.id)
    ) is None:
        db.add(EventInvitation(event_id=event_id, user_id=target.id, invited_by=user.id))
        notify(db, target.id, "event.invitation", "You were invited to an event", event.title, "event", event.id, user.id)
        record_audit_event(db, user.id, "event.invited", "event", event.id, {"invited": str(target.id)})
        db.commit()


@router.delete("/{event_id}", response_model=EventOut)
def cancel_event(
    event_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EventOut:
    event = _visible_event_or_404(db, user, event_id)
    if event.organizer_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the organizer can cancel this event.")
    if event.status == "scheduled":
        event.status = "cancelled"
        registrants = db.scalars(
            select(EventRegistration.user_id).where(
                EventRegistration.event_id == event_id, EventRegistration.status == "registered"
            )
        )
        for registrant in registrants:
            notify(db, registrant, "event.cancelled", "An event you registered for was cancelled", event.title, "event", event.id, user.id)
        record_audit_event(db, user.id, "event.cancelled", "event", event.id)
        db.commit()
    return _event_out(db, event, user)
