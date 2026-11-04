"""Social Portal routes (planned, M2): feed, posts, comments, reactions, communities, discussions, events, invitations, notifications, connections."""

from fastapi import APIRouter

router = APIRouter(prefix="/social", tags=["user-social"])
