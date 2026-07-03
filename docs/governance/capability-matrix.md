# Platform Capability Matrix

**Executive view** of Verdin platform capabilities — what exists, what version introduced it, readiness by layer, and dependencies.

**Last updated:** 2026-07-02  
**Maintainers:** Update this document in every epic PR that ships or materially advances a capability.

**Version 4.5 sign-off:** [version-4.5-scope.md](version-4.5-scope.md) · Release notes: [v4.5.0.md](../release-notes/v4.5.0.md)  
**Version 4.8 sign-off:** [version-4.8-scope.md](version-4.8-scope.md) · Release notes: [v4.8.0.md](../release-notes/v4.8.0.md)  
**Version 5.0 sign-off:** [version-5.0-scope.md](version-5.0-scope.md) · Release notes: [v5.0.0.md](../release-notes/v5.0.0.md)  
**Version 5.0+ sign-off:** [version-5.0-plus-scope.md](version-5.0-plus-scope.md) · Checklist: [version-5.0-plus-completion-checklist.md](../development/version-5.0-plus-completion-checklist.md)

## Status legend

| Symbol  | Meaning                                        |
| ------- | ---------------------------------------------- |
| ✅      | Production-ready / complete for target version |
| 🚧      | In progress, scaffold, or partial              |
| Planned | Scheduled; not started                         |
| —       | Not applicable or not started                  |
| Partial | Feature exists in limited form (see notes)     |

## Layer columns

| Column       | Meaning                                                         |
| ------------ | --------------------------------------------------------------- |
| **Backend**  | SQLAlchemy model + repository + service + router                |
| **Frontend** | Staff web UI (`apps/web`) integrated with `@verdin/api-client`  |
| **API**      | REST endpoints live + documented + client functions implemented |
| **AI**       | AI/ML capability (heuristic, LLM, OCR, etc.)                    |
| **Tests**    | Automated tests covering primary behavior                       |

---

## Version 4.3.1 — Operational Core completion (shipped)

Mission Control dashboard and governance refinements shipped in tag `v4.3.1`. See [`docs/release-notes/v4.3.1.md`](../release-notes/v4.3.1.md).

| Capability                | Version | Status | Backend | Frontend | API | AI  | Tests | Notes                               |
| ------------------------- | ------- | ------ | ------- | -------- | --- | --- | ----- | ----------------------------------- |
| Mission Control Dashboard | 4.3.1   | ✅     | ✅      | ✅       | ✅  | —   | ✅    | Single `GET /dashboard` product API |

---

## Version 4.3.0 — Operational Core (shipped)

| Capability                      | Version | Status  | Backend | Frontend | API | AI      | Tests | Notes                                                 |
| ------------------------------- | ------- | ------- | ------- | -------- | --- | ------- | ----- | ----------------------------------------------------- |
| Platform Foundation             | 4.2     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | Shipped in 4.2 — monorepo, auth, RBAC, CI             |
| **Case Management**             | 4.3     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | CRUD, filters, RBAC, full UI                          |
| **Credit Account Intelligence** | 4.3     | ✅      | ✅      | ✅       | ✅  | Partial | ✅    | Heuristic risk/readiness scoring in `intelligence.py` |
| **Document Foundation**         | 4.3     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | Upload, versioning, MinIO, duplicate detection/review |
| **OCR Pipeline**                | 4.3     | ✅      | ✅      | ✅       | ✅  | ✅      | ✅    | Async worker extraction; pypdf + tesseract            |
| **AI Classification**           | 4.3     | ✅      | ✅      | Partial  | ✅  | Partial | ✅    | Rule-based classifier framework                       |
| **Metadata Extraction**         | 4.3     | ✅      | ✅      | ✅       | ✅  | Partial | ✅    | Rule-based extraction; `packages/document-metadata`   |
| **Entity Resolution**           | 4.3     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | Deterministic matching; `packages/entity-resolution`  |
| Timeline & Audit Engine         | 4.3     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | Event bus + append-only timeline                      |
| Task Management                 | 4.3     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | CRUD, complete/reopen, filters, timeline events, UI   |
| Operational Dashboard           | 4.3.1   | ✅      | ✅      | ✅       | ✅  | —       | ✅    | Mission Control — shipped in v4.3.1                   |
| Client Management               | 4.8     | Partial | ✅      | ✅       | ✅  | —       | ✅    | Staff clients UI shipped in 5.0+ slice 3              |

### Document Intelligence Platform (4.3 epic)

