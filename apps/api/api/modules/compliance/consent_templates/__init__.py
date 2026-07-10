"""Consent document templates — defaults, rendering, and merge-field context."""

from api.modules.compliance.consent_templates.keys import (
    DISPUTE_MAIL_REQUIRED_TEMPLATES,
    LEGAL_REVIEW_NOTICE,
    TEMPLATE_CONSENT_TYPE,
    TEMPLATE_LABELS,
    ConsentDocumentTemplateKey,
)

__all__ = [
    "ConsentDocumentTemplateKey",
    "DISPUTE_MAIL_REQUIRED_TEMPLATES",
    "LEGAL_REVIEW_NOTICE",
    "TEMPLATE_CONSENT_TYPE",
    "TEMPLATE_LABELS",
]
