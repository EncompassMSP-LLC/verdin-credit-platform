"""Text extraction for document OCR."""

from __future__ import annotations

from io import BytesIO

OCR_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/tiff",
    }
)


class OcrExtractionError(Exception):
    """Raised when text cannot be extracted from a document."""


class UnsupportedOcrFormatError(OcrExtractionError):
    """Raised when the MIME type is not supported for OCR."""


def is_ocr_eligible(mime_type: str | None) -> bool:
    return mime_type in OCR_MIME_TYPES


def extract_text(data: bytes, mime_type: str | None) -> str:
    if not is_ocr_eligible(mime_type):
        raise UnsupportedOcrFormatError(f"Unsupported MIME type for OCR: {mime_type}")

    if mime_type == "application/pdf":
        return _extract_pdf_text(data)
    return _extract_image_text(data)


def _extract_pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        reader = PdfReader(BytesIO(data))
    except PdfReadError as exc:
        raise OcrExtractionError(f"Invalid PDF: {exc}") from exc

    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(part.strip() for part in pages if part and part.strip())
    if not text:
        raise OcrExtractionError("No extractable text found in PDF")
    return text


def _extract_image_text(data: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise OcrExtractionError(
            "Image OCR requires pytesseract and Pillow with Tesseract installed"
        ) from exc

    image = Image.open(BytesIO(data))
    text = pytesseract.image_to_string(image).strip()
    if not text:
        raise OcrExtractionError("No extractable text found in image")
    return text
