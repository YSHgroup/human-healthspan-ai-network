import re
from typing import Final
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import User
from app.models.platform import Badge, Organization, OrganizationMember

ROLE_ORDER: Final[tuple[str, ...]] = (
    "founder",
    "owner",
    "administrator",
    "research_leader",
    "researcher",
    "contributor",
    "member",
)
MANAGE_ROLES: Final[frozenset[str]] = frozenset({"founder", "owner", "administrator"})
LEAD_ROLES: Final[frozenset[str]] = MANAGE_ROLES | {"research_leader"}
RESEARCH_ROLES: Final[frozenset[str]] = LEAD_ROLES | {"researcher"}
DEFAULT_BADGES: Final[tuple[tuple[str, str, str], ...]] = (
    ("contributor", "Contributor", "Contributes to this organization's work."),
    ("core-contributor", "Core Contributor", "Sustained, verified contribution to this organization."),
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:60] or "organization"


def unique_slug(db: Session, name: str) -> str:
    base = slugify(name)
    candidate, counter = base, 2
    while db.scalar(select(Organization.id).where(Organization.slug == candidate)) is not None:
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def membership(db: Session, organization_id: UUID, user_id: UUID) -> OrganizationMember | None:
    return db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
    )


def organization_or_404(db: Session, organization_id: UUID) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None or not organization.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    return organization


def require_member(
    db: Session, user: User, organization_id: UUID, roles: frozenset[str] | None = None
) -> OrganizationMember:
    """Org data isolation: non-members get 404 (existence is not revealed), wrong role gets 403."""
    organization_or_404(db, organization_id)
    member = membership(db, organization_id, user.id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")
    if roles is not None and member.role not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your organization role does not allow this.")
    return member


def create_default_badges(db: Session, organization: Organization) -> list[Badge]:
    badges = [
        Badge(
            slug=f"{organization.slug}-{suffix}",
            name=f"{organization.name} {label}",
            description=description,
            kind="organization_contributor",
            organization_id=organization.id,
        )
        for suffix, label, description in DEFAULT_BADGES
    ]
    db.add_all(badges)
    db.flush()
    return badges
