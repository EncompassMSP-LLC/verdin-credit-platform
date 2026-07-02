"""LLM provider completion clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from verdin_llm_gateway.config import LlmGatewaySettings, LlmProvider
from verdin_llm_gateway.exceptions import LlmProviderNotConfiguredError


@dataclass(frozen=True, slots=True)
class LlmChatMessage:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class LlmCompletionResult:
    content: str
    model: str
    provider: str


class LlmCompletionClient(Protocol):
    async def complete(
        self,
        messages: list[LlmChatMessage],
        *,
        model: str | None = None,
    ) -> LlmCompletionResult: ...


class OpenAiCompatibleClient:
    def __init__(self, settings: LlmGatewaySettings) -> None:
        self._settings = settings
        self._api_key = settings.llm_api_key or ""
        self._default_model = settings.llm_model or ""
        self._timeout = settings.llm_timeout_seconds

    def _endpoint(self, model: str) -> str:
        if self._settings.llm_provider is LlmProvider.AZURE_OPENAI:
            base = (self._settings.llm_base_url or "").rstrip("/")
            if not base:
                raise LlmProviderNotConfiguredError("LLM_BASE_URL is required for azure_openai")
            return f"{base}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
        return "https://api.openai.com/v1/chat/completions"

    def _headers(self) -> dict[str, str]:
        if self._settings.llm_provider is LlmProvider.AZURE_OPENAI:
            return {"api-key": self._api_key, "Content-Type": "application/json"}
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    async def complete(
        self,
        messages: list[LlmChatMessage],
        *,
        model: str | None = None,
    ) -> LlmCompletionResult:
        resolved_model = model or self._default_model
        payload = {
            "model": resolved_model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": 0.2,
        }
        if self._settings.llm_provider is LlmProvider.AZURE_OPENAI:
            payload.pop("model")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                self._endpoint(resolved_model),
                headers=self._headers(),
                json=payload,
            )
        if response.status_code >= 400:
            raise RuntimeError(f"LLM provider error ({response.status_code}): {response.text}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return LlmCompletionResult(
            content=str(content).strip(),
            model=resolved_model,
            provider=self._settings.llm_provider.value,
        )


class AnthropicClient:
    def __init__(self, settings: LlmGatewaySettings) -> None:
        self._settings = settings
        self._api_key = settings.llm_api_key or ""
        self._default_model = settings.llm_model or ""
        self._timeout = settings.llm_timeout_seconds

    async def complete(
        self,
        messages: list[LlmChatMessage],
        *,
        model: str | None = None,
    ) -> LlmCompletionResult:
        resolved_model = model or self._default_model
        system_parts = [message.content for message in messages if message.role == "system"]
        chat_messages = [
            {"role": message.role, "content": message.content}
            for message in messages
            if message.role in {"user", "assistant"}
        ]
        payload: dict[str, object] = {
            "model": resolved_model,
            "max_tokens": 1024,
            "messages": chat_messages,
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if response.status_code >= 400:
            raise RuntimeError(f"LLM provider error ({response.status_code}): {response.text}")

        data = response.json()
        text_blocks = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
        content = "\n".join(text_blocks).strip()
        return LlmCompletionResult(
            content=content,
            model=resolved_model,
            provider=self._settings.llm_provider.value,
        )


def get_llm_completion_client(settings: LlmGatewaySettings | None = None) -> LlmCompletionClient:
    current = settings or LlmGatewaySettings()
    if not current.is_provider_configured:
        raise LlmProviderNotConfiguredError(
            "LLM provider is not configured. Set LLM_PROVIDER, LLM_API_KEY, and LLM_MODEL."
        )
    if current.llm_provider in {LlmProvider.OPENAI, LlmProvider.AZURE_OPENAI}:
        return OpenAiCompatibleClient(current)
    if current.llm_provider is LlmProvider.ANTHROPIC:
        return AnthropicClient(current)
    raise LlmProviderNotConfiguredError(f"Unsupported LLM provider: {current.llm_provider.value}")
