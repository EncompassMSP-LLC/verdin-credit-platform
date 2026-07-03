"""Portal push notification configuration and send helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from typing import Protocol

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.core.feature_flags import FeatureFlag, is_feature_enabled


class PortalPushProvider(StrEnum):
    NONE = "none"
    WEB_PUSH = "web_push"


class PortalPushSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    portal_push_provider: PortalPushProvider = Field(default=PortalPushProvider.NONE)
    portal_push_vapid_public_key: str | None = None
    portal_push_vapid_private_key: str | None = None
    portal_push_vapid_subject: str | None = None


@dataclass(frozen=True, slots=True)
class PortalPushMessage:
    title: str
    body: str
    action_url: str | None = None


@dataclass(frozen=True, slots=True)
class PortalPushSendResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None


class PortalPushStatus:
    def __init__(
        self,
        *,
        enabled: bool,
        ready: bool,
        provider: str,
        vapid_public_key: str | None,
        blockers: list[str],
    ) -> None:
        self.enabled = enabled
        self.ready = ready
        self.provider = provider
        self.vapid_public_key = vapid_public_key
        self.blockers = blockers


class PortalPushNotReadyError(Exception):
    def __init__(self, blockers: list[str]) -> None:
        self.blockers = blockers
        super().__init__("Portal push is not ready")


class PortalPushAdapter(Protocol):
    async def send(
        self,
        *,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        message: PortalPushMessage,
    ) -> PortalPushSendResult: ...


class NoopPortalPushAdapter:
    async def send(
        self,
        *,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        message: PortalPushMessage,
    ) -> PortalPushSendResult:
        _ = (endpoint, p256dh_key, auth_key, message)
        return PortalPushSendResult(
            success=True,
            provider_message_id="noop-portal-push",
        )


class WebPushPortalPushAdapter:
    """Scaffold adapter — records intent without external Web Push HTTP calls."""

    async def send(
        self,
        *,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        message: PortalPushMessage,
    ) -> PortalPushSendResult:
        _ = (p256dh_key, auth_key, message)
        if not endpoint:
            return PortalPushSendResult(success=False, error="Push endpoint is required")
        return PortalPushSendResult(
            success=True,
            provider_message_id=f"web-push-scaffold:{endpoint[:48]}",
        )


@lru_cache
def get_portal_push_settings() -> PortalPushSettings:
    return PortalPushSettings()


def get_portal_push_status(settings: PortalPushSettings | None = None) -> PortalPushStatus:
    feature_enabled = is_feature_enabled(FeatureFlag.ENABLE_PORTAL_PUSH)
    current = settings or get_portal_push_settings()
    blockers: list[str] = []

    if not feature_enabled:
        blockers.append("ENABLE_PORTAL_PUSH is false")

    if current.portal_push_provider == PortalPushProvider.NONE:
        blockers.append("PORTAL_PUSH_PROVIDER is not configured")

    if current.portal_push_provider == PortalPushProvider.WEB_PUSH:
        if not current.portal_push_vapid_public_key:
            blockers.append("PORTAL_PUSH_VAPID_PUBLIC_KEY is not configured")
        if not current.portal_push_vapid_private_key:
            blockers.append("PORTAL_PUSH_VAPID_PRIVATE_KEY is not configured")
        if not current.portal_push_vapid_subject:
            blockers.append("PORTAL_PUSH_VAPID_SUBJECT is not configured")

    return PortalPushStatus(
        enabled=feature_enabled,
        ready=len(blockers) == 0,
        provider=current.portal_push_provider.value,
        vapid_public_key=current.portal_push_vapid_public_key,
        blockers=blockers,
    )


def require_portal_push_ready(settings: PortalPushSettings | None = None) -> PortalPushStatus:
    status = get_portal_push_status(settings)
    if not status.ready:
        raise PortalPushNotReadyError(status.blockers)
    return status


def get_portal_push_adapter(settings: PortalPushSettings | None = None) -> PortalPushAdapter:
    current = settings or get_portal_push_settings()
    if current.portal_push_provider == PortalPushProvider.WEB_PUSH:
        return WebPushPortalPushAdapter()
    return NoopPortalPushAdapter()


async def send_portal_push_message(
    *,
    endpoint: str,
    p256dh_key: str,
    auth_key: str,
    message: PortalPushMessage,
    settings: PortalPushSettings | None = None,
) -> PortalPushSendResult:
    current = settings or get_portal_push_settings()
    status = require_portal_push_ready(current)
    adapter = get_portal_push_adapter(current)
    _ = status
    return await adapter.send(
        endpoint=endpoint,
        p256dh_key=p256dh_key,
        auth_key=auth_key,
        message=message,
    )
