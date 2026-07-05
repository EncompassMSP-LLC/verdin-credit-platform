# Platform Capability Matrix

**Executive view** of Verdin platform capabilities — what exists, what version introduced it, readiness by layer, and dependencies.

**Last updated:** 2026-07-05  
**Maintainers:** Update this document in every epic PR that ships or materially advances a capability.

**Version 4.5 sign-off:** [version-4.5-scope.md](version-4.5-scope.md) · Release notes: [v4.5.0.md](../release-notes/v4.5.0.md)  
**Version 4.8 sign-off:** [version-4.8-scope.md](version-4.8-scope.md) · Release notes: [v4.8.0.md](../release-notes/v4.8.0.md)  
**Version 5.0 sign-off:** [version-5.0-scope.md](version-5.0-scope.md) · Release notes: [v5.0.0.md](../release-notes/v5.0.0.md)  
**Version 5.0+ sign-off:** [version-5.0-plus-scope.md](version-5.0-plus-scope.md) · Checklist: [version-5.0-plus-completion-checklist.md](../development/version-5.0-plus-completion-checklist.md)
**Version 5.1 sign-off:** [version-5.1-scope.md](version-5.1-scope.md) · Release notes: [v5.1.0.md](../release-notes/v5.1.0.md)
**Version 5.2 sign-off:** [version-5.2-scope.md](version-5.2-scope.md) · Release notes: [v5.2.0.md](../release-notes/v5.2.0.md)
**Version 5.3 sign-off:** [version-5.3-scope.md](version-5.3-scope.md) · Release notes: [v5.3.0.md](../release-notes/v5.3.0.md)
**Version 5.6 sign-off:** [version-5.6-scope.md](version-5.6-scope.md) · Release notes: [v5.6.0.md](../release-notes/v5.6.0.md)

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

## Version 5.1 — Production Hardening (sign-off)

Scope: [version-5.1-scope.md](version-5.1-scope.md) · Checklist: [version-5.1-completion-checklist.md](../development/version-5.1-completion-checklist.md) · Release notes: [v5.1.0.md](../release-notes/v5.1.0.md)

| Capability              | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies  | Notes                                                                 |
| ----------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------- | --------------------------------------------------------------------- |
| API key auth middleware | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Org admin     | `GET /reporting/operations` via `X-API-Key` or Bearer key             |
| Identity enrollment     | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Enterprise    | TOTP + OIDC staff enrollment behind `ENABLE_ENTERPRISE`               |
| Stripe billing scaffold | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Org admin     | Customer + subscription + webhook; billing on org summary             |
| Retention enforcement   | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Compliance    | Manual + scheduled jobs; audit log; `audit_logs` skipped              |
| Portal push scaffold    | 5.1     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Client portal | Web Push scaffold; staff message dispatch; `ENABLE_PORTAL_PUSH`       |
| Materialized reporting  | 5.1     | Partial | ✅      | —        | ✅  | —   | ✅    | Reporting     | Bureau + team MVs; scheduled refresh; `ENABLE_MATERIALIZED_REPORTING` |

### Version 5.1 epic sign-off

| Epic                      | 5.1 outcome | Exit note                                                               |
| ------------------------- | ----------- | ----------------------------------------------------------------------- |
| API integrations          | Partial ✅  | API key middleware on reporting operations; rate-limit UI → 5.2+        |
| Identity enrollment       | Partial ✅  | TOTP + OIDC staff enrollment; SCIM / multi-IdP → 5.2+                   |
| Billing                   | Partial ✅  | Stripe customer + subscription scaffold; usage metering → 5.2+          |
| Communications production | Deferred    | Production SMS not merged for v5.1.0; Twilio scaffold → 5.2+            |
| Compliance enforcement    | Partial ✅  | Retention enforcement jobs + audit; `audit_logs` purge deferred         |
| LLM expansion             | Deferred    | Document summary UI + endpoint not in v5.1.0; case summary UI from 5.0+ |
| Portal real-time          | Partial ✅  | Push subscription scaffold + staff dispatch; real Web Push HTTP → 5.2+  |
| Reporting depth           | Partial ✅  | Materialized bureau/team views + refresh jobs; revenue metrics → 5.2+   |

---

## Version 5.2 — Deferred production surfaces (sign-off)

