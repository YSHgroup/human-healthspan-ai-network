from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import orchestrator
from app.api.dependencies import get_current_user
from app.db.base import utc_now
from app.db.session import get_db
from app.domains.organizations.service import LEAD_ROLES, MANAGE_ROLES, require_member
from app.domains.subscriptions.service import use_feature
from app.models.domain import User
from app.models.platform import (
    AIConversation,
    AIFeedback,
    AIMessage,
    AIRun,
    ConsentRecord,
    OrgAIInstance,
    OrgKnowledgeDocument,
)
from app.schemas.platform import (
    AIAnswerOut,
    AIChatRequest,
    AIConversationOut,
    AIFeedbackCreate,
    AIMessageOut,
    OrgAICreate,
    OrgAIOut,
    OrgAIUpdate,
    OrgDocumentCreate,
    OrgDocumentOut,
)
from app.services.audit import record_audit_event

general_router = APIRouter(tags=["ai-general"])
scientist_router = APIRouter(tags=["ai-scientist"])
organization_ai_router = APIRouter(tags=["organization-ai"])


def to_answer(response: orchestrator.AIResponse) -> AIAnswerOut:
    return AIAnswerOut(
        system=response.system,
        status=response.status,
        answer=response.answer,
        sources=response.sources,
        evidence_summary=response.evidence_summary,
        uncertainty=response.uncertainty,
        disclaimer=response.disclaimer,
        run_id=response.run_id,
        conversation_id=response.conversation_id,
        provider=response.provider,
        model_version=response.model_version,
    )


