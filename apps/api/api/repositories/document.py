"""Document repository protocol (Sprint 2 implementation)."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.documents.models import Document


@runtime_checkable
class DocumentRepositoryProtocol(Protocol):
    async def get_by_id(self, document_id: str | uuid.UUID) -> Document | None: ...

    async def list_by_case(
        self,
        case_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]: ...

    async def create(self, document: Document) -> Document: ...

    async def update(self, document: Document) -> Document: ...