Scope: [version-5.2-scope.md](version-5.2-scope.md) · Checklist: [version-5.2-completion-checklist.md](../development/version-5.2-completion-checklist.md) · Release notes: [v5.2.0.md](../release-notes/v5.2.0.md)

| Capability             | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies  | Notes                                                           |
| ---------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------- | --------------------------------------------------------------- |
| Production SMS         | 5.2     | Partial | ✅      | —        | ✅  | —   | ✅    | Notifications | Twilio send + audit log; `deliver_sms` on create                |
| LLM document summaries | 5.2     | Partial | ✅      | ✅       | ✅  | ✅  | ✅    | LLM gates     | `POST /documents/{id}/llm-summary`; `DocumentLlmSummaryPanel`   |
| Portal Web Push HTTP   | 5.2     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Client portal | VAPID Web Push send on staff-message dispatch; `pywebpush`      |
| Revenue analytics      | 5.2     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Billing       | `GET /reporting/revenue`; readiness score from billing state    |
| API key rate limiting  | 5.2     | Partial | ✅      | —        | ✅  | —   | ✅    | Org admin     | Redis fixed-window limit on `GET /reporting/operations` via key |

### Version 5.2 epic sign-off

| Epic                      | 5.2 outcome | Exit note                                                          |
| ------------------------- | ----------- | ------------------------------------------------------------------ |
| Communications production | Partial ✅  | Twilio SMS + audit log; marketing campaigns → 5.3+                 |
| LLM expansion             | Partial ✅  | Document summary endpoint + staff UI; batch jobs → 5.3+            |
| Portal push production    | Partial ✅  | Web Push HTTP on staff dispatch; native mobile push → 5.3+         |
| Revenue analytics         | Partial ✅  | Billing-derived readiness read model; usage metering → 5.3+        |
| API integrations depth    | Partial ✅  | API key rate-limit scaffold; developer portal + rotation UI → 5.3+ |

---

## Version 5.3 — Enterprise depth (sign-off)

Scope: [version-5.3-scope.md](version-5.3-scope.md) · Checklist: [version-5.3-completion-checklist.md](../development/version-5.3-completion-checklist.md) · Release notes: [v5.3.0.md](../release-notes/v5.3.0.md)

| Capability           | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies | Notes                                                  |
| -------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------ | ------------------------------------------------------ |
| Usage metering       | 5.3     | Partial | ✅      | —        | ✅  | —   | ✅    | Billing      | `GET /billing/usage/summary`; usage event audit log    |
| SCIM provisioning    | 5.3     | Partial | ✅      | —        | ✅  | —   | ✅    | Enterprise   | `GET/POST /enterprise/scim/v2/*`; provision audit log  |
| Predictive analytics | 5.3     | Partial | ✅      | —        | ✅  | —   | ✅    | Reporting    | `GET /reporting/predictive/outcomes`; snapshot refresh |
| API developer portal | 5.3     | Partial | ✅      | ✅       | ✅  | —   | ✅    | Org admin    | `GET /org-admin/developer-portal`; key rotation        |
| Batch LLM summaries  | 5.3     | Partial | ✅      | —        | ✅  | ✅  | ✅    | LLM gates    | `POST /documents/batch-llm-summaries/run`; worker job  |

### Version 5.3 epic sign-off

| Epic                   | 5.3 outcome | Exit note                                                         |
| ---------------------- | ----------- | ----------------------------------------------------------------- |
| Billing usage metering | Partial ✅  | Usage event scaffold + summary read; invoicing/dunning → 5.4+     |
| Identity provisioning  | Partial ✅  | SCIM 2.0 provision scaffold + audit; multi-IdP federation → 5.4+  |
| Predictive analytics   | Partial ✅  | Org outcome aggregates + refresh; model serving/benchmarks → 5.4+ |
| API integrations depth | Partial ✅  | Developer portal + key rotation; public OAuth portal → 5.4+       |
| LLM operations depth   | Partial ✅  | Batch document summarization job; autonomous agents → 5.4+        |

---

## Version 5.4 — Production operations (shipped)

Scope: [version-5.4-scope.md](version-5.4-scope.md) · Checklist: [version-5.4-completion-checklist.md](../development/version-5.4-completion-checklist.md)

