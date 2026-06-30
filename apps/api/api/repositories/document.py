"""Document repository protocol."""

import uuid
from typing import Protocol, runtime_checkable

from api.modules.documents.models import Document, DocumentVersion
from api.modules.documents.parsed_report_models import DocumentParsedCreditReport
from api.modules.documents.repository import DocumentListFilters


@runtime_checkable
class DocumentRepositoryProtocol(Protocol):
    async def get_by_id(
        self,
        document_id: str | uuid.UUID,
        *,
        organization_id: uuid.UUID | None = None,
        include_versions: bool = False,
    ) -> Document | None: ...

    async def find_by_hash(
        self,
        organization_id: uuid.UUID,
        file_hash: str,
    ) -> Document | None: ...

    async def list_documents(
        self,
        filters: DocumentListFilters,
    ) -> tuple[list[Document], int]: ...

    async def create(self, document: Document) -> Document: ...

    async def create_version(self, version: DocumentVersion) -> DocumentVersion: ...

    async def update(self, document: Document) -> Document: ...

    async def list_versions(self, document_id: uuid.UUID) -> list[DocumentVersion]: ...

    async def get_parsed_credit_report(
        self,
        document_id: uuid.UUID,
        *,
        organization_id: uuid.UUID,
    ) -> DocumentParsedCreditReport | None: ...
