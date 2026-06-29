"""Unit tests for OCR text extraction."""

from worker.ocr.extractor import (
    OcrExtractionError,
    UnsupportedOcrFormatError,
    extract_text,
    is_ocr_eligible,
)

# Minimal valid PDF with extractable text ("Credit Report Sample")
SAMPLE_TEXT_PDF = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 51 >> stream
BT /F1 12 Tf 100 700 Td (Credit Report Sample) Tj ET
endstream
endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000261 00000 n
0000000363 00000 n
trailer << /Size 6 /Root 1 0 R >>
startxref
434
%%EOF"""


def test_is_ocr_eligible_pdf() -> None:
    assert is_ocr_eligible("application/pdf") is True


def test_is_ocr_eligible_docx() -> None:
    assert (
        is_ocr_eligible(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        is False
    )


def test_extract_pdf_text() -> None:
    text = extract_text(SAMPLE_TEXT_PDF, "application/pdf")
    assert "Credit Report Sample" in text


def test_extract_unsupported_mime_type() -> None:
    try:
        extract_text(b"hello", "text/plain")
    except UnsupportedOcrFormatError:
        pass
    else:
        raise AssertionError("Expected UnsupportedOcrFormatError")


def test_extract_pdf_without_text_raises() -> None:
    empty_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF"
    try:
        extract_text(empty_pdf, "application/pdf")
    except OcrExtractionError:
        pass
    else:
        raise AssertionError("Expected OcrExtractionError")
