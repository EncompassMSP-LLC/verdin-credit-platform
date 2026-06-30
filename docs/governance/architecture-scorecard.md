# Architecture Decision Scorecard — Sprint 4.3.1

**Purpose:** one-page executive engineering review for a release. This is not an ADR — it summarizes architectural health at a point in time and points to evidence.

**Release scope:** Operational Core stabilization (`v4.3.1` tag shipped; Sprint 4.3.1 validation in progress)  
**Last reviewed:** 2026-06-29  
**As-built reference:** [`docs/architecture/v4.3.0-snapshot.md`](../architecture/v4.3.0-snapshot.md)

## Scorecard

| Area               | Status | Notes                                                                                                                                                              |
| ------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Modularity         | ✅     | Domain modules under `apps/api/api/modules/` are isolated; shared logic lives in `packages/`                                                                       |
| Repository pattern | ✅     | Routers delegate to services; repositories own SQLAlchemy access — no direct DB access in routers                                                                  |
| Event bus          | ✅     | `packages/event-bus` wired through domain services; timeline subscriber persists append-only events                                                                |
| Testability        | ✅     | 120 API integration tests, 7 worker tests, 1 E2E golden path (`test_full_case_lifecycle`), CI + E2E workflows                                                      |
| Performance        | 🟡     | Login exceeds `<150 ms` target (330.89 ms avg verified; bcrypt-bound); all other SLA targets pass — see [baseline](../quality/performance/v4.3.1-baseline.md)      |
| Security           | ✅     | Sprint review checklist complete with no unresolved findings — see [security review](../quality/security/v4.3.1-review.md)                                         |
| Documentation      | ✅     | Architecture snapshot, capability matrix, quality area, API reference, and sprint plan are current                                                                 |
| Release governance | ✅     | Semantic tags, GitHub Releases, capability matrix updates, and stabilization sprint cadence established                                                            |
| Technical debt     | 🟡     | Known items tracked in [engineering changelog](../engineering/changelog.md) — dashboard aggregation concentration, in-process event bus, login profiling follow-up |

## Evidence links

| Area                  | Primary reference                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Modularity & layering | [Architecture snapshot](../architecture/v4.3.0-snapshot.md), [ADR 009](../adr/009-architecture-governance.md)          |
| Event bus             | [Timeline release notes](../release-notes/v4.3-m5-timeline-audit-engine.md)                                            |
| Testability           | [`tests/e2e/README.md`](../../tests/e2e/README.md), [E2E strategy](../quality/testing/e2e-strategy.md)                 |
| Performance           | [v4.3.1 baseline](../quality/performance/v4.3.1-baseline.md), [CI thresholds](../quality/performance/ci-thresholds.md) |
| Security              | [v4.3.1 security review](../quality/security/v4.3.1-review.md)                                                         |
| Technical debt        | [Engineering changelog](../engineering/changelog.md)                                                                   |
| Sprint exit criteria  | [Operational Core stabilization](../sprint-4.3.1/operational-core-stabilization.md)                                    |

## Version 4.5 readiness

Sprint 4.3.1 must close the 🟡 items above before Version 4.5 implementation begins. The first 4.5 epic — Credit Report Import Wizard — should build on a pluggable parser framework (`packages/report-parsers/`) rather than embedding bureau-specific logic in the document pipeline. See the engineering changelog for the planned package shape.

## How to update this scorecard

Update this document when tagging a release or closing a stabilization sprint:

1. Re-read the [architecture snapshot](../architecture/v4.3.0-snapshot.md) (or publish a new snapshot if the module map changed materially).
2. Refresh [repository health](repository-health.md) metrics from CI and local measurement scripts.
3. Set each area to ✅ (healthy), 🟡 (known gap with tracked follow-up), or 🔴 (blocks release).
4. Link every 🟡 or 🔴 row to a sprint doc, quality artifact, GitHub issue, or ADR.
5. Commit the scorecard update in the same PR as the release notes or sprint close-out.