Epic plan: [`docs/epics/document-intelligence-platform.md`](../epics/document-intelligence-platform.md)

| Milestone                         | Version | Status | Backend | Frontend | API | AI      | Tests | Branch                                   |
| --------------------------------- | ------- | ------ | ------- | -------- | --- | ------- | ----- | ---------------------------------------- |
| **M1 — Document Foundation**      | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | `feature/document-foundation`            |
| **M2 — OCR Pipeline**             | 4.3     | ✅     | ✅      | ✅       | ✅  | ✅      | ✅    | `feature/document-ocr`                   |
| M3 — AI Classification            | 4.3     | ✅     | ✅      | Partial  | ✅  | Partial | ✅    | `feature/document-classification`        |
| M4 — Metadata & Entity Resolution | 4.3     | ✅     | ✅      | ✅       | ✅  | Partial | ✅    | `feature/document-entity-resolution`     |
| M5 — Timeline Integration         | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | `feature/document-timeline`              |
| M6 — Mission Control Dashboard    | 4.3.1   | ✅     | ✅      | ✅       | ✅  | Partial | ✅    | `feature/task-management` — tag `v4.3.1` |

### 4.3 completion checklist

- [x] Case Management
- [x] Credit Account Intelligence
- [x] Document Foundation (M1)
- [x] OCR Pipeline (M2)
- [x] AI Classification (M3 — rules engine)
- [x] Metadata & Entity Resolution (M4)
- [x] Timeline & Audit Engine
- [x] Task Management (full module)
- [x] Operational Dashboard (Mission Control) — v4.3.1

> **Release history:** `v4.3.0` is the initial Operational Core GA. `v4.3.1` completes it with Mission Control and governance refinements. **Sprint 4.3.1** validates the release before Version 4.5 automation begins.

### Sprint 4.3.1 — Operational Core Stabilization (shipped)

Engineering milestone — not a semantic version. **Complete** — gate cleared for Version 4.5 automation.

Plan: [`docs/sprint-4.3.1/operational-core-stabilization.md`](../sprint-4.3.1/operational-core-stabilization.md)

| Focus Area              | Status      | Outcome                                                                                                        |
| ----------------------- | ----------- | -------------------------------------------------------------------------------------------------------------- |
| End-to-end validation   | ✅ Complete | `tests/e2e` lifecycle + dispute letter gate; Playwright dispute UI smoke                                       |
| Performance baselines   | ✅ Complete | Metrics captured in [`docs/quality/performance/v4.3.1-baseline.md`](../quality/performance/v4.3.1-baseline.md) |
| Security review         | ✅ Complete | Pass/fail review complete in [`docs/quality/security/v4.3.1-review.md`](../quality/security/v4.3.1-review.md)  |
| Test coverage expansion | ✅ Complete | Worker failure handling, event bus, dashboard aggregation, entity resolution, timeline, and RBAC paths covered |
| Branch protection       | ✅ Complete | `main` requires PR review, strict CI status checks, and the E2E workflow                                       |
| Defect gate             | ✅ Complete | No critical or high-severity defects found in the Sprint 4.3.1 security review                                 |

---

## Version 4.2 — Platform Foundation (shipped)

| Capability                 | Version | Status | Backend | Frontend | API | AI  | Tests | Dependencies | Notes                              |
| -------------------------- | ------- | ------ | ------- | -------- | --- | --- | ----- | ------------ | ---------------------------------- |
| Monorepo & CI/CD           | 4.2     | ✅     | ✅      | ✅       | ✅  | —   | ✅    | —            | pnpm, Turborepo, GitHub Actions    |
| Authentication (JWT)       | 4.2     | ✅     | ✅      | ✅       | ✅  | —   | ✅    | —            | Login, refresh, `/auth/me`         |
| RBAC (5 roles)             | 4.2     | ✅     | ✅      | ✅       | ✅  | —   | ✅    | Auth         | Enforced in services               |
| Organization tenancy       | 4.2     | ✅     | ✅      | —        | ✅  | —   | ✅    | Auth         | `organization_id` scoping          |
| Domain module pattern      | 4.2     | ✅     | —       | —        | —   | —   | —     | —            | router → service → repository      |
| Background worker scaffold | 4.2     | ✅     | —       | —        | —   | —   | —     | Redis        | Job registry; OCR + classify jobs  |
| Feature flags              | 4.2     | ✅     | ✅      | —        | —   | —   | —     | —            | `ENABLE_AI`, `ENABLE_IMPORTS`      |
| Shared packages            | 4.2     | ✅     | —       | ✅       | ✅  | —   | —     | —            | shared, ui, validation, api-client |

