"""Anthropic Claude Messages API provider."""

from urllib.parse import urljoin

import httpx

from healthspan_ai.gateway.providers.errors import (
    ProviderConfigurationError,
    ProviderRequestError,
)
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig

DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
MAX_OUTPUT_TOKENS = 1024
MAX_RECORDED_TOKEN_COUNT = 2_147_483_647


def _token_count(usage: object, key: str) -> int | None:
    if not isinstance(usage, dict):
        return None
    value = usage.get(key)
    if type(value) is int and 0 <= value <= MAX_RECORDED_TOKEN_COUNT:
        return value
    return None


async def complete(config: GatewayConfig, messages: list[ChatMessage]) -> Completion:
    api_key = (config.api_key or "").strip()
    model = (config.model or "").strip()
    base_url = (config.base_url or DEFAULT_BASE_URL).strip()
    if not api_key or not model:
        raise ProviderConfigurationError("AI_PROVIDER=claude requires AI_API_KEY and AI_MODEL")

    system_messages = [message.content for message in messages if message.role == "system"]
    conversation = [
        {"role": message.role, "content": message.content}
        for message in messages
        if message.role in {"user", "assistant"}
    ]
    payload: dict[str, object] = {
        "model": model,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "messages": conversation,
    }
    if system_messages:
        payload["system"] = "\n\n".join(system_messages)

    try:
        async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
            response = await client.post(
                urljoin(base_url.rstrip("/") + "/", "messages"),
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        blocks = data["content"]
        if not isinstance(blocks, list):
            raise ProviderRequestError("Claude returned an invalid completion")
        content = "".join(
            block["text"]
            for block in blocks
            if isinstance(block, dict)
            and block.get("type") == "text"
            and isinstance(block.get("text"), str)
        )
        if not content.strip():
            raise ProviderRequestError("Claude returned an empty completion")
        response_model = data.get("model")
        if not isinstance(response_model, str) or not response_model.strip():
            response_model = model
        usage = data.get("usage")
        return Completion(
            provider=config.provider,
            model=response_model,
            content=content.strip(),
            input_tokens=_token_count(usage, "input_tokens"),
            output_tokens=_token_count(usage, "output_tokens"),
        )
    except ProviderConfigurationError:
        raise
    except ProviderRequestError:
        raise
    except httpx.HTTPStatusError as exc:
        raise ProviderRequestError(
            f"AI provider returned HTTP {exc.response.status_code}"
        ) from exc
    except httpx.TimeoutException as exc:
        raise ProviderRequestError("AI provider request timed out") from exc
    except httpx.NetworkError as exc:
        raise ProviderRequestError("Could not connect to AI provider") from exc
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise ProviderRequestError("AI provider request failed") from exc