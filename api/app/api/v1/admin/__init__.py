"""Admin API (planned, M3): users, organizations, communities, events, moderation, reports,
subscriptions, payments, badges, certifications, ai-monitoring, configuration, audit.

Every administrative permission is enforced by the backend.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])
