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

| Version   | Theme                                           | Status      | Focus                                                                                                                                            |
| --------- | ----------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **4.2**   | Platform Foundation                             | **Shipped** | Monorepo, auth, RBAC, domain module pattern, worker scaffold, CI/CD                                                                              |
| **4.3.0** | Operational Core                                | **Shipped** | Cases, accounts, documents, OCR, intelligence, timeline, tasks                                                                                   |
| **4.3.1** | Operational Core Completion                     | **Shipped** | Mission Control dashboard, governance refinements, release stabilization                                                                         |
| **4.5**   | Automation                                      | **Shipped** | Import wizard, dispute lifecycle, workflow auto-tasks, rules AI (`v4.5.0`)                                                                       |
| **4.8**   | Operations                                      | **Shipped** | Client portal, notifications, LLM policy gates, reporting (`v4.8.0`)                                                                             |
| **5.0**   | Enterprise Edition                              | **Shipped** | Compliance, SSO/MFA, LLM summaries, production email, portal expansion (`v5.0.0`)                                                                |
| **5.0+**  | Product Hardening                               | **Shipped** | Pilot-ready staff + portal UI for 5.0 APIs                                                                                                       |
| **5.1**   | Production Hardening                            | **Shipped** | API keys, billing, IdP enrollment, enforcement, push, materialized reporting (`v5.1.0`)                                                          |
| **5.2**   | Deferred Production Surfaces                    | **Shipped** | SMS, LLM document summaries, Web Push HTTP, revenue analytics (`v5.2.0`)                                                                         |
| **5.3**   | Enterprise Depth                                | **Shipped** | Usage metering, SCIM, predictive analytics, API developer surfaces (`v5.3.0`)                                                                    |
| **5.4**   | Production Operations                           | **Shipped** | Invoicing/dunning, multi-IdP federation, marketing SMS, agent observability (`v5.4.0`)                                                           |
| **5.5**   | Production Automation                           | **Shipped** | Invoice collection, SAML metadata, SMS delivery worker, agent execution scaffold                                                                 |
| **5.6**   | Compliance-Reviewed Depth                       | Released    | HRIS sync, SMS deliverability, LLM dispute augment, dispute filing prep                                                                          |
| **5.7**   | Autonomous Workflows (gated)                    | Released    | Bureau submission, agent tool-calling, SAML cert rotation, Stripe invoice PDF                                                                    |
| **5.8**   | Production Integrations (gated)                 | Released    | Supervised agent loops, bureau live API, Stripe tax, HRIS lifecycle sync (`v5.8.0`)                                                              |
| **5.9**   | Autonomous Production (gated)                   | Released    | Unsupervised agent loops, bureau filing, live Stripe Tax, SAML rotation (`v5.9.0`)                                                               |
| **5.10**  | Production Automation (gated)                   | Released    | Arbitrary execution, bureau re-filing, charge retry, SAML passwordless                                                                           |
| **5.11**  | Production Execution (gated)                    | Released    | Unsupervised re-filing, live charge retry, HRIS passwordless UI, bulk IdP provisioning                                                           |
| **5.12**  | Expansion Surfaces (gated)                      | Released    | Bureau live API scaffold, public OAuth portal, cross-org benchmarks, passkeys (`v5.12.0`)                                                        |
| **5.13**  | Native Mobile Depth (gated)                     | Released    | Native passkey client, OAuth marketplace, autonomous API filing, export audit (`v5.13.0`)                                                        |
| **5.14**  | Production Distribution (gated)                 | Released    | Live blob export, unsupervised filing loops, public marketplace, app store readiness (`v5.14.0`)                                                 |
| **5.15**  | Identity Theft Detection                        | Released    | Phase 8 Case Center, portal attestation, §605B packet export (`v5.15.0`)                                                                         |
| **5.16**  | Identity-Theft Recovery Depth                   | Released    | Phase 9 §605B evidence bundling, mixed-file detection, submission readiness, lock-aware prepare (`v5.16.0`)                                      |
| **5.17**  | Dispute Response & Reinvestigation              | Released    | Phase 10 dispute response intake, §611 reinvestigation clock, re-dispute readiness, case dashboard (`v5.17.0`)                                   |
| **5.18**  | Reinvestigation Depth & Litigation              | Released    | Phase 11 per-letter multi-round clock, 45-day extended window, outcome analytics, litigation-readiness packet (`v5.18.0`)                        |
| **5.19**  | Reinvestigation Analytics & Evidence Depth      | Released    | Phase 12 analytics date-range/bureau slicing, per-recipient clock splits, cross-bureau litigation evidence, evidence export (`v5.19.0`)          |
| **5.20**  | Reinvestigation Analytics & Evidence Refinement | Released    | Phase 13 per-bureau analytics breakdown, per-recipient extended-window accuracy, PDF evidence export, cross-bureau discrepancy depth (`v5.20.0`) |
| **5.21**  | Reinvestigation Analytics & Evidence Polish     | Released    | Phase 14 per-recipient analytics breakdown, cross-bureau high_balance/credit_limit, structured PDF litigation export layout (`v5.21.0`)          |
| **16.0**  | Reinvestigation Operations & Configuration      | Released    | Phase 15 org cross-bureau tolerance, bureau response ingestion audit scaffold, org-internal outcome benchmarks (`v16.0.0`)                       |
| **17.0**  | Reinvestigation Operations Surfaces             | Released    | Phase 16 Reporting Center benchmarks UI, Compliance Center ingestion audit UI (`v17.0.0`)                                                        |
| **18.0**  | Reinvestigation Operations Polish               | Released    | Phase 17 org benchmark window defaults, ingestion audit case/account scope UI (`v18.0.0`)                                                        |
| **19.0**  | Reinvestigation Benchmark Depth                 | Released    | Phase 18 per-bureau benchmark window defaults, outcome benchmarks per-bureau breakdown (`v19.0.0`)                                               |
| **20.0**  | Reinvestigation Benchmark Parity                | Released    | Phase 19 benchmarks `group_by=recipient`, aggregate rates CSV export (no PII) (`v20.0.0`)                                                        |
| **21.0**  | Reinvestigation Operations Filters              | Released    | Phase 20 per-recipient benchmark window defaults, ingestion audit bureau/status list filters (`v21.0.0`)                                         |
| **22.0**  | Document Pipeline Hardening                     | Released    | Phase 21 widen metadata payment_status, operator re-parse credit report (`v22.0.0`)                                                              |
| **23.0**  | Document Pipeline Recovery Depth                | Planned     | Phase 22 async metadata re-extract enqueue, case-level bulk credit-report re-parse                                                               |

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

