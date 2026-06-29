"""Case management permissions."""

from api.core.constants import UserRole

CASE_READ_ROLE = UserRole.READ_ONLY
CASE_WRITE_ROLE = UserRole.CASE_MANAGER
CASE_DELETE_ROLE = UserRole.ADMIN
