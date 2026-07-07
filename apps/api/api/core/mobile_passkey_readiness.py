"""Admin-gated mobile passkey readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.hris_passwordless_ui import get_hris_passwordless_ui_status


@dataclass(frozen=True)
class MobilePasskeyReadinessStatus:
    enabled: bool
    ready: bool
    hris_passwordless_ui_ready: bool
    blockers: tuple[str, ...]


def get_mobile_passkey_readiness_status() -> MobilePasskeyReadinessStatus:
    passkey_enabled = is_feature_enabled(FeatureFlag.ENABLE_MOBILE_PASSKEY_READINESS)
    ui_status = get_hris_passwordless_ui_status()

    blockers: list[str] = []
    if not passkey_enabled:
        blockers.append("ENABLE_MOBILE_PASSKEY_READINESS is false")
    if passkey_enabled and not ui_status.ready:
        blockers.extend(ui_status.blockers)

    enabled = passkey_enabled and ui_status.enabled
    return MobilePasskeyReadinessStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        hris_passwordless_ui_ready=ui_status.ready,
        blockers=tuple(blockers),
    )
