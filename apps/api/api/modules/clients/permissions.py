"""Client management permissions."""

from api.core.constants import UserRole

CLIENT_READ_ROLE = UserRole.READ_ONLY
CLIENT_WRITE_ROLE = UserRole.CASE_MANAGER
CLIENT_DELETE_ROLE = UserRole.ADMIN
