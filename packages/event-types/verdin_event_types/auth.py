"""Authentication domain event types."""

from enum import StrEnum


class AuthEventType(StrEnum):
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
