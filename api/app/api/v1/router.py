from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.user import router as user_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(user_router)
api_router.include_router(admin_router)
