"""Application-wide constants and enumerations."""

from enum import StrEnum

APP_NAME = "Verdin Credit Platform"
APP_VERSION = "4.2.0"

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_BEARER = "bearer"

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    CASE_MANAGER = "case_manager"
    REVIEWER = "reviewer"
    READ_ONLY = "read_only"


ROLE_LABELS: dict[UserRole, str] = {
    UserRole.OWNER: "Owner",
    UserRole.ADMIN: "Admin",
    UserRole.CASE_MANAGER: "Case Manager",
    UserRole.REVIEWER: "Reviewer",
    UserRole.READ_ONLY: "Read Only",
}
