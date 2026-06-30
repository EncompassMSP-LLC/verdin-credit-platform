"""Persist and load structured parsed credit reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from worker.parsed_report_tables import document_parsed_credit_reports_table


@dataclass(frozen=True, slots=True)
class ParsedCreditReportRecord:
    document_id: UUID
    organization_id: UUID
    schema_version: str
    bureau: str
    parser_name: str
    parser_confidence: float
    parsed_report: dict
    is_partial: bool
    warnings: tuple[str, ...]
    parsed_at: datetime


def upsert_parsed_credit_report(
    session: Session,
    *,
    document_id: UUID,
    organization_id: UUID,
    schema_version: str,
    bureau: str,
    parser_name: str,
    parser_confidence: float,
    parsed_report: dict,
    is_partial: bool,
    warnings: tuple[str, ...],
) -> None:
    now = datetime.now(UTC)
    parsed_at = now
    stmt = insert(document_parsed_credit_reports_table).values(
        id=uuid4(),
        document_id=document_id,
        organization_id=organization_id,
        schema_version=schema_version,
        bureau=bureau,
        parser_name=parser_name,
        parser_confidence=parser_confidence,
        parsed_report=parsed_report,
        is_partial=is_partial,
        warnings=list(warnings),
        parsed_at=parsed_at,
        created_at=now,
        updated_at=now,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[document_parsed_credit_reports_table.c.document_id],
        set_={
            "organization_id": organization_id,
            "schema_version": schema_version,
            "bureau": bureau,
            "parser_name": parser_name,
            "parser_confidence": parser_confidence,
            "parsed_report": parsed_report,
            "is_partial": is_partial,
            "warnings": list(warnings),
            "parsed_at": parsed_at,
            "updated_at": now,
        },
    )
    session.execute(stmt)


def get_parsed_credit_report(
    session: Session,
    document_id: UUID,
) -> ParsedCreditReportRecord | None:
    row = session.execute(
        select(
            document_parsed_credit_reports_table.c.document_id,
            document_parsed_credit_reports_table.c.organization_id,
            document_parsed_credit_reports_table.c.schema_version,
            document_parsed_credit_reports_table.c.bureau,
            document_parsed_credit_reports_table.c.parser_name,
            document_parsed_credit_reports_table.c.parser_confidence,
            document_parsed_credit_reports_table.c.parsed_report,
            document_parsed_credit_reports_table.c.is_partial,
            document_parsed_credit_reports_table.c.warnings,
            document_parsed_credit_reports_table.c.parsed_at,
        ).where(document_parsed_credit_reports_table.c.document_id == document_id)
    ).one_or_none()
    if row is None:
        return None
    warnings = row.warnings or []
    return ParsedCreditReportRecord(
        document_id=row.document_id,
        organization_id=row.organization_id,
        schema_version=row.schema_version,
        bureau=row.bureau,
        parser_name=row.parser_name,
        parser_confidence=float(row.parser_confidence),
        parsed_report=dict(row.parsed_report),
        is_partial=bool(row.is_partial),
        warnings=tuple(str(item) for item in warnings),
        parsed_at=row.parsed_at,
    )
