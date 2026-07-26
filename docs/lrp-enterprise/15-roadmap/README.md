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

| Doc                          | Path                                                                                                                         |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **V1.0 master release plan** | [`lending-readiness-platform-v1.0-release-plan.md`](lending-readiness-platform-v1.0-release-plan.md)                         |
| Feature traceability matrix  | [`v1.0-feature-traceability-matrix.md`](v1.0-feature-traceability-matrix.md)                                                 |
| Gap analysis                 | [`v1.0-gap-analysis.md`](v1.0-gap-analysis.md)                                                                               |
| Executable checklist         | [`../../development/lrp-platform-v1.0-completion-checklist.md`](../../development/lrp-platform-v1.0-completion-checklist.md) |
| Product backlog              | [`product-backlog.md`](product-backlog.md)                                                                                   |
| Release roadmap (v1.1+)      | [`release-roadmap.md`](release-roadmap.md)                                                                                   |
| Technical debt register      | [`technical-debt-register.md`](technical-debt-register.md)                                                                   |
| Risk register                | [`risk-register.md`](risk-register.md)                                                                                       |
| ADR-013 (edition, not fork)  | [`../../adr/013-lrp-edition-on-shared-platform.md`](../../adr/013-lrp-edition-on-shared-platform.md)                         |
| Sprint loop                  | `.cursor/rules/lrp-platform-v1-sprint-loop.mdc`                                                                              |
| Phase 4 handoff (from ops)   | [`../04-operations/business-ops-package/phase-4-handoff.md`](../04-operations/business-ops-package/phase-4-handoff.md)       |

Milestones: **M1** Core → **M2** Readiness → **M3** Automation → **M4** Partner Experience → **M5** Public Experience → **M6** Production Readiness.

## Platform engineering (parallel)

Shared-platform slices (e.g. `ENABLE_MORTGAGE_PARTNER`, Version 29.0 foundation) continue; LRP V1.0 wires them into production UX.

## Canonical sources

- [Product roadmap](../../roadmap/README.md) — Version 29.0 Mortgage Partner Edition
- [Version 29.0 checklist](../../development/version-29.0-completion-checklist.md)
- [LRP Platform V1.0 checklist](../../development/lrp-platform-v1.0-completion-checklist.md)
- [Capability matrix §29.0](../../governance/capability-matrix.md)
- [Business Ops Package checklist](../04-operations/business-ops-package/00-completion-checklist.md)
