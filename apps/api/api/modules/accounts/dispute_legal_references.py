"""Select the strongest available FCRA citation for dispute letter drafts.

Investigator aid only — not legal advice. Falls back to the procedural
dispute right (§611 CRA / §623 furnisher) when no finding-backed sections exist.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from api.modules.accounts.dispute_drafts import DisputeRecipientType
from api.modules.accounts.dispute_mail_addresses import (
    FCRA_CRA_CITATION,
    FCRA_FURNISHER_CITATION,
)
from api.modules.documents.cross_bureau_comparison import tradeline_match_key
from api.modules.documents.litigation_strength import heuristic_rule_score

FCRA_SECTION_CITATIONS: dict[str, str] = {
    "605": "15 U.S.C. § 1681c (FCRA Section 605)",
    "607": "15 U.S.C. § 1681e (FCRA Section 607)",
    "611": FCRA_CRA_CITATION,
    "623": FCRA_FURNISHER_CITATION,
}

# Prefer obsolescence / accuracy substance when ordering finding sections.
# §605 obsolescence is the strongest deletion-oriented statutory path.
_SECTION_SUBSTANCE_ORDER: dict[str, int] = {
    "605": 0,
    "607": 1,
    "623": 2,
    "611": 3,
}

_MAX_CITATIONS = 3
_MAX_ALTERNATIVES = 3

# Extra ranking weight toward deletion / unverifiable-removal paths.
_DELETION_SECTION_BONUS: dict[str, int] = {
    "605": 12,  # obsolete adverse info — delete/block reporting
    "607": 6,  # accuracy / reasonable procedures
    "623": 4,  # furnisher accuracy duties
    "611": 1,  # procedural reinvestigation right
}


@dataclass(frozen=True, slots=True)
class LegalCitationCandidate:
    rule_id: str
    fcra_sections: tuple[str, ...]
    score: int
    matched: bool = True
    severity: str = "medium"
    bureau: str | None = None


@dataclass(frozen=True, slots=True)
class SelectedLegalReference:
    citations: tuple[str, ...]
    sections: tuple[str, ...]
    source_rule_id: str | None
    source: Literal["finding", "default"]

    @property
    def pursuant_clause(self) -> str:
        if not self.citations:
            return FCRA_CRA_CITATION
        if len(self.citations) == 1:
            return self.citations[0]
        if len(self.citations) == 2:
            return f"{self.citations[0]} and {self.citations[1]}"
        return f"{', '.join(self.citations[:-1])}, and {self.citations[-1]}"


@dataclass(frozen=True, slots=True)
class LegalReferenceAlternative:
    """Compared FCRA finding option for investigator review (not legal advice)."""

    rule_id: str
    score: int
    deletion_affinity: int
    citations: tuple[str, ...]
    sections: tuple[str, ...]
    selected: bool
    rationale: str


def deletion_affinity(candidate: LegalCitationCandidate) -> int:
    """Prefer statutory paths most likely to support deletion / block reporting."""
    affinity = 0
    for section in candidate.fcra_sections:
        affinity += _DELETION_SECTION_BONUS.get(section, 0)
    lowered = candidate.rule_id.lower()
    if "obsolete" in lowered:
        affinity += 8
    elif any(token in lowered for token in ("delete", "removed", "disappeared", "missing")):
        affinity += 4
    elif any(token in lowered for token in ("mismatch", "incorrect", "inaccurate", "dofd")):
        affinity += 3
    return affinity


def _rank_matched_candidates(
    candidates: Sequence[LegalCitationCandidate],
) -> list[LegalCitationCandidate]:
    matched = [c for c in candidates if c.fcra_sections and c.matched]
    return sorted(
        matched,
        key=lambda c: (c.score, deletion_affinity(c), len(c.fcra_sections)),
        reverse=True,
    )


def _sections_for_candidate(
    recipient_type: DisputeRecipientType,
    candidate: LegalCitationCandidate,
) -> tuple[str, ...]:
    procedural = procedural_section(recipient_type)
    sections: list[str] = []
    if procedural not in candidate.fcra_sections:
        sections.append(procedural)

    ordered_finding = sorted(
        candidate.fcra_sections,
        key=lambda section: _SECTION_SUBSTANCE_ORDER.get(section, 99),
    )
    for section in ordered_finding:
        if section not in sections:
            sections.append(section)
        if len(sections) >= _MAX_CITATIONS:
            break
    return tuple(sections)


def _rationale_for_candidate(candidate: LegalCitationCandidate, *, selected: bool) -> str:
    affinity = deletion_affinity(candidate)
    section_hint = ", ".join(f"§{s}" for s in candidate.fcra_sections) or "no sections"
    prefix = "Selected" if selected else "Compared"
    if "605" in candidate.fcra_sections:
        focus = "obsolescence / deletion-oriented (§605)"
    elif "607" in candidate.fcra_sections:
        focus = "accuracy / reasonable procedures (§607)"
    elif "623" in candidate.fcra_sections:
        focus = "furnisher accuracy duties (§623)"
    else:
        focus = "procedural dispute rights"
    return (
        f"{prefix} `{candidate.rule_id}` ({section_hint}) — {focus}; "
        f"strength {candidate.score}/100, deletion affinity {affinity}."
    )


def procedural_section(recipient_type: DisputeRecipientType) -> str:
    return "611" if recipient_type == "credit_bureau" else "623"


def citation_for_section(section: str) -> str:
    normalized = section.strip().lstrip("§").strip()
    return FCRA_SECTION_CITATIONS.get(normalized, f"FCRA Section {normalized}")


def score_candidate(rule_id: str, severity: str = "medium") -> int:
    return heuristic_rule_score(rule_id, severity)


def candidates_from_fcra_documents(
    documents: Sequence[Any],
    *,
    creditor_name: str,
    account_number_masked: str | None,
    bureau: str | None = None,
) -> list[LegalCitationCandidate]:
    """Build scored citation candidates from case/document FCRA finding payloads."""
    target_key = tradeline_match_key(creditor_name, account_number_masked)
    candidates: list[LegalCitationCandidate] = []

    for document in documents:
        doc_bureau = getattr(document, "bureau", None)
        if doc_bureau is None and isinstance(document, dict):
            doc_bureau = document.get("bureau")
        findings = getattr(document, "findings", None)
        if findings is None and isinstance(document, dict):
            findings = document.get("findings") or []

        for finding in findings or []:
            if isinstance(finding, dict):
                rule_id = str(finding.get("rule_id") or "")
                sections_raw = finding.get("fcra_sections") or []
                severity = str(finding.get("severity") or "medium")
                finding_creditor = finding.get("creditor_name")
                finding_masked = finding.get("account_number_masked")
            else:
                rule_id = str(getattr(finding, "rule_id", "") or "")
                sections_raw = getattr(finding, "fcra_sections", ()) or ()
                severity = str(getattr(finding, "severity", "medium") or "medium")
                finding_creditor = getattr(finding, "creditor_name", None)
                finding_masked = getattr(finding, "account_number_masked", None)

            sections = tuple(
                str(section).strip().lstrip("§").strip()
                for section in sections_raw
                if str(section).strip()
            )
            if not rule_id or not sections:
                continue

            finding_key = tradeline_match_key(
                str(finding_creditor or ""),
                str(finding_masked) if finding_masked else None,
            )
            matched = bool(target_key and finding_key and target_key == finding_key)
            if not matched and target_key and finding_key:
                # Creditor-only soft match when account suffixes differ.
                matched = target_key.split(":", 1)[0] == finding_key.split(":", 1)[0]

            score = score_candidate(rule_id, severity)
            if bureau and isinstance(doc_bureau, str) and doc_bureau.lower() == bureau.lower():
                score = min(100, score + 3)

            candidates.append(
                LegalCitationCandidate(
                    rule_id=rule_id,
                    fcra_sections=sections,
                    score=score,
                    matched=matched,
                    severity=severity,
                    bureau=str(doc_bureau) if doc_bureau else None,
                )
            )

    return candidates


def select_best_legal_reference(
    recipient_type: DisputeRecipientType,
    candidates: Sequence[LegalCitationCandidate] = (),
) -> SelectedLegalReference:
    """Pick procedural dispute right plus strongest deletion-oriented finding sections.

    Ranking compares all matched findings by litigation-strength score, then by
    deletion affinity (§605 obsolescence preferred), then by section coverage.
    """
    procedural = procedural_section(recipient_type)
    ranked = _rank_matched_candidates(candidates)
    if not ranked:
        return SelectedLegalReference(
            citations=(citation_for_section(procedural),),
            sections=(procedural,),
            source_rule_id=None,
            source="default",
        )

    best = ranked[0]
    sections = _sections_for_candidate(recipient_type, best)
    return SelectedLegalReference(
        citations=tuple(citation_for_section(section) for section in sections),
        sections=sections,
        source_rule_id=best.rule_id,
        source="finding",
    )


def rank_legal_alternatives(
    recipient_type: DisputeRecipientType,
    candidates: Sequence[LegalCitationCandidate] = (),
    *,
    limit: int = _MAX_ALTERNATIVES,
) -> list[LegalReferenceAlternative]:
    """Return top compared finding options with the selected deletion path first."""
    ranked = _rank_matched_candidates(candidates)
    if not ranked:
        procedural = procedural_section(recipient_type)
        return [
            LegalReferenceAlternative(
                rule_id="default.procedural",
                score=0,
                deletion_affinity=_DELETION_SECTION_BONUS.get(procedural, 0),
                citations=(citation_for_section(procedural),),
                sections=(procedural,),
                selected=True,
                rationale=(
                    "No matched FCRA finding sections — using procedural dispute right "
                    f"(§{procedural}). Investigator aid only — not legal advice."
                ),
            )
        ]

    alternatives: list[LegalReferenceAlternative] = []
    seen_rules: set[str] = set()
    for index, candidate in enumerate(ranked):
        if candidate.rule_id in seen_rules:
            continue
        seen_rules.add(candidate.rule_id)
        sections = _sections_for_candidate(recipient_type, candidate)
        selected = index == 0
        alternatives.append(
            LegalReferenceAlternative(
                rule_id=candidate.rule_id,
                score=candidate.score,
                deletion_affinity=deletion_affinity(candidate),
                citations=tuple(citation_for_section(section) for section in sections),
                sections=sections,
                selected=selected,
                rationale=_rationale_for_candidate(candidate, selected=selected),
            )
        )
        if len(alternatives) >= limit:
            break
    return alternatives
