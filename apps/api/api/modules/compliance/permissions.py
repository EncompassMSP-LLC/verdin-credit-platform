"""Compliance center permissions."""

from api.core.constants import UserRole

COMPLIANCE_READ_ROLE = UserRole.READ_ONLY
COMPLIANCE_WRITE_ROLE = UserRole.CASE_MANAGER
COMPLIANCE_ADMIN_ROLE = UserRole.ADMIN
