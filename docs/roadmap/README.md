# Product Roadmap

This directory is the **master planning layer** for the Verdin Credit Platform. Every sprint, epic, and release should trace back to a version milestone defined here.

**Executive status view:** [Platform Capability Matrix](../governance/capability-matrix.md)

## How to use this roadmap

1. **Pick the target version** for your sprint (usually the next unreleased milestone).
2. **Read the domain section** in [`v5.0-enterprise.md`](v5.0-enterprise.md) for long-term intent.
3. **Check [`../architecture/README.md`](../architecture/README.md)** before designing features — architecture docs are the technical constitution.
4. **Record significant decisions** as ADRs in [`../adr/`](../adr/).
5. **Record sprint-level engineering context** in [`../engineering/changelog.md`](../engineering/changelog.md).
6. **Follow the [release cadence](../governance/README.md#release-cadence)** — `main` releasable, `feature/*` capabilities, `sprint/*` stabilization, semantic tags, GitHub Releases.
7. **Ship with engineering standards** — documentation, tests, RBAC, audit events, API reference, frontend integration, CI validation.

## Release and sprint timeline

```text
v4.3.0 — Initial Operational Core (released)
    ↓
v4.3.1 — Mission Control, dashboard completion, governance updates (released)
    ↓
Sprint 4.3.1 — E2E validation, performance baselines, security review, coverage (current)
    ↓
v4.5.0 — Automation Platform (planned)
```

Semantic versions (`v4.3.0`, `v4.3.1`, `v4.5.0`) are product releases. Sprints (`Sprint 4.3.1`) are engineering milestones that harden a release before the next version opens.

## Version milestones

| Version   | Theme                       | Status      | Focus                                                                    |
| --------- | --------------------------- | ----------- | ------------------------------------------------------------------------ |
| **4.2**   | Platform Foundation         | **Shipped** | Monorepo, auth, RBAC, domain module pattern, worker scaffold, CI/CD      |
| **4.3.0** | Operational Core            | **Shipped** | Cases, accounts, documents, OCR, intelligence, timeline, tasks           |
| **4.3.1** | Operational Core Completion | **Shipped** | Mission Control dashboard, governance refinements, release stabilization |
| **4.5**   | Automation                  | Planned     | Import wizard, bureau parsing, workflow, disputes, AI assistant          |
| **4.8**   | Operations                  | Planned     | Client portal, notifications, reporting expansions                       |
| **5.0**   | Enterprise Edition          | Planned     | Multi-tenancy, compliance center, enterprise admin, predictive analytics |

### Sprint milestones

| Sprint    | Theme                          | Status             | Focus                                                            |
| --------- | ------------------------------ | ------------------ | ---------------------------------------------------------------- |
| **4.3.1** | Operational Core Stabilization | **Current sprint** | E2E validation, performance baselines, security review, coverage |

### Version 4.3.0 — Initial Operational Core

| Capability                  | Status |
| --------------------------- | ------ |
| Platform Foundation         | ✅     |
| Case Management             | ✅     |
| Credit Account Intelligence | ✅     |
| Document Foundation         | ✅     |
| OCR Pipeline                | ✅     |
| AI Classification           | ✅     |
| Metadata Extraction         | ✅     |
| Entity Resolution           | ✅     |
| Timeline Engine             | ✅     |
| Task Management             | ✅     |

**Tag:** `v4.3.0` — initial Operational Core GA.

### Version 4.3.1 — Operational Core completion

| Capability                | Status |
| ------------------------- | ------ |
| Mission Control Dashboard | ✅     |
| Governance & release docs | ✅     |

**Tag:** `v4.3.1` — Mission Control product API, dashboard UI, and governance refinements.

Release notes: [`docs/release-notes/v4.3.1.md`](../release-notes/v4.3.1.md)

### Sprint 4.3.1 — Operational Core Stabilization

Current sprint plan: [`docs/sprint-4.3.1/operational-core-stabilization.md`](../sprint-4.3.1/operational-core-stabilization.md)

Sprint 4.3.1 is an **engineering milestone**, not a semantic version. It validates that the Operational Core works as one product before 4.5 begins:

- 100% end-to-end workflow pass rate in CI for the complete case lifecycle
- Performance baselines captured and documented
- Security review completed with tracked findings
- Coverage target established (85–90% on core services and critical workflows)
- No critical or high-severity defects before opening Version 4.5

### Version 4.5 — Automation focus

Every 4.5 feature should leverage the Operational Core rather than modify its foundations.

Organize Version 4.5 into four focused epics:

| Epic | Theme                      | Included capabilities                                                                                              |
| ---- | -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 1    | Credit Report Intelligence | Import Wizard, bureau-specific parsers, historical report comparison, duplicate detection                          |
| 2    | Workflow Automation        | Workflow engine, scheduled jobs, SLA monitoring, automatic task generation, reminder engine                        |
| 3    | AI Assistance              | Case summaries, document summaries, dispute recommendations, missing evidence detection, next-best-action guidance |
| 4    | Client Experience          | Client Portal, secure messaging, notifications, uploads, progress tracking                                         |

Architectural recommendation: introduce a unified `packages/job-orchestrator/` layer during Version 4.5 so OCR, classification, metadata extraction, entity resolution, workflows, notifications, AI summaries, and imports share retry policies, scheduling, metrics, and queue abstractions.

## Sprint → version mapping

| Sprint work                               | Version / Sprint | Architecture domain                          |
| ----------------------------------------- | ---------------- | -------------------------------------------- |
| Sprint 2 Epic 1 — Case Management         | 4.3              | Case Management                              |
| Sprint 2 Epic 2 — Account Intelligence    | 4.3              | Credit Account Intelligence                  |
| Document Intelligence M1 — Foundation     | 4.3              | Document Foundation                          |
| Document Intelligence M2 — OCR            | 4.3              | OCR Pipeline                                 |
| Document Intelligence M3 — Classification | 4.3              | AI Classification (rules engine)             |
| Timeline & audit events                   | 4.3              | Timeline & Audit Engine                      |
| Task management completion                | 4.3              | Task Management                              |
| Mission Control Dashboard                 | 4.3.1            | Operational Dashboard                        |
| Operational Core stabilization            | Sprint 4.3.1     | Validation, performance, security, coverage  |
| Workflow automation (planned)             | 4.5              | Workflow Automation                          |
| Credit report import (planned)            | 4.5              | Credit Report Import                         |
| Advanced OCR & bureau parsing (planned)   | 4.5              | Document Intelligence                        |
| Dispute generation (planned)              | 4.5              | Dispute Generation                           |
| AI case assistant (planned)               | 4.5              | AI Assistant                                 |
| Notifications & messaging (planned)       | 4.5              | Communications                               |
| Client portal (planned)                   | 4.8              | Client Portal                                |
| Enterprise admin & compliance (planned)   | 5.0              | Enterprise Administration, Compliance Center |

## Primary document

- **[Version 5.0 Enterprise Roadmap](v5.0-enterprise.md)** — vision, domains, AI phases, security, integrations, success metrics, and release timeline.

## Related documentation

- [Platform Capability Matrix](../governance/capability-matrix.md) — executive readiness view
- [Governance hub](../governance/README.md) — feature lifecycle and build order
- [Engineering Decision Log](../engineering/changelog.md) — technical rationale across milestones
- [Sprint 4.3.1 stabilization](../sprint-4.3.1/operational-core-stabilization.md)
- [Release notes — v4.3.1](../release-notes/v4.3.1.md)
- [Release notes — v4.3.0 GA](../release-notes/v4.3.0-ga.md)
- [Architecture](../architecture/README.md) — technical constitution
- [ADR index](../adr/README.md) — architecture decision records
- [Release notes](../release-notes/) — shipped change logs
- [Developer guide](../developer-guide.md) — day-to-day development
