"""Role-based access control utilities."""

from enum import IntEnum

from api.core.constants import UserRole


class RoleLevel(IntEnum):
    READ_ONLY = 1
    REVIEWER = 2
    CASE_MANAGER = 3
    ADMIN = 4
    OWNER = 5


ROLE_LEVELS: dict[UserRole, RoleLevel] = {
    UserRole.READ_ONLY: RoleLevel.READ_ONLY,
    UserRole.REVIEWER: RoleLevel.REVIEWER,
    UserRole.CASE_MANAGER: RoleLevel.CASE_MANAGER,
    UserRole.ADMIN: RoleLevel.ADMIN,
    UserRole.OWNER: RoleLevel.OWNER,
}


def has_permission(user_role: UserRole, required_role: UserRole) -> bool:
    return ROLE_LEVELS[user_role] >= ROLE_LEVELS[required_role]
