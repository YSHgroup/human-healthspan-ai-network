"""Permission-aware retrieval for the three AI systems.

Each retriever has its own, explicit knowledge boundary. None of them reads personal health
tables, messages or other members' private data (Blueprint 7.2, Architecture 6.4, 13.4).
Candidates are selected in SQL with permission filters applied *before* ranking.
"""
import re
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.ai.types import Source
from app.models.domain import (
    Community,
    Evidence,
    Hypothesis,
    Literature,
    Post,
    ResearchProject,
    ResearchQuestion,
    User,
)
from app.models.platform import OrgKnowledgeDocument, ProjectOrganization
from app.services.authorization import AuthorizationService

STOPWORDS = frozenset(
    "the and for are but not you your with that this from have has had was were what when where which who whom "
    "how does can could should would will about into than then them they their there here been being also "
    "any all its it's our out over per via why".split()
)
SNIPPET_LENGTH = 360
CANDIDATE_FACTOR = 6


def tokenize(text: str) -> list[str]:
    seen: list[str] = []
    for token in re.findall(r"[a-z0-9]{3,}", text.lower()):
        if token not in STOPWORDS and token not in seen:
            seen.append(token)
    return seen[:8]


def _snippet(text: str | None) -> str:
    cleaned = " ".join((text or "").split())
    return cleaned if len(cleaned) <= SNIPPET_LENGTH else cleaned[: SNIPPET_LENGTH - 1].rstrip() + "…"


def _score(tokens: Iterable[str], title: str, body: str | None) -> int:
    title_l, body_l = title.lower(), (body or "").lower()
    total = 0
    for token in tokens:
        if token in title_l:
            total += 3
        if token in body_l:
            total += 1
    return total


def _like_any(columns, tokens: list[str]):
    return or_(*[column.ilike(f"%{token}%") for token in tokens for column in columns])


def _rank(scored: list[tuple[int, Source]], limit: int) -> list[Source]:
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: (-item[0], item[1].title))
    return [source for _, source in scored[:limit]]


def _project_sources(
    db: Session, tokens: list[str], project_ids, limit: int, organization_id: str | None = None
) -> list[tuple[int, Source]]:
    scored: list[tuple[int, Source]] = []
    pool = limit * CANDIDATE_FACTOR
    literature = db.scalars(
        select(Literature)
        .where(Literature.project_id.in_(project_ids), _like_any([Literature.title, Literature.authors], tokens))
        .limit(pool)
    )
    for item in literature:
        scored.append(
            (
                _score(tokens, item.title, item.authors),
                Source(
                    id=str(item.id),
                    kind="literature",
                    title=item.title,
                    snippet=_snippet(item.authors or "No author information recorded."),
                    evidence_class=item.source_type,
                    source_url=item.source_url,
                    project_id=str(item.project_id),
                    organization_id=organization_id,
                ),
            )
        )
    evidence = db.scalars(
        select(Evidence)
        .where(Evidence.project_id.in_(project_ids), _like_any([Evidence.summary], tokens))
        .limit(pool)
    )
    for item in evidence:
        scored.append(
            (
                _score(tokens, item.label, item.summary),
                Source(
                    id=str(item.id),
                    kind="evidence",
                    title=f"Evidence record ({item.label})",
                    snippet=_snippet(item.summary),
                    evidence_class=item.label,
                    source_url=item.source_url,
                    project_id=str(item.project_id),
                    organization_id=organization_id,
                ),
            )
        )
    return scored


