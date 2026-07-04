"""Tests for portal push delivery adapters."""

from unittest.mock import MagicMock

import pytest
from pywebpush import WebPushException

from api.core.portal_push import (
    PortalPushMessage,
    PortalPushProvider,
    PortalPushSettings,
    WebPushPortalPushAdapter,
    get_portal_push_status,
    send_portal_push_message,
)


@pytest.mark.asyncio
async def test_web_push_adapter_success(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_response = MagicMock(status_code=201)

    def fake_webpush(**_kwargs: object) -> MagicMock:
        return fake_response

    monkeypatch.setattr("api.core.portal_push.webpush", fake_webpush)

    settings = PortalPushSettings(
        portal_push_provider=PortalPushProvider.WEB_PUSH,
        portal_push_vapid_public_key="test-public-key",
        portal_push_vapid_private_key="test-private-key",
        portal_push_vapid_subject="mailto:push@verdin.demo",
    )
    adapter = WebPushPortalPushAdapter(settings)
    result = await adapter.send(
        endpoint="https://push.example.test/subscription/1",
        p256dh_key="p256dh",
        auth_key="auth",
        message=PortalPushMessage(title="Hello", body="World", action_url="/portal/messages"),
    )
    assert result.success is True
    assert result.provider_message_id == "web-push:201"


@pytest.mark.asyncio
async def test_web_push_adapter_handles_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_webpush(**_kwargs: object) -> None:
        raise WebPushException("subscription expired")

    monkeypatch.setattr("api.core.portal_push.webpush", fake_webpush)

    settings = PortalPushSettings(
        portal_push_provider=PortalPushProvider.WEB_PUSH,
        portal_push_vapid_public_key="test-public-key",
        portal_push_vapid_private_key="test-private-key",
        portal_push_vapid_subject="mailto:push@verdin.demo",
    )
    adapter = WebPushPortalPushAdapter(settings)
    result = await adapter.send(
        endpoint="https://push.example.test/subscription/1",
        p256dh_key="p256dh",
        auth_key="auth",
        message=PortalPushMessage(title="Hello", body="World"),
    )
    assert result.success is False
    assert "subscription expired" in (result.error or "")


def test_get_portal_push_status_web_push_blockers() -> None:
    settings = PortalPushSettings(portal_push_provider=PortalPushProvider.WEB_PUSH)
    status = get_portal_push_status(settings)
    assert status.provider == "web_push"
    assert status.ready is False
    assert any("VAPID" in blocker for blocker in status.blockers)


@pytest.mark.asyncio
async def test_send_portal_push_message_uses_injected_adapter() -> None:
    class StubAdapter:
        async def send(
            self,
            *,
            endpoint: str,
            p256dh_key: str,
            auth_key: str,
            message: PortalPushMessage,
        ):
            assert endpoint == "https://push.example.test/subscription/1"
            assert p256dh_key == "p256dh"
            assert auth_key == "auth"
            assert message.title == "Hello"
            from api.core.portal_push import PortalPushSendResult

            return PortalPushSendResult(success=True, provider_message_id="stub")

    settings = PortalPushSettings(
        portal_push_provider=PortalPushProvider.WEB_PUSH,
        portal_push_vapid_public_key="test-public-key",
        portal_push_vapid_private_key="test-private-key",
        portal_push_vapid_subject="mailto:push@verdin.demo",
    )

    def fake_feature_enabled(flag: object) -> bool:
        return True

    from api.core import portal_push

    original = portal_push.is_feature_enabled
    portal_push.is_feature_enabled = fake_feature_enabled  # type: ignore[method-assign]
    try:
        result = await send_portal_push_message(
            endpoint="https://push.example.test/subscription/1",
            p256dh_key="p256dh",
            auth_key="auth",
            message=PortalPushMessage(title="Hello", body="World"),
            settings=settings,
            adapter=StubAdapter(),
        )
    finally:
        portal_push.is_feature_enabled = original

    assert result.success is True
    assert result.provider_message_id == "stub"
