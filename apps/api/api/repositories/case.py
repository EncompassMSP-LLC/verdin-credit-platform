"""Case repository protocol (Sprint 2 implementation)."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.cases.models import Case


@runtime_checkable
class CaseRepositoryProtocol(Protocol):
    async def get_by_id(self, case_id: str | uuid.UUID) -> Case | None: ...

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Case]: ...

    async def create(self, case: Case) -> Case: ...

    async def update(self, case: Case) -> Case: ...
