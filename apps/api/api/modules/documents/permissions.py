"""Document management permissions."""

from api.core.constants import UserRole

DOCUMENT_READ_ROLE = UserRole.READ_ONLY
DOCUMENT_WRITE_ROLE = UserRole.CASE_MANAGER
DOCUMENT_DELETE_ROLE = UserRole.ADMIN
