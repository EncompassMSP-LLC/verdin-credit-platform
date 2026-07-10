"""Signed consent enforcement for dispute workflows."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from api.modules.compliance.consent_signature import is_consent_signed
from api.modules.compliance.consent_templates.keys import (
    DISPUTE_MAIL_REQUIRED_TEMPLATES,
    TEMPLATE_LABELS,
    ConsentDocumentTemplateKey,
)
from api.modules.compliance.models import ConsentStatus, ConsentType
from api.modules.compliance.repository import ConsentListFilters, ConsentRepository

# Legacy consent-type labels retained for manual consent logging UI.
CONSENT_TYPE_LABELS: dict[ConsentType, str] = {
    ConsentType.CROA_SERVICES: "CROA services agreement",
    ConsentType.FCRA_DISPUTE: "FCRA dispute authorization",
    ConsentType.FDCPA_CONTACT: "FDCPA contact consent",
    ConsentType.MARKETING: "Marketing consent",
    ConsentType.DATA_PROCESSING: "Data processing consent",
}

DISPUTE_MAIL_REQUIRED_CONSENTS: tuple[ConsentType, ...] = (
    ConsentType.CROA_SERVICES,
    ConsentType.FCRA_DISPUTE,
)


async def get_missing_signed_template_keys(
    consent_repo: ConsentRepository,
    *,
    organization_id: uuid.UUID,
    client_id: uuid.UUID,
    required_keys: tuple[ConsentDocumentTemplateKey, ...] = DISPUTE_MAIL_REQUIRED_TEMPLATES,
) -> list[ConsentDocumentTemplateKey]:
    records, _ = await consent_repo.list_consents(
        ConsentListFilters(
            organization_id=organization_id,
            client_id=client_id,
            status=ConsentStatus.GRANTED,
            skip=0,
            limit=500,
        )
    )
    signed_keys: set[ConsentDocumentTemplateKey] = set()
    required_values = {key.value for key in required_keys}
    for record in records:
        if record.document_template_key is None:
            continue
        if record.document_template_key not in required_values:
            continue
        if not is_consent_signed(record):
            continue
        signed_keys.add(ConsentDocumentTemplateKey(record.document_template_key))
    return [key for key in required_keys if key not in signed_keys]


async def get_missing_signed_consents(
    consent_repo: ConsentRepository,
    *,
    organization_id: uuid.UUID,
    client_id: uuid.UUID,
    required_types: tuple[ConsentType, ...] = DISPUTE_MAIL_REQUIRED_CONSENTS,
) -> list[ConsentType]:
    """Legacy consent-type view derived from missing template keys."""
    missing_keys = await get_missing_signed_template_keys(
        consent_repo,
        organization_id=organization_id,
        client_id=client_id,
    )
    missing_types: list[ConsentType] = []
    croa_keys = {
        ConsentDocumentTemplateKey.CROA_DISCLOSURE,
        ConsentDocumentTemplateKey.CROA_SERVICE_AGREEMENT,
    }
    if (
        any(key in missing_keys for key in croa_keys)
        and ConsentType.CROA_SERVICES in required_types
    ):
        missing_types.append(ConsentType.CROA_SERVICES)
    if (
        ConsentDocumentTemplateKey.FCRA_AUTHORIZATION in missing_keys
        and ConsentType.FCRA_DISPUTE in required_types
    ):
        missing_types.append(ConsentType.FCRA_DISPUTE)
    return missing_types


async def require_signed_consents(
    consent_repo: ConsentRepository,
    *,
    organization_id: uuid.UUID,
    client_id: uuid.UUID,
    required_keys: tuple[ConsentDocumentTemplateKey, ...] = DISPUTE_MAIL_REQUIRED_TEMPLATES,
) -> None:
    missing = await get_missing_signed_template_keys(
        consent_repo,
        organization_id=organization_id,
        client_id=client_id,
        required_keys=required_keys,
    )
    if not missing:
        return

    missing_labels = [TEMPLATE_LABELS[key] for key in missing]
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": "Signed client consent documents are required before this action",
            "missing_template_keys": [key.value for key in missing],
            "missing_template_labels": missing_labels,
            "missing_consent_types": await _legacy_missing_types(
                consent_repo, organization_id, client_id
            ),
            "missing_consent_labels": [
                CONSENT_TYPE_LABELS[consent_type]
                for consent_type in await get_missing_signed_consents(
                    consent_repo,
                    organization_id=organization_id,
                    client_id=client_id,
                )
            ],
        },
    )


async def _legacy_missing_types(
    consent_repo: ConsentRepository,
    organization_id: uuid.UUID,
    client_id: uuid.UUID,
) -> list[str]:
    missing = await get_missing_signed_consents(
        consent_repo,
        organization_id=organization_id,
        client_id=client_id,
    )
    return [consent_type.value for consent_type in missing]
