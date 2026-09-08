from fastapi import APIRouter
from app.schemas.content import PostCreate, PostOut
from app.schemas.research import ResearchQuestionCreate, ResearchQuestionOut

router = APIRouter()

@router.get("/version")
def version():
    return {"api": "v1", "round": 2}

@router.post("/posts", response_model=PostOut)
def create_post(payload: PostCreate):
    # Persistence is intentionally isolated behind the service layer for the next implementation pass.
    return PostOut(id="demo-post", author_id=payload.author_id, body=payload.body)

@router.post("/research/questions", response_model=ResearchQuestionOut)
def create_research_question(payload: ResearchQuestionCreate):
    return ResearchQuestionOut(
        id="demo-question",
        project_id=payload.project_id,
        title=payload.title,
        description=payload.description,
        evidence_status="unclassified",
    )
