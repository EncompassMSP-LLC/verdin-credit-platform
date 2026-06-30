"""Task management permissions."""

from api.core.constants import UserRole

TASK_READ_ROLE = UserRole.READ_ONLY
TASK_WRITE_ROLE = UserRole.CASE_MANAGER
TASK_DELETE_ROLE = UserRole.ADMIN