### Version 5.0+ — Product Hardening (pilot ready)

Scope and checklist: [`docs/governance/version-5.0-plus-scope.md`](../governance/version-5.0-plus-scope.md) · [`docs/development/version-5.0-plus-completion-checklist.md`](../development/version-5.0-plus-completion-checklist.md)

| Epic | Theme                   | 5.0+ outcome | Notes                                             |
| ---- | ----------------------- | ------------ | ------------------------------------------------- |
| 1    | Developer experience    | Partial      | `predev` api-client build on `pnpm dev`           |
| 2    | Client management UI    | Partial      | Staff clients CRUD, contacts, portal provision    |
| 3    | Case–client linking UI  | Partial      | `client_id` picker on case forms                  |
| 4    | Portal product UI       | Partial      | Document upload + messaging on linked cases       |
| 5    | Compliance UI           | Partial      | Consent + retention policy staff UI               |
| 6    | Enterprise reporting UI | Partial      | Bureau performance + team productivity dashboards |
| 7    | Org admin UI            | Partial      | API key lifecycle management                      |
| 8    | LLM assistance UI       | Partial      | Case summary trigger on case detail               |

**Pilot ready** — all 5.0+ checklist slices complete; deferrals documented in scope doc.

### Version 5.1 — Production Hardening (released)

Scope and checklist: [`docs/governance/version-5.1-scope.md`](../governance/version-5.1-scope.md) · [`docs/development/version-5.1-completion-checklist.md`](../development/version-5.1-completion-checklist.md)

| Epic | Theme                     | 5.1 outcome | Notes                                             |
| ---- | ------------------------- | ----------- | ------------------------------------------------- |
| 1    | API integrations          | Partial ✅  | API key middleware on `GET /reporting/operations` |
| 2    | Identity enrollment       | Partial ✅  | TOTP + OIDC staff enrollment                      |
| 3    | Billing                   | Partial ✅  | Stripe customer + subscription scaffold           |
| 4    | Communications production | Deferred    | Production SMS → 5.2+                             |
| 5    | Compliance enforcement    | Partial ✅  | Retention enforcement jobs + audit                |
| 6    | LLM expansion             | Deferred    | Document summary UI → 5.2+                        |
| 7    | Portal real-time          | Partial ✅  | Push notification scaffold for portal messaging   |
| 8    | Reporting depth           | Partial ✅  | Materialized bureau/team reporting views          |

**Tag:** `v5.1.0` — Production Hardening.

Release notes: [`docs/release-notes/v5.1.0.md`](../release-notes/v5.1.0.md)

### Version 5.2 — Deferred Production Surfaces (shipped)

Scope and checklist: [`docs/governance/version-5.2-scope.md`](../governance/version-5.2-scope.md) · [`docs/development/version-5.2-completion-checklist.md`](../development/version-5.2-completion-checklist.md)

| Epic | Theme                     | 5.2 outcome | Notes                                   |
| ---- | ------------------------- | ----------- | --------------------------------------- |
| 1    | Communications production | Partial ✅  | Twilio SMS delivery (5.1 deferral)      |
| 2    | LLM expansion             | Partial ✅  | Document summary endpoint + staff UI    |
| 3    | Portal push production    | Partial ✅  | Real Web Push HTTP for portal messaging |
| 4    | Revenue analytics         | Partial ✅  | Billing-derived org revenue read model  |
| 5    | API integrations depth    | Partial ✅  | API key rate-limit scaffold             |

**Tag:** `v5.2.0` — Deferred Production Surfaces.

Release notes: [`docs/release-notes/v5.2.0.md`](../release-notes/v5.2.0.md)

### Version 5.3 — Enterprise Depth (shipped)