| Capability           | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies  | Notes                                                            |
| -------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------- | ---------------------------------------------------------------- |
| Billing invoicing    | 5.4     | Partial | ✅      | —        | ✅  | —   | ✅    | Billing       | `GET /billing/invoicing/status`; dunning run scaffold            |
| Multi-IdP federation | 5.4     | Partial | ✅      | —        | ✅  | —   | ✅    | Enterprise    | `GET /enterprise/federation/providers`; provider registry        |
| Marketing SMS        | 5.4     | Partial | ✅      | —        | ✅  | —   | ✅    | Notifications | `GET /notifications/sms-campaigns/status`; campaign run scaffold |
| Agent observability  | 5.4     | Partial | ✅      | —        | ✅  | —   | ✅    | AI gates      | `GET /llm/agents/status`; agent run audit scaffold               |

### Version 5.4 epic sign-off

| Epic                     | 5.4 outcome | Exit note                                                            |
| ------------------------ | ----------- | -------------------------------------------------------------------- |
| Billing invoicing        | Partial ✅  | Invoice/dunning run scaffold; Stripe PDF + payment collection → 5.5+ |
| Identity federation      | Partial ✅  | Multi-IdP provider registry + SAML metadata upload scaffold          |
| Communications marketing | Partial ✅  | Campaign enqueue audit; bulk send + deliverability dashboards → 5.5+ |
| AI agent observability   | Partial ✅  | Agent run audit + timeline correlation; autonomous execution → 5.5+  |

---

## Version 5.5 — Production automation (shipped)

Scope: [version-5.5-scope.md](version-5.5-scope.md) · Checklist: [version-5.5-completion-checklist.md](../development/version-5.5-completion-checklist.md)

| Capability             | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies  | Notes                                                     |
| ---------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------- | --------------------------------------------------------- |
| Invoice collection     | 5.5     | Partial | ✅      | —        | ✅  | —   | ✅    | Billing       | `GET /billing/collection/status`; collection run scaffold |
| SAML metadata upload   | 5.5     | Partial | ✅      | —        | ✅  | —   | ✅    | Enterprise    | `POST /enterprise/federation/saml-metadata/upload`        |
| Marketing SMS delivery | 5.5     | Partial | ✅      | —        | ✅  | —   | ✅    | Notifications | `sms_marketing_campaign_delivery` worker + delivery audit |
| Agent execution        | 5.5     | Partial | ✅      | —        | ✅  | —   | ✅    | AI gates      | `POST /llm/execution/steps/{id}/approve`                  |

### Version 5.5 epic sign-off

| Epic                       | 5.5 outcome | Exit note                                                         |
| -------------------------- | ----------- | ----------------------------------------------------------------- |
| Billing invoice collection | Partial ✅  | Collection run scaffold; Stripe PDF API + tax calc → 5.6+         |
| SAML federation metadata   | Partial ✅  | Metadata upload audit; HRIS sync + cert rotation → 5.6+           |
| Marketing SMS delivery     | Partial ✅  | Worker Twilio delivery audit; deliverability dashboards → 5.6+    |
| Agent execution scaffold   | Partial ✅  | Human-gated approve path; autonomous filing + tool calling → 5.6+ |

---

## Version 5.6 — Compliance-reviewed production depth (sign-off)

Scope: [version-5.6-scope.md](version-5.6-scope.md) · Checklist: [version-5.6-completion-checklist.md](../development/version-5.6-completion-checklist.md) · Release notes: [v5.6.0.md](../release-notes/v5.6.0.md)

| Capability                   | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies  | Notes                                                     |
| ---------------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------- | --------------------------------------------------------- |
| HRIS bidirectional sync      | 5.6     | Partial | ✅      | —        | ✅  | —   | ✅    | Enterprise    | `GET /enterprise/federation/hris-sync/status`             |
| SMS deliverability dashboard | 5.6     | Partial | ✅      | —        | ✅  | —   | ✅    | Notifications | `GET /notifications/sms-campaigns/deliverability/summary` |
| LLM dispute draft augment    | 5.6     | Partial | ✅      | —        | ✅  | ✅  | ✅    | AI gates      | `POST /accounts/{id}/dispute-draft/llm-augment`           |
| Dispute filing prep          | 5.6     | Partial | ✅      | —        | ✅  | —   | ✅    | Disputes      | `POST /compliance/dispute-filing/accounts/{id}/prep`      |

### Version 5.6 epic sign-off

