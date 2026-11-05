"""Provider-independent chat contracts."""

from dataclasses import dataclass
from typing import Literal


Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class GatewayConfig:
    provider: str
    model: str | None
    api_key: str | None
    base_url: str | None
    timeout_seconds: float


@dataclass(frozen=True)
class Completion:
    provider: str
    model: str | None
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
