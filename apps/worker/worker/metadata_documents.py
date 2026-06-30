"""Document metadata and entity resolution persistence for worker jobs."""

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from worker.documents_table import documents_table
from worker.metadata_tables import (
    accounts_table,
    cases_table,
    document_entity_resolutions_table,
    document_metadata_table,
)


@dataclass(frozen=True, slots=True)
class MetadataDocumentRecord:
    id: uuid.UUID
    organization_id: uuid.UUID
    case_id: uuid.UUID
    account_id: uuid.UUID | None
    ocr_text: str | None
    file_name: str
    title: str
    document_type: str | None
    deleted_at: datetime | None


@dataclass(frozen=True, slots=True)
class StoredMetadata:
    consumer_name: str | None
    bureau: str | None
    creditor: str | None
    collection_agency: str | None
    account_number_masked: str | None
    report_date: date | None
    open_date: date | None
    balance: float | None
    payment_status: str | None
    addresses: list[str]
    phone_numbers: list[str]
    ssn_masked: str | None
    metadata_status: str


@dataclass(frozen=True, slots=True)
class CaseRecord:
    id: uuid.UUID
    client_name: str
    case_number: str | None


@dataclass(frozen=True, slots=True)
class AccountRecord:
    id: uuid.UUID
    creditor_name: str
    account_number_masked: str | None
    bureau: str
    balance: float | None


def get_document_for_metadata(
    session: Session,
    document_id: uuid.UUID,
) -> MetadataDocumentRecord | None:
    row = session.execute(
        select(
            documents_table.c.id,
            documents_table.c.organization_id,
            documents_table.c.case_id,
            documents_table.c.account_id,
            documents_table.c.ocr_text,
            documents_table.c.file_name,
            documents_table.c.title,
            documents_table.c.document_type,
            documents_table.c.deleted_at,
        ).where(documents_table.c.id == document_id)
    ).one_or_none()
    if row is None:
        return None
    return MetadataDocumentRecord(
        id=row.id,
        organization_id=row.organization_id,
        case_id=row.case_id,
        account_id=row.account_id,
        ocr_text=row.ocr_text,
        file_name=row.file_name,
        title=row.title,
        document_type=row.document_type,
        deleted_at=row.deleted_at,
    )


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def upsert_metadata(
    session: Session,
    document: MetadataDocumentRecord,
    *,
    consumer_name: str | None,
    bureau: str | None,
    creditor: str | None,
    collection_agency: str | None,
    account_number_masked: str | None,
    report_date: str | None,
    open_date: str | None,
    balance: float | None,
    payment_status: str | None,
    addresses: tuple[str, ...],
    phone_numbers: tuple[str, ...],
    ssn_masked: str | None,
    confidence_score: float,
    extraction_method: str = "rules",
) -> None:
    now = datetime.now(UTC)
    existing = session.execute(
        select(document_metadata_table.c.id).where(
            document_metadata_table.c.document_id == document.id
        )
    ).one_or_none()

    values = {
        "consumer_name": consumer_name,
        "bureau": bureau,
        "creditor": creditor,
        "collection_agency": collection_agency,
        "account_number_masked": account_number_masked,
        "report_date": _parse_date(report_date),
        "open_date": _parse_date(open_date),
        "balance": Decimal(str(balance)) if balance is not None else None,
        "payment_status": payment_status,
        "addresses": list(addresses),
        "phone_numbers": list(phone_numbers),
        "ssn_masked": ssn_masked,
        "confidence_score": Decimal(str(confidence_score)),
        "extraction_method": extraction_method,
        "metadata_status": "extracted",
        "extracted_at": now,
        "extraction_error": None,
        "updated_at": now,
    }

    if existing is None:
        session.execute(
            document_metadata_table.insert().values(
                id=uuid.uuid4(),
                document_id=document.id,
                organization_id=document.organization_id,
                created_at=now,
                **values,
            )
        )
    else:
        session.execute(
            update(document_metadata_table)
            .where(document_metadata_table.c.document_id == document.id)
            .values(**values)
        )


