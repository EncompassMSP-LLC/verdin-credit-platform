"""Account repository protocol (Sprint 2 implementation)."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.accounts.models import Account


@runtime_checkable
class AccountRepositoryProtocol(Protocol):
    async def get_by_id(self, account_id: str | uuid.UUID) -> Account | None: ...

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Account]: ...

    async def create(self, account: Account) -> Account: ...

    async def update(self, account: Account) -> Account: ...
