"""Task repository protocol."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.tasks.models import Task
from api.modules.tasks.repository import TaskListFilters


@runtime_checkable
class TaskRepositoryProtocol(Protocol):
    async def get_by_id(
        self,
        task_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Task | None: ...

    async def list_tasks(self, filters: TaskListFilters) -> tuple[list[Task], int]: ...

    async def create(self, task: Task) -> Task: ...

    async def update(self, task: Task) -> Task: ...
