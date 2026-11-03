"""Common AI orchestration and governance layer (Blueprint 7.5).

One audited entry point, three isolated systems. Each system performs its own authorization before
any retrieval happens, and every run is recorded (without storing prompt text in the run/audit
tables) so AI behavior can be reviewed.
"""
import time
from collections import Counter
from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.providers import ExtractiveProvider, ProviderResult, select_provider
from app.ai.retrieval import GeneralRetriever, OrganizationRetriever, ScientistRetriever
from app.ai.types import AI_SYSTEMS, EVIDENCE_CLASS_LABELS, WEAK_EVIDENCE_CLASSES, Source
from app.domains.organizations.service import require_member
from app.domains.research.access import has_research_access
from app.models.domain import User
from app.models.platform import AIConversation, AIMessage, AIRun, OrgAIInstance
from app.services.audit import record_audit_event

DISCLAIMERS = {
    "general": (
        "General information from public platform knowledge, not medical advice. "
        "Talk to a qualified clinician about personal health decisions."
    ),
    "scientist": (
        "AI-assisted research support grounded in projects you are authorized to read. "
        "Hypotheses are proposals, not discoveries; verify claims against the cited sources."
    ),
    "organization": (
        "Answer based only on this organization's approved knowledge and the projects you may read. "
        "It does not reflect other organizations or private member data."
    ),
}
NO_SOURCES_MESSAGE = (
    "I could not find sufficiently relevant sources within the knowledge this assistant is allowed to use, "
    "so I will not guess. Try rephrasing, add literature or documents to an appropriate workspace, or ask a researcher."
)


@dataclass
class AIResponse:
    system: str
    status: str
    answer: str
    sources: list[dict]
    evidence_summary: dict[str, int]
    uncertainty: str
    disclaimer: str
    run_id: UUID
    conversation_id: UUID
    provider: str
    model_version: str


def _uncertainty(sources: list[Source]) -> tuple[dict[str, int], str]:
    counts = Counter(source.evidence_class for source in sources)
    summary = {EVIDENCE_CLASS_LABELS.get(key, key): value for key, value in counts.items()}
    if not sources:
        return summary, "No supporting sources were available."
    weak = sum(value for key, value in counts.items() if key in WEAK_EVIDENCE_CLASSES)
    if weak == len(sources):
        level = "All retrieved sources are weak or unvalidated evidence (opinion, preprints, community claims or hypotheses)."
    elif weak:
        level = "The sources mix stronger and weaker evidence; weaker items are labelled and should not be treated as established."
    else:
        level = "Sources are not marked as weak evidence, but study quality and limitations are not assessed automatically."
    return summary, level + " This is not a systematic review and the source set may be incomplete."


def _authorize(db: Session, user: User, system: str, organization_id: UUID | None) -> OrgAIInstance | None:
    if system not in AI_SYSTEMS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown AI system.")
    if system == "scientist":
        if not has_research_access(db, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The Private AI Scientist requires approved researcher membership.",
            )
        return None
    if system == "organization":
        if organization_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="organization_id is required.")
        require_member(db, user, organization_id)
        instance = db.scalar(select(OrgAIInstance).where(OrgAIInstance.organization_id == organization_id))
        if instance is None or instance.status != "active":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This organization has no active AI instance.")
        return instance
    return None


def _conversation(
    db: Session, user: User, system: str, organization_id: UUID | None, conversation_id: UUID | None, prompt: str
) -> AIConversation:
    if conversation_id is not None:
        conversation = db.get(AIConversation, conversation_id)
        if (
            conversation is None
            or conversation.user_id != user.id
            or conversation.system != system
            or conversation.organization_id != organization_id
        ):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI conversation not found.")
        return conversation
    conversation = AIConversation(
        user_id=user.id, system=system, organization_id=organization_id, title=" ".join(prompt.split())[:80]
    )
    db.add(conversation)
    db.flush()
    return conversation


def ask(
    db: Session,
    user: User,
    system: str,
    prompt: str,
    organization_id: UUID | None = None,
    conversation_id: UUID | None = None,
) -> AIResponse:
    started = time.perf_counter()
    instance = _authorize(db, user, system, organization_id)
    conversation = _conversation(db, user, system, organization_id, conversation_id, prompt)

    if system == "general":
        sources = GeneralRetriever(db).retrieve(prompt)
    elif system == "scientist":
        sources = ScientistRetriever(db, user).retrieve(prompt)
    else:
        sources = OrganizationRetriever(db, user, organization_id).retrieve(prompt)  # type: ignore[arg-type]

    if sources:
        provider = select_provider(system)
        try:
            result: ProviderResult = provider.generate(
                system, prompt, sources, instance.instructions if instance else ""
            )
        except Exception:  # noqa: BLE001 - never fail the request because a provider is down
            result = ExtractiveProvider().generate(system, prompt, sources)
            record_audit_event(db, user.id, "ai.provider_fallback", "ai_run", details={"system": system})
        run_status = "answered"
        answer = result.text
    else:
        result = ProviderResult(NO_SOURCES_MESSAGE, "none", "none", False)
        run_status = "insufficient_evidence"
        answer = NO_SOURCES_MESSAGE

    serialized = [source.to_dict(index) for index, source in enumerate(sources, start=1)]
    summary, uncertainty = _uncertainty(sources)
    run = AIRun(
        user_id=user.id,
        system=system,
        organization_id=organization_id,
        conversation_id=conversation.id,
        provider=result.provider,
        model_version=result.model_version,
        status=run_status,
        source_count=len(sources),
        source_refs=[{"id": item["id"], "kind": item["kind"], "title": item["title"]} for item in serialized],
        external_provider_used=result.external,
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
    db.add(run)
    db.add(AIMessage(conversation_id=conversation.id, role="user", content=prompt, sources=[]))
    db.add(AIMessage(conversation_id=conversation.id, role="assistant", content=answer, sources=serialized))
    db.flush()
    record_audit_event(
        db,
        user.id,
        "ai.run",
        "ai_run",
        run.id,
        {
            "system": system,
            "organization_id": str(organization_id) if organization_id else None,
            "source_count": len(sources),
            "status": run_status,
            "external": result.external,
        },
    )
    db.commit()
    return AIResponse(
        system=system,
        status=run_status,
        answer=answer,
        sources=serialized,
        evidence_summary=summary,
        uncertainty=uncertainty,
        disclaimer=DISCLAIMERS[system],
        run_id=run.id,
        conversation_id=conversation.id,
        provider=result.provider,
        model_version=result.model_version,
    )
