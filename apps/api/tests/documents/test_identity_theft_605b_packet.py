"""Unit tests for FCRA §605B block packet builders."""

from __future__ import annotations

import uuid
import zipfile
from datetime import date
from io import BytesIO

from api.modules.documents.identity_theft_605b_packet import (
    FCRA_605B_CITATION,
    BlockTradeline,
    PacketExhibit,
    build_605b_block_letter_body,
    build_605b_packet_manifest,
    build_605b_packet_zip,
    build_block_letter_context,
    exhibit_archive_path,
    exhibit_type_skip_reason,
    export_block_letter,
    fcra_605b_packet_filename,
    parse_bureau,
)


def test_fcra_605b_packet_filename() -> None:
    case_id = uuid.UUID("12345678-1234-1234-1234-123456789abc")
    assert fcra_605b_packet_filename(case_id) == "fcra-605b-block-packet-12345678.zip"


def test_parse_bureau_aliases() -> None:
    assert parse_bureau("Experian") is not None
    assert parse_bureau("trans-union") is not None
    assert parse_bureau("not-a-bureau") is None


def test_build_605b_block_letter_body_cites_605b_not_611() -> None:
    review_id = uuid.uuid4()
    context = build_block_letter_context(
        letter_date=date(2026, 7, 14),
        consumer_name="Jordan Consumer",
        consumer_address_lines=["123 Main St", "Austin, TX 78701"],
        organization_name="Verdin Demo Org",
        bureau="experian",
        tradelines=[
            BlockTradeline(
                creditor_name="Fake Bank",
                account_number_masked="****1234",
                match_key="fake|1234",
                bureau="experian",
                review_id=review_id,
            )
        ],
        attestation_recorded=True,
        packet_readiness=40,
        missing_evidence=["FTC_IDENTITY_THEFT_REPORT"],
    )
    body = build_605b_block_letter_body(context)
    assert FCRA_605B_CITATION in body
    assert "§605B" in body
    assert "not an ordinary" in body.lower() or "Not an ordinary" in body
    assert "Fake Bank" in body
    assert "****1234" in body
    assert "1681i" not in body


def test_build_605b_packet_zip_includes_readme_and_letters() -> None:
    case_id = uuid.uuid4()
    manifest = build_605b_packet_manifest(
        case_id=case_id,
        consumer_name="Jordan Consumer",
        confirmed_count=1,
        bureau_labels=["Experian"],
        packet_readiness=40,
        missing_evidence=["FTC_IDENTITY_THEFT_REPORT"],
        evidence_checklist=[{"item_id": "GOVERNMENT_ID", "label": "ID", "status": "unknown"}],
    )
    context = build_block_letter_context(
        letter_date=date(2026, 7, 14),
        consumer_name="Jordan Consumer",
        consumer_address_lines=None,
        organization_name=None,
        bureau="experian",
        tradelines=[
            BlockTradeline(
                creditor_name="Fake Bank",
                account_number_masked=None,
                match_key=None,
                bureau="experian",
                review_id=uuid.uuid4(),
            )
        ],
        attestation_recorded=True,
        packet_readiness=40,
        missing_evidence=["FTC_IDENTITY_THEFT_REPORT"],
    )
    text_bytes, text_path = export_block_letter(context, "text")
    pdf_bytes, pdf_path = export_block_letter(context, "pdf")
    assert text_path.endswith(".txt")
    assert pdf_path.endswith(".pdf")
    assert pdf_bytes.startswith(b"%PDF")

    packet = build_605b_packet_zip(
        manifest_markdown=manifest,
        letter_files=[(text_path, text_bytes)],
    )
    with zipfile.ZipFile(BytesIO(packet)) as archive:
        names = set(archive.namelist())
        assert "README.md" in names
        assert text_path in names
        readme = archive.read("README.md").decode("utf-8")
        assert "staff-mediated" in readme.lower() or "does **not** submit" in readme
        assert str(case_id) in readme


def test_exhibit_type_skip_reason_allows_pdf_and_images() -> None:
    assert exhibit_type_skip_reason("application/pdf") is None
    assert exhibit_type_skip_reason("image/png") is None
    assert exhibit_type_skip_reason("application/pdf; charset=binary") is None
    assert exhibit_type_skip_reason("application/zip") is not None
    assert exhibit_type_skip_reason(None) is not None


def test_exhibit_archive_path_is_indexed_and_slugged() -> None:
    path = exhibit_archive_path(1, "Police Report #12.pdf")
    assert path.startswith("exhibits/01-")
    assert path.endswith(".pdf")
    assert " " not in path


def test_manifest_lists_attached_and_skipped_exhibits() -> None:
    case_id = uuid.uuid4()
    exhibits = [
        PacketExhibit(
            document_id=uuid.uuid4(),
            title="Police Report",
            file_name="police-report.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            status="attached",
            path="exhibits/01-police-report.pdf",
        ),
        PacketExhibit(
            document_id=uuid.uuid4(),
            title="Archive",
            file_name="evidence.zip",
            mime_type="application/zip",
            size_bytes=2048,
            status="skipped_type",
            skip_reason="unsupported content type (application/zip)",
        ),
    ]
    manifest = build_605b_packet_manifest(
        case_id=case_id,
        consumer_name="Jordan Consumer",
        confirmed_count=1,
        bureau_labels=["Experian"],
        packet_readiness=40,
        missing_evidence=[],
        evidence_checklist=[],
        exhibits=exhibits,
    )
    assert "Evidence exhibits attached: 1" in manifest
    assert "exhibits/01-police-report.pdf" in manifest
    assert "unsupported content type" in manifest
    assert "evidence.zip" in manifest


def test_build_605b_packet_zip_includes_exhibits() -> None:
    manifest = build_605b_packet_manifest(
        case_id=uuid.uuid4(),
        consumer_name="Jordan Consumer",
        confirmed_count=1,
        bureau_labels=["Experian"],
        packet_readiness=40,
        missing_evidence=[],
        evidence_checklist=[],
        exhibits=[
            PacketExhibit(
                document_id=uuid.uuid4(),
                title="Police Report",
                file_name="police-report.pdf",
                mime_type="application/pdf",
                size_bytes=5,
                status="attached",
                path="exhibits/01-police-report.pdf",
            )
        ],
    )
    packet = build_605b_packet_zip(
        manifest_markdown=manifest,
        letter_files=[("letters/605b-block-experian.txt", b"letter")],
        exhibit_files=[("exhibits/01-police-report.pdf", b"%PDF-x")],
    )
    with zipfile.ZipFile(BytesIO(packet)) as archive:
        names = set(archive.namelist())
        assert "exhibits/01-police-report.pdf" in names
        assert archive.read("exhibits/01-police-report.pdf") == b"%PDF-x"