---

## Version 4.5 — Automation (shipped — `v4.5.0`)

Scope and deferrals: [version-4.5-scope.md](version-4.5-scope.md)

| Capability                      | Version | Status  | Backend | Frontend | API | AI      | Tests | Dependencies        | Notes                                                           |
| ------------------------------- | ------- | ------- | ------- | -------- | --- | ------- | ----- | ------------------- | --------------------------------------------------------------- |
| Workflow Automation             | 4.5     | Partial | 🚧      | 🚧       | 🚧  | —       | ✅    | Timeline, Tasks     | Auto-tasks only; BPM/cron/notifications deferred to 4.8         |
| Credit Report Import Wizard     | 4.5     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | Documents, OCR      | Wizard, comparison, duplicate detection, in-wizard retry        |
| OCR Pipeline                    | 4.3     | ✅      | ✅      | ✅       | ✅  | ✅      | ✅    | Documents, Worker   | Shipped in 4.3 Operational Core                                 |
| Document Classification         | 4.3     | Partial | ✅      | —        | ✅  | Partial | ✅    | OCR                 | Rules engine; LLM augmentation deferred to 4.8                  |
| Entity Extraction               | 4.5     | Partial | ✅      | ✅       | ✅  | Partial | ✅    | OCR, Accounts       | Parser tradelines + account candidates; LLM NER deferred to 4.8 |
| AI Case Summaries               | 4.8     | —       | —       | —        | —   | —       | —     | Cases, Documents    | **Deferred** from 4.5 — LLM requires provider + PII policy      |
| AI Recommendation Engine        | 4.5     | Partial | ✅      | ✅       | —   | Partial | ✅    | Accounts            | Rules: suggestions + missing evidence; LLM deferred to 4.8      |
| Dispute Generation (foundation) | 4.5     | Partial | ✅      | ✅       | ✅  | Partial | ✅    | Accounts, Documents | Staff-mediated lifecycle + export; auto-filing deferred to 5.0+ |

### Version 4.5 epic sign-off

| Epic                        | v4.5.0 outcome | Exit note                                       |
| --------------------------- | -------------- | ----------------------------------------------- |
| Credit Report Intelligence  | ✅             | Epics 1.1–1.10 shipped (Innovis parser → 4.8)   |
| Workflow Automation         | Partial        | Auto-tasks shipped; engine/reminders → 4.8      |
| Dispute Generation          | Partial        | Foundation lifecycle shipped; mail/auto → later |
| AI Assistance (rules)       | Partial        | Heuristics shipped; all LLM surfaces → 4.8      |
| Client Experience (roadmap) | Deferred 4.8   | Portal, messaging, notifications                |

---

## Version 4.8 — Operations (shipped — `v4.8.0`)

Scope: [version-4.8-scope.md](version-4.8-scope.md) · Release notes: [v4.8.0.md](../release-notes/v4.8.0.md)

| Capability              | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies | Notes                                                              |
| ----------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------ | ------------------------------------------------------------------ |
| In-App Notifications    | 4.8     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Auth         | Staff bell + API; production email in 5.0 slice 3                  |
| Client Portal           | 4.8     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Client Mgmt  | Auth, case progress, portal upload + messaging on linked cases     |
| Client Management       | 4.8     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Auth         | Staff clients UI + contact CRUD; portal provision in 5.0+ slice 3  |
| Workflow Scheduled Jobs | 4.8     | Partial | ✅      | —        | —   | —   | ✅    | Worker       | `overdue_investigation_scan` job; manual POST endpoint retained    |
| Job Orchestration       | 4.8     | Partial | 🚧      | —        | —   | —   | ✅    | Worker, API  | Retry/metrics + cron wired in 5.0 slice 5; PG persistence deferred |
| LLM Policy Gates        | 4.8     | Partial | ✅      | —        | ✅  | —   | ✅    | —            | `packages/llm-gateway` + `ENABLE_LLM`; no provider calls yet       |
| Operations Reporting    | 4.8     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Dashboard    | `GET /reporting/operations`; embedded in Mission Control dashboard |

### Version 4.8 epic sign-off

