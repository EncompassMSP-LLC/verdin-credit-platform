"""Admin-gated native mobile passkey client helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.mobile_passkey_readiness import get_mobile_passkey_readiness_status


@dataclass(frozen=True)
class NativeMobilePasskeyClientStatus:
    enabled: bool
    ready: bool
    mobile_passkey_readiness_ready: bool
    blockers: tuple[str, ...]


def get_native_mobile_passkey_client_status() -> NativeMobilePasskeyClientStatus:
    client_enabled = is_feature_enabled(FeatureFlag.ENABLE_NATIVE_MOBILE_PASSKEY_CLIENT)
    readiness_status = get_mobile_passkey_readiness_status()

    blockers: list[str] = []
    if not client_enabled:
        blockers.append("ENABLE_NATIVE_MOBILE_PASSKEY_CLIENT is false")
    if client_enabled and not readiness_status.ready:
        blockers.extend(readiness_status.blockers)

    enabled = client_enabled and readiness_status.enabled
    return NativeMobilePasskeyClientStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        mobile_passkey_readiness_ready=readiness_status.ready,
        blockers=tuple(blockers),
    )