| Epic                         | 5.6 outcome | Exit note                                                           |
| ---------------------------- | ----------- | ------------------------------------------------------------------- |
| HRIS bidirectional sync      | Partial ✅  | Sync run audit scaffold; full lifecycle sync + cert rotation → 5.7+ |
| SMS deliverability dashboard | Partial ✅  | Metrics read model; failover + alerting → 5.7+                      |
| LLM dispute draft augment    | Partial ✅  | ADR-012-gated augment audit; auto-send + unsupervised loops → 5.7+  |
| Dispute filing prep          | Partial ✅  | Admin-gated prep audit; autonomous bureau filing → 5.7+             |

---

## AI capability tracker

| AI feature                    | Phase | Version | Status  | Location                                                                  |
| ----------------------------- | ----- | ------- | ------- | ------------------------------------------------------------------------- |
| Risk score (heuristic)        | —     | 4.3     | ✅      | `accounts/intelligence.py`                                                |
| Readiness score (heuristic)   | —     | 4.3     | ✅      | `accounts/intelligence.py`                                                |
| Dispute readiness rules       | —     | 4.3     | ✅      | `accounts/intelligence.py`                                                |
| Next action recommendations   | —     | 4.3     | ✅      | Heuristic text; LLM in 4.5                                                |
| OCR                           | 1     | 4.3     | ✅      | `worker/jobs/ocr.py`                                                      |
| Document classification       | 1     | 4.3     | Partial | Rules in `modules/documents/classification/`; LLM augment → 5.0           |
| Metadata / entity extraction  | 1     | 4.5     | Partial | Parser bridge + candidates; LLM NER → 5.0                                 |
| LLM policy gates              | 2     | 4.8     | Partial | `packages/llm-gateway` + `GET /llm/status`; no provider calls             |
| Case summaries (LLM)          | 2     | 5.0     | Partial | Endpoint + staff UI behind `ENABLE_LLM` + PII scrub                       |
| Document summaries (LLM)      | 2     | 5.2     | Partial | `POST /documents/{id}/llm-summary` + staff UI behind `ENABLE_LLM`         |
| LLM dispute draft augment     | 2     | 5.6     | Partial | `POST /accounts/{id}/dispute-draft/llm-augment`; no auto-send             |
| AI workflow orchestration     | 3     | 5.0+    | Planned | Deferred from 5.0 RC — requires compliance + observability prerequisites  |
| Predictive outcomes           | 3     | 5.3     | Partial | `GET /reporting/predictive/outcomes`; snapshot refresh scaffold           |
| Batch document summaries      | 2     | 5.3     | Partial | `POST /documents/batch-llm-summaries/run`; worker job behind `ENABLE_LLM` |
| Agent observability           | 3     | 5.4     | Partial | `GET /llm/agents/status`; run audit + timeline correlation scaffold       |
| Agent execution (human-gated) | 3     | 5.5     | Partial | `POST /llm/execution/steps/{id}/approve`; no autonomous filing            |
| Autonomous dispute prep       | 4     | 5.6     | Partial | Compliance-gated filing prep audit; no bureau submission                  |

See [AI Architecture](../architecture/ai-architecture.md).

---

## Version 5.7 — Compliance-gated autonomous workflows (in progress)

Scope: [version-5.7-scope.md](version-5.7-scope.md) · Checklist: [version-5.7-completion-checklist.md](../development/version-5.7-completion-checklist.md)

| Capability                  | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies | Notes                                                                         |
| --------------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ------------ | ----------------------------------------------------------------------------- |
| Dispute bureau submission   | 5.7     | Partial | ✅      | —        | ✅  | —   | ✅    | Disputes     | `POST /compliance/dispute-bureau-submission/prep-runs/{id}/submit`            |
| Agent external tool-calling | 5.7     | Partial | ✅      | —        | ✅  | —   | ✅    | AI gates     | `POST /llm/tool-calling/requests`                                             |
| SAML certificate rotation   | 5.7     | Partial | ✅      | —        | ✅  | —   | ✅    | Enterprise   | `POST /enterprise/federation/saml-cert-rotation/metadata-uploads/{id}/rotate` |
| Stripe invoice PDF          | 5.7     | Planned | —       | —        | —   | —   | —     | Billing      | PDF generation run audit → slice 5                                            |

---

## Related documents

- [Governance hub](README.md) — lifecycle and build order
- [V5.0 Enterprise Roadmap](../roadmap/v5.0-enterprise.md)
- [Release notes — M2 OCR](../release-notes/v4.3-m2-ocr-pipeline.md)
- [Architecture constitution](../architecture/README.md)
