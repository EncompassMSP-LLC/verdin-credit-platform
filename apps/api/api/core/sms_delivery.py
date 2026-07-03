"""SMS delivery configuration, provider adapters, and send helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from typing import Protocol

import httpx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.feature_flags import FeatureFlag, is_feature_enabled


class SmsProvider(StrEnum):
    NONE = "none"
    TWILIO = "twilio"


class SmsDeliverySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    sms_provider: SmsProvider = Field(default=SmsProvider.NONE)
    sms_from_number: str | None = None
    sms_twilio_account_sid: str | None = None
    sms_twilio_auth_token: str | None = None


@dataclass(frozen=True, slots=True)
class SmsMessage:
    to: str
    body: str


@dataclass(frozen=True, slots=True)
class SmsSendResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class SmsDeliveryStatus:
    def __init__(
        self,
        *,
        enabled: bool,
        ready: bool,
        provider: str,
        from_number: str | None,
        blockers: list[str],
    ) -> None:
        self.enabled = enabled
        self.ready = ready
        self.provider = provider
        self.from_number = from_number
        self.blockers = blockers


class SmsDeliveryNotReadyError(Exception):
    def __init__(self, blockers: list[str]) -> None:
        self.blockers = blockers
        super().__init__("SMS delivery is not ready")


class SmsProviderAdapter(Protocol):
    async def send(self, message: SmsMessage, *, from_number: str) -> SmsSendResult: ...


class TwilioSmsAdapter:
    def __init__(self, settings: SmsDeliverySettings) -> None:
        self._account_sid = settings.sms_twilio_account_sid or ""
        self._auth_token = settings.sms_twilio_auth_token or ""

    async def send(self, message: SmsMessage, *, from_number: str) -> SmsSendResult:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self._account_sid}/Messages.json"
        payload = {"To": message.to, "From": from_number, "Body": message.body}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    url,
                    auth=(self._account_sid, self._auth_token),
                    data=payload,
                )
            if response.status_code >= 400:
                return SmsSendResult(success=False, error=response.text)
            data = response.json()
            return SmsSendResult(success=True, provider_message_id=data.get("sid"))
        except Exception as exc:  # noqa: BLE001 — provider errors surfaced to audit log
            return SmsSendResult(success=False, error=str(exc))


@lru_cache
def get_sms_delivery_settings() -> SmsDeliverySettings:
    return SmsDeliverySettings()


def get_sms_delivery_status(settings: SmsDeliverySettings | None = None) -> SmsDeliveryStatus:
    feature_enabled = is_feature_enabled(FeatureFlag.ENABLE_SMS_DELIVERY)
    current = settings or get_sms_delivery_settings()
    blockers: list[str] = []

    if not feature_enabled:
        blockers.append("ENABLE_SMS_DELIVERY is false")

    if current.sms_provider == SmsProvider.NONE:
        blockers.append("SMS_PROVIDER is not configured")

    if not current.sms_from_number:
        blockers.append("SMS_FROM_NUMBER is not configured")

    if current.sms_provider == SmsProvider.TWILIO:
        if not current.sms_twilio_account_sid:
            blockers.append("SMS_TWILIO_ACCOUNT_SID is not configured for twilio provider")
        if not current.sms_twilio_auth_token:
            blockers.append("SMS_TWILIO_AUTH_TOKEN is not configured for twilio provider")

    return SmsDeliveryStatus(
        enabled=feature_enabled,
        ready=len(blockers) == 0,
        provider=current.sms_provider.value,
        from_number=current.sms_from_number,
        blockers=blockers,
    )


def require_sms_delivery_ready(
    settings: SmsDeliverySettings | None = None,
) -> SmsDeliveryStatus:
    status = get_sms_delivery_status(settings)
    if not status.ready:
        raise SmsDeliveryNotReadyError(status.blockers)
    return status


def get_sms_provider_adapter(
    settings: SmsDeliverySettings | None = None,
) -> SmsProviderAdapter:
    current = settings or get_sms_delivery_settings()
    if current.sms_provider == SmsProvider.TWILIO:
        return TwilioSmsAdapter(current)
    raise SmsDeliveryNotReadyError(["SMS_PROVIDER is not configured"])


async def send_sms_message(
    message: SmsMessage,
    *,
    settings: SmsDeliverySettings | None = None,
    adapter: SmsProviderAdapter | None = None,
) -> SmsSendResult:
    current = settings or get_sms_delivery_settings()
    status = require_sms_delivery_ready(current)
    from_number = status.from_number
    if from_number is None:
        raise SmsDeliveryNotReadyError(["SMS_FROM_NUMBER is not configured"])

    provider = adapter or get_sms_provider_adapter(current)
    return await provider.send(message, from_number=from_number)
