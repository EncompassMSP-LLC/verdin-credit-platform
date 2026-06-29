"""Case repository protocol."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.cases.models import Case
from api.modules.cases.repository import CaseListFilters


@runtime_checkable
class CaseRepositoryProtocol(Protocol):
    async def get_by_id(
        self,
        case_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Case | None: ...

    async def get_by_case_number(self, case_number: str) -> Case | None: ...

    async def list_cases(self, filters: CaseListFilters) -> tuple[list[Case], int]: ...

    async def create(self, case: Case) -> Case: ...

    async def update(self, case: Case) -> Case: ...
