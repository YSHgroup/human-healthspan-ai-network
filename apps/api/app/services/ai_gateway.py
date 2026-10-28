from typing import Protocol


class AIProvider(Protocol):
    async def answer(self, prompt: str, context: list[dict]) -> dict:
        """Return a structured response from an approved model provider."""


class AIProviderNotConfigured(RuntimeError):
    pass


class AIGateway:
    """Provider-neutral boundary; no external model is enabled by default."""

    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider

    async def answer(self, prompt: str, context: list[dict]) -> dict:
        if self.provider is None:
            raise AIProviderNotConfigured("Attach an approved model provider before enabling AI endpoints.")
        if not prompt.strip():
            raise ValueError("AI prompt cannot be blank.")
        return await self.provider.answer(prompt, context)
