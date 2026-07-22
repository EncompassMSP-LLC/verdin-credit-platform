"""Credit report parser regression corpus harness."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any

from verdin_report_parsers import ParsedDocument
from verdin_report_parsers.base import CreditReportParser
from verdin_report_parsers.models import ParsedCreditReport
from verdin_report_parsers.parsers.equifax.parser import EquifaxParser
from verdin_report_parsers.parsers.experian.parser import ExperianParser
from verdin_report_parsers.parsers.identityiq.parser import IdentityIQParser
from verdin_report_parsers.parsers.transunion.parser import TransUnionParser

REPO_ROOT = Path(__file__).resolve().parents[4]
CORPUS_ROOT = REPO_ROOT / "tests" / "fixtures" / "credit_reports"

_VOLATILE_METADATA_KEYS = frozenset({"parsed_at"})


def extract_pdf_text(pdf_bytes: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(pdf_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(part.strip() for part in pages if part and part.strip())
    if not text:
        raise ValueError("No extractable text found in PDF fixture")
    return text


def normalize_report_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Drop volatile metadata fields before comparing parser output."""
    normalized = json.loads(json.dumps(data))
    metadata = normalized.get("metadata")
    if isinstance(metadata, dict):
        for key in _VOLATILE_METADATA_KEYS:
            metadata.pop(key, None)
    return normalized


def report_to_comparable_dict(report: ParsedCreditReport) -> dict[str, Any]:
    return normalize_report_dict(report.as_dict())


def discover_experian_fixtures() -> list[Path]:
    return discover_bureau_fixtures("experian")


def discover_equifax_fixtures() -> list[Path]:
    return discover_bureau_fixtures("equifax")


def discover_transunion_fixtures() -> list[Path]:
    return discover_bureau_fixtures("transunion")


def discover_identityiq_fixtures() -> list[Path]:
    return discover_bureau_fixtures("identityiq")


def discover_bureau_fixtures(bureau: str) -> list[Path]:
    fixture_dir = CORPUS_ROOT / bureau / "2026"
    if not fixture_dir.is_dir():
        return []
    return sorted(fixture_dir.glob("report_*.pdf"))


def load_expected_fixture(pdf_path: Path) -> dict[str, Any]:
    expected_path = pdf_path.with_suffix(".expected.json")
    if not expected_path.is_file():
        raise FileNotFoundError(f"Missing expected fixture: {expected_path}")
    return json.loads(expected_path.read_text(encoding="utf-8"))


def parse_fixture_pdf(
    pdf_path: Path,
    *,
    parser: CreditReportParser | None = None,
    title_prefix: str = "Experian Credit Report",
) -> ParsedCreditReport:
    parser = parser or ExperianParser()
    pdf_bytes = pdf_path.read_bytes()
    ocr_text = extract_pdf_text(pdf_bytes)
    stem = pdf_path.stem
    document = ParsedDocument(
        ocr_text=ocr_text,
        file_name=pdf_path.name,
        title=f"{title_prefix} - {stem}",
        mime_type="application/pdf",
        document_type="credit_report",
        classification_confidence=0.95,
        document_id=f"fixture-{stem}",
    )
    return parser.parse(document)


def parse_equifax_fixture_pdf(
    pdf_path: Path,
    *,
    parser: EquifaxParser | None = None,
) -> ParsedCreditReport:
    return parse_fixture_pdf(
        pdf_path,
        parser=parser or EquifaxParser(),
        title_prefix="Equifax Credit Report",
    )


def parse_transunion_fixture_pdf(
    pdf_path: Path,
    *,
    parser: TransUnionParser | None = None,
) -> ParsedCreditReport:
    return parse_fixture_pdf(
        pdf_path,
        parser=parser or TransUnionParser(),
        title_prefix="TransUnion Credit Report",
    )


def parse_identityiq_fixture_pdf(
    pdf_path: Path,
    *,
    parser: IdentityIQParser | None = None,
) -> ParsedCreditReport:
    return parse_fixture_pdf(
        pdf_path,
        parser=parser or IdentityIQParser(),
        title_prefix="IdentityIQ Credit Report",
    )


def assert_report_matches_expected(actual: ParsedCreditReport, expected: dict[str, Any]) -> None:
    actual_dict = report_to_comparable_dict(actual)
    expected_dict = normalize_report_dict(expected)
    assert actual_dict == expected_dict


def write_expected_snapshot(pdf_path: Path) -> Path:
    """Regenerate expected JSON for a corpus fixture (developer utility)."""
    report = parse_fixture_pdf(pdf_path)
    expected_path = pdf_path.with_suffix(".expected.json")
    expected_path.write_text(
        json.dumps(report_to_comparable_dict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return expected_path
