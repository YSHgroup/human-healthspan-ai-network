"""Social Portal API routes."""

from fastapi import APIRouter

from app.api.v1.user.social.communities import router as communities_router
from app.api.v1.user.social.feed import router as feed_router
from app.api.v1.user.social.messaging import router as messaging_router

router = APIRouter(prefix="/social", tags=["user-social"])
router.include_router(communities_router)
router.include_router(feed_router)
router.include_router(messaging_router)