Scope and checklist: [`docs/governance/version-5.3-scope.md`](../governance/version-5.3-scope.md) · [`docs/development/version-5.3-completion-checklist.md`](../development/version-5.3-completion-checklist.md)

| Epic | Theme                  | 5.3 outcome | Notes                                     |
| ---- | ---------------------- | ----------- | ----------------------------------------- |
| 1    | Billing usage metering | Partial ✅  | Usage event scaffold + org read model     |
| 2    | Identity provisioning  | Partial ✅  | SCIM 2.0 provision scaffold               |
| 3    | Predictive analytics   | Partial ✅  | Historical outcome aggregates + reporting |
| 4    | API integrations depth | Partial ✅  | Key rotation + internal developer portal  |
| 5    | LLM operations depth   | Partial ✅  | Batch document summarization worker job   |

**Tag:** `v5.3.0` — Enterprise Depth.

Release notes: [`docs/release-notes/v5.3.0.md`](../release-notes/v5.3.0.md)

### Version 5.4 — Production Operations (shipped)

Scope and checklist: [`docs/governance/version-5.4-scope.md`](../governance/version-5.4-scope.md) · [`docs/development/version-5.4-completion-checklist.md`](../development/version-5.4-completion-checklist.md)

| Epic | Theme                    | 5.4 outcome | Notes                                        |
| ---- | ------------------------ | ----------- | -------------------------------------------- |
| 1    | Billing invoicing        | Partial ✅  | Invoice/dunning scaffold + staff reads       |
| 2    | Identity federation      | Partial ✅  | Multi-IdP federation config scaffold         |
| 3    | Communications marketing | Partial ✅  | Marketing SMS campaign enqueue scaffold      |
| 4    | AI agent observability   | Partial ✅  | Agent run audit + status (no autonomous run) |

**Tag:** `v5.4.0` — Production Operations.

Release notes: [`docs/release-notes/v5.4.0.md`](../release-notes/v5.4.0.md)

### Version 5.5 — Production Automation (shipped)

Scope and checklist: [`docs/governance/version-5.5-scope.md`](../governance/version-5.5-scope.md) · [`docs/development/version-5.5-completion-checklist.md`](../development/version-5.5-completion-checklist.md)

| Epic | Theme                      | 5.5 outcome | Notes                                          |
| ---- | -------------------------- | ----------- | ---------------------------------------------- |
| 1    | Billing invoice collection | Partial ✅  | Invoice PDF + payment collection scaffold      |
| 2    | SAML federation metadata   | Partial ✅  | Metadata upload + validation scaffold          |
| 3    | Marketing SMS delivery     | Partial ✅  | Worker job for campaign run delivery           |
| 4    | Agent execution scaffold   | Partial ✅  | Human-gated agent steps (no autonomous filing) |

**Tag:** `v5.5.0` — Production Automation.

Release notes: [`docs/release-notes/v5.5.0.md`](../release-notes/v5.5.0.md)

### Version 5.6 — Compliance-Reviewed Production Depth (released)

Scope and checklist: [`docs/governance/version-5.6-scope.md`](../governance/version-5.6-scope.md) · [`docs/development/version-5.6-completion-checklist.md`](../development/version-5.6-completion-checklist.md)

| Epic | Theme                         | 5.6 outcome | Notes                                              |
| ---- | ----------------------------- | ----------- | -------------------------------------------------- |
| 1    | HRIS bidirectional sync       | Partial ✅  | Sync run audit + status scaffold                   |
| 2    | SMS deliverability dashboards | Partial ✅  | Delivery metrics read model + status endpoint      |
| 3    | LLM dispute draft augment     | Partial ✅  | ADR-012-gated augment scaffold (no auto-send)      |
| 4    | Dispute filing prep           | Partial ✅  | Compliance-gated prep audit (no bureau submission) |

**Tag:** `v5.6.0` — Compliance-Reviewed Production Depth.

Release notes: [`docs/release-notes/v5.6.0.md`](../release-notes/v5.6.0.md)

### Version 5.7 — Compliance-Gated Autonomous Workflows (released)

Scope and checklist: [`docs/governance/version-5.7-scope.md`](../governance/version-5.7-scope.md) · [`docs/development/version-5.7-completion-checklist.md`](../development/version-5.7-completion-checklist.md)

| Epic | Theme                       | 5.7 outcome | Notes                                                     |
| ---- | --------------------------- | ----------- | --------------------------------------------------------- |
| 1    | Dispute bureau submission   | Partial ✅  | Admin-gated submission run audit (no unsupervised filing) |
| 2    | Agent external tool-calling | Partial ✅  | Human-gated tool invocation audit scaffold                |
| 3    | SAML certificate rotation   | Partial ✅  | Cert rotation run audit + status scaffold                 |
| 4    | Stripe invoice PDF          | Partial ✅  | Invoice PDF generation run audit scaffold                 |

**Tag:** `v5.7.0` — Compliance-Gated Autonomous Workflows.

Release notes: [`docs/release-notes/v5.7.0.md`](../release-notes/v5.7.0.md)

### Version 5.8 — Compliance-Gated Production Integrations (released)

Scope and checklist: [`docs/governance/version-5.8-scope.md`](../governance/version-5.8-scope.md) · [`docs/development/version-5.8-completion-checklist.md`](../development/version-5.8-completion-checklist.md)

