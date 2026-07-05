"""Admin-gated SAML automated rotation readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.saml_certificate_rotation import get_saml_certificate_rotation_status


@dataclass(frozen=True)
class SamlAutomatedRotationStatus:
    enabled: bool
    ready: bool
    cert_rotation_ready: bool
    blockers: tuple[str, ...]


def get_saml_automated_rotation_status() -> SamlAutomatedRotationStatus:
    automated_enabled = is_feature_enabled(FeatureFlag.ENABLE_SAML_AUTOMATED_ROTATION)
    rotation_status = get_saml_certificate_rotation_status()

    blockers: list[str] = []
    if not automated_enabled:
        blockers.append("ENABLE_SAML_AUTOMATED_ROTATION is false")
    if automated_enabled and not rotation_status.ready:
        blockers.extend(rotation_status.blockers)

    enabled = automated_enabled and rotation_status.enabled
    return SamlAutomatedRotationStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        cert_rotation_ready=rotation_status.ready,
        blockers=tuple(blockers),
    )
