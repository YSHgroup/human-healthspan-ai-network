"""User API: one backend area serving the three user portals."""

from fastapi import APIRouter

from app.api.v1.user.ai_chat import router as ai_chat_router
from app.api.v1.user.auth import router as auth_router
from app.api.v1.user.personal import router as personal_router
from app.api.v1.user.researcher import router as researcher_router
from app.api.v1.user.social import router as social_router

router = APIRouter(prefix="/user")
router.include_router(ai_chat_router)
router.include_router(auth_router)
router.include_router(social_router)
router.include_router(personal_router)
router.include_router(researcher_router)
