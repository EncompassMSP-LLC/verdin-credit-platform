"""Unit tests for entity resolution engine."""

from verdin_entity_resolution import (
    AccountCandidate,
    CaseCandidate,
    ResolutionContext,
    resolve_entities,
)
from verdin_entity_resolution.constants import ResolutionStatus

from tests.documents.test_metadata_extraction import SAMPLE_CREDIT_REPORT_TEXT


def _metadata_from_text() -> dict[str, object]:
    return {
        "consumer_name": "Doc Client",
        "bureau": "equifax",
        "creditor": "Example Bank",
        "collection_agency": None,
        "account_number_masked": "****1234",
        "report_date": "2026-01-15",
        "open_date": None,
        "balance": 1500.0,
        "payment_status": "Late 60",
        "addresses": [],
        "phone_numbers": [],
        "ssn_masked": None,
    }


def test_account_resolution_matched() -> None:
    context = ResolutionContext(
        organization_id="org-1",
        document_case_id="case-1",
        metadata=_metadata_from_text(),
        cases=(CaseCandidate(id="case-1", client_name="Doc Client", case_number="C-001"),),
        accounts=(
            AccountCandidate(
                id="acct-1",
                creditor_name="Example Bank",
                account_number_masked="****1234",
                bureau="equifax",
                balance=1500.0,
            ),
        ),
    )
    results = resolve_entities(context)
    account = next(row for row in results if row.entity_type.value == "account")
    assert account.resolution_status == ResolutionStatus.MATCHED
    assert account.matched_entity_id == "acct-1"
    assert account.confidence_score >= 0.7


def test_account_resolution_ambiguous() -> None:
    context = ResolutionContext(
        organization_id="org-1",
        document_case_id="case-1",
        metadata=_metadata_from_text(),
        cases=(),
        accounts=(
            AccountCandidate(
                id="acct-1",
                creditor_name="Example Bank",
                account_number_masked="****1234",
                bureau="equifax",
                balance=1500.0,
            ),
            AccountCandidate(
                id="acct-2",
                creditor_name="Example Bank NA",
                account_number_masked="****1234",
                bureau="equifax",
                balance=1500.0,
            ),
        ),
    )
    results = resolve_entities(context)
    account = next(row for row in results if row.entity_type.value == "account")
    assert account.resolution_status == ResolutionStatus.AMBIGUOUS
    assert account.matched_entity_id is None
    assert len(account.candidate_entity_ids) >= 2


def test_account_resolution_unmatched() -> None:
    context = ResolutionContext(
        organization_id="org-1",
        document_case_id="case-1",
        metadata=_metadata_from_text(),
        cases=(),
        accounts=(
            AccountCandidate(
                id="acct-9",
                creditor_name="Unrelated Creditor",
                account_number_masked="****9999",
                bureau="experian",
                balance=50.0,
            ),
        ),
    )
    results = resolve_entities(context)
    account = next(row for row in results if row.entity_type.value == "account")
    assert account.resolution_status == ResolutionStatus.UNMATCHED
    assert account.matched_entity_id is None


def test_case_resolution_uses_consumer_name() -> None:
    context = ResolutionContext(
        organization_id="org-1",
        document_case_id="case-1",
        metadata=_metadata_from_text(),
        cases=(
            CaseCandidate(id="case-1", client_name="Doc Client", case_number="C-001"),
            CaseCandidate(id="case-2", client_name="Other Person", case_number="C-002"),
        ),
        accounts=(),
    )
    results = resolve_entities(context)
    case = next(row for row in results if row.entity_type.value == "case")
    assert case.resolution_status == ResolutionStatus.MATCHED
    assert case.matched_entity_id == "case-1"


def test_extraction_sample_text_is_usable() -> None:
    assert "Doc Client" in SAMPLE_CREDIT_REPORT_TEXT
