"""Task domain event types."""

from enum import StrEnum


class TaskEventType(StrEnum):
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_REOPENED = "TASK_REOPENED"
    TASK_DELETED = "TASK_DELETED"