| Epic                | v4.8.0 outcome | Exit note                                                                    |
| ------------------- | -------------- | ---------------------------------------------------------------------------- |
| Notifications       | Partial        | In-app + staff UI shipped; email/SMS provider sends deferred                 |
| Workflow Operations | Partial        | Overdue scan worker + in-process cron via job-orchestrator; cron UI deferred |
| Client Experience   | Partial        | Clients, portal auth, read-only progress; messaging/upload → 5.0             |
| AI Assistance (LLM) | Partial        | Policy ADR + gates only; summary endpoints post-gate → 5.0                   |
| Reporting           | Partial        | Operations read model + dashboard embed; materialized views → 5.0            |

---

## Version 5.0 — Enterprise Edition (shipped — `v5.0.0`)

Scope: [version-5.0-scope.md](version-5.0-scope.md) · Release notes: [v5.0.0.md](../release-notes/v5.0.0.md)

| Capability           | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies  | Notes                                                       |
| -------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------- | ----------------------------------------------------------- |
| Case–client linking  | 5.0     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Clients       | `cases.client_id` FK; picker on case forms in 5.0+ slice 4  |
| Production email     | 5.0     | Partial | ✅      | —        | ✅  | —   | ✅    | Notifications | SMTP/SendGrid send + audit log; SMS deferred                |
| LLM case summaries   | 5.0     | Partial | ✅      | ✅       | ✅  | —   | ✅    | LLM gates     | `POST /cases/{id}/llm-summary`; document summaries deferred |
| Job orchestrator     | 5.0     | Partial | ✅      | —        | —   | —   | ✅    | Worker        | Runner retry/metrics + overdue scan cron registration       |
| SSO / MFA            | 5.0     | Partial | ✅      | —        | ✅  | —   | ✅    | Auth          | `GET /enterprise/status`; IdP/TOTP wiring deferred          |
| Compliance center    | 5.0     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Timeline      | Consent records + retention policy placeholders             |
| Portal expansion     | 5.0     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Portal        | Document upload + secure messaging on linked cases          |
| Enterprise reporting | 5.0     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Reporting     | Bureau performance + team productivity read models          |
| Org admin / API keys | 5.0     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Enterprise    | Org summary + API key lifecycle behind `ENABLE_ENTERPRISE`  |

### Version 5.0 epic sign-off

| Epic                  | v5.0.0 outcome | Exit note                                                                   |
| --------------------- | -------------- | --------------------------------------------------------------------------- |
| Data & client linking | Partial        | `cases.client_id` FK shipped; bulk import/CRM sync → 5.0+                   |
| Communications        | Partial        | Production email + audit; SMS production → 5.0+                             |
| AI Assistance (LLM)   | Partial        | Case summary post-gate; document summaries + LLM augment → 5.0+             |
| Platform operations   | Partial        | Orchestrator retry/metrics + cron; PG job persistence → 5.0+                |
| Enterprise identity   | Partial        | SSO/MFA readiness scaffold; IdP enrollment + SCIM → 5.0+                    |
| Compliance            | Partial        | Consent + retention placeholders; enforcement + legal workflows → 5.0+      |
| Client portal         | Partial        | Upload + messaging scaffold; real-time delivery + billing → 5.0+            |
| Enterprise admin      | Partial        | API key lifecycle; usage analytics + billing admin → 5.0+                   |
| Reporting & analytics | Partial        | Bureau + team productivity read models; materialized views + revenue → 5.0+ |

---

## Version 5.0+ — Product Hardening (pilot ready)

Scope: [version-5.0-plus-scope.md](version-5.0-plus-scope.md) · Checklist: [version-5.0-plus-completion-checklist.md](../development/version-5.0-plus-completion-checklist.md)

| Capability              | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies | Notes                                                     |
| ----------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------ | --------------------------------------------------------- |
| Web dev DX (`predev`)   | 5.0+    | Partial | —       | ✅       | —   | —   | —     | Monorepo     | `@verdin/api-client` + validation build before `pnpm dev` |
| Staff client management | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | Auth         | Clients list/CRUD, contacts, portal provision             |
| Case–client linking UI  | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | Clients      | `client_id` picker on case create/edit                    |
| Portal product surfaces | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | Portal       | Upload + messaging UI on linked cases                     |
| Staff portal messaging  | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | Messaging    | Case message thread panel on staff case detail            |
| Compliance center UI    | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | Compliance   | Consent + retention policy management at `/compliance`    |
| Enterprise reporting UI | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | Reporting    | Operations, bureau, team tabs at `/reporting`             |
| Org admin UI            | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | Enterprise   | Org summary + API key lifecycle at `/org-admin`           |
| LLM case summary UI     | 5.0+    | Partial | ✅      | ✅       | ✅  | —   | ✅    | LLM gates    | `CaseLlmSummaryPanel` on case detail behind `ENABLE_LLM`  |

