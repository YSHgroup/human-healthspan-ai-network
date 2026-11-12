"""OpenAI-compatible chat-completions provider adapter."""

from urllib.parse import urljoin

import httpx

from healthspan_ai.shared.contracts.chat import ChatMessage, Completion, GatewayConfig


class ProviderConfigurationError(Exception):
    """The selected provider is missing required configuration."""


class ProviderRequestError(Exception):
    """The provider rejected or failed to complete a request."""


async def complete(
    config: GatewayConfig,
    messages: list[ChatMessage],
) -> Completion:
    api_key = (config.api_key or "").strip()
    model = (config.model or "").strip()
    base_url = (config.base_url or "").strip()

    if not api_key or not model or not base_url:
        raise ProviderConfigurationError(
            "AI_PROVIDER=openai-compatible requires AI_API_KEY, AI_MODEL and AI_BASE_URL"
        )

    url = urljoin(base_url.rstrip("/") + "/", "chat/completions")
    payload = {
        "model": model,
        "messages": [{"role": message.role, "content": message.content} for message in messages],
    }
    try:
        async with httpx.AsyncClient(timeout=config.timeout_seconds) as client:
            response = await client.post(
                url,
                headers={"Authorization": "******"},
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ProviderRequestError("AI provider returned an empty completion")
        usage = data.get("usage") or {}
        return Completion(
            provider=config.provider,
            model=data.get("model", model),
            content=content.strip(),
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )
    except ProviderConfigurationError:
        raise
    except ProviderRequestError:
        raise
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise ProviderRequestError("AI provider request failed") from exc
