"""Account domain event types."""

from enum import StrEnum


class AccountEventType(StrEnum):
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED"
    ACCOUNT_STATUS_CHANGED = "ACCOUNT_STATUS_CHANGED"
