from dataclasses import dataclass
from typing import Final, Literal

AISystem = Literal["general", "scientist", "organization"]
AI_SYSTEMS: Final[tuple[str, ...]] = ("general", "scientist", "organization")

# Blueprint section 8 evidence classes. Literature/evidence records map onto these.
EVIDENCE_CLASS_LABELS: Final[dict[str, str]] = {
    "peer_reviewed": "Peer-reviewed research",
    "clinical": "Clinical trial evidence",
    "human_observational": "Human observational evidence",
    "animal": "Animal evidence",
    "cell_based": "Cellular / in-vitro evidence",
    "computational": "Computational evidence",
    "preprint": "Preprint",
    "expert_opinion": "Expert opinion",
    "community_claim": "Community experience",
    "ai_generated_hypothesis": "AI-generated hypothesis",
    "speculation": "Speculation",
    "paper": "Published paper (review status not recorded)",
    "document": "Document",
    "dataset": "Dataset",
    "organization_document": "Organization document",
    "community_description": "Community description",
    "hypothesis": "Researcher hypothesis (unvalidated)",
    "research_question": "Research question",
    "other": "Other source",
}
# Classes that must never be presented as established findings.
WEAK_EVIDENCE_CLASSES: Final[frozenset[str]] = frozenset(
    {
        "preprint",
        "expert_opinion",
        "community_claim",
        "ai_generated_hypothesis",
        "speculation",
        "hypothesis",
        "research_question",
        "community_description",
    }
)


@dataclass(frozen=True)
class Source:
    id: str
    kind: str
    title: str
    snippet: str
    evidence_class: str
    source_url: str | None = None
    project_id: str | None = None
    organization_id: str | None = None

    @property
    def evidence_label(self) -> str:
        return EVIDENCE_CLASS_LABELS.get(self.evidence_class, self.evidence_class)

    def to_dict(self, index: int) -> dict[str, str | int | None]:
        return {
            "index": index,
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "snippet": self.snippet,
            "evidence_class": self.evidence_class,
            "evidence_label": self.evidence_label,
            "source_url": self.source_url,
            "project_id": self.project_id,
            "organization_id": self.organization_id,
        }
