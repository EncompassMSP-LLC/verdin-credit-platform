"""Compliance center timeline event types."""

from enum import StrEnum


class ComplianceEventType(StrEnum):
    CONSENT_RECORDED = "compliance.consent_recorded"
    CONSENT_WITHDRAWN = "compliance.consent_withdrawn"
    RETENTION_POLICY_CREATED = "compliance.retention_policy_created"
    RETENTION_POLICY_UPDATED = "compliance.retention_policy_updated"
