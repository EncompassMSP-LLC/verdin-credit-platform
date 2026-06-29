# Product Roadmap

This directory is the **master planning layer** for the Verdin Credit Platform. Every sprint, epic, and release should trace back to a version milestone defined here.

**Executive status view:** [Platform Capability Matrix](../governance/capability-matrix.md)

## How to use this roadmap

1. **Pick the target version** for your sprint (usually the next unreleased milestone).
2. **Read the domain section** in [`v5.0-enterprise.md`](v5.0-enterprise.md) for long-term intent.
3. **Check [`../architecture/README.md`](../architecture/README.md)** before designing features — architecture docs are the technical constitution.
4. **Record significant decisions** as ADRs in [`../adr/`](../adr/).
5. **Ship with engineering standards** — documentation, tests, RBAC, audit events, API reference, frontend integration, CI validation.

## Version milestones

| Version | Theme               | Status               | Focus                                                                       |
| ------- | ------------------- | -------------------- | --------------------------------------------------------------------------- |
| **4.2** | Platform Foundation | **Shipped**          | Monorepo, auth, RBAC, domain module pattern, worker scaffold, CI/CD         |
| **4.3** | Operational Core    | **Shipped (v4.3.0)** | Cases, accounts, documents, OCR, metadata, timeline, tasks, Mission Control |
| **4.5** | Automation          | Planned              | Import wizard, AI assistant, dispute generation, workflow automation        |
| **4.8** | Operations          | Planned              | Reporting, dashboards, client portal, notifications                         |
| **5.0** | Enterprise Edition  | Planned              | Multi-tenancy, compliance center, enterprise admin, predictive analytics    |

### Version 4.3 — Operational Core (complete)

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
| Mission Control Dashboard   | ✅     |

**Current work:** Stabilization cycle — E2E workflows, test coverage, performance profiling, security review.

**Release:** Tag **`v4.3.0`** after Operational Dashboard merge.

### Version 4.5 — Automation (next)

| Phase | Focus                                                                           |
| ----- | ------------------------------------------------------------------------------- |
| 1     | Credit Report Import Wizard — bureau-specific parsing, report comparison        |
| 2     | AI Case Assistant — summaries, recommendations                                  |
| 3     | Dispute Generation Engine — bureau letters, furnisher disputes, CFPB complaints |
| 4     | Workflow automation — scheduled jobs, reminders, auto task generation           |
| 5     | Client Portal — secure messaging, client uploads, status tracking               |

## Sprint → version mapping

| Sprint work                               | Version | Architecture domain                          |
| ----------------------------------------- | ------- | -------------------------------------------- |
| Sprint 2 Epic 1 — Case Management         | 4.3     | Case Management                              |
| Sprint 2 Epic 2 — Account Intelligence    | 4.3     | Credit Account Intelligence                  |
| Document Intelligence M1 — Foundation     | 4.3     | Document Foundation                          |
| Document Intelligence M2 — OCR            | 4.3     | OCR Pipeline                                 |
| Document Intelligence M3 — Classification | 4.3     | AI Classification (rules engine)             |
| Timeline & audit events (planned)         | 4.3     | Timeline & Audit Engine                      |
| Task management completion (planned)      | 4.3     | Task Management                              |
| Workflow automation (planned)             | 4.5     | Workflow Automation                          |
| Credit report import (planned)            | 4.5     | Credit Report Import                         |
| Dispute generation (planned)              | 4.5     | Dispute Generation                           |
| Reporting & dashboards (planned)          | 4.8     | Reporting & Analytics                        |
| Client portal (planned)                   | 4.8     | Client Portal                                |
| Enterprise admin & compliance (planned)   | 5.0     | Enterprise Administration, Compliance Center |

## Primary document

- **[Version 5.0 Enterprise Roadmap](v5.0-enterprise.md)** — vision, domains, AI phases, security, integrations, success metrics, and release timeline.

## Related documentation

- [Platform Capability Matrix](../governance/capability-matrix.md) — executive readiness view
- [Governance hub](../governance/README.md) — feature lifecycle and build order
- [Release notes — M2 OCR](../release-notes/v4.3-m2-ocr-pipeline.md)
- [Architecture](../architecture/README.md) — technical constitution
- [ADR index](../adr/README.md) — architecture decision records
- [Release notes](../release-notes/) — shipped change logs
- [Developer guide](../developer-guide.md) — day-to-day development
