"""Account repository protocol."""

import uuid
from typing import Any, Protocol, runtime_checkable

from api.modules.accounts.models import Account
from api.modules.accounts.repository import AccountListFilters


@runtime_checkable
class AccountRepositoryProtocol(Protocol):
    async def get_by_id(
        self,
        account_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
    ) -> Account | None: ...

    async def list_accounts(
        self,
        filters: AccountListFilters,
    ) -> tuple[list[Account], int]: ...

    async def list_by_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Account], int]: ...

    async def create(self, account: Account) -> Account: ...

    async def update(self, account: Account) -> Account: ...

    async def get_intelligence_summary(
        self,
        organization_id: uuid.UUID,
        *,
        case_id: uuid.UUID | None = None,
    ) -> dict[str, Any]: ...
