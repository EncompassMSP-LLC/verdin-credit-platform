"""Email delivery configuration, provider adapters, and send helpers."""

from __future__ import annotations

import asyncio
import smtplib
import time
from dataclasses import dataclass
from email.message import EmailMessage as StdEmailMessage
from enum import StrEnum
from functools import lru_cache
from typing import Protocol
from urllib.parse import quote

import httpx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.feature_flags import FeatureFlag, is_feature_enabled

_GRAPH_SCOPE = "https://graph.microsoft.com/.default"
_GRAPH_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
_GRAPH_SEND_MAIL_URL = "https://graph.microsoft.com/v1.0/users/{user}/sendMail"

# tenant:client_id -> (access_token, expires_at_epoch)
_graph_token_cache: dict[str, tuple[str, float]] = {}


class EmailProvider(StrEnum):
    NONE = "none"
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    MICROSOFT_GRAPH = "microsoft_graph"


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
    email_smtp_use_tls: bool = True
    email_smtp_username: str | None = None
    email_smtp_password: str | None = None
    email_sendgrid_api_key: str | None = None
    # Microsoft Graph (OAuth2 client credentials) — preferred for Microsoft 365
    email_graph_tenant_id: str | None = None
    email_graph_client_id: str | None = None
    email_graph_client_secret: str | None = None
    email_graph_save_to_sent_items: bool = True


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
        self._use_tls = settings.email_smtp_use_tls
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
                if self._use_tls:
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


class MicrosoftGraphEmailAdapter:
    """Send mail via Microsoft Graph using app-only (client credentials) OAuth2."""

    def __init__(self, settings: EmailDeliverySettings) -> None:
        self._tenant_id = (settings.email_graph_tenant_id or "").strip()
        self._client_id = (settings.email_graph_client_id or "").strip()
        self._client_secret = settings.email_graph_client_secret or ""
        self._save_to_sent = settings.email_graph_save_to_sent_items

    async def _access_token(self, client: httpx.AsyncClient) -> str:
        cache_key = f"{self._tenant_id}:{self._client_id}"
        cached = _graph_token_cache.get(cache_key)
        now = time.time()
        if cached is not None and cached[1] > now + 60:
            return cached[0]

        token_url = _GRAPH_TOKEN_URL.format(tenant=quote(self._tenant_id, safe=""))
        response = await client.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": _GRAPH_SCOPE,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Graph token request failed: {response.text}")
        payload = response.json()
        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise RuntimeError("Graph token response missing access_token")
        expires_in = int(payload.get("expires_in") or 3600)
        _graph_token_cache[cache_key] = (access_token, now + expires_in)
        return access_token

    async def send(self, message: EmailMessage, *, from_address: str) -> EmailSendResult:
        body_content_type = "HTML" if message.body_html else "Text"
        body_content = message.body_html if message.body_html else message.body_text
        payload = {
            "message": {
                "subject": message.subject,
                "body": {"contentType": body_content_type, "content": body_content},
                "toRecipients": [{"emailAddress": {"address": message.to}}],
            },
            "saveToSentItems": self._save_to_sent,
        }
        user_path = quote(from_address, safe="@")
        send_url = _GRAPH_SEND_MAIL_URL.format(user=user_path)

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                token = await self._access_token(client)
                response = await client.post(
                    send_url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            if response.status_code >= 400:
                return EmailSendResult(success=False, error=response.text)
            # Graph sendMail returns 202 Accepted with empty body
            return EmailSendResult(success=True, provider_message_id=None)
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

    if current.email_provider == EmailProvider.MICROSOFT_GRAPH:
        if not current.email_graph_tenant_id:
            blockers.append("EMAIL_GRAPH_TENANT_ID is not configured for microsoft_graph provider")
        if not current.email_graph_client_id:
            blockers.append("EMAIL_GRAPH_CLIENT_ID is not configured for microsoft_graph provider")
        if not current.email_graph_client_secret:
            blockers.append(
                "EMAIL_GRAPH_CLIENT_SECRET is not configured for microsoft_graph provider"
            )

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
    if current.email_provider == EmailProvider.MICROSOFT_GRAPH:
        return MicrosoftGraphEmailAdapter(current)
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
