"""Email delivery configuration, provider adapters, and send helpers."""

from __future__ import annotations

import asyncio
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage as StdEmailMessage
from enum import StrEnum
from functools import lru_cache
from typing import Protocol

import httpx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.feature_flags import FeatureFlag, is_feature_enabled


class EmailProvider(StrEnum):
    NONE = "none"
    SMTP = "smtp"
    SENDGRID = "sendgrid"


class EmailDeliverySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    email_provider: EmailProvider = Field(default=EmailProvider.NONE)
    email_from_address: str | None = None
    email_smtp_host: str | None = None
    email_smtp_port: int = 587
    email_smtp_username: str | None = None
    email_smtp_password: str | None = None
    email_sendgrid_api_key: str | None = None


@dataclass(frozen=True, slots=True)
class EmailMessage:
    to: str
    subject: str
    body_text: str
    body_html: str | None = None


@dataclass(frozen=True, slots=True)
class EmailSendResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class EmailDeliveryStatus:
    def __init__(
        self,
        *,
        enabled: bool,
        ready: bool,
        provider: str,
        from_address: str | None,
        blockers: list[str],
    ) -> None:
        self.enabled = enabled
        self.ready = ready
        self.provider = provider
        self.from_address = from_address
        self.blockers = blockers


class EmailDeliveryNotReadyError(Exception):
    def __init__(self, blockers: list[str]) -> None:
        self.blockers = blockers
        super().__init__("Email delivery is not ready")


class EmailProviderAdapter(Protocol):
    async def send(self, message: EmailMessage, *, from_address: str) -> EmailSendResult: ...


class SmtpEmailAdapter:
    def __init__(self, settings: EmailDeliverySettings) -> None:
        self._host = settings.email_smtp_host or ""
        self._port = settings.email_smtp_port
        self._username = settings.email_smtp_username
        self._password = settings.email_smtp_password

    async def send(self, message: EmailMessage, *, from_address: str) -> EmailSendResult:
        def _send_sync() -> EmailSendResult:
            msg = StdEmailMessage()
            msg["From"] = from_address
            msg["To"] = message.to
            msg["Subject"] = message.subject
            msg.set_content(message.body_text)
            if message.body_html:
                msg.add_alternative(message.body_html, subtype="html")

            with smtplib.SMTP(self._host, self._port, timeout=30) as smtp:
                smtp.starttls()
                if self._username and self._password:
                    smtp.login(self._username, self._password)
                smtp.send_message(msg)
            return EmailSendResult(success=True)

        try:
            return await asyncio.to_thread(_send_sync)
        except Exception as exc:  # noqa: BLE001 — provider errors surfaced to audit log
            return EmailSendResult(success=False, error=str(exc))


class SendGridEmailAdapter:
    def __init__(self, settings: EmailDeliverySettings) -> None:
        self._api_key = settings.email_sendgrid_api_key or ""

    async def send(self, message: EmailMessage, *, from_address: str) -> EmailSendResult:
        content = [{"type": "text/plain", "value": message.body_text}]
        if message.body_html:
            content.append({"type": "text/html", "value": message.body_html})

        payload = {
            "personalizations": [{"to": [{"email": message.to}]}],
            "from": {"email": from_address},
            "subject": message.subject,
            "content": content,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                )
            if response.status_code >= 400:
                return EmailSendResult(success=False, error=response.text)
            return EmailSendResult(
                success=True,
                provider_message_id=response.headers.get("X-Message-Id"),
            )
        except Exception as exc:  # noqa: BLE001 — provider errors surfaced to audit log
            return EmailSendResult(success=False, error=str(exc))


@lru_cache
def get_email_delivery_settings() -> EmailDeliverySettings:
    return EmailDeliverySettings()


def get_email_delivery_status(settings: EmailDeliverySettings | None = None) -> EmailDeliveryStatus:
    feature_enabled = is_feature_enabled(FeatureFlag.ENABLE_EMAIL_DELIVERY)
    current = settings or get_email_delivery_settings()
    blockers: list[str] = []

    if not feature_enabled:
        blockers.append("ENABLE_EMAIL_DELIVERY is false")

    if current.email_provider == EmailProvider.NONE:
        blockers.append("EMAIL_PROVIDER is not configured")

    if not current.email_from_address:
        blockers.append("EMAIL_FROM_ADDRESS is not configured")

    if current.email_provider == EmailProvider.SMTP and not current.email_smtp_host:
        blockers.append("EMAIL_SMTP_HOST is not configured for smtp provider")

    if current.email_provider == EmailProvider.SENDGRID and not current.email_sendgrid_api_key:
        blockers.append("EMAIL_SENDGRID_API_KEY is not configured for sendgrid provider")

    return EmailDeliveryStatus(
        enabled=feature_enabled,
        ready=len(blockers) == 0,
        provider=current.email_provider.value,
        from_address=current.email_from_address,
        blockers=blockers,
    )


def require_email_delivery_ready(
    settings: EmailDeliverySettings | None = None,
) -> EmailDeliveryStatus:
    status = get_email_delivery_status(settings)
    if not status.ready:
        raise EmailDeliveryNotReadyError(status.blockers)
    return status


def get_email_provider_adapter(
    settings: EmailDeliverySettings | None = None,
) -> EmailProviderAdapter:
    current = settings or get_email_delivery_settings()
    if current.email_provider == EmailProvider.SMTP:
        return SmtpEmailAdapter(current)
    if current.email_provider == EmailProvider.SENDGRID:
        return SendGridEmailAdapter(current)
    raise EmailDeliveryNotReadyError(["EMAIL_PROVIDER is not configured"])


async def send_email_message(
    message: EmailMessage,
    *,
    settings: EmailDeliverySettings | None = None,
    adapter: EmailProviderAdapter | None = None,
) -> EmailSendResult:
    current = settings or get_email_delivery_settings()
    status = require_email_delivery_ready(current)
    from_address = status.from_address
    if from_address is None:
        raise EmailDeliveryNotReadyError(["EMAIL_FROM_ADDRESS is not configured"])

    provider = adapter or get_email_provider_adapter(current)
    return await provider.send(message, from_address=from_address)
