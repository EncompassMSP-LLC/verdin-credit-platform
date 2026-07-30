"""Content-policy malware scan for message attachments (LRP-302B).

Default mode ``policy`` validates MIME allowlist, extension, and magic bytes.
Mode ``required`` fails closed when an external engine is not configured.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from api.modules.messaging.attachment_models import MessageAttachmentScanStatus

# Keep aligned with documents.service.ALLOWED_MIME_TYPES (message attach subset).
ALLOWED_ATTACHMENT_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }
)

_ALLOWED_EXTENSIONS = frozenset(
    {".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".doc", ".docx", ".txt"}
)

_BLOCKED_EXTENSIONS = frozenset(
    {
        ".exe",
        ".bat",
        ".cmd",
        ".com",
        ".msi",
        ".scr",
        ".js",
        ".jse",
        ".vbs",
        ".vbe",
        ".wsf",
        ".wsh",
        ".ps1",
        ".sh",
        ".bash",
        ".dll",
        ".so",
        ".jar",
        ".apk",
        ".dmg",
        ".iso",
        ".zip",
        ".rar",
        ".7z",
        ".gz",
        ".tar",
        ".bz2",
        ".html",
        ".htm",
        ".svg",
        ".php",
        ".asp",
        ".aspx",
    }
)

_MIME_MAGIC: dict[str, tuple[bytes, ...]] = {
    "application/pdf": (b"%PDF",),
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/tiff": (b"II*\x00", b"MM\x00*"),
    "application/msword": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (b"PK\x03\x04",),
}


@dataclass(frozen=True, slots=True)
class AttachmentScanResult:
    status: MessageAttachmentScanStatus
    detail: str | None = None
    display_filename: str = "attachment"
    mime_type: str = "application/octet-stream"


def sanitize_display_filename(raw_name: str | None) -> str:
    base = PurePosixPath((raw_name or "attachment").replace("\\", "/")).name.strip()
    cleaned = "".join(
        char if char.isalnum() or char in {".", "-", "_", " "} else "_" for char in base
    ).strip(" ._")
    return (cleaned or "attachment")[:255]


def _extension(filename: str) -> str:
    return PurePosixPath(filename).suffix.lower()


def scan_attachment_bytes(
    *,
    data: bytes,
    declared_mime: str,
    filename: str | None,
    max_bytes: int,
    mode: str = "policy",
) -> AttachmentScanResult:
    """Return clean/rejected/failed/pending for attachment bytes (never logs content)."""
    display = sanitize_display_filename(filename)
    ext = _extension(display)
    mime = (declared_mime or "application/octet-stream").split(";")[0].strip().lower()

    if mode not in {"policy", "required"}:
        return AttachmentScanResult(
            status=MessageAttachmentScanStatus.FAILED,
            detail="Unknown attachment scan mode",
            display_filename=display,
            mime_type=mime,
        )

    if mode == "required":
        # External engine not wired in this release — fail closed.
        return AttachmentScanResult(
            status=MessageAttachmentScanStatus.FAILED,
            detail="Malware scanner unavailable",
            display_filename=display,
            mime_type=mime,
        )

    if not data:
        return AttachmentScanResult(
            status=MessageAttachmentScanStatus.REJECTED,
            detail="Empty file",
            display_filename=display,
            mime_type=mime,
        )
    if len(data) > max_bytes:
        return AttachmentScanResult(
            status=MessageAttachmentScanStatus.REJECTED,
            detail="File exceeds maximum upload size",
            display_filename=display,
            mime_type=mime,
        )
    if ext in _BLOCKED_EXTENSIONS:
        return AttachmentScanResult(
            status=MessageAttachmentScanStatus.REJECTED,
            detail="Blocked file type",
            display_filename=display,
            mime_type=mime,
        )
    if ext and ext not in _ALLOWED_EXTENSIONS:
        return AttachmentScanResult(
            status=MessageAttachmentScanStatus.REJECTED,
            detail="Unsupported file extension",
            display_filename=display,
            mime_type=mime,
        )
    if mime not in ALLOWED_ATTACHMENT_MIME_TYPES:
        return AttachmentScanResult(
            status=MessageAttachmentScanStatus.REJECTED,
            detail="Unsupported MIME type",
            display_filename=display,
            mime_type=mime,
        )

    magic_prefixes = _MIME_MAGIC.get(mime)
    if magic_prefixes is not None:
        if not any(data.startswith(prefix) for prefix in magic_prefixes):
            return AttachmentScanResult(
                status=MessageAttachmentScanStatus.REJECTED,
                detail="MIME type does not match file content",
                display_filename=display,
                mime_type=mime,
            )
    elif mime == "text/plain":
        # Reject obvious binary payloads claiming to be text.
        if b"\x00" in data[:4096]:
            return AttachmentScanResult(
                status=MessageAttachmentScanStatus.REJECTED,
                detail="MIME type does not match file content",
                display_filename=display,
                mime_type=mime,
            )

    return AttachmentScanResult(
        status=MessageAttachmentScanStatus.CLEAN,
        detail=None,
        display_filename=display,
        mime_type=mime,
    )
