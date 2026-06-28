"""Authentication domain module."""

from api.core.constants import UserRole
from api.core.permissions import has_permission
from api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from api.modules.auth.dependencies import get_current_user, require_role
from api.modules.auth.models import Organization, User
from api.modules.auth.service import AuthService

__all__ = [
    "AuthService",
    "Organization",
    "User",
    "UserRole",
    "get_current_user",
    "has_permission",
    "require_role",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
