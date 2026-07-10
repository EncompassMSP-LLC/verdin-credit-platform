"""Helpers for determining whether a consent record counts as signed."""

from api.modules.compliance.models import (
    ConsentRecord,
    ConsentSignatureMethod,
    ConsentStatus,
)


def is_consent_signed(record: ConsentRecord) -> bool:
    if record.status != ConsentStatus.GRANTED:
        return False
    if record.document_id is not None:
        return True
    if record.signature_method in {
        ConsentSignatureMethod.PORTAL_ATTESTATION.value,
        ConsentSignatureMethod.PORTAL_SIGNATURE_IMAGE.value,
        ConsentSignatureMethod.PORTAL_GENERATED_DOCUMENT.value,
    }:
        return record.signed_at is not None and bool(record.signer_name)
    return False
