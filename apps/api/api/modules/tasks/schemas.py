"""Tasks domain schemas."""

import uuid
from datetime import datetime

from api.core.responses import BaseSchema
from api.modules.tasks.models import TaskPriority, TaskStatus


class TaskResponse(BaseSchema):
    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    case_id: uuid.UUID
    assigned_to_id: uuid.UUID | None
    created_at: datetime
