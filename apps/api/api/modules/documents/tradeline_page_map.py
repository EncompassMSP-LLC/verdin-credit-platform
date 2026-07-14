"""Helpers for persisted tradeline PDF page maps on parsed credit reports."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

PAGE_MAP_SCANNER_VERSION = 1
CACHE_MISS = object()


def page_map_entry_key(creditor_name: str, account_number_masked: str | None) -> str:
    creditor = creditor_name.strip().lower()
    masked = (account_number_masked or "").strip().lower()
    return f"{creditor}|{masked}"


def empty_page_map(*, file_hash: str) -> dict[str, Any]:
    return {
        "scanner_version": PAGE_MAP_SCANNER_VERSION,
        "file_hash": file_hash,
        "scanned_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "entries": [],
    }


def normalize_page_map(raw: object, *, file_hash: str) -> dict[str, Any] | None:
    """Return a usable page map when it matches the current document hash."""
    if not isinstance(raw, dict):
        return None
    if raw.get("file_hash") != file_hash:
        return None
    if int(raw.get("scanner_version") or 0) != PAGE_MAP_SCANNER_VERSION:
        return None
    entries = raw.get("entries")
    if not isinstance(entries, list):
        return None
    return raw


def get_cached_pages(
    page_map: dict[str, Any] | None,
    *,
    creditor_name: str | None,
    account_number_masked: str | None,
) -> object:
    """Return cached pages, ``None`` for known unavailable, or ``CACHE_MISS``."""
    if page_map is None or not creditor_name:
        return CACHE_MISS
    key = page_map_entry_key(creditor_name, account_number_masked)
    for entry in page_map.get("entries") or []:
        if not isinstance(entry, dict):
            continue
        entry_creditor = str(entry.get("creditor_name") or "")
        entry_masked = entry.get("account_number_masked")
        entry_masked_str = str(entry_masked) if entry_masked is not None else None
        if page_map_entry_key(entry_creditor, entry_masked_str) != key:
            continue
        confidence = entry.get("confidence")
        pages_raw = entry.get("page_numbers")
        if confidence == "matched" and isinstance(pages_raw, list):
            pages = tuple(int(page) for page in pages_raw if isinstance(page, int))
            return pages if pages else CACHE_MISS
        if confidence == "unavailable":
            return ()
        return CACHE_MISS
    return CACHE_MISS


def merge_page_map_entry(
    page_map: dict[str, Any] | None,
    *,
    file_hash: str,
    creditor_name: str,
    account_number_masked: str | None,
    pages: tuple[int, ...],
) -> dict[str, Any]:
    """Upsert a scan result into the page map (empty tuple = unavailable)."""
    base = deepcopy(page_map) if page_map is not None else empty_page_map(file_hash=file_hash)
    base["scanner_version"] = PAGE_MAP_SCANNER_VERSION
    base["file_hash"] = file_hash
    base["scanned_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entries = list(base.get("entries") or [])
    key = page_map_entry_key(creditor_name, account_number_masked)
    entry = {
        "creditor_name": creditor_name,
        "account_number_masked": account_number_masked,
        "page_numbers": list(pages),
        "confidence": "matched" if pages else "unavailable",
    }
    replaced = False
    for index, existing in enumerate(entries):
        if not isinstance(existing, dict):
            continue
        existing_creditor = str(existing.get("creditor_name") or "")
        existing_masked = existing.get("account_number_masked")
        existing_masked_str = str(existing_masked) if existing_masked is not None else None
        if page_map_entry_key(existing_creditor, existing_masked_str) == key:
            entries[index] = entry
            replaced = True
            break
    if not replaced:
        entries.append(entry)
    base["entries"] = entries
    return base


def lookup_cached_tradeline_pages(
    page_map_raw: object,
    *,
    file_hash: str,
    creditor_name: str | None,
    account_number_masked: str | None,
) -> tuple[int, ...] | None:
    """Return cached pages, ``()`` if unavailable, or ``None`` on cache miss."""
    page_map = normalize_page_map(page_map_raw, file_hash=file_hash)
    cached = get_cached_pages(
        page_map,
        creditor_name=creditor_name,
        account_number_masked=account_number_masked,
    )
    if cached is CACHE_MISS:
        return None
    return cached if isinstance(cached, tuple) else None


def page_map_update_from_scan(
    *,
    page_map_raw: object,
    file_hash: str,
    creditor_name: str,
    account_number_masked: str | None,
    scanned_pages: tuple[int, ...],
) -> dict[str, Any]:
    """Merge a scan result into the tradeline page map (raw or normalized)."""
    page_map = normalize_page_map(page_map_raw, file_hash=file_hash)
    return merge_page_map_entry(
        page_map,
        file_hash=file_hash,
        creditor_name=creditor_name,
        account_number_masked=account_number_masked,
        pages=scanned_pages,
    )


def lookup_or_locate_tradeline_pages(
    page_map: dict[str, Any] | None,
    *,
    file_hash: str | None,
    creditor_name: str | None,
    account_number_masked: str | None,
    pdf_bytes: bytes | None,
    locate: Callable[..., tuple[int, ...] | None],
) -> tuple[tuple[int, ...] | None, dict[str, Any] | None]:
    """Resolve pages from cache or locate+write-through on miss.

    Returns ``(pages, updated_page_map)``. ``updated_page_map`` is set only when
    a locate ran successfully and ``file_hash`` is available for persistence.
    """
    cached = get_cached_pages(
        page_map,
        creditor_name=creditor_name,
        account_number_masked=account_number_masked,
    )
    if cached is not CACHE_MISS:
        return (cached if isinstance(cached, tuple) else None), None

    if not creditor_name or not pdf_bytes:
        return None, None

    located = locate(
        pdf_bytes,
        target_creditor=creditor_name,
        target_account_masked=account_number_masked,
    )
    if located is None:
        return None, None

    if not file_hash:
        return located, None

    updated = merge_page_map_entry(
        page_map,
        file_hash=file_hash,
        creditor_name=creditor_name,
        account_number_masked=account_number_masked,
        pages=located,
    )
    return located, updated