| Epic | Theme                       | 5.8 outcome | Notes                                                |
| ---- | --------------------------- | ----------- | ---------------------------------------------------- |
| 1    | Agent supervised loops      | Partial ✅  | Multi-step loop audit with human gates between steps |
| 2    | Bureau live API integration | Partial ✅  | Operator-gated bureau API invocation audit scaffold  |
| 3    | Stripe tax calculation      | Partial ✅  | Tax calculation run audit scaffold                   |
| 4    | HRIS lifecycle sync         | Partial ✅  | Full employee lifecycle sync run audit scaffold      |

**Tag:** `v5.8.0` — Compliance-Gated Production Integrations.

Release notes: [`docs/release-notes/v5.8.0.md`](../release-notes/v5.8.0.md)

### Version 5.9 — Compliance-Gated Autonomous Production (released)

Scope and checklist: [`docs/governance/version-5.9-scope.md`](../governance/version-5.9-scope.md) · [`docs/development/version-5.9-completion-checklist.md`](../development/version-5.9-completion-checklist.md)

| Epic | Theme                    | 5.9 outcome | Notes                                                    |
| ---- | ------------------------ | ----------- | -------------------------------------------------------- |
| 1    | Agent unsupervised loops | Partial ✅  | Multi-step loop audit without per-step human gates       |
| 2    | Autonomous bureau filing | Partial ✅  | Operator-gated autonomous filing run audit scaffold      |
| 3    | Live Stripe Tax API      | Partial ✅  | Admin-gated live Stripe Tax calculation invocation audit |
| 4    | SAML automated rotation  | Partial ✅  | Federation cert automated rotation run audit scaffold    |

**Tag:** `v5.9.0` — Compliance-Gated Autonomous Production.

Release notes: [`docs/release-notes/v5.9.0.md`](../release-notes/v5.9.0.md)

### Version 5.10 — Compliance-Gated Production Automation (released)

Scope and checklist: [`docs/governance/version-5.10-scope.md`](../governance/version-5.10-scope.md) · [`docs/development/version-5.10-completion-checklist.md`](../development/version-5.10-completion-checklist.md)

| Epic | Theme                        | 5.10 outcome | Notes                                                 |
| ---- | ---------------------------- | ------------ | ----------------------------------------------------- |
| 1    | Agent arbitrary execution    | Partial ✅   | Admin-gated arbitrary execution run audit scaffold    |
| 2    | Bureau re-filing audit       | Partial ✅   | Operator-gated re-filing run audit scaffold           |
| 3    | Stripe charge retry          | Partial ✅   | Admin-gated charge retry run audit scaffold           |
| 4    | SAML passwordless enrollment | Partial ✅   | Federation passwordless enrollment run audit scaffold |

**Tag:** `v5.10.0` — Compliance-Gated Production Automation.

Release notes: [`docs/release-notes/v5.10.0.md`](../release-notes/v5.10.0.md)

### Version 5.11 — Compliance-Gated Production Execution (released)

Scope and checklist: [`docs/governance/version-5.11-scope.md`](../governance/version-5.11-scope.md) · [`docs/development/version-5.11-completion-checklist.md`](../development/version-5.11-completion-checklist.md)

| Epic | Theme                         | 5.11 outcome | Notes                                                    |
| ---- | ----------------------------- | ------------ | -------------------------------------------------------- |
| 1    | Unsupervised bureau re-filing | Partial ✅   | Operator-gated unsupervised re-filing run audit scaffold |
| 2    | Live charge retry execution   | Partial ✅   | Admin-gated live charge retry execution audit scaffold   |
| 3    | HRIS passwordless UI          | Partial ✅   | HRIS-linked passwordless enrollment UI audit scaffold    |
| 4    | Multi-IdP bulk provisioning   | Partial ✅   | Federation bulk IdP provisioning run audit scaffold      |

**Tag:** `v5.11.0` — Compliance-Gated Production Execution.

Release notes: [`docs/release-notes/v5.11.0.md`](../release-notes/v5.11.0.md)

### Version 5.12 — Compliance-Gated Expansion Surfaces (shipped)

Scope and checklist: [`docs/governance/version-5.12-scope.md`](../governance/version-5.12-scope.md) · [`docs/development/version-5.12-completion-checklist.md`](../development/version-5.12-completion-checklist.md)

| Epic | Theme                         | 5.12 outcome | Notes                                                    |
| ---- | ----------------------------- | ------------ | -------------------------------------------------------- |
| 1    | Bureau live API invocation    | Partial ✅   | Operator-gated bureau API invocation run audit scaffold  |
| 2    | Public OAuth developer portal | Partial ✅   | Org-scoped OAuth developer portal registration scaffold  |
| 3    | Cross-org benchmark analytics | Partial ✅   | Governance-gated cross-org benchmark read model scaffold |
| 4    | Mobile passkey readiness      | Partial ✅   | Web-first passkey readiness and audit scaffold           |

**Tag:** `v5.12.0`

Release notes: [`docs/release-notes/v5.12.0.md`](../release-notes/v5.12.0.md)

### Version 5.13 — Native Mobile Depth (shipped)

