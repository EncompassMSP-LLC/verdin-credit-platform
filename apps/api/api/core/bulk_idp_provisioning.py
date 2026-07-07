"""Admin-gated multi-IdP bulk provisioning readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.hris_passwordless_ui import get_hris_passwordless_ui_status


@dataclass(frozen=True)
class BulkIdpProvisioningStatus:
    enabled: bool
    ready: bool
    hris_passwordless_ui_ready: bool
    blockers: tuple[str, ...]


def get_bulk_idp_provisioning_status() -> BulkIdpProvisioningStatus:
    provisioning_enabled = is_feature_enabled(FeatureFlag.ENABLE_MULTI_IDP_BULK_PROVISIONING)
    ui_status = get_hris_passwordless_ui_status()

    blockers: list[str] = []
    if not provisioning_enabled:
        blockers.append("ENABLE_MULTI_IDP_BULK_PROVISIONING is false")
    if provisioning_enabled and not ui_status.ready:
        blockers.extend(ui_status.blockers)

    enabled = provisioning_enabled and ui_status.enabled
    return BulkIdpProvisioningStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        hris_passwordless_ui_ready=ui_status.ready,
        blockers=tuple(blockers),
    )
