from fastapi import APIRouter

from app.api.admin.router import router as admin_router
from app.api.user import router as user_router
from app.api.v1_routes import router as legacy_router

router = APIRouter()
# Admin API first so its richer /admin/* routes win over any legacy stubs with the same path.
router.include_router(admin_router, prefix="/admin")
router.include_router(user_router)
# Legacy MVP routes remain available for backwards compatibility (apps/web, existing clients, tests).
router.include_router(legacy_router)
