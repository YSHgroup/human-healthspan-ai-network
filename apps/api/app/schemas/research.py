from datetime import datetime
from typing import Literal
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_http_url(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    parsed = urlsplit(value)
    try:
        parsed.port
    except ValueError as exc:
        raise ValueError("Source URL contains an invalid port.") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Source URL must be an HTTP(S) URL without embedded credentials.")
    return value


class ResearchQuestionCreate(BaseModel):
    project_id: UUID
    title: str = Field(min_length=3, max_length=500)
    description: str = Field(min_length=1, max_length=10000)

    @field_validator("title", "description")
    @classmethod
    def values_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This value cannot be blank.")
        return value.strip()


class ResearchQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    author_id: UUID
    title: str
    description: str
    evidence_status: str
    created_at: datetime


class HypothesisCreate(BaseModel):
    research_question_id: UUID | None = None
    title: str = Field(min_length=3, max_length=300)
    description: str = Field(min_length=1, max_length=10000)

    @field_validator("title", "description")
    @classmethod
    def values_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This value cannot be blank.")
        return value.strip()


class HypothesisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    research_question_id: UUID | None
    author_id: UUID
    title: str
    description: str
    origin: str
    status: str
    created_at: datetime


class ResearchProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1, max_length=10000)
    visibility: Literal["private", "team", "public"] = "private"

    @field_validator("title", "description")
    @classmethod
    def values_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This value cannot be blank.")
        return value.strip()


class ResearchProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    visibility: Literal["private", "team", "public"] | None = None


class ResearchProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    title: str
    description: str
    visibility: str
    status: str
    created_at: datetime


class ResearchMemberCreate(BaseModel):
    user_id: UUID
    role: Literal["member", "reviewer"] = "member"


class ResearchMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: str
    created_at: datetime


class LiteratureCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    authors: str | None = Field(default=None, max_length=1000)
    publication_year: int | None = Field(default=None, ge=1400, le=2200)
    source_url: str | None = Field(default=None, max_length=2000)
    doi: str | None = Field(default=None, max_length=255)
    source_type: Literal["paper", "preprint", "document", "dataset", "other"] = "paper"

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Literature title cannot be blank.")
        return value.strip()

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_http(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class LiteratureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    authors: str | None
    publication_year: int | None
    source_url: str | None
    doi: str | None
    source_type: str
    provenance: dict
    created_at: datetime


class EvidenceCreate(BaseModel):
    literature_id: UUID | None = None
    label: Literal[
        "peer_reviewed",
        "preprint",
        "clinical",
        "human_observational",
        "animal",
        "cell_based",
        "computational",
        "expert_opinion",
        "community_claim",
        "ai_generated_hypothesis",
    ]
    summary: str = Field(min_length=1, max_length=5000)
    source_url: str | None = Field(default=None, max_length=2000)

    @field_validator("summary")
    @classmethod
    def summary_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Evidence summary cannot be blank.")
        return value.strip()

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_http(cls, value: str | None) -> str | None:
        return validate_http_url(value)


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    literature_id: UUID | None
    label: str
    summary: str
    source_url: str | None
    provenance: dict
    review_status: str
    created_at: datetime