Scope and checklist: [`docs/governance/version-5.13-scope.md`](../governance/version-5.13-scope.md) · [`docs/development/version-5.13-completion-checklist.md`](../development/version-5.13-completion-checklist.md)

| Epic | Theme                                 | 5.13 outcome | Notes                                                          |
| ---- | ------------------------------------- | ------------ | -------------------------------------------------------------- |
| 1    | Native mobile passkey client          | Partial ✅   | Operator-gated native passkey client enrollment audit scaffold |
| 2    | OAuth marketplace publishing          | Partial ✅   | Admin-gated marketplace listing audit from approved OAuth apps |
| 3    | Fully autonomous bureau API filing    | Partial ✅   | Admin-gated fully autonomous API filing audit scaffold         |
| 4    | Unredacted cross-org benchmark export | Partial ✅   | Admin-gated export audit (no live blob / raw tenant PII)       |

**Tag:** `v5.13.0`

Release notes: [`docs/release-notes/v5.13.0.md`](../release-notes/v5.13.0.md)

### Version 5.14 — Production Distribution Depth (Released)

**Tag:** `v5.14.0`

Release notes: [`docs/release-notes/v5.14.0.md`](../release-notes/v5.14.0.md)

Scope and checklist: [`docs/governance/version-5.14-scope.md`](../governance/version-5.14-scope.md) · [`docs/development/version-5.14-completion-checklist.md`](../development/version-5.14-completion-checklist.md)

| Epic | Theme                                 | 5.14 outcome | Notes                                                             |
| ---- | ------------------------------------- | ------------ | ----------------------------------------------------------------- |
| 1    | Live unredacted benchmark blob export | Partial ✅   | Secure export pipeline from approved unredacted export audit runs |
| 2    | Unsupervised autonomous filing loops  | Partial ✅   | Operator-gated unsupervised filing loop audit scaffold            |
| 3    | Public OAuth marketplace listings     | Partial ✅   | Public listing publish from approved marketplace publishing runs  |
| 4    | Native mobile app store distribution  | Partial ✅   | App store distribution readiness from native passkey client runs  |

### Version 5.15 — Identity Theft Detection & Recovery (Released)

**Tag:** `v5.15.0`

Release notes: [`docs/release-notes/v5.15.0.md`](../release-notes/v5.15.0.md)

Scope and checklist: [`docs/governance/version-5.15-scope.md`](../governance/version-5.15-scope.md) · [`docs/development/version-5.15-completion-checklist.md`](../development/version-5.15-completion-checklist.md)

| Epic | Theme                                      | 5.15 outcome | Notes                                                 |
| ---- | ------------------------------------------ | ------------ | ----------------------------------------------------- |
| 1    | Identity Theft Detection & Recovery Engine | ✅           | Phase 8 Case Center, attestation gates, dispute pause |
| 2    | Portal consumer confirmation / attestation | ✅           | Portal-scoped confirm + attestation                   |
| 3    | §605B packet export / bureau block letters | Partial ✅   | Staff-mediated ZIP letters; no live bureau submission |
| 4    | Capability matrix / governance sign-off    | ✅           | Scope, checklist, matrix, release notes               |

### Version 5.16 — Identity-Theft Recovery Depth (Released)

**Tag:** `v5.16.0`

Release notes: [`docs/release-notes/v5.16.0.md`](../release-notes/v5.16.0.md)

Scope and checklist: [`docs/governance/version-5.16-scope.md`](../governance/version-5.16-scope.md) · [`docs/development/version-5.16-completion-checklist.md`](../development/version-5.16-completion-checklist.md)

Compliance Intelligence Phase 9 deepens the shipped Phase 8 engine. Live unsupervised bureau §605B submission and unrestricted cross-tenant PII export remain deferred to 5.17+ pending legal/compliance sign-off.

| Epic | Theme                                          | 5.16 outcome | Notes                                                          |
| ---- | ---------------------------------------------- | ------------ | -------------------------------------------------------------- |
| 1    | §605B evidence exhibit bundling                | ✅           | Staff-selected evidence documents bundled into the §605B ZIP   |
| 2    | Mixed-file / personal-info variation detection | ✅           | Advisory name/SSN/address/DOB variation signals (never labels) |
| 3    | §605B submission-readiness audit               | ✅           | Operator-gated readiness run audit; no live bureau submission  |
| 4    | Lock-aware dispute preparation                 | ✅           | `prepare` + strategy stages respect confirmed theft locks      |

### Version 5.17 — Dispute Response & Reinvestigation Tracking (released — `v5.17.0`)

Scope and checklist: [`docs/governance/version-5.17-scope.md`](../governance/version-5.17-scope.md) · [`docs/development/version-5.17-completion-checklist.md`](../development/version-5.17-completion-checklist.md) · Release notes: [`docs/release-notes/v5.17.0.md`](../release-notes/v5.17.0.md)

Compliance Intelligence Phase 10 closes the dispute loop: staff-entered bureau/furnisher response records, the FCRA §611 reinvestigation clock, and advisory re-dispute / escalation readiness. Live bureau response ingestion, automated re-dispute filing, and unsupervised escalation remain deferred to 5.18+ pending legal/compliance sign-off.

