"""HRIS bidirectional sync scaffold helpers."""

from __future__ import annotations

from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.saml_federation_metadata import get_saml_federation_metadata_status


@dataclass(frozen=True)
class HrisBidirectionalSyncStatus:
    enabled: bool
    ready: bool
    saml_metadata_ready: bool
    blockers: tuple[str, ...]


def get_hris_bidirectional_sync_status() -> HrisBidirectionalSyncStatus:
    sync_enabled = is_feature_enabled(FeatureFlag.ENABLE_HRIS_BIDIRECTIONAL_SYNC)
    metadata_status = get_saml_federation_metadata_status()

    blockers: list[str] = []
    if not sync_enabled:
        blockers.append("ENABLE_HRIS_BIDIRECTIONAL_SYNC is false")
    if not metadata_status.enabled:
        blockers.append("ENABLE_SAML_FEDERATION_METADATA is false")
    if sync_enabled and metadata_status.enabled and not metadata_status.ready:
        blockers.extend(metadata_status.blockers)

    enabled = sync_enabled and metadata_status.enabled
    return HrisBidirectionalSyncStatus(
        enabled=enabled,
        ready=enabled and metadata_status.ready,
        saml_metadata_ready=metadata_status.ready,
        blockers=tuple(blockers),
    )


def compute_hris_sync_run_counts(
    *,
    run_kind: str,
    valid_metadata_upload_count: int,
) -> tuple[int, int]:
    if valid_metadata_upload_count <= 0:
        return 0, 0

    records_synced = 0
    records_skipped = 0
    if run_kind == "employees_inbound":
        records_synced = 1
    elif run_kind == "employees_outbound":
        records_skipped = 1
    return records_synced, records_skipped
