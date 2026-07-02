"""LLM completion client unit tests."""

import pytest
from verdin_llm_gateway.client import LlmChatMessage, LlmGatewaySettings, LlmProvider, OpenAiCompatibleClient


@pytest.mark.asyncio
async def test_openai_compatible_client_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json() -> dict[str, object]:
            return {"choices": [{"message": {"content": "Summary text"}}]}

    class FakeClient:
        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, *args: object, **kwargs: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr("verdin_llm_gateway.client.httpx.AsyncClient", lambda **kwargs: FakeClient())

    settings = LlmGatewaySettings(
        llm_provider=LlmProvider.OPENAI,
        llm_api_key="test-key",
        llm_model="gpt-4o-mini",
    )
    client = OpenAiCompatibleClient(settings)
    result = await client.complete([LlmChatMessage(role="user", content="Summarize")])

    assert result.content == "Summary text"
    assert result.model == "gpt-4o-mini"
    assert result.provider == "openai"
