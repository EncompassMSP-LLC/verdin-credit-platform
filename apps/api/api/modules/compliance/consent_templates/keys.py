"""Consent and contract document template identifiers."""

from enum import StrEnum

from api.modules.compliance.models import ConsentType


class ConsentDocumentTemplateKey(StrEnum):
    CROA_DISCLOSURE = "croa_disclosure"
    CROA_SERVICE_AGREEMENT = "croa_service_agreement"
    FCRA_AUTHORIZATION = "fcra_authorization"


DISPUTE_MAIL_REQUIRED_TEMPLATES: tuple[ConsentDocumentTemplateKey, ...] = (
    ConsentDocumentTemplateKey.CROA_DISCLOSURE,
    ConsentDocumentTemplateKey.CROA_SERVICE_AGREEMENT,
    ConsentDocumentTemplateKey.FCRA_AUTHORIZATION,
)

TEMPLATE_LABELS: dict[ConsentDocumentTemplateKey, str] = {
    ConsentDocumentTemplateKey.CROA_DISCLOSURE: "CROA disclosure statement",
    ConsentDocumentTemplateKey.CROA_SERVICE_AGREEMENT: "Credit repair service agreement",
    ConsentDocumentTemplateKey.FCRA_AUTHORIZATION: "FCRA dispute authorization",
}

TEMPLATE_CONSENT_TYPE: dict[ConsentDocumentTemplateKey, ConsentType] = {
    ConsentDocumentTemplateKey.CROA_DISCLOSURE: ConsentType.CROA_SERVICES,
    ConsentDocumentTemplateKey.CROA_SERVICE_AGREEMENT: ConsentType.CROA_SERVICES,
    ConsentDocumentTemplateKey.FCRA_AUTHORIZATION: ConsentType.FCRA_DISPUTE,
}

LEGAL_REVIEW_NOTICE = (
    "DRAFT FOR LEGAL REVIEW — This template is a starter document only. "
    "Your organization's counsel must review and approve all language, fees, "
    "and cancellation terms before use with consumers."
)
