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
