"""Compliance center status helpers."""

from api.modules.compliance.models import ConsentType, RetentionScope
from api.modules.compliance.schemas import ComplianceCenterStatusResponse

_COMPLIANCE_CAPABILITIES = [
    "consent_record_crud",
    "consent_withdrawal",
    "retention_policy_placeholders",
    "org_scoped_consent_history",
    "retention_enforcement_jobs",
]

_DEFERRED_CAPABILITIES = [
    "legal_sign_off_workflows",
    "automated_bureau_filing",
    "full_audit_export_suite",
]


def get_compliance_center_status() -> ComplianceCenterStatusResponse:
    return ComplianceCenterStatusResponse(
        consent_records_enabled=True,
        retention_policies_enabled=True,
        consent_type_count=len(ConsentType),
        retention_scope_count=len(RetentionScope),
        capabilities=list(_COMPLIANCE_CAPABILITIES),
        deferred_capabilities=list(_DEFERRED_CAPABILITIES),
    )
