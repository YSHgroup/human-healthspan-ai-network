from fastapi import APIRouter
router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/ask")
def ask_ai(payload: dict):
    # Provider/model integration is deliberately behind the AI gateway.
    return {
        "status": "not_configured",
        "answer": None,
        "sources": [],
        "message": "Configure an AI provider and RAG pipeline in the next round."
    }
