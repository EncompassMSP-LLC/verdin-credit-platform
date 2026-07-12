"""Compliance finding → evidence document linking (Phase 5 scaffold).

Aggregates Metro 2 / FCRA findings with report document pointers and case
exhibits. Page numbers are best-effort when a page lookup callback is provided;
exact OCR line maps are deferred.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

SourceKind = Literal["metro2", "fcra"]
ExhibitRole = Literal["identity", "proof_of_address", "supporting", "suggested"]
PageConfidence = Literal["matched", "unavailable", "deferred"]


@dataclass(frozen=True, slots=True)
class ExhibitInput:
    document_id: uuid.UUID
    document_type: str
    role: ExhibitRole
    label: str


@dataclass(frozen=True, slots=True)
class ReportLink:
    document_id: uuid.UUID
    bureau: str | None
    download_path: str
    page_numbers: tuple[int, ...] | None
    page_confidence: PageConfidence
    excerpt_available: bool


@dataclass(frozen=True, slots=True)
class ExhibitLink:
    document_id: uuid.UUID
    document_type: str
    role: ExhibitRole
    label: str


@dataclass(frozen=True, slots=True)
class EvidenceLinkItem:
    source_kind: SourceKind
    source_id: str
    rule_id: str
    severity: str
    title: str
    bureau: str | None
    tradeline_index: int | None
    creditor_name: str | None
    account_number_masked: str | None
    report_links: tuple[ReportLink, ...]
    exhibit_links: tuple[ExhibitLink, ...]
    checklist_hints: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CaseComplianceEvidenceLinksResult:
    case_id: uuid.UUID
    summary: dict[str, int]
    items: tuple[EvidenceLinkItem, ...]


PageLookup = Callable[[uuid.UUID, str | None, str | None], tuple[int, ...] | None]


def _download_path(document_id: uuid.UUID) -> str:
    return f"/documents/{document_id}/download"


def _checklist_hints(*, source_kind: SourceKind, rule_id: str) -> tuple[str, ...]:
    hints: list[str] = ["Preserve the source bureau PDF for this finding"]
    lowered = rule_id.lower()
    if "dofd" in lowered or "obsolete" in lowered:
        hints.append("Account statements covering the first delinquency / aging dates")
        hints.append("Prior monthly credit reports showing DOFD continuity")
    if "balance" in lowered or "past_due" in lowered:
        hints.append("Monthly statements showing balance and past-due amounts")
    if "collection" in lowered or "original_creditor" in lowered:
        hints.append("Collection notices naming the original creditor")
    if "closed" in lowered or "date_closed" in lowered:
        hints.append("Closure / paid-in-full letters if available")
    if source_kind == "fcra":
        hints.append("Document any prior dispute submissions and CRA responses")
    return tuple(dict.fromkeys(hints))


def _report_link_for_document(
    *,
    document_id: uuid.UUID,
    bureau: str | None,
    creditor_name: str | None,
    account_number_masked: str | None,
    page_lookup: PageLookup | None,
) -> ReportLink:
    page_numbers: tuple[int, ...] | None = None
    page_confidence: PageConfidence = "deferred"
    if page_lookup is not None and creditor_name:
        located = page_lookup(document_id, creditor_name, account_number_masked)
        if located is None:
            page_confidence = "unavailable"
            page_numbers = None
        else:
            page_numbers = located
            page_confidence = "matched" if located else "unavailable"
    return ReportLink(
        document_id=document_id,
        bureau=bureau,
        download_path=_download_path(document_id),
        page_numbers=page_numbers,
        page_confidence=page_confidence,
        excerpt_available=True,
    )


def _finding_source_id(
    source_kind: SourceKind, rule_id: str, tradeline_index: int, bureau: str
) -> str:
    return f"{source_kind}:{bureau}:{rule_id}#{tradeline_index}"


def build_case_compliance_evidence_links(
    *,
    case_id: uuid.UUID,
    metro2_documents: list[dict[str, Any]],
    fcra_documents: list[dict[str, Any]],
    exhibits: list[ExhibitInput],
    page_lookup: PageLookup | None = None,
) -> CaseComplianceEvidenceLinksResult:
    """Build evidence-link records from finding payloads.

    Each document dict should include: document_id, bureau, findings (list of
    finding dicts with rule_id, severity, title, tradeline_index, creditor_name,
    account_number_masked).
    """
    exhibit_links = tuple(
        ExhibitLink(
            document_id=item.document_id,
            document_type=item.document_type,
            role=item.role,
            label=item.label,
        )
        for item in exhibits
    )
    items: list[EvidenceLinkItem] = []

    for source_kind, documents in (("metro2", metro2_documents), ("fcra", fcra_documents)):
        for document in documents:
            document_id = document.get("document_id")
            bureau = document.get("bureau")
            if not isinstance(document_id, uuid.UUID):
                continue
            findings = document.get("findings")
            if not isinstance(findings, list):
                continue
            for finding in findings:
                if not isinstance(finding, dict):
                    continue
                rule_id = str(finding.get("rule_id") or "unknown")
                tradeline_index = finding.get("tradeline_index")
                index = tradeline_index if isinstance(tradeline_index, int) else 0
                creditor = finding.get("creditor_name")
                masked = finding.get("account_number_masked")
                creditor_name = creditor if isinstance(creditor, str) else None
                account_masked = masked if isinstance(masked, str) else None
                bureau_name = bureau if isinstance(bureau, str) else "unknown"
                items.append(
                    EvidenceLinkItem(
                        source_kind=source_kind,  # type: ignore[arg-type]
                        source_id=_finding_source_id(
                            source_kind,  # type: ignore[arg-type]
                            rule_id,
                            index,
                            bureau_name,
                        ),
                        rule_id=rule_id,
                        severity=str(finding.get("severity") or "low"),
                        title=str(finding.get("title") or rule_id),
                        bureau=bureau_name,
                        tradeline_index=index,
                        creditor_name=creditor_name,
                        account_number_masked=account_masked,
                        report_links=(
                            _report_link_for_document(
                                document_id=document_id,
                                bureau=bureau_name,
                                creditor_name=creditor_name,
                                account_number_masked=account_masked,
                                page_lookup=page_lookup,
                            ),
                        ),
                        exhibit_links=exhibit_links,
                        checklist_hints=_checklist_hints(
                            source_kind=source_kind,  # type: ignore[arg-type]
                            rule_id=rule_id,
                        ),
                    )
                )

    with_pages = sum(
        1
        for item in items
        if any(
            link.page_confidence == "matched" and link.page_numbers for link in item.report_links
        )
    )
    summary = {
        "findings_linked": len(items),
        "with_pages": with_pages,
        "missing_pages": len(items) - with_pages,
        "exhibits_available": len(exhibit_links),
        "report_links": sum(len(item.report_links) for item in items),
    }
    return CaseComplianceEvidenceLinksResult(
        case_id=case_id,
        summary=summary,
        items=tuple(items),
    )
