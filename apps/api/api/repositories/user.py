"""User repository protocol."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.auth.models import User


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(self, user: User) -> User: ...

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]: ...