class GeneralRetriever:
    """Public and approved common platform knowledge only."""

    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, query: str, limit: int = 6) -> list[Source]:
        tokens = tokenize(query)
        if not tokens:
            return []
        public_projects = select(ResearchProject.id).where(ResearchProject.visibility == "public")
        scored = _project_sources(self.db, tokens, public_projects, limit)
        communities = self.db.scalars(
            select(Community)
            .where(Community.is_active.is_(True), _like_any([Community.name, Community.description], tokens))
            .limit(limit * CANDIDATE_FACTOR)
        )
        for item in communities:
            scored.append(
                (
                    _score(tokens, item.name, item.description),
                    Source(
                        id=str(item.id),
                        kind="community",
                        title=item.name,
                        snippet=_snippet(item.description),
                        evidence_class="community_description",
                    ),
                )
            )
        posts = self.db.execute(
            select(Post)
            .join(User, User.id == Post.author_id)
            .where(
                Post.deleted_at.is_(None),
                User.is_active.is_(True),
                Post.classification.in_(["scientific_evidence", "expert_interpretation"]),
                _like_any([Post.body], tokens),
            )
            .limit(limit * CANDIDATE_FACTOR)
        )
        for (post,) in posts:
            evidence_class = "expert_opinion" if post.classification == "expert_interpretation" else "community_claim"
            scored.append(
                (
                    _score(tokens, "", post.body),
                    Source(
                        id=str(post.id),
                        kind="post",
                        title="Community post (" + post.classification.replace("_", " ") + ")",
                        snippet=_snippet(post.body),
                        evidence_class=evidence_class,
                    ),
                )
            )
        return _rank(scored, limit)


class ScientistRetriever:
    """Private AI Scientist: only projects the requesting researcher is authorized to read."""

    def __init__(self, db: Session, principal: User):
        self.db = db
        self.principal = principal

    def retrieve(self, query: str, limit: int = 8) -> list[Source]:
        tokens = tokenize(query)
        if not tokens:
            return []
        readable = AuthorizationService(self.db).readable_project_ids(self.principal)
        scored = _project_sources(self.db, tokens, readable, limit)
        hypotheses = self.db.scalars(
            select(Hypothesis)
            .where(Hypothesis.project_id.in_(readable), _like_any([Hypothesis.title, Hypothesis.description], tokens))
            .limit(limit * CANDIDATE_FACTOR)
        )
        for item in hypotheses:
            evidence_class = "ai_generated_hypothesis" if item.origin == "ai" else "hypothesis"
            scored.append(
                (
                    _score(tokens, item.title, item.description),
                    Source(
                        id=str(item.id),
                        kind="hypothesis",
                        title=item.title,
                        snippet=_snippet(item.description),
                        evidence_class=evidence_class,
                        project_id=str(item.project_id),
                    ),
                )
            )
        questions = self.db.scalars(
            select(ResearchQuestion)
            .where(
                ResearchQuestion.project_id.in_(readable),
                _like_any([ResearchQuestion.title, ResearchQuestion.description], tokens),
            )
            .limit(limit * CANDIDATE_FACTOR)
        )
        for item in questions:
            scored.append(
                (
                    _score(tokens, item.title, item.description),
                    Source(
                        id=str(item.id),
                        kind="research_question",
                        title=item.title,
                        snippet=_snippet(item.description),
                        evidence_class="research_question",
                        project_id=str(item.project_id),
                    ),
                )
            )
        return _rank(scored, limit)


class OrganizationRetriever:
    """Organization AI: that organization's documents and its attached projects the user may read."""

    def __init__(self, db: Session, principal: User, organization_id: UUID):
        self.db = db
        self.principal = principal
        self.organization_id = organization_id

    def retrieve(self, query: str, limit: int = 8) -> list[Source]:
        tokens = tokenize(query)
        if not tokens:
            return []
        org_id = str(self.organization_id)
        scored: list[tuple[int, Source]] = []
        documents = self.db.scalars(
            select(OrgKnowledgeDocument)
            .where(
                OrgKnowledgeDocument.organization_id == self.organization_id,
                OrgKnowledgeDocument.deleted_at.is_(None),
                _like_any([OrgKnowledgeDocument.title, OrgKnowledgeDocument.content], tokens),
            )
            .limit(limit * CANDIDATE_FACTOR)
        )
        for item in documents:
            scored.append(
                (
                    _score(tokens, item.title, item.content),
                    Source(
                        id=str(item.id),
                        kind="organization_document",
                        title=item.title,
                        snippet=_snippet(item.content),
                        evidence_class="organization_document",
                        source_url=None,
                        organization_id=org_id,
                    ),
                )
            )
        attached = select(ProjectOrganization.project_id).where(ProjectOrganization.organization_id == self.organization_id)
        readable = AuthorizationService(self.db).readable_project_ids(self.principal)
        accessible = select(ResearchProject.id).where(
            ResearchProject.id.in_(attached), ResearchProject.id.in_(readable)
        )
        scored.extend(_project_sources(self.db, tokens, accessible, limit, organization_id=org_id))
        return _rank(scored, limit)
