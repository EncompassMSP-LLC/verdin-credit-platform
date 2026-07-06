"""Admin-gated HRIS passwordless UI readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.saml_passwordless_enrollment import get_saml_passwordless_enrollment_status


@dataclass(frozen=True)
class HrisPasswordlessUiStatus:
    enabled: bool
    ready: bool
    passwordless_enrollment_ready: bool
    blockers: tuple[str, ...]


def get_hris_passwordless_ui_status() -> HrisPasswordlessUiStatus:
    ui_enabled = is_feature_enabled(FeatureFlag.ENABLE_HRIS_PASSWORDLESS_UI)
    enrollment_status = get_saml_passwordless_enrollment_status()

    blockers: list[str] = []
    if not ui_enabled:
        blockers.append("ENABLE_HRIS_PASSWORDLESS_UI is false")
    if ui_enabled and not enrollment_status.ready:
        blockers.extend(enrollment_status.blockers)

    enabled = ui_enabled and enrollment_status.enabled
    return HrisPasswordlessUiStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        passwordless_enrollment_ready=enrollment_status.ready,
        blockers=tuple(blockers),
    )
