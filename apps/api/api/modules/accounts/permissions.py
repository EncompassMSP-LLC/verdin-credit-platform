"""Account management permissions."""

from api.core.constants import UserRole

ACCOUNT_READ_ROLE = UserRole.READ_ONLY
ACCOUNT_WRITE_ROLE = UserRole.CASE_MANAGER
ACCOUNT_DELETE_ROLE = UserRole.ADMIN
