"""Unit tests for tradeline page map cache helpers."""

from __future__ import annotations

from api.modules.documents.tradeline_page_map import (
    CACHE_MISS,
    get_cached_pages,
    lookup_cached_tradeline_pages,
    lookup_or_locate_tradeline_pages,
    merge_page_map_entry,
    normalize_page_map,
    page_map_entry_key,
    page_map_update_from_scan,
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


def test_lookup_cached_tradeline_pages_hit_and_miss() -> None:
    page_map = merge_page_map_entry(
        None,
        file_hash="hash1",
        creditor_name="Metro Retail",
        account_number_masked="****1111",
        pages=(2,),
    )
    assert lookup_cached_tradeline_pages(
        page_map,
        file_hash="hash1",
        creditor_name="Metro Retail",
        account_number_masked="****1111",
    ) == (2,)
    assert (
        lookup_cached_tradeline_pages(
            page_map,
            file_hash="hash1",
            creditor_name="Missing",
            account_number_masked=None,
        )
        is None
    )


def test_lookup_or_locate_writes_through_on_miss() -> None:
    def _locate(
        _pdf: bytes,
        *,
        target_creditor: str,
        target_account_masked: str | None,
    ) -> tuple[int, ...] | None:
        assert target_creditor == "Metro Retail"
        assert target_account_masked == "****1111"
        return (4, 5)

    pages, updated = lookup_or_locate_tradeline_pages(
        None,
        file_hash="hash1",
        creditor_name="Metro Retail",
        account_number_masked="****1111",
        pdf_bytes=b"%PDF-fake",
        locate=_locate,
    )
    assert pages == (4, 5)
    assert updated is not None
    assert updated["entries"][0]["page_numbers"] == [4, 5]


def test_lookup_or_locate_reuses_cache_without_locate() -> None:
    page_map = merge_page_map_entry(
        None,
        file_hash="hash1",
        creditor_name="Metro Retail",
        account_number_masked="****1111",
        pages=(9,),
    )

    def _locate(*_args: object, **_kwargs: object) -> tuple[int, ...] | None:
        raise AssertionError("locate should not run on cache hit")

    pages, updated = lookup_or_locate_tradeline_pages(
        page_map,
        file_hash="hash1",
        creditor_name="Metro Retail",
        account_number_masked="****1111",
        pdf_bytes=b"%PDF-fake",
        locate=_locate,
    )
    assert pages == (9,)
    assert updated is None


def test_page_map_update_from_scan_wrapper() -> None:
    updated = page_map_update_from_scan(
        page_map_raw=None,
        file_hash="hash2",
        creditor_name="Metro Retail",
        account_number_masked=None,
        scanned_pages=(),
    )
    assert updated["entries"][0]["confidence"] == "unavailable"
