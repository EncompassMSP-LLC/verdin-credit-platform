"""Admin-gated SAML certificate rotation readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.hris_bidirectional_sync import get_hris_bidirectional_sync_status


@dataclass(frozen=True)
class SamlCertificateRotationStatus:
    enabled: bool
    ready: bool
    hris_sync_ready: bool
    blockers: tuple[str, ...]


def get_saml_certificate_rotation_status() -> SamlCertificateRotationStatus:
    rotation_enabled = is_feature_enabled(FeatureFlag.ENABLE_SAML_CERTIFICATE_ROTATION)
    hris_status = get_hris_bidirectional_sync_status()

    blockers: list[str] = []
    if not rotation_enabled:
        blockers.append("ENABLE_SAML_CERTIFICATE_ROTATION is false")
    if rotation_enabled and not hris_status.ready:
        blockers.extend(hris_status.blockers)

    enabled = rotation_enabled and hris_status.enabled
    return SamlCertificateRotationStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        hris_sync_ready=hris_status.ready,
        blockers=tuple(blockers),
    )
