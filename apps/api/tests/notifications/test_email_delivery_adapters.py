"""Email delivery adapter unit tests."""

import pytest

from api.core.email_delivery import (
    EmailDeliveryNotReadyError,
    EmailDeliverySettings,
    EmailMessage,
    EmailProvider,
    SendGridEmailAdapter,
    get_email_delivery_status,
    require_email_delivery_ready,
    send_email_message,
)


@pytest.mark.asyncio
async def test_sendgrid_adapter_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        status_code = 202
        text = ""
        headers = {"X-Message-Id": "sg-123"}

    class FakeClient:
        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, *args: object, **kwargs: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr("api.core.email_delivery.httpx.AsyncClient", lambda **kwargs: FakeClient())

    settings = EmailDeliverySettings(
        email_provider=EmailProvider.SENDGRID,
        email_from_address="no-reply@example.com",
        email_sendgrid_api_key="test-key",
    )
    adapter = SendGridEmailAdapter(settings)
    result = await adapter.send(
        EmailMessage(to="user@example.com", subject="Hello", body_text="Body"),
        from_address="no-reply@example.com",
    )
    assert result.success is True
    assert result.provider_message_id == "sg-123"


def test_require_email_delivery_ready_raises_when_blocked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_EMAIL_DELIVERY", "false")
    from api.core.email_delivery import get_email_delivery_settings

    get_email_delivery_settings.cache_clear()
    with pytest.raises(EmailDeliveryNotReadyError):
        require_email_delivery_ready()


@pytest.mark.asyncio
async def test_send_email_message_uses_injected_adapter() -> None:
    class StubAdapter:
        async def send(self, message: EmailMessage, *, from_address: str):
            assert message.to == "user@example.com"
            assert from_address == "no-reply@example.com"
            from api.core.email_delivery import EmailSendResult

            return EmailSendResult(success=True, provider_message_id="stub")

    settings = EmailDeliverySettings(
        email_provider=EmailProvider.SMTP,
        email_from_address="no-reply@example.com",
        email_smtp_host="smtp.example.com",
    )

    def fake_feature_enabled(flag: object) -> bool:
        return True

    from api.core import email_delivery

    original = email_delivery.is_feature_enabled
    email_delivery.is_feature_enabled = fake_feature_enabled  # type: ignore[method-assign]
    try:
        result = await send_email_message(
            EmailMessage(to="user@example.com", subject="Hi", body_text="There"),
            settings=settings,
            adapter=StubAdapter(),
        )
    finally:
        email_delivery.is_feature_enabled = original

    assert result.success is True
    assert result.provider_message_id == "stub"


def test_get_email_delivery_status_sendgrid_blocker() -> None:
    settings = EmailDeliverySettings(
        email_provider=EmailProvider.SENDGRID,
        email_from_address="no-reply@example.com",
    )
    status = get_email_delivery_status(settings)
    assert any("EMAIL_SENDGRID_API_KEY" in blocker for blocker in status.blockers)


def test_get_email_delivery_status_microsoft_graph_blockers() -> None:
    settings = EmailDeliverySettings(
        email_provider=EmailProvider.MICROSOFT_GRAPH,
        email_from_address="info@example.com",
    )
    status = get_email_delivery_status(settings)
    assert any("EMAIL_GRAPH_TENANT_ID" in b for b in status.blockers)
    assert any("EMAIL_GRAPH_CLIENT_ID" in b for b in status.blockers)
    assert any("EMAIL_GRAPH_CLIENT_SECRET" in b for b in status.blockers)


def test_get_email_delivery_status_microsoft_graph_ready() -> None:
    settings = EmailDeliverySettings(
        email_provider=EmailProvider.MICROSOFT_GRAPH,
        email_from_address="info@example.com",
        email_graph_tenant_id="tenant-id",
        email_graph_client_id="client-id",
        email_graph_client_secret="client-secret",
    )

    def fake_feature_enabled(flag: object) -> bool:
        return True

    from api.core import email_delivery

    original = email_delivery.is_feature_enabled
    email_delivery.is_feature_enabled = fake_feature_enabled  # type: ignore[method-assign]
    try:
        status = get_email_delivery_status(settings)
    finally:
        email_delivery.is_feature_enabled = original

    assert status.ready is True
    assert status.provider == "microsoft_graph"
    assert status.blockers == []


@pytest.mark.asyncio
async def test_microsoft_graph_adapter_success(monkeypatch: pytest.MonkeyPatch) -> None:
    from api.core import email_delivery

    email_delivery._graph_token_cache.clear()
    calls: list[tuple[str, dict[str, object]]] = []

    class FakeResponse:
        def __init__(self, status_code: int, payload: dict[str, object] | None = None) -> None:
            self.status_code = status_code
            self._payload = payload or {}
            self.text = ""
            self.headers: dict[str, str] = {}

        def json(self) -> dict[str, object]:
            return self._payload

    class FakeClient:
        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, url: str, *args: object, **kwargs: object) -> FakeResponse:
            calls.append((url, kwargs))
            if "oauth2/v2.0/token" in url:
                return FakeResponse(
                    200,
                    {"access_token": "graph-token", "expires_in": 3600},
                )
            assert "Authorization" in kwargs.get("headers", {})  # type: ignore[operator]
            assert "sendMail" in url
            return FakeResponse(202)

    monkeypatch.setattr("api.core.email_delivery.httpx.AsyncClient", lambda **kwargs: FakeClient())

    settings = EmailDeliverySettings(
        email_provider=EmailProvider.MICROSOFT_GRAPH,
        email_from_address="info@example.com",
        email_graph_tenant_id="tenant-id",
        email_graph_client_id="client-id",
        email_graph_client_secret="client-secret",
    )
    from api.core.email_delivery import MicrosoftGraphEmailAdapter

    adapter = MicrosoftGraphEmailAdapter(settings)
    result = await adapter.send(
        EmailMessage(to="user@example.com", subject="Hello", body_text="Body"),
        from_address="info@example.com",
    )
    assert result.success is True
    assert len(calls) == 2
    assert "oauth2/v2.0/token" in calls[0][0]
    assert "sendMail" in calls[1][0]


@pytest.mark.asyncio
async def test_smtp_adapter_skips_tls_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    tls_called: list[bool] = []

    class FakeSmtp:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            assert host == "mailpit"
            assert port == 1025

        def __enter__(self) -> "FakeSmtp":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def starttls(self) -> None:
            tls_called.append(True)

        def login(self, username: str, password: str) -> None:
            raise AssertionError("login should not be called for Mailpit")

        def send_message(self, msg: object) -> None:
            return None

    monkeypatch.setattr("api.core.email_delivery.smtplib.SMTP", FakeSmtp)

    from api.core.email_delivery import SmtpEmailAdapter

    settings = EmailDeliverySettings(
        email_provider=EmailProvider.SMTP,
        email_from_address="no-reply@example.com",
        email_smtp_host="mailpit",
        email_smtp_port=1025,
        email_smtp_use_tls=False,
    )
    adapter = SmtpEmailAdapter(settings)
    result = await adapter.send(
        EmailMessage(to="user@example.com", subject="Hello", body_text="Body"),
        from_address="no-reply@example.com",
    )
    assert result.success is True
    assert tls_called == []
