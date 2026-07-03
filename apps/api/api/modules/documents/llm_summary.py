"""LLM-powered document summary generation."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from verdin_llm_gateway import (
    LlmChatMessage,
    LlmCompletionClient,
    LlmFeatureDisabledError,
    LlmPiiPolicyError,
    LlmProviderNotConfiguredError,
    get_llm_completion_client,
    get_llm_settings,
    scrub_payload,
)

from api.core.events import publish_platform_event
from api.core.llm import require_llm_gateway
from api.core.permissions import has_permission
from api.modules.auth.models import User
from api.modules.documents.metadata_models import DocumentMetadata
from api.modules.documents.metadata_repository import DocumentMetadataRepository
from api.modules.documents.models import Document
from api.modules.documents.permissions import DOCUMENT_WRITE_ROLE
from api.modules.documents.repository import DocumentRepository
from api.modules.documents.schemas import DocumentLlmSummaryResponse
from api.modules.timeline.builders import document_llm_summary_event

OCR_EXCERPT_MAX_CHARS = 4000


class DocumentLlmSummaryService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        metadata_repo: DocumentMetadataRepository,
        session: AsyncSession | None = None,
        llm_client: LlmCompletionClient | None = None,
    ) -> None:
        self._documents = document_repo
        self._metadata = metadata_repo
        self._session = session
        self._llm_client = llm_client

    @classmethod
    def from_session(cls, session: AsyncSession) -> DocumentLlmSummaryService:
        return cls(
            DocumentRepository(session),
            DocumentMetadataRepository(session),
            session=session,
        )

    def _require_organization(self, user: User) -> uuid.UUID:
        if user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to an organization",
            )
        return user.organization_id

    def _require_write(self, user: User) -> None:
        if not has_permission(user.role, DOCUMENT_WRITE_ROLE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to generate document summaries",
            )

    async def _get_document(self, document_id: uuid.UUID, organization_id: uuid.UUID) -> Document:
        document = await self._documents.get_by_id(document_id, organization_id=organization_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document

    @staticmethod
    def _ocr_excerpt(document: Document) -> str | None:
        if not document.ocr_text:
            return None
        text = document.ocr_text.strip()
        if not text:
            return None
        if len(text) <= OCR_EXCERPT_MAX_CHARS:
            return text
        return f"{text[:OCR_EXCERPT_MAX_CHARS]}…"

    @staticmethod
    def _metadata_context(metadata: DocumentMetadata | None) -> dict[str, object] | None:
        if metadata is None:
            return None
        return dict(metadata.as_resolution_metadata())

    @staticmethod
    def _build_document_context(
        document: Document,
        metadata: DocumentMetadata | None,
    ) -> dict[str, object]:
        return {
            "document": {
                "title": document.title,
                "file_name": document.file_name,
                "document_type": document.document_type,
                "processing_status": document.processing_status,
                "metadata_status": (
                    metadata.metadata_status if metadata is not None else "pending"
                ),
                "description": document.description,
                "mime_type": document.mime_type,
            },
            "metadata": DocumentLlmSummaryService._metadata_context(metadata),
            "ocr_excerpt": DocumentLlmSummaryService._ocr_excerpt(document),
        }

    @staticmethod
    def _build_prompt(context: dict[str, object]) -> tuple[str, str]:
        system_prompt = (
            "You are a credit repair operations assistant. Summarize the document context "
            "for staff review. Focus on document type, extracted metadata, and key facts "
            "from OCR text when present. Do not invent facts not present in the context."
        )
        user_prompt = (
            "Generate a concise document summary from this scrubbed JSON context:\n"
            f"{json.dumps(context, indent=2, default=str)}"
        )
        return system_prompt, user_prompt

    @staticmethod
    def _prompt_hash(system_prompt: str, user_prompt: str) -> str:
        digest = hashlib.sha256()
        digest.update(system_prompt.encode("utf-8"))
        digest.update(b"\n")
        digest.update(user_prompt.encode("utf-8"))
        return digest.hexdigest()

    async def generate_summary(
        self,
        user: User,
        document_id: uuid.UUID,
    ) -> DocumentLlmSummaryResponse:
        self._require_write(user)
        organization_id = self._require_organization(user)

        try:
            gate_status = require_llm_gateway()
        except LlmFeatureDisabledError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except LlmProviderNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except LlmPiiPolicyError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        document = await self._get_document(document_id, organization_id)
        metadata = await self._metadata.get_metadata_by_document(
            document_id,
            organization_id=organization_id,
        )

        raw_context = self._build_document_context(document, metadata)
        scrubbed_context = scrub_payload(raw_context)
        system_prompt, user_prompt = self._build_prompt(scrubbed_context)
        prompt_hash = self._prompt_hash(system_prompt, user_prompt)

        client = self._llm_client or get_llm_completion_client(get_llm_settings())
        try:
            completion = await client.complete(
                [
                    LlmChatMessage(role="system", content=system_prompt),
                    LlmChatMessage(role="user", content=user_prompt),
                ],
                model=gate_status.model,
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

        generated_at = datetime.now(UTC)
        if self._session is not None:
            await publish_platform_event(
                self._session,
                document_llm_summary_event(
                    document=document,
                    performed_by=user.id,
                    model=completion.model,
                    provider=completion.provider,
                    prompt_hash=prompt_hash,
                    generated_at=generated_at,
                ),
            )

        return DocumentLlmSummaryResponse(
            document_id=document.id,
            summary=completion.content,
            model=completion.model,
            provider=completion.provider,
            prompt_hash=prompt_hash,
            generated_at=generated_at,
            pii_scrubbed=True,
        )