### Version 5.0+ epic sign-off

| Epic                    | 5.0+ outcome | Exit note                                                        |
| ----------------------- | ------------ | ---------------------------------------------------------------- |
| Developer experience    | Partial ✅   | `predev` builds api-client; no hot-reload package watch in 5.0+  |
| Client management UI    | Partial ✅   | Staff clients CRUD + contacts + portal provision                 |
| Case–client linking UI  | Partial ✅   | `client_id` picker on case forms                                 |
| Portal product UI       | Partial ✅   | Document upload + messaging; real-time push + billing → 5.1+     |
| Compliance UI           | Partial ✅   | Consent + retention staff UI; enforcement jobs → 5.1+            |
| Enterprise reporting UI | Partial ✅   | Bureau + team dashboards; materialized views + revenue → 5.1+    |
| Org admin UI            | Partial ✅   | API key lifecycle UI; API key auth middleware → 5.1              |
| LLM assistance UI       | Partial ✅   | Case summary trigger UI; document summaries + LLM augment → 5.1+ |

---

## Version 5.1 — Production Hardening (in progress)

Scope: [version-5.1-scope.md](version-5.1-scope.md) · Checklist: [version-5.1-completion-checklist.md](../development/version-5.1-completion-checklist.md)

| Capability              | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies  | Notes                                                           |
| ----------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------- | --------------------------------------------------------------- |
| API key auth middleware | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Org admin     | `GET /reporting/operations` via `X-API-Key` or Bearer key       |
| Identity enrollment     | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Enterprise    | TOTP + OIDC staff enrollment behind `ENABLE_ENTERPRISE`         |
| Stripe billing scaffold | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Org admin     | Customer + subscription + webhook; billing on org summary       |
| Retention enforcement   | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Compliance    | Manual + scheduled jobs; audit log; `audit_logs` skipped        |
| Portal push scaffold    | 5.1     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Client portal | Web Push scaffold; staff message dispatch; `ENABLE_PORTAL_PUSH` |

---

## AI capability tracker

| AI feature                   | Phase | Version | Status  | Location                                                                 |
| ---------------------------- | ----- | ------- | ------- | ------------------------------------------------------------------------ |
| Risk score (heuristic)       | —     | 4.3     | ✅      | `accounts/intelligence.py`                                               |
| Readiness score (heuristic)  | —     | 4.3     | ✅      | `accounts/intelligence.py`                                               |
| Dispute readiness rules      | —     | 4.3     | ✅      | `accounts/intelligence.py`                                               |
| Next action recommendations  | —     | 4.3     | ✅      | Heuristic text; LLM in 4.5                                               |
| OCR                          | 1     | 4.3     | ✅      | `worker/jobs/ocr.py`                                                     |
| Document classification      | 1     | 4.3     | Partial | Rules in `modules/documents/classification/`; LLM augment → 5.0          |
| Metadata / entity extraction | 1     | 4.5     | Partial | Parser bridge + candidates; LLM NER → 5.0                                |
| LLM policy gates             | 2     | 4.8     | Partial | `packages/llm-gateway` + `GET /llm/status`; no provider calls            |
| Case summaries (LLM)         | 2     | 5.0     | Partial | Endpoint + staff UI behind `ENABLE_LLM` + PII scrub                      |
| Document summaries (LLM)     | 2     | 5.0     | —       | Deferred post-gate; requires approved provider integration               |
| LLM dispute draft augment    | 2     | 5.0     | —       | Rules default in 4.5; LLM augment post-gate                              |
| AI workflow orchestration    | 3     | 5.0+    | Planned | Deferred from 5.0 RC — requires compliance + observability prerequisites |
| Predictive outcomes          | 3     | 5.1+    | Planned | Deferred — needs historical data pipeline                                |
| Autonomous dispute prep      | 4     | 5.0+    | Planned | Compliance gates required                                                |

See [AI Architecture](../architecture/ai-architecture.md).

---

## Related documents

- [Governance hub](README.md) — lifecycle and build order
- [V5.0 Enterprise Roadmap](../roadmap/v5.0-enterprise.md)
- [Release notes — M2 OCR](../release-notes/v4.3-m2-ocr-pipeline.md)
- [Architecture constitution](../architecture/README.md)
