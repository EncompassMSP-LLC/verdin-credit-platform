"""Unit tests for FCRA §605B block packet builders."""

from __future__ import annotations

import uuid
import zipfile
from datetime import date
from io import BytesIO

from api.modules.documents.identity_theft_605b_packet import (
    FCRA_605B_CITATION,
    BlockTradeline,
    build_605b_block_letter_body,
    build_605b_packet_manifest,
    build_605b_packet_zip,
    build_block_letter_context,
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
