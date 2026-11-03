"""Replaceable model providers (Architecture 6.2: external model integration first).

* ``ExtractiveProvider`` is the default. It runs entirely offline, never invents content and only
  restates retrieved, cited sources. It is the baseline against which real models are evaluated.
* ``AnthropicProvider`` is an optional adapter for the General Platform AI. It is only selected when
  AI_PROVIDER=anthropic, AI_API_KEY and AI_MODEL are configured. Private AI Scientist and
  Organization AI never use it unless AI_ALLOW_EXTERNAL_FOR_PRIVATE=true is set deliberately.
  The adapter has not been exercised against the live API in this repository's test suite.
"""
from dataclasses import dataclass

import httpx

from app.ai.types import Source
from app.core.config import settings


@dataclass(frozen=True)
class ProviderResult:
    text: str
    provider: str
    model_version: str
    external: bool


class ExtractiveProvider:
    name = "extractive"
    model_version = "extractive-v1"
    external = False

    def generate(self, system: str, prompt: str, sources: list[Source], instructions: str = "") -> ProviderResult:
        lines = ["These are the most relevant sources I could find for your question. I have not added claims beyond them:"]
        for index, source in enumerate(sources, start=1):
            lines.append(f"[{index}] {source.title} — {source.evidence_label}: {source.snippet}")
        return ProviderResult("\n".join(lines), self.name, self.model_version, False)


class AnthropicProvider:
    name = "anthropic"
    external = True
    endpoint = "https://api.anthropic.com/v1/messages"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model_version = model

    def generate(self, system: str, prompt: str, sources: list[Source], instructions: str = "") -> ProviderResult:
        context = "\n".join(
            f"[{index}] {source.title} ({source.evidence_label}): {source.snippet}"
            for index, source in enumerate(sources, start=1)
        )
        system_prompt = (
            "You are a careful scientific assistant for a health and longevity research network. "
            "Answer ONLY from the numbered sources provided and cite them like [1]. "
            "If the sources are insufficient, say so. Distinguish established evidence from weak evidence "
            "(preprints, opinion, community experience, hypotheses). Never give a diagnosis or personal medical advice. "
            + (instructions or "")
        )
        response = httpx.post(
            self.endpoint,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model_version,
                "max_tokens": 800,
                "system": system_prompt,
                "messages": [{"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {prompt}"}],
            },
            timeout=30.0,
        )
        response.raise_for_status()
        blocks = response.json().get("content", [])
        text = "".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()
        if not text:
            raise RuntimeError("The model provider returned no text.")
        return ProviderResult(text, self.name, self.model_version, True)


def provider_status() -> dict[str, str | bool]:
    configured = settings.ai_provider == "anthropic" and bool(settings.ai_api_key) and bool(settings.ai_model)
    return {
        "configured_provider": settings.ai_provider,
        "external_provider_ready": configured,
        "external_allowed_for_private_systems": settings.ai_allow_external_for_private,
        "fallback_provider": ExtractiveProvider.name,
    }


def select_provider(system: str):
    """Choose a provider while enforcing data boundaries per AI system."""
    external_ready = settings.ai_provider == "anthropic" and settings.ai_api_key and settings.ai_model
    if external_ready and (system == "general" or settings.ai_allow_external_for_private):
        return AnthropicProvider(settings.ai_api_key or "", settings.ai_model or "")
    return ExtractiveProvider()