def get_metadata_for_resolution(
    session: Session,
    document_id: uuid.UUID,
) -> StoredMetadata | None:
    row = session.execute(
        select(
            document_metadata_table.c.consumer_name,
            document_metadata_table.c.bureau,
            document_metadata_table.c.creditor,
            document_metadata_table.c.collection_agency,
            document_metadata_table.c.account_number_masked,
            document_metadata_table.c.report_date,
            document_metadata_table.c.open_date,
            document_metadata_table.c.balance,
            document_metadata_table.c.payment_status,
            document_metadata_table.c.addresses,
            document_metadata_table.c.phone_numbers,
            document_metadata_table.c.ssn_masked,
            document_metadata_table.c.metadata_status,
        ).where(document_metadata_table.c.document_id == document_id)
    ).one_or_none()
    if row is None:
        return None
    return StoredMetadata(
        consumer_name=row.consumer_name,
        bureau=row.bureau,
        creditor=row.creditor,
        collection_agency=row.collection_agency,
        account_number_masked=row.account_number_masked,
        report_date=row.report_date,
        open_date=row.open_date,
        balance=float(row.balance) if row.balance is not None else None,
        payment_status=row.payment_status,
        addresses=list(row.addresses or []),
        phone_numbers=list(row.phone_numbers or []),
        ssn_masked=row.ssn_masked,
        metadata_status=row.metadata_status,
    )


def list_cases(session: Session, organization_id: uuid.UUID) -> list[CaseRecord]:
    rows = session.execute(
        select(
            cases_table.c.id,
            cases_table.c.client_name,
            cases_table.c.case_number,
        )
        .where(
            cases_table.c.organization_id == organization_id,
            cases_table.c.deleted_at.is_(None),
        )
        .limit(200)
    ).all()
    return [
        CaseRecord(id=row.id, client_name=row.client_name, case_number=row.case_number)
        for row in rows
    ]


def list_accounts(
    session: Session, case_id: uuid.UUID, organization_id: uuid.UUID
) -> list[AccountRecord]:
    rows = session.execute(
        select(
            accounts_table.c.id,
            accounts_table.c.creditor_name,
            accounts_table.c.account_number_masked,
            accounts_table.c.bureau,
            accounts_table.c.balance,
        )
        .where(
            accounts_table.c.case_id == case_id,
            accounts_table.c.organization_id == organization_id,
            accounts_table.c.deleted_at.is_(None),
        )
        .limit(200)
    ).all()
    return [
        AccountRecord(
            id=row.id,
            creditor_name=row.creditor_name,
            account_number_masked=row.account_number_masked,
            bureau=row.bureau,
            balance=float(row.balance) if row.balance is not None else None,
        )
        for row in rows
    ]


def replace_resolutions(
    session: Session,
    document: MetadataDocumentRecord,
    resolutions: list[dict[str, object]],
) -> None:
    session.execute(
        delete(document_entity_resolutions_table).where(
            document_entity_resolutions_table.c.document_id == document.id
        )
    )
    now = datetime.now(UTC)
    for resolution in resolutions:
        session.execute(
            document_entity_resolutions_table.insert().values(
                id=uuid.uuid4(),
                document_id=document.id,
                organization_id=document.organization_id,
                entity_type=resolution["entity_type"],
                matched_entity_id=resolution.get("matched_entity_id"),
                confidence_score=Decimal(str(resolution["confidence_score"])),
                resolution_status=resolution["resolution_status"],
                resolution_method=resolution["resolution_method"],
                reasoning=resolution.get("reasoning"),
                candidate_entity_ids=list(resolution.get("candidate_entity_ids") or []),
                created_at=now,
                updated_at=now,
            )
        )


def link_document_account(
    session: Session, document_id: uuid.UUID, account_id: uuid.UUID
) -> None:
    session.execute(
        update(documents_table)
        .where(documents_table.c.id == document_id)
        .values(account_id=account_id)
    )
