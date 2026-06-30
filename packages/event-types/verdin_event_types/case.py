"""Case domain event types."""

from enum import StrEnum


class CaseEventType(StrEnum):
    CASE_CREATED = "CASE_CREATED"
    CASE_UPDATED = "CASE_UPDATED"
    CASE_CLOSED = "CASE_CLOSED"
