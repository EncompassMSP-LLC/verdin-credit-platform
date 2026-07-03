"""SMS delivery adapter unit tests."""

import pytest

from api.core.sms_delivery import (
    SmsDeliveryNotReadyError,
    SmsDeliverySettings,
    SmsMessage,
    SmsProvider,
    TwilioSmsAdapter,
    get_sms_delivery_status,
    require_sms_delivery_ready,
    send_sms_message,
)


@pytest.mark.asyncio
async def test_twilio_adapter_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        status_code = 201
        text = ""

        def json(self) -> dict[str, str]:
            return {"sid": "SMfake123"}

    class FakeClient:
        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, *args: object, **kwargs: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr("api.core.sms_delivery.httpx.AsyncClient", lambda **kwargs: FakeClient())

    settings = SmsDeliverySettings(
        sms_provider=SmsProvider.TWILIO,
        sms_from_number="+15555550100",
        sms_twilio_account_sid="ACtest",
        sms_twilio_auth_token="token",
    )
    adapter = TwilioSmsAdapter(settings)
    result = await adapter.send(
        SmsMessage(to="+15555550123", body="Hello"),
        from_number="+15555550100",
    )
    assert result.success is True
    assert result.provider_message_id == "SMfake123"


def test_require_sms_delivery_ready_raises_when_blocked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_SMS_DELIVERY", "false")
    from api.core.sms_delivery import get_sms_delivery_settings

    get_sms_delivery_settings.cache_clear()
    with pytest.raises(SmsDeliveryNotReadyError):
        require_sms_delivery_ready()


@pytest.mark.asyncio
async def test_send_sms_message_uses_injected_adapter() -> None:
    class StubAdapter:
        async def send(self, message: SmsMessage, *, from_number: str):
            assert message.to == "+15555550123"
            assert from_number == "+15555550100"
            from api.core.sms_delivery import SmsSendResult

            return SmsSendResult(success=True, provider_message_id="stub")

    settings = SmsDeliverySettings(
        sms_provider=SmsProvider.TWILIO,
        sms_from_number="+15555550100",
        sms_twilio_account_sid="ACtest",
        sms_twilio_auth_token="token",
    )

    def fake_feature_enabled(flag: object) -> bool:
        return True

    from api.core import sms_delivery

    original = sms_delivery.is_feature_enabled
    sms_delivery.is_feature_enabled = fake_feature_enabled  # type: ignore[method-assign]
    try:
        result = await send_sms_message(
            SmsMessage(to="+15555550123", body="Hi"),
            settings=settings,
            adapter=StubAdapter(),
        )
    finally:
        sms_delivery.is_feature_enabled = original

    assert result.success is True
    assert result.provider_message_id == "stub"


def test_get_sms_delivery_status_twilio_blocker() -> None:
    settings = SmsDeliverySettings(
        sms_provider=SmsProvider.TWILIO,
        sms_from_number="+15555550100",
    )
    status = get_sms_delivery_status(settings)
    assert any("SMS_TWILIO" in blocker for blocker in status.blockers)