| Epic | Theme                                          | 5.17 target | Notes                                                                |
| ---- | ---------------------------------------------- | ----------- | -------------------------------------------------------------------- |
| 1    | Dispute response intake + persistence          | Released    | Auditable per-letter response records (staff-entered)                |
| 2    | §611 reinvestigation clock & no-response       | Released    | 30-day deadline from dispute mail date; overdue / awaiting detection |
| 3    | Reinvestigation outcome & re-dispute readiness | Released    | Advisory re-dispute / CFPB / attorney escalation signals             |
| 4    | Case reinvestigation summary read model + UI   | Released    | Per-case reinvestigation dashboard surface                           |

### Version 5.18 — Reinvestigation Depth & Litigation Readiness (released — `v5.18.0`)

Scope and checklist: [`docs/governance/version-5.18-scope.md`](../governance/version-5.18-scope.md) · [`docs/development/version-5.18-completion-checklist.md`](../development/version-5.18-completion-checklist.md) · Release notes: [`docs/release-notes/v5.18.0.md`](../release-notes/v5.18.0.md)

Compliance Intelligence Phase 11 deepens the 5.17 reinvestigation lifecycle: per-letter multi-round §611 clocks (keyed off `sent_at`), the extended 45-day reinvestigation window, per-org outcome trend analytics, and an operator-gated litigation-readiness evidence packet for attorney handoff. Live bureau response ingestion, automated re-dispute filing, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (5.19+ or never) pending legal/compliance sign-off.

| Epic | Theme                                        | 5.18 target | Notes                                                         |
| ---- | -------------------------------------------- | ----------- | ------------------------------------------------------------- |
| 1    | Per-letter multi-round reinvestigation clock | Released    | Each sent round on its own `sent_at`-keyed §611 deadline      |
| 2    | Extended 45-day reinvestigation window       | Released    | §611 45-day extension when documents added mid-window         |
| 3    | Reinvestigation outcome analytics read model | Released    | Per-org deletion/verify/correction rates + time-to-resolution |
| 4    | Litigation-readiness evidence packet         | Released    | Operator-gated §611/§623 evidence bundle for attorney handoff |

### Version 5.19 — Reinvestigation Analytics & Evidence Depth (released — `v5.19.0`)

Scope and checklist: [`docs/governance/version-5.19-scope.md`](../governance/version-5.19-scope.md) · [`docs/development/version-5.19-completion-checklist.md`](../development/version-5.19-completion-checklist.md) · Release notes: [`docs/release-notes/v5.19.0.md`](../release-notes/v5.19.0.md)

Compliance Intelligence Phase 12 deepens the 5.18 analytics and evidence surfaces: date-range + per-bureau slicing on reinvestigation outcome analytics, per-recipient (bureau vs furnisher) §611 clock/round splits, cross-bureau discrepancy evidence in the litigation-readiness assessment, and an operator-gated litigation evidence export for attorney handoff. Live bureau response ingestion, automated re-dispute filing, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (5.20+ or never) pending legal/compliance sign-off.

| Epic | Theme                                      | 5.19 target | Notes                                                          |
| ---- | ------------------------------------------ | ----------- | -------------------------------------------------------------- |
| 1    | Reinvestigation analytics slicing          | Released    | Date-range + per-bureau filters on the outcome analytics model |
| 2    | Per-recipient reinvestigation clock splits | Released    | §611 clock start / round counts split by recipient             |
| 3    | Litigation packet cross-bureau evidence    | Released    | Cross-bureau discrepancy signals as willful-noncompliance ind. |
| 4    | Operator-gated litigation evidence export  | Released    | Downloadable evidence document (text) for attorney handoff     |

### Version 5.20 — Reinvestigation Analytics & Evidence Refinement (released — `v5.20.0`)

Scope and checklist: [`docs/governance/version-5.20-scope.md`](../governance/version-5.20-scope.md) · [`docs/development/version-5.20-completion-checklist.md`](../development/version-5.20-completion-checklist.md) · Release notes: [`docs/release-notes/v5.20.0.md`](../release-notes/v5.20.0.md)

Compliance Intelligence Phase 13 refines the 5.19 analytics and evidence surfaces by closing their documented limitations: a single-call per-bureau breakdown on reinvestigation outcome analytics, the §611(a)(1)(B) extended-window flag computed per recipient sub-clock, a PDF format on the operator-gated litigation evidence export, and a balance tolerance band plus extra compared fields in cross-bureau discrepancy detection. Live bureau response ingestion, automated re-dispute filing, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (5.21+ or never) pending legal/compliance sign-off.

| Epic | Theme                                  | 5.20 target | Notes                                                          |
| ---- | -------------------------------------- | ----------- | -------------------------------------------------------------- |
| 1    | Per-bureau analytics breakdown         | Released    | Single-call per-bureau roll-up on the outcome analytics model  |
| 2    | Per-recipient extended-window accuracy | Released    | §611 45-day flag computed per recipient sub-clock              |
| 3    | PDF litigation evidence export         | Released    | `pdf` format on the operator-gated litigation evidence export  |
| 4    | Cross-bureau discrepancy depth         | Released    | Balance tolerance band + extra fields in cross-bureau evidence |

### Version 5.21 — Reinvestigation Analytics & Evidence Polish (released — `v5.21.0`)

