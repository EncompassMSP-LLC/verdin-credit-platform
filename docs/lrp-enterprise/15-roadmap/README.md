# 15 — Roadmap

Edition delivery tracking.

## Active program (blueprint-first)

| Stage | Focus                   | Status                        |
| ----- | ----------------------- | ----------------------------- |
| 1     | Company Blueprint       | **In progress**               |
| 2     | Product Blueprint       | Queued                        |
| 3     | Design System           | Queued                        |
| 4     | Technology Architecture | Queued                        |
| 5     | Cursor Development      | Blocked until Stages 1–4 exit |

Master: [Build Bible v2.0](../build-bible/README.md) · [Stages](../stages/README.md) · [Program pivot](../00-executive/program-pivot.md)

## Business Operations Package (Phase 3 company ops) — COMPLETE

Lender-ready organization runbooks (onboarding → automation):

→ [`../04-operations/business-ops-package/`](../04-operations/business-ops-package/)

## Phase 4 — Lending Readiness Platform™ V1.0 (active)

Turn ops runbooks into working software on the shared monorepo (not a product fork).

| Doc                                             | Path                                                                                                                         |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **V1.0 release plan** (gap matrix + milestones) | [`lending-readiness-platform-v1.0-release-plan.md`](lending-readiness-platform-v1.0-release-plan.md)                         |
| **Executable checklist**                        | [`../../development/lrp-platform-v1.0-completion-checklist.md`](../../development/lrp-platform-v1.0-completion-checklist.md) |
| Sprint loop                                     | `.cursor/rules/lrp-platform-v1-sprint-loop.mdc`                                                                              |
| Phase 4 handoff (from ops)                      | [`../04-operations/business-ops-package/phase-4-handoff.md`](../04-operations/business-ops-package/phase-4-handoff.md)       |

Milestones: **M1** core modules → **M2** automation → **M3** portals → **M4** intelligence/AI → **M5** production hardening.

## Platform engineering (parallel)

Shared-platform slices (e.g. `ENABLE_MORTGAGE_PARTNER`, Version 29.0 foundation) continue; LRP V1.0 wires them into production UX.

## Canonical sources

- [Product roadmap](../../roadmap/README.md) — Version 29.0 Mortgage Partner Edition
- [Version 29.0 checklist](../../development/version-29.0-completion-checklist.md)
- [LRP Platform V1.0 checklist](../../development/lrp-platform-v1.0-completion-checklist.md)
- [Capability matrix §29.0](../../governance/capability-matrix.md)
- [Business Ops Package checklist](../04-operations/business-ops-package/00-completion-checklist.md)
