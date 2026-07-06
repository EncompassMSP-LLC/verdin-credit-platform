"""Admin-gated SAML passwordless enrollment readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.saml_automated_rotation import get_saml_automated_rotation_status


@dataclass(frozen=True)
class SamlPasswordlessEnrollmentStatus:
    enabled: bool
    ready: bool
    automated_rotation_ready: bool
    blockers: tuple[str, ...]


def get_saml_passwordless_enrollment_status() -> SamlPasswordlessEnrollmentStatus:
    enrollment_enabled = is_feature_enabled(FeatureFlag.ENABLE_SAML_PASSWORDLESS_ENROLLMENT)
    automated_status = get_saml_automated_rotation_status()

    blockers: list[str] = []
    if not enrollment_enabled:
        blockers.append("ENABLE_SAML_PASSWORDLESS_ENROLLMENT is false")
    if enrollment_enabled and not automated_status.ready:
        blockers.extend(automated_status.blockers)

    enabled = enrollment_enabled and automated_status.enabled
    return SamlPasswordlessEnrollmentStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        automated_rotation_ready=automated_status.ready,
        blockers=tuple(blockers),
    )
