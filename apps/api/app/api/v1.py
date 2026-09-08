from fastapi import APIRouter
from app.api.v1_routes import router as domain_router

router = APIRouter()
router.include_router(domain_router)
