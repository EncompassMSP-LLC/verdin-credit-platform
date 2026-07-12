"""Unit tests for compliance evidence-link aggregation."""

from __future__ import annotations

import uuid

from api.modules.accounts.dispute_report_redaction import locate_tradeline_pages
from api.modules.documents.evidence_links import (
    ExhibitInput,
    build_case_compliance_evidence_links,
)


def test_build_case_compliance_evidence_links_joins_findings_and_exhibits() -> None:
    case_id = uuid.uuid4()
    document_id = uuid.uuid4()
    identity_id = uuid.uuid4()

    result = build_case_compliance_evidence_links(
        case_id=case_id,
        metro2_documents=[
            {
                "document_id": document_id,
                "bureau": "experian",
                "findings": [
                    {
                        "rule_id": "metro2.past_due_without_dofd",
                        "severity": "high",
                        "title": "Past-due without DOFD",
                        "tradeline_index": 0,
                        "creditor_name": "Capital One",
                        "account_number_masked": "****4242",
                    }
                ],
            }
        ],
        fcra_documents=[
            {
                "document_id": document_id,
                "bureau": "experian",
                "findings": [
                    {
                        "rule_id": "fcra.adverse_missing_dofd",
                        "severity": "high",
                        "title": "Adverse missing DOFD",
                        "tradeline_index": 0,
                        "creditor_name": "Capital One",
                        "account_number_masked": "****4242",
                    }
                ],
            }
        ],
        exhibits=[
            ExhibitInput(
                document_id=identity_id,
                document_type="identity_document",
                role="identity",
                label="Government-issued photo ID",
            )
        ],
    )

    assert result.summary["findings_linked"] == 2
    assert result.summary["exhibits_available"] == 1
    assert result.summary["with_pages"] == 0
    assert len(result.items) == 2
    first = result.items[0]
    assert first.report_links[0].document_id == document_id
    assert first.report_links[0].download_path == f"/documents/{document_id}/download"
    assert first.report_links[0].page_confidence == "deferred"
    assert first.exhibit_links[0].document_id == identity_id
    assert any("DOFD" in hint or "delinquency" in hint for hint in first.checklist_hints)


def test_build_case_compliance_evidence_links_uses_page_lookup() -> None:
    case_id = uuid.uuid4()
    document_id = uuid.uuid4()

    def lookup(
        doc_id: uuid.UUID,
        creditor: str | None,
        _masked: str | None,
    ) -> tuple[int, ...] | None:
        assert doc_id == document_id
        assert creditor == "Metro Retail"
        return (3, 7)

    result = build_case_compliance_evidence_links(
        case_id=case_id,
        metro2_documents=[
            {
                "document_id": document_id,
                "bureau": "equifax",
                "findings": [
                    {
                        "rule_id": "metro2.closed_with_balance",
                        "severity": "high",
                        "title": "Closed with balance",
                        "tradeline_index": 1,
                        "creditor_name": "Metro Retail",
                        "account_number_masked": "****1111",
                    }
                ],
            }
        ],
        fcra_documents=[],
        exhibits=[],
        page_lookup=lookup,
    )

    link = result.items[0].report_links[0]
    assert link.page_numbers == (3, 7)
    assert link.page_confidence == "matched"
    assert result.summary["with_pages"] == 1


def test_locate_tradeline_pages_returns_none_for_non_pdf() -> None:
    assert (
        locate_tradeline_pages(
            b"not-a-pdf",
            target_creditor="Capital One",
            target_account_masked="****1234",
        )
        is None
    )
