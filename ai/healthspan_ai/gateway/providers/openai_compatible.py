"""OpenAI-compatible chat-completions provider adapter."""

import json
from collections.abc import AsyncIterator
from urllib.parse import urljoin

import httpx

from healthspan_ai.gateway.providers.errors import (
    ProviderConfigurationError,
    ProviderRequestError,
)
from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig

MAX_RECORDED_TOKEN_COUNT = 2_147_483_647


def _optional_token_count(usage: object, key: str) -> int | None:
    if not isinstance(usage, dict):
        return None
    value = usage.get(key)
    if type(value) is int and 0 <= value <= MAX_RECORDED_TOKEN_COUNT:
        return value
    return None


async def complete(
    config: GatewayConfig,
    messages: list[ChatMessage],
) -> Completion:
    return await complete_compatible(config, messages)


async def complete_compatible(
    config: GatewayConfig,
    messages: list[ChatMessage],
    *,
    default_base_url: str | None = None,
    require_api_key: bool = True,
) -> Completion:
    api_key = (config.api_key or "").strip()
    model = (config.model or "").strip()
    base_url = (config.base_url or default_base_url or "").strip()

    if (require_api_key and not api_key) or not model or not base_url:
        raise ProviderConfigurationError(
            "The selected AI provider requires an AI_MODEL and endpoint"
            + (" and AI_API_KEY" if require_api_key else "")
        )

    url = urljoin(base_url.rstrip("/") + "/", "chat/completions")
    payload = {
        "model": model,
        "messages": [{"role": message.role, "content": message.content} for message in messages],
    }
    try:
        async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        message = data["choices"][0]["message"]
        content = message["content"]
        if not isinstance(content, str) or not content.strip():
            raise ProviderRequestError("AI provider returned an empty completion")
        raw_sources = message.get("sources")
        sources = (
            tuple(source.strip() for source in raw_sources if isinstance(source, str) and source.strip())
            if isinstance(raw_sources, list)
            else ()
        )
        source_notice = message.get("source_notice")
        if not isinstance(source_notice, str):
            source_notice = None
        usage = data.get("usage")
        response_model = data.get("model")
        if not isinstance(response_model, str) or not response_model.strip():
            response_model = model
        return Completion(
            provider=config.provider,
            model=response_model,
            content=content.strip(),
            input_tokens=_optional_token_count(usage, "prompt_tokens"),
            output_tokens=_optional_token_count(usage, "completion_tokens"),
            sources=sources,
            source_notice=source_notice,
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


async def stream_compatible(
    config: GatewayConfig,
    messages: list[ChatMessage],
    *,
    default_base_url: str | None = None,
    require_api_key: bool = True,
) -> AsyncIterator[str]:
    return _stream_compatible(
        config,
        messages,
        default_base_url=default_base_url,
        require_api_key=require_api_key,
    )


async def _stream_compatible(
    config: GatewayConfig,
    messages: list[ChatMessage],
    *,
    default_base_url: str | None = None,
    require_api_key: bool = True,
) -> AsyncIterator[str]:
    api_key = (config.api_key or "").strip()
    model = (config.model or "").strip()
    base_url = (config.base_url or default_base_url or "").strip()
    if (require_api_key and not api_key) or not model or not base_url:
        raise ProviderConfigurationError(
            "The selected AI provider requires an AI_MODEL and endpoint"
            + (" and AI_API_KEY" if require_api_key else "")
        )

    url = urljoin(base_url.rstrip("/") + "/", "chat/completions")
    payload = {
        "model": model,
        "messages": [{"role": message.role, "content": message.content} for message in messages],
        "stream": True,
    }
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if not data or data == "[DONE]":
                        continue
                    try:
                        chunk = json.loads(data)
                        choices = chunk.get("choices")
                        if not isinstance(choices, list) or not choices:
                            continue
                        delta = choices[0].get("delta", {})
                        content = delta.get("content") if isinstance(delta, dict) else None
                        if isinstance(content, str) and content:
                            yield content
                    except (json.JSONDecodeError, AttributeError, IndexError, TypeError) as exc:
                        raise ProviderRequestError("AI provider returned an invalid stream") from exc
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
    except httpx.HTTPError as exc:
        raise ProviderRequestError("AI provider request failed") from exc
