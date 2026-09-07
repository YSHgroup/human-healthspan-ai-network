from fastapi import APIRouter
router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("")
def list_posts():
    return {"items": []}

@router.post("")
def create_post(payload: dict):
    return {"status": "created", "post": payload}