# ------------------------------------------------------------------ General Platform AI
@general_router.post("/chat", response_model=AIAnswerOut)
def general_chat(
    payload: AIChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AIAnswerOut:
    return to_answer(orchestrator.ask(db, user, "general", payload.prompt, None, payload.conversation_id))


@general_router.get("/conversations", response_model=list[AIConversationOut])
def list_ai_conversations(
    system: Annotated[str | None, Query(pattern="^(general|scientist|organization)$")] = None,
    organization_id: UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AIConversation]:
    query = select(AIConversation).where(AIConversation.user_id == user.id)
    if system:
        query = query.where(AIConversation.system == system)
    if organization_id:
        query = query.where(AIConversation.organization_id == organization_id)
    return list(db.scalars(query.order_by(AIConversation.created_at.desc()).limit(limit)))


@general_router.get("/conversations/{conversation_id}/messages", response_model=list[AIMessageOut])
def ai_conversation_messages(
    conversation_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[AIMessage]:
    conversation = db.get(AIConversation, conversation_id)
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI conversation not found.")
    return list(
        db.scalars(select(AIMessage).where(AIMessage.conversation_id == conversation_id).order_by(AIMessage.created_at.asc()))
    )


@general_router.post("/runs/{run_id}/feedback", status_code=status.HTTP_204_NO_CONTENT)
def ai_feedback(
    run_id: UUID,
    payload: AIFeedbackCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    run = db.get(AIRun, run_id)
    if run is None or run.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI run not found.")
    if payload.permitted_use == "training":
        consent = db.scalar(
            select(ConsentRecord.granted).where(ConsentRecord.user_id == user.id, ConsentRecord.purpose == "ai_training")
        )
        if run.system != "general" or not consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Training use requires your explicit ai_training consent and is only available for General AI runs.",
            )
    feedback = db.scalar(select(AIFeedback).where(AIFeedback.run_id == run_id, AIFeedback.user_id == user.id))
    if feedback is None:
        feedback = AIFeedback(run_id=run_id, user_id=user.id, organization_id=run.organization_id, rating=payload.rating)
        db.add(feedback)
    feedback.rating, feedback.comment, feedback.permitted_use = payload.rating, payload.comment, payload.permitted_use
    record_audit_event(db, user.id, "ai.feedback", "ai_run", run_id, {"rating": payload.rating, "use": payload.permitted_use})
    db.commit()


# ------------------------------------------------------------------ Private AI Scientist
@scientist_router.post("/chat", response_model=AIAnswerOut)
def scientist_chat(
    payload: AIChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AIAnswerOut:
    return to_answer(orchestrator.ask(db, user, "scientist", payload.prompt, None, payload.conversation_id))


# ------------------------------------------------------------------ Organization AI
def _instance_or_404(db: Session, organization_id: UUID) -> OrgAIInstance:
    instance = db.scalar(select(OrgAIInstance).where(OrgAIInstance.organization_id == organization_id))
    if instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This organization has no AI instance.")
    return instance


@organization_ai_router.post("/{organization_id}", response_model=OrgAIOut, status_code=status.HTTP_201_CREATED)
def create_org_ai(
    organization_id: UUID,
    payload: OrgAICreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgAIInstance:
    require_member(db, user, organization_id, MANAGE_ROLES)
    if db.scalar(select(OrgAIInstance.id).where(OrgAIInstance.organization_id == organization_id)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This organization already has an AI instance.")
    if not use_feature(db, "organization", organization_id, "organization.ai"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="An Organization AI entitlement is required.")
    instance = OrgAIInstance(
        organization_id=organization_id, name=payload.name, instructions=payload.instructions, created_by=user.id
    )
    db.add(instance)
    db.flush()
    record_audit_event(db, user.id, "organization_ai.created", "organization", organization_id)
    db.commit()
    db.refresh(instance)
    return instance


@organization_ai_router.get("/{organization_id}", response_model=OrgAIOut)
def get_org_ai(organization_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrgAIInstance:
    require_member(db, user, organization_id)
    return _instance_or_404(db, organization_id)


@organization_ai_router.patch("/{organization_id}", response_model=OrgAIOut)
def update_org_ai(
    organization_id: UUID,
    payload: OrgAIUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgAIInstance:
    require_member(db, user, organization_id, MANAGE_ROLES)
    instance = _instance_or_404(db, organization_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(instance, field, value)
    record_audit_event(db, user.id, "organization_ai.updated", "organization", organization_id)
    db.commit()
    db.refresh(instance)
    return instance


@organization_ai_router.post(
    "/{organization_id}/documents", response_model=OrgDocumentOut, status_code=status.HTTP_201_CREATED
)
def add_org_document(
    organization_id: UUID,
    payload: OrgDocumentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgKnowledgeDocument:
    require_member(db, user, organization_id, LEAD_ROLES)
    _instance_or_404(db, organization_id)
    document = OrgKnowledgeDocument(
        organization_id=organization_id,
        added_by=user.id,
        title=payload.title,
        content=payload.content,
        source_label=payload.source_label,
    )
    db.add(document)
    db.flush()
    record_audit_event(db, user.id, "organization_ai.document_added", "organization", organization_id, {"document": str(document.id)})
    db.commit()
    db.refresh(document)
    return document


@organization_ai_router.get("/{organization_id}/documents", response_model=list[OrgDocumentOut])
def list_org_documents(
    organization_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[OrgKnowledgeDocument]:
    require_member(db, user, organization_id)
    return list(
        db.scalars(
            select(OrgKnowledgeDocument)
            .where(OrgKnowledgeDocument.organization_id == organization_id, OrgKnowledgeDocument.deleted_at.is_(None))
            .order_by(OrgKnowledgeDocument.created_at.desc())
        )
    )


@organization_ai_router.delete("/{organization_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_org_document(
    organization_id: UUID,
    document_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    require_member(db, user, organization_id, LEAD_ROLES)
    document = db.get(OrgKnowledgeDocument, document_id)
    if document is None or document.organization_id != organization_id or document.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    document.deleted_at = utc_now()
    record_audit_event(db, user.id, "organization_ai.document_removed", "organization", organization_id, {"document": str(document_id)})
    db.commit()


@organization_ai_router.post("/{organization_id}/chat", response_model=AIAnswerOut)
def org_ai_chat(
    organization_id: UUID,
    payload: AIChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AIAnswerOut:
    return to_answer(orchestrator.ask(db, user, "organization", payload.prompt, organization_id, payload.conversation_id))
