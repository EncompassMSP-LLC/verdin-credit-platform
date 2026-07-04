"""Batch document LLM summary worker processor."""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from verdin_llm_gateway import (
    LlmChatMessage,
    get_llm_completion_client,
    get_llm_settings,
    require_llm_ready,
    scrub_payload,
)

from worker.batch_summary_tables import (
    batch_document_summary_runs_table,
    documents_table,
)
from worker.timeline import append_timeline_event

logger = structlog.get_logger(__name__)

STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
_EVENT_TYPE = "DOCUMENT_LLM_SUMMARY_GENERATED"
_EVENT_CATEGORY = "document"
_OCR_TEXT_MAX_CHARS = 12_000


@dataclass(frozen=True, slots=True)
class BatchDocumentLlmSummaryResult:
    run_id: uuid.UUID
    documents_succeeded: int
    documents_failed: int
    status: str
    error_message: str | None = None


def _truncate_ocr_text(ocr_text: str | None) -> str | None:
    if ocr_text is None:
        return None
    if len(ocr_text) <= _OCR_TEXT_MAX_CHARS:
        return ocr_text
    return ocr_text[:_OCR_TEXT_MAX_CHARS]


def _build_context(row: Any) -> dict[str, object]:
    return {
        "document": {
            "title": row.title,
            "file_name": row.file_name,
            "document_type": row.document_type,
            "processing_status": row.processing_status,
            "ocr_text": _truncate_ocr_text(row.ocr_text),
        }
    }


def _build_prompt(context: dict[str, object]) -> tuple[str, str]:
    system_prompt = (
        "You are a credit repair operations assistant. Summarize the document context "
        "for staff review. Focus on document type, key entities, dispute relevance, "
        "and recommended next actions. Do not invent facts not present in the context."
    )
    user_prompt = (
        "Generate a concise document summary from this scrubbed JSON context:\n"
        f"{json.dumps(context, indent=2, default=str)}"
    )
    return system_prompt, user_prompt


def _prompt_hash(system_prompt: str, user_prompt: str) -> str:
    digest = hashlib.sha256()
    digest.update(system_prompt.encode("utf-8"))
    digest.update(b"\n")
    digest.update(user_prompt.encode("utf-8"))
    return digest.hexdigest()


async def _complete_summary(
    system_prompt: str, user_prompt: str, model: str | None
) -> Any:
    client = get_llm_completion_client(get_llm_settings())
    return await client.complete(
        [
            LlmChatMessage(role="system", content=system_prompt),
            LlmChatMessage(role="user", content=user_prompt),
        ],
        model=model,
    )


def _process_document(
    session: Session,
    *,
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    performed_by_user_id: uuid.UUID | None,
    model: str | None,
) -> bool:
    row = (
        session.execute(
            select(documents_table).where(
                documents_table.c.id == document_id,
                documents_table.c.organization_id == organization_id,
                documents_table.c.deleted_at.is_(None),
            )
        )
        .mappings()
        .first()
    )
    if row is None:
        return False

    context = scrub_payload(_build_context(row))
    system_prompt, user_prompt = _build_prompt(context)
    prompt_hash = _prompt_hash(system_prompt, user_prompt)

    try:
        completion = asyncio.run(_complete_summary(system_prompt, user_prompt, model))
    except Exception:
        logger.exception("batch_document_summary_failed", document_id=str(document_id))
        return False

    generated_at = datetime.now(UTC)
    append_timeline_event(
        session,
        organization_id=organization_id,
        event_type=_EVENT_TYPE,
        event_category=_EVENT_CATEGORY,
        title="LLM document summary generated",
        description=f"An LLM summary was generated for document '{row.title}'.",
        source_module="documents",
        case_id=row.case_id,
        account_id=row.account_id,
        document_id=document_id,
        performed_by=performed_by_user_id,
        metadata={
            "model": completion.model,
            "provider": completion.provider,
            "prompt_hash": prompt_hash,
            "generated_at": generated_at.isoformat(),
            "batch": True,
        },
    )
    return True


def run_batch_document_llm_summary(
    session: Session,
    *,
    run_id: uuid.UUID,
    organization_id: uuid.UUID,
    document_ids: list[str],
    performed_by_user_id: uuid.UUID | None,
) -> BatchDocumentLlmSummaryResult:
    started_at = datetime.now(UTC)
    session.execute(
        update(batch_document_summary_runs_table)
        .where(batch_document_summary_runs_table.c.id == run_id)
        .values(status=STATUS_RUNNING, started_at=started_at, updated_at=started_at)
    )

    try:
        gate_status = require_llm_ready(
            feature_enabled=True, settings=get_llm_settings()
        )
    except Exception as exc:
        completed_at = datetime.now(UTC)
        error_message = str(exc)
        session.execute(
            update(batch_document_summary_runs_table)
            .where(batch_document_summary_runs_table.c.id == run_id)
            .values(
                status=STATUS_FAILED,
                completed_at=completed_at,
                error_message=error_message,
                updated_at=completed_at,
            )
        )
        return BatchDocumentLlmSummaryResult(
            run_id=run_id,
            documents_succeeded=0,
            documents_failed=len(document_ids),
            status=STATUS_FAILED,
            error_message=error_message,
        )

    succeeded = 0
    failed = 0
    for raw_id in document_ids:
        document_id = uuid.UUID(raw_id)
        if _process_document(
            session,
            organization_id=organization_id,
            document_id=document_id,
            performed_by_user_id=performed_by_user_id,
            model=gate_status.model,
        ):
            succeeded += 1
        else:
            failed += 1

    completed_at = datetime.now(UTC)
    final_status = STATUS_COMPLETED if failed == 0 else STATUS_COMPLETED
    session.execute(
        update(batch_document_summary_runs_table)
        .where(batch_document_summary_runs_table.c.id == run_id)
        .values(
            status=final_status,
            documents_succeeded=succeeded,
            documents_failed=failed,
            completed_at=completed_at,
            updated_at=completed_at,
        )
    )
    logger.info(
        "batch_document_llm_summary_completed",
        run_id=str(run_id),
        documents_succeeded=succeeded,
        documents_failed=failed,
    )
    return BatchDocumentLlmSummaryResult(
        run_id=run_id,
        documents_succeeded=succeeded,
        documents_failed=failed,
        status=final_status,
    )
