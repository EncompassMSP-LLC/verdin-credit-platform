"""Unit tests for checklist exhibit ZIP packets."""

from __future__ import annotations

import uuid
import zipfile
from io import BytesIO

from api.modules.documents.checklist_packet import (
    build_checklist_packet_zip,
    checklist_packet_filename,
)


def test_checklist_packet_filename() -> None:
    case_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    assert checklist_packet_filename("cfpb", case_id) == "cfpb-checklist-packet-12345678.zip"
    assert (
        checklist_packet_filename("attorney", case_id) == "attorney-checklist-packet-12345678.zip"
    )


def test_build_checklist_packet_zip_includes_markdown_and_exhibits() -> None:
    packet = build_checklist_packet_zip(
        markdown_name="cfpb-checklist-12345678.md",
        markdown_bytes=b"# CFPB checklist\n",
        exhibits=[
            ("exhibits/identity.pdf", b"%PDF-identity"),
            ("exhibits/credit-reports/report__abcd1234.pdf", b"%PDF-report"),
        ],
    )
    with zipfile.ZipFile(BytesIO(packet), "r") as archive:
        names = set(archive.namelist())
        assert "cfpb-checklist-12345678.md" in names
        assert "exhibits/identity.pdf" in names
        assert "exhibits/credit-reports/report__abcd1234.pdf" in names
        assert archive.read("cfpb-checklist-12345678.md").startswith(b"# CFPB")


def test_build_checklist_packet_zip_without_exhibits_still_has_markdown() -> None:
    packet = build_checklist_packet_zip(
        markdown_name="attorney-checklist-12345678.md",
        markdown_bytes=b"# Attorney checklist\n",
        exhibits=[],
    )
    with zipfile.ZipFile(BytesIO(packet), "r") as archive:
        assert archive.namelist() == ["attorney-checklist-12345678.md"]


def test_dispute_letter_exhibit_path_and_bytes() -> None:
    from api.modules.documents.checklist_packet import (
        dispute_letter_exhibit_bytes,
        dispute_letter_exhibit_path,
    )

    letter_id = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    path = dispute_letter_exhibit_path(
        status="approved",
        recipient_type="credit_bureau",
        letter_id=letter_id,
    )
    assert path == "exhibits/dispute-letters/approved_credit_bureau__aaaaaaaa.txt"
    assert dispute_letter_exhibit_bytes("Subject line\n\nBody\n").startswith(b"Subject")


def test_build_checklist_packet_zip_includes_letter_text_exhibits() -> None:
    packet = build_checklist_packet_zip(
        markdown_name="cfpb-checklist-12345678.md",
        markdown_bytes=b"# CFPB checklist\n",
        exhibits=[
            ("exhibits/dispute-letters/draft_credit_bureau__abcd1234.txt", b"Letter body\n"),
        ],
    )
    with zipfile.ZipFile(BytesIO(packet), "r") as archive:
        assert "exhibits/dispute-letters/draft_credit_bureau__abcd1234.txt" in archive.namelist()
        assert archive.read(
            "exhibits/dispute-letters/draft_credit_bureau__abcd1234.txt"
        ).startswith(b"Letter")
