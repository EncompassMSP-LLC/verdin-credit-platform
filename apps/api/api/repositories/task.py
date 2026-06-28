"""Task repository protocol (Sprint 2 implementation)."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.tasks.models import Task


@runtime_checkable
class TaskRepositoryProtocol(Protocol):
    async def get_by_id(self, task_id: str | uuid.UUID) -> Task | None: ...

    async def list_by_case(
        self,
        case_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Task]: ...

    async def create(self, task: Task) -> Task: ...

    async def update(self, task: Task) -> Task: ...
