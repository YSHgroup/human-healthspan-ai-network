from fastapi import APIRouter

from app.ai.router import general_router
from app.api.user.personal import router as personal_router
from app.api.user.researcher import router as researcher_router
from app.api.user.social import router as social_router

router = APIRouter(prefix="/user")
router.include_router(social_router, prefix="/social")
router.include_router(personal_router, prefix="/personal")
router.include_router(researcher_router, prefix="/researcher")
router.include_router(general_router, prefix="/ai/general")
