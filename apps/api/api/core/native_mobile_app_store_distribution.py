"""Admin-gated native mobile app store distribution helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.native_mobile_passkey_client import get_native_mobile_passkey_client_status


@dataclass(frozen=True)
class NativeMobileAppStoreDistributionStatus:
    enabled: bool
    ready: bool
    native_mobile_passkey_client_ready: bool
    blockers: tuple[str, ...]


def get_native_mobile_app_store_distribution_status() -> NativeMobileAppStoreDistributionStatus:
    distribution_enabled = is_feature_enabled(
        FeatureFlag.ENABLE_NATIVE_MOBILE_APP_STORE_DISTRIBUTION
    )
    client_status = get_native_mobile_passkey_client_status()

    blockers: list[str] = []
    if not distribution_enabled:
        blockers.append("ENABLE_NATIVE_MOBILE_APP_STORE_DISTRIBUTION is false")
    if distribution_enabled and not client_status.ready:
        blockers.extend(client_status.blockers)

    enabled = distribution_enabled and client_status.enabled
    return NativeMobileAppStoreDistributionStatus(
        enabled=enabled,
        ready=enabled and not blockers,
        native_mobile_passkey_client_ready=client_status.ready,
        blockers=tuple(blockers),
    )
