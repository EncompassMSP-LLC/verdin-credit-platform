"""Export consultation pack draft as text or ZIP (staff-gated; never auto-sent)."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO
from typing import Any, Literal

from api.modules.accounts.credit_analysis import ADVISORY_DISCLAIMER

ConsultationPackExportFormat = Literal["text", "zip"]


def _artifact_text(name: str, artifact: dict[str, Any]) -> str:
    lines = [
        f"# {artifact.get('title', name)}",
        f"Status: {artifact.get('status', 'draft')}",
        "",
        ADVISORY_DISCLAIMER,
        "",
    ]
    if "body" in artifact:
        lines.append(str(artifact["body"]))
    elif "subject" in artifact:
        lines.append(f"Subject: {artifact['subject']}")
        lines.append("")
        lines.append(str(artifact.get("body", "")))
        lines.append("")
        lines.append(f"Send policy: {artifact.get('send_policy', '')}")
    else:
        lines.append(json.dumps(artifact, indent=2, default=str))
    return "\n".join(lines).strip() + "\n"


def build_consultation_pack_text(payload: dict[str, Any]) -> str:
    artifacts = payload.get("artifacts") or {}
    sections = [
        "CONSULTATION COMPLETED PACK (DRAFT)",
        f"Case: {payload.get('case_title')} ({payload.get('case_id')})",
        "",
        ADVISORY_DISCLAIMER,
        "",
        "Send guardrails: never auto-transmitted; partner notification remains draft.",
        "",
    ]
    for key, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            continue
        sections.append("=" * 60)
        sections.append(_artifact_text(key, artifact))
        sections.append("")
    return "\n".join(sections).strip() + "\n"


def build_consultation_pack_zip(payload: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    artifacts = payload.get("artifacts") or {}
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("00-README.txt", build_consultation_pack_text(payload))
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "schema_version": payload.get("schema_version"),
                    "case_id": payload.get("case_id"),
                    "send_guardrails": payload.get("send_guardrails"),
                    "artifact_keys": list(artifacts.keys()),
                },
                indent=2,
            )
            + "\n",
        )
        for index, (key, artifact) in enumerate(artifacts.items(), start=1):
            if not isinstance(artifact, dict):
                continue
            archive.writestr(
                f"{index:02d}-{key}.txt",
                _artifact_text(key, artifact),
            )
            archive.writestr(
                f"{index:02d}-{key}.json",
                json.dumps(artifact, indent=2, default=str) + "\n",
            )
    return buffer.getvalue()


def build_consultation_pack_export(
    payload: dict[str, Any],
    *,
    case_id: str,
    export_format: ConsultationPackExportFormat,
) -> tuple[bytes, str, str]:
    short = case_id.replace("-", "")[:8]
    if export_format == "zip":
        return (
            build_consultation_pack_zip(payload),
            f"consultation-pack-{short}.zip",
            "application/zip",
        )
    return (
        build_consultation_pack_text(payload).encode("utf-8"),
        f"consultation-pack-{short}.txt",
        "text/plain; charset=utf-8",
    )
