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
Sprint 4.3.1 — E2E validation, performance baselines, security review, coverage (shipped)
    ↓
v4.5.0 — Automation Platform (released)
    ↓
v4.8.0 — Operations (released)
    ↓
v5.0 — Enterprise Edition (released)
```

Semantic versions (`v4.3.0`, `v4.3.1`, `v4.5.0`) are product releases. Sprints (`Sprint 4.3.1`) are engineering milestones that harden a release before the next version opens.

## Version milestones

| Version   | Theme                       | Status      | Focus                                                                             |
| --------- | --------------------------- | ----------- | --------------------------------------------------------------------------------- |
| **4.2**   | Platform Foundation         | **Shipped** | Monorepo, auth, RBAC, domain module pattern, worker scaffold, CI/CD               |
| **4.3.0** | Operational Core            | **Shipped** | Cases, accounts, documents, OCR, intelligence, timeline, tasks                    |
| **4.3.1** | Operational Core Completion | **Shipped** | Mission Control dashboard, governance refinements, release stabilization          |
| **4.5**   | Automation                  | **Shipped** | Import wizard, dispute lifecycle, workflow auto-tasks, rules AI (`v4.5.0`)        |
| **4.8**   | Operations                  | **Shipped** | Client portal, notifications, LLM policy gates, reporting (`v4.8.0`)              |
| **5.0**   | Enterprise Edition          | **Shipped** | Compliance, SSO/MFA, LLM summaries, production email, portal expansion (`v5.0.0`) |

### Sprint milestones

| Sprint    | Theme                          | Status      | Focus                                                      |
| --------- | ------------------------------ | ----------- | ---------------------------------------------------------- |
| **4.3.1** | Operational Core Stabilization | **Shipped** | E2E gate, performance baselines, security review, coverage |

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

### Sprint 4.3.1 — Operational Core Stabilization (shipped)

Plan: [`docs/sprint-4.3.1/operational-core-stabilization.md`](../sprint-4.3.1/operational-core-stabilization.md)

Sprint 4.3.1 validated the Operational Core before Version 4.5 automation. **All exit criteria met** — including E2E lifecycle, dispute letter gate, performance baselines, security review, and branch protection.

### Version 4.5 — Automation (shipped)

Scope and deferrals: [`docs/governance/version-4.5-scope.md`](../governance/version-4.5-scope.md)

Every 4.5 feature builds on the Operational Core without modifying its foundations.

| Epic | Theme                      | v4.5.0 outcome | Notes                                                        |
| ---- | -------------------------- | -------------- | ------------------------------------------------------------ |
| 1    | Credit Report Intelligence | ✅ Shipped     | Import wizard, parsers, comparison, duplicate detection      |
| 2    | Workflow Automation        | Partial        | Event-driven auto-tasks; BPM/cron/notifications → 4.8        |
| 3    | Dispute Generation         | Partial        | Rule-based letter lifecycle + export; auto-filing → 5.0+     |
| 4    | AI Assistance              | Partial        | Heuristic + rules intelligence; LLM surfaces → 4.8           |
| —    | Client Experience          | Deferred 4.8   | Portal, messaging, notifications (moved out of 4.5 RC scope) |

**Deferred from 4.5 to 4.8:** client portal, notification delivery, LLM case/document summaries, LLM classification augmentation, full workflow engine, `packages/job-orchestrator/`.

**Tag:** `v4.5.0` — Automation Platform.

Release notes: [`docs/release-notes/v4.5.0.md`](../release-notes/v4.5.0.md)

### Version 4.8 — Operations (shipped)

Scope and deferrals: [`docs/governance/version-4.8-scope.md`](../governance/version-4.8-scope.md)

| Epic | Theme               | v4.8.0 outcome | Notes                                                    |
| ---- | ------------------- | -------------- | -------------------------------------------------------- |
| 1    | Notifications       | Partial        | In-app + staff UI; email readiness scaffold; sends → 5.0 |
| 2    | Workflow Operations | Partial        | Overdue scan worker + job-orchestrator scaffold          |
| 3    | Client Experience   | Partial        | Clients, portal auth, read-only case progress            |
| 4    | AI Assistance       | Partial        | ADR-012 + `ENABLE_LLM` gates; summary endpoints → 5.0    |
| 5    | Reporting           | Partial        | Operations read model + Mission Control dashboard embed  |

**Tag:** `v4.8.0` — Operations.

Release notes: [`docs/release-notes/v4.8.0.md`](../release-notes/v4.8.0.md)

### Version 5.0 — Enterprise Edition (shipped)

Scope and deferrals: [`docs/governance/version-5.0-scope.md`](../governance/version-5.0-scope.md)

| Epic | Theme                 | v5.0.0 outcome | Notes                                                    |
| ---- | --------------------- | -------------- | -------------------------------------------------------- |
| 1    | Data & client linking | Partial        | `cases.client_id` FK; bulk import → 5.0+                 |
| 2    | Communications        | Partial        | Production email + audit; SMS production → 5.0+          |
| 3    | AI Assistance (LLM)   | Partial        | Case summary post-gate; document summaries → 5.0+        |
| 4    | Platform operations   | Partial        | Orchestrator retry/metrics + cron; PG persistence → 5.0+ |
| 5    | Enterprise identity   | Partial        | SSO/MFA readiness scaffold; IdP enrollment → 5.0+        |
| 6    | Compliance            | Partial        | Consent + retention placeholders; enforcement → 5.0+     |
| 7    | Client portal         | Partial        | Upload + messaging scaffold; real-time delivery → 5.0+   |
| 8    | Enterprise admin      | Partial        | API key lifecycle; SCIM/billing admin → 5.0+             |
| 9    | Reporting & analytics | Partial        | Bureau + team productivity; materialized views → 5.0+    |

**Tag:** `v5.0.0` — Enterprise Edition.

Release notes: [`docs/release-notes/v5.0.0.md`](../release-notes/v5.0.0.md)

## Sprint → version mapping

| Sprint work                               | Version / Sprint | Architecture domain                                      |
| ----------------------------------------- | ---------------- | -------------------------------------------------------- |
| Sprint 2 Epic 1 — Case Management         | 4.3              | Case Management                                          |
| Sprint 2 Epic 2 — Account Intelligence    | 4.3              | Credit Account Intelligence                              |
| Document Intelligence M1 — Foundation     | 4.3              | Document Foundation                                      |
| Document Intelligence M2 — OCR            | 4.3              | OCR Pipeline                                             |
| Document Intelligence M3 — Classification | 4.3              | AI Classification (rules engine)                         |
| Timeline & audit events                   | 4.3              | Timeline & Audit Engine                                  |
| Task management completion                | 4.3              | Task Management                                          |
| Mission Control Dashboard                 | 4.3.1            | Operational Dashboard                                    |
| Operational Core stabilization            | Sprint 4.3.1     | Validation, performance, security, coverage              |
| Workflow automation (planned)             | 4.5              | Workflow Automation                                      |
| Credit report import (planned)            | 4.5              | Credit Report Import                                     |
| Advanced OCR & bureau parsing (planned)   | 4.5              | Document Intelligence                                    |
| Dispute generation (planned)              | 4.5              | Dispute Generation                                       |
| AI case assistant (planned)               | 4.8              | AI Assistant (LLM policy gates shipped; summaries → 5.0) |
| Notifications & messaging (planned)       | 4.8              | Communications (in-app shipped; provider sends → 5.0)    |
| Client portal (planned)                   | 4.8              | Client Portal (auth + read-only progress shipped)        |
| Enterprise admin & compliance (planned)   | 5.0              | Enterprise Administration, Compliance Center             |

## Primary document

- **[Version 5.0 Enterprise Roadmap](v5.0-enterprise.md)** — vision, domains, AI phases, security, integrations, success metrics, and release timeline.

## Related documentation

- [Platform Capability Matrix](../governance/capability-matrix.md) — executive readiness view
- [Governance hub](../governance/README.md) — feature lifecycle and build order
- [Engineering Decision Log](../engineering/changelog.md) — technical rationale across milestones
- [Sprint 4.3.1 stabilization](../sprint-4.3.1/operational-core-stabilization.md)
- [Release notes — v4.3.1](../release-notes/v4.3.1.md)
- [Release notes — v4.5.0](../release-notes/v4.5.0.md)
- [Version 5.0 completion checklist](../development/version-5.0-completion-checklist.md)
- [Release notes — v4.8.0](../release-notes/v4.8.0.md)
- [Release notes — v5.0.0](../release-notes/v5.0.0.md)
- [Release notes — v4.3.0 GA](../release-notes/v4.3.0-ga.md)
- [Architecture](../architecture/README.md) — technical constitution
- [ADR index](../adr/README.md) — architecture decision records
- [Release notes](../release-notes/) — shipped change logs
- [Developer guide](../developer-guide.md) — day-to-day development
