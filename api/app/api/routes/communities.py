from fastapi import APIRouter
router = APIRouter(prefix="/communities", tags=["communities"])

@router.get("")
def list_communities():
    return {"items": [
        {"slug": "healthy-aging", "name": "Healthy Aging"},
        {"slug": "fitness-strength", "name": "Fitness & Strength"},
        {"slug": "nutrition", "name": "Nutrition"},
        {"slug": "skin-health", "name": "Skin & Appearance"},
        {"slug": "brain-health", "name": "Brain & Cognition"},
        {"slug": "biomedical-research", "name": "Biomedical Research"},
    ]}
