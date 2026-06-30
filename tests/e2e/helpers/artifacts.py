"""Diagnostic artifact collection for E2E runs.

Every stage records its key request/response payloads into a collector. When a
test fails, the collector is flushed to ``tests/e2e/_artifacts/<test>/`` so the
exact API responses, OCR output, and dashboard snapshot are available for
debugging in CI (uploaded as a workflow artifact).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ArtifactCollector:
    """Accumulates named diagnostic payloads for a single test."""

    def __init__(self, name: str, output_dir: Path) -> None:
        self._name = name
        self._output_dir = output_dir
        self._items: list[dict[str, Any]] = []

    def record(self, label: str, payload: Any) -> None:
        """Capture a labelled payload (response body, status, timings, etc.)."""
        self._items.append(
            {
                "label": label,
                "recorded_at": datetime.now(UTC).isoformat(),
                "payload": _coerce(payload),
            }
        )

    def dump(self) -> Path | None:
        """Write all recorded payloads to disk. Returns the directory written."""
        if not self._items:
            return None
        target_dir = self._output_dir / _safe_name(self._name)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "artifacts.json"
        target.write_text(
            json.dumps(
                {"test": self._name, "items": self._items},
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        return target_dir


def _coerce(payload: Any) -> Any:
    """Best-effort conversion of arbitrary payloads into JSON-friendly data."""
    if isinstance(payload, (str, int, float, bool)) or payload is None:
        return payload
    if isinstance(payload, dict):
        return {str(key): _coerce(value) for key, value in payload.items()}
    if isinstance(payload, (list, tuple)):
        return [_coerce(item) for item in payload]
    return str(payload)


def _safe_name(name: str) -> str:
    return "".join(char if char.isalnum() or char in "-_." else "_" for char in name)
