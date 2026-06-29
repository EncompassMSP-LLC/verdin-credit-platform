"""Task domain event types."""

from enum import StrEnum


class TaskEventType(StrEnum):
    TASK_CREATED = "TASK_CREATED"
    TASK_COMPLETED = "TASK_COMPLETED"