Scope and checklist: [`docs/governance/version-5.21-scope.md`](../governance/version-5.21-scope.md) · [`docs/development/version-5.21-completion-checklist.md`](../development/version-5.21-completion-checklist.md) · Release notes: [`docs/release-notes/v5.21.0.md`](../release-notes/v5.21.0.md)

Compliance Intelligence Phase 14 polishes the 5.20 analytics and evidence surfaces by closing their documented limitations: a single-call per-recipient (bureau vs furnisher) breakdown on reinvestigation outcome analytics, high-balance and credit-limit comparison in cross-bureau discrepancy detection, and a structured multi-section layout for the litigation evidence PDF. Live bureau response ingestion, automated re-dispute filing, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (5.22+ or never) pending legal/compliance sign-off.

| Epic | Theme                                    | 5.21 target | Notes                                                                |
| ---- | ---------------------------------------- | ----------- | -------------------------------------------------------------------- |
| 1    | Per-recipient analytics breakdown        | Released    | Single-call `group_by=recipient` roll-up on the outcome analytics    |
| 2    | Cross-bureau high_balance / credit_limit | Released    | Compare high balance and credit limit across sibling bureaus         |
| 3    | Structured PDF litigation export layout  | Released    | Multi-section reportlab layout for the operator-gated litigation PDF |

### Version 16.0 — Reinvestigation Operations & Configuration (released — `v16.0.0`)

Scope and checklist: [`docs/governance/version-16.0-scope.md`](../governance/version-16.0-scope.md) · [`docs/development/version-16.0-completion-checklist.md`](../development/version-16.0-completion-checklist.md) · Release notes: [`docs/release-notes/v16.0.0.md`](../release-notes/v16.0.0.md)

