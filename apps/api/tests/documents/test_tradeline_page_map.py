"""Unit tests for tradeline page map cache helpers."""

from __future__ import annotations

from api.modules.documents.tradeline_page_map import (
    CACHE_MISS,
    get_cached_pages,
    merge_page_map_entry,
    normalize_page_map,
    page_map_entry_key,
)


def test_page_map_entry_key_normalizes() -> None:
    assert page_map_entry_key("Metro Retail", "****1111") == page_map_entry_key(
        "metro retail", "****1111"
    )


def test_normalize_page_map_rejects_stale_hash() -> None:
    raw = {
        "scanner_version": 1,
        "file_hash": "abc",
        "entries": [],
    }
    assert normalize_page_map(raw, file_hash="abc") is raw
    assert normalize_page_map(raw, file_hash="def") is None


def test_merge_and_get_cached_pages() -> None:
    updated = merge_page_map_entry(
        None,
        file_hash="hash1",
        creditor_name="Metro Retail",
        account_number_masked="****1111",
        pages=(3, 7),
    )
    assert get_cached_pages(
        updated,
        creditor_name="Metro Retail",
        account_number_masked="****1111",
    ) == (3, 7)

    unavailable = merge_page_map_entry(
        updated,
        file_hash="hash1",
        creditor_name="Other Co",
        account_number_masked=None,
        pages=(),
    )
    assert (
        get_cached_pages(
            unavailable,
            creditor_name="Other Co",
            account_number_masked=None,
        )
        == ()
    )
    assert (
        get_cached_pages(
            unavailable,
            creditor_name="Missing",
            account_number_masked=None,
        )
        is CACHE_MISS
    )
