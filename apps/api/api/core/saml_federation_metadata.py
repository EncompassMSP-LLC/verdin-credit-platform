"""SAML federation metadata upload readiness helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass

from api.core.feature_flags import FeatureFlag, is_feature_enabled
from api.core.idp_federation import get_idp_federation_status

_ENTITY_ID_PATTERN = re.compile(r'entityID="([^"]+)"', re.IGNORECASE)


@dataclass(frozen=True)
class SamlFederationMetadataStatus:
    enabled: bool
    ready: bool
    federation_ready: bool
    blockers: tuple[str, ...]


def get_saml_federation_metadata_status() -> SamlFederationMetadataStatus:
    federation_status = get_idp_federation_status()
    metadata_enabled = is_feature_enabled(FeatureFlag.ENABLE_SAML_FEDERATION_METADATA)

    blockers: list[str] = []
    if not metadata_enabled:
        blockers.append("ENABLE_SAML_FEDERATION_METADATA is false")
    if not federation_status.enabled:
        blockers.append("ENABLE_IDP_FEDERATION is false")
    if metadata_enabled and federation_status.enabled and not federation_status.ready:
        blockers.extend(federation_status.blockers)

    enabled = metadata_enabled and federation_status.enabled
    return SamlFederationMetadataStatus(
        enabled=enabled,
        ready=enabled and federation_status.ready,
        federation_ready=federation_status.ready,
        blockers=tuple(blockers),
    )


def validate_saml_metadata_xml(metadata_xml: str) -> tuple[str | None, str | None]:
    """Return ``(entity_id, error_message)`` — entity ID on success, error on failure."""
    stripped = metadata_xml.strip()
    if not stripped:
        return None, "metadata_xml must not be empty"
    if "EntityDescriptor" not in stripped:
        return None, "metadata_xml must contain an EntityDescriptor element"
    match = _ENTITY_ID_PATTERN.search(stripped)
    if match is None:
        return None, "metadata_xml must include entityID attribute"
    return match.group(1), None
