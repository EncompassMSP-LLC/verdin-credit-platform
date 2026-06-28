"""Shared core package — reusable utilities for all domain modules."""

from api.core.audit import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
    apply_audit_on_create,
    apply_audit_on_update,
)
from api.core.config import Settings, get_settings
from api.core.constants import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ROLE_LABELS,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_BEARER,
    TOKEN_TYPE_REFRESH,
    UserRole,
)
from api.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
    VerdinError,
    register_exception_handlers,
)
from api.core.logging import get_logger, setup_logging
from api.core.pagination import PaginatedResponse, PaginationParams, paginate
from api.core.permissions import ROLE_LEVELS, RoleLevel, has_permission
from api.core.responses import (
    BaseSchema,
    ErrorResponse,
    HealthResponse,
    IDResponse,
    MessageResponse,
    VersionResponse,
)
from api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "ROLE_LABELS",
    "ROLE_LEVELS",
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_BEARER",
    "TOKEN_TYPE_REFRESH",
    "AuditMixin",
    "BaseSchema",
    "ConflictError",
    "ErrorResponse",
    "ForbiddenError",
    "HealthResponse",
    "IDResponse",
    "MessageResponse",
    "NotFoundError",
    "PaginatedResponse",
    "PaginationParams",
    "RoleLevel",
    "Settings",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UnauthorizedError",
    "UserRole",
    "ValidationError",
    "VerdinError",
    "VersionResponse",
    "apply_audit_on_create",
    "apply_audit_on_update",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_logger",
    "get_settings",
    "has_permission",
    "hash_password",
    "paginate",
    "register_exception_handlers",
    "setup_logging",
    "verify_password",
]
