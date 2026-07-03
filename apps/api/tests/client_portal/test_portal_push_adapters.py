"""Tests for portal push delivery adapters."""

from api.core.portal_push import (
    PortalPushMessage,
    PortalPushProvider,
    PortalPushSettings,
    WebPushPortalPushAdapter,
    get_portal_push_status,
)


async def test_web_push_adapter_records_scaffold_send() -> None:
    adapter = WebPushPortalPushAdapter()
    result = await adapter.send(
        endpoint="https://push.example.test/subscription/1",
        p256dh_key="p256dh",
        auth_key="auth",
        message=PortalPushMessage(title="Hello", body="World"),
    )
    assert result.success is True
    assert result.provider_message_id is not None


def test_get_portal_push_status_web_push_blockers() -> None:
    settings = PortalPushSettings(portal_push_provider=PortalPushProvider.WEB_PUSH)
    status = get_portal_push_status(settings)
    assert status.provider == "web_push"
    assert status.ready is False
    assert any("VAPID" in blocker for blocker in status.blockers)