Compliance Intelligence Phase 15 closes the configuration and operations gaps deferred from 5.21: per-org cross-bureau monetary tolerance, a bureau response ingestion audit scaffold (no live polling), and org-internal reinvestigation outcome benchmarks. Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (17.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                                           | 16.0 target | Notes                                                             |
| ---- | ----------------------------------------------- | ----------- | ----------------------------------------------------------------- |
| 1    | Org-configurable cross-bureau balance tolerance | Released    | Per-org monetary tolerance for cross-bureau discrepancy detection |
| 2    | Bureau response ingestion audit scaffold        | Released    | Compliance audit runs for planned ingestion; no live bureau API   |
| 3    | Org-internal reinvestigation benchmarks         | Released    | Org-scoped historical baselines on outcome analytics              |

### Version 17.0 — Reinvestigation Operations Surfaces (released — `v17.0.0`)

Scope and checklist: [`docs/governance/version-17.0-scope.md`](../governance/version-17.0-scope.md) · [`docs/development/version-17.0-completion-checklist.md`](../development/version-17.0-completion-checklist.md) · Release notes: [`docs/release-notes/v17.0.0.md`](../release-notes/v17.0.0.md)

Compliance Intelligence Phase 16 surfaces the Phase 15 operator APIs in staff UI: Reporting Center org-internal benchmarks and Compliance Center bureau response ingestion audit (start stays deferred). Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (18.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                                       | 17.0 target | Notes                                                          |
| ---- | ------------------------------------------- | ----------- | -------------------------------------------------------------- |
| 1    | Reporting Center org-internal benchmarks UI | Released    | Staff UI for trailing baseline/recent rates + advisory deltas  |
| 2    | Compliance Center ingestion audit UI        | Released    | Staff UI for deferred ingestion audit runs; no live bureau API |

### Version 18.0 — Reinvestigation Operations Polish (released — `v18.0.0`)

Scope and checklist: [`docs/governance/version-18.0-scope.md`](../governance/version-18.0-scope.md) · [`docs/development/version-18.0-completion-checklist.md`](../development/version-18.0-completion-checklist.md) · Release notes: [`docs/release-notes/v18.0.0.md`](../release-notes/v18.0.0.md)

Compliance Intelligence Phase 17 polishes Phase 15/16 operator surfaces without crossing the live-bureau frontier: org-configurable default windows for org-internal outcome benchmarks, and case/account scoping on the Compliance Center ingestion audit UI. Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (19.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                                      | 18.0 target | Notes                                                              |
| ---- | ------------------------------------------ | ----------- | ------------------------------------------------------------------ |
| 1    | Org-configurable benchmark window defaults | Released    | Per-org baseline/recent days on dispute settings + Reporting UI    |
| 2    | Ingestion audit case/account scope UI      | Released    | Optional case_id / account_id on Compliance Center start + filters |

### Version 19.0 — Reinvestigation Benchmark Depth (released — `v19.0.0`)

Scope and checklist: [`docs/governance/version-19.0-scope.md`](../governance/version-19.0-scope.md) · [`docs/development/version-19.0-completion-checklist.md`](../development/version-19.0-completion-checklist.md) · Release notes: [`docs/release-notes/v19.0.0.md`](../release-notes/v19.0.0.md)

Compliance Intelligence Phase 18 deepens org-internal outcome benchmarks without crossing the live-bureau frontier: optional per-bureau window defaults on dispute settings, and a single-call per-bureau breakdown on the Outcome benchmarks API/UI. Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (20.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                                   | 19.0 target | Notes                                                                      |
| ---- | --------------------------------------- | ----------- | -------------------------------------------------------------------------- |
| 1    | Per-bureau benchmark window defaults    | Released    | Optional Equifax/Experian/TransUnion overrides; fall back to org-wide pair |
| 2    | Outcome benchmarks per-bureau breakdown | Released    | `group_by=bureau` parity with outcome analytics + Reporting Center table   |

### Version 20.0 — Reinvestigation Benchmark Parity (released — `v20.0.0`)

Scope and checklist: [`docs/governance/version-20.0-scope.md`](../governance/version-20.0-scope.md) · [`docs/development/version-20.0-completion-checklist.md`](../development/version-20.0-completion-checklist.md) · Release notes: [`docs/release-notes/v20.0.0.md`](../release-notes/v20.0.0.md)

Compliance Intelligence Phase 19 closes parity gaps on org-internal outcome benchmarks without crossing the live-bureau frontier: single-call `group_by=recipient` on the Outcome benchmarks API/UI (matching outcome analytics), and an operator-gated aggregate rates CSV export with no PII. Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (21.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                                          | 20.0 target | Notes                                                                      |
| ---- | ---------------------------------------------- | ----------- | -------------------------------------------------------------------------- |
| 1    | Outcome benchmarks per-recipient breakdown     | Released    | `group_by=recipient` parity with outcome analytics + Reporting Center UI   |
| 2    | Org-internal benchmarks aggregate rates export | Released    | Operator-gated CSV of windows + rates (counts only; no client/account IDs) |

### Version 21.0 — Reinvestigation Operations Filters (released — `v21.0.0`)

Scope and checklist: [`docs/governance/version-21.0-scope.md`](../governance/version-21.0-scope.md) · [`docs/development/version-21.0-completion-checklist.md`](../development/version-21.0-completion-checklist.md) · Release notes: [`docs/release-notes/v21.0.0.md`](../release-notes/v21.0.0.md)

Compliance Intelligence Phase 20 polishes remaining non-blocked configuration and audit-filter gaps without crossing the live-bureau frontier: optional per-recipient (credit bureau vs furnisher) benchmark window defaults on dispute settings, and Compliance Center ingestion audit list filters for `bureau_target` and `status`. Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (22.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                                      | 21.0 target | Notes                                                                    |
| ---- | ------------------------------------------ | ----------- | ------------------------------------------------------------------------ |
| 1    | Per-recipient benchmark window defaults    | Released    | Optional credit_bureau / furnisher overrides; fall back to org-wide pair |
| 2    | Ingestion audit bureau/status list filters | Released    | Optional bureau_target + status on Compliance Center ingestion run list  |

### Version 22.0 — Document Pipeline Hardening (released — `v22.0.0`)

Scope and checklist: [`docs/governance/version-22.0-scope.md`](../governance/version-22.0-scope.md) · [`docs/development/version-22.0-completion-checklist.md`](../development/version-22.0-completion-checklist.md) · Release notes: [`docs/release-notes/v22.0.0.md`](../release-notes/v22.0.0.md)

Compliance Intelligence Phase 21 hardens the owned document pipeline without crossing the live-bureau frontier: widen `document_metadata.payment_status` for bureau status narratives, and add an operator-gated re-parse action for classified credit reports with OCR. Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (23.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                           | 22.0 target | Notes                                                                  |
| ---- | ------------------------------- | ----------- | ---------------------------------------------------------------------- |
| 1    | Widen metadata payment_status   | Released    | varchar(255) so charged-off / past-due narratives persist              |
| 2    | Operator re-parse credit report | Released    | Staff POST enqueue document_credit_report_parse for eligible documents |

### Version 23.0 — Document Pipeline Recovery Depth (planned)

Scope and checklist: [`docs/governance/version-23.0-scope.md`](../governance/version-23.0-scope.md) · [`docs/development/version-23.0-completion-checklist.md`](../development/version-23.0-completion-checklist.md)

Compliance Intelligence Phase 22 deepens owned document-pipeline recovery without crossing the live-bureau frontier: operator-gated async metadata re-extract enqueue, and case-level bulk credit-report re-parse for eligible documents. Live bureau response ingestion execution, automated re-dispute filing execution, unsupervised escalation, automated litigation filing, and cross-tenant benchmarks remain deferred (24.0+ or never) pending legal/compliance sign-off.

| Epic | Theme                                  | 23.0 target | Notes                                                         |
| ---- | -------------------------------------- | ----------- | ------------------------------------------------------------- |
| 1    | Operator async metadata re-extract     | Shipped     | Enqueue document_metadata_extract; keep sync extract endpoint |
| 2    | Case-level bulk credit-report re-parse | Shipped     | Enqueue parse for all OCR'd credit_report docs on a case      |

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
- [Release notes — v5.1.0](../release-notes/v5.1.0.md)
- [Release notes — v4.3.0 GA](../release-notes/v4.3.0-ga.md)
- [Architecture](../architecture/README.md) — technical constitution
- [ADR index](../adr/README.md) — architecture decision records
- [Release notes](../release-notes/) — shipped change logs
- [Developer guide](../developer-guide.md) — day-to-day development
