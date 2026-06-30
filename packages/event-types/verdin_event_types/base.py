"""Shared event type constants."""

from enum import StrEnum


class EventCategory(StrEnum):
    CASE = "case"
    ACCOUNT = "account"
    DOCUMENT = "document"
    AUTH = "auth"
    TASK = "task"
    AI = "ai"
