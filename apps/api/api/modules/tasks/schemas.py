"""Tasks domain schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from api.core.pagination import PaginationParams
from api.core.responses import BaseSchema
from api.modules.tasks.models import Task, TaskPriority, TaskStatus

TaskSortField = Literal[
    "created_at",
    "updated_at",
    "title",
    "status",
    "priority",
    "due_date",
]
TaskSortOrder = Literal["asc", "desc"]


class TaskCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    assigned_user_id: uuid.UUID | None = None
    source_module: str | None = Field(default=None, max_length=50)
    source_event_id: uuid.UUID | None = None


class TaskUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    assigned_user_id: uuid.UUID | None = None
    source_module: str | None = Field(default=None, max_length=50)
    source_event_id: uuid.UUID | None = None


class TaskListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    case_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    assigned_user_id: uuid.UUID | None = None
    due_before: datetime | None = None
    due_after: datetime | None = None
    overdue: bool | None = None
    sort_by: TaskSortField = "created_at"
    sort_order: TaskSortOrder = "desc"


class TaskResponse(BaseSchema):
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID | None
    account_id: uuid.UUID | None
    document_id: uuid.UUID | None
    assigned_user_id: uuid.UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    completed_at: datetime | None
    completed_by_id: uuid.UUID | None
    source_module: str | None
    source_event_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    created_by_id: uuid.UUID | None
    updated_by_id: uuid.UUID | None

    @classmethod
    def from_model(cls, task: Task) -> "TaskResponse":
        return cls(
            id=task.id,
            organization_id=task.organization_id,
            case_id=task.case_id,
            account_id=task.account_id,
            document_id=task.document_id,
            assigned_user_id=task.assigned_user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            completed_at=task.completed_at,
            completed_by_id=task.completed_by_id,
            source_module=task.source_module,
            source_event_id=task.source_event_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            deleted_at=task.deleted_at,
            created_by_id=task.created_by_id,
            updated_by_id=task.updated_by_id,
        )
