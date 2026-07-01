# Platform Capability Matrix

**Executive view** of Verdin platform capabilities — what exists, what version introduced it, readiness by layer, and dependencies.

**Last updated:** 2026-06-29  
**Maintainers:** Update this document in every epic PR that ships or materially advances a capability.

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

| Capability                      | Version | Status | Backend | Frontend | API | AI      | Tests | Notes                                                 |
| ------------------------------- | ------- | ------ | ------- | -------- | --- | ------- | ----- | ----------------------------------------------------- |
| Platform Foundation             | 4.2     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | Shipped in 4.2 — monorepo, auth, RBAC, CI             |
| **Case Management**             | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | CRUD, filters, RBAC, full UI                          |
| **Credit Account Intelligence** | 4.3     | ✅     | ✅      | ✅       | ✅  | Partial | ✅    | Heuristic risk/readiness scoring in `intelligence.py` |
| **Document Foundation**         | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | Upload, versioning, MinIO, duplicate detection/review |
| **OCR Pipeline**                | 4.3     | ✅     | ✅      | ✅       | ✅  | ✅      | ✅    | Async worker extraction; pypdf + tesseract            |
| **AI Classification**           | 4.3     | ✅     | ✅      | Partial  | ✅  | Partial | ✅    | Rule-based classifier framework                       |
| **Metadata Extraction**         | 4.3     | ✅     | ✅      | ✅       | ✅  | Partial | ✅    | Rule-based extraction; `packages/document-metadata`   |
| **Entity Resolution**           | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | Deterministic matching; `packages/entity-resolution`  |
| Timeline & Audit Engine         | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | Event bus + append-only timeline                      |
| Task Management                 | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | CRUD, complete/reopen, filters, timeline events, UI   |
| Operational Dashboard           | 4.3.1   | ✅     | ✅      | ✅       | ✅  | —       | ✅    | Mission Control — shipped in v4.3.1                   |
| Client Management               | 4.3     | —      | —       | —        | —   | —       | —     | Deferred to 4.8                                       |

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

### Sprint 4.3.1 — Operational Core Stabilization (in progress)

Engineering milestone — not a semantic version.

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

## Version 4.5 — Automation

| Capability                      | Version | Status  | Backend | Frontend | API | AI      | Tests | Dependencies        | Notes                                                    |
| ------------------------------- | ------- | ------- | ------- | -------- | --- | ------- | ----- | ------------------- | -------------------------------------------------------- |
| Workflow Automation             | 4.5     | Partial | 🚧      | 🚧       | 🚧  | —       | ✅    | Timeline, Tasks     | Auto tasks incl. overdue investigation escalation        |
| Credit Report Import Wizard     | 4.5     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | Documents, OCR      | Wizard, comparison, duplicate detection, in-wizard retry |
| OCR Pipeline                    | 4.3     | ✅      | ✅      | ✅       | ✅  | ✅      | ✅    | Documents, Worker   | Shipped in 4.3 Operational Core                          |
| Document Classification         | 4.3     | 🚧      | 🚧      | —        | 🚧  | 🚧      | 🚧    | OCR                 | Rules engine in 4.3; LLM augmentation in 4.5             |
| Entity Extraction               | 4.5     | Partial | 🚧      | 🚧       | 🚧  | ✅      | ✅    | OCR, Accounts       | Parser tradelines produce account candidates             |
| AI Case Summaries               | 4.5     | Planned | —       | —        | —   | ✅      | —     | Cases, Documents    | Phase 2 AI                                               |
| AI Recommendation Engine        | 4.5     | Partial | 🚧      | —        | —   | Partial | ✅    | Accounts            | Dispute suggestions + missing evidence detector          |
| Dispute Generation (foundation) | 4.5     | Partial | 🚧      | 🚧       | 🚧  | ✅      | ✅    | Accounts, Documents | Templates, outcomes, export; E2E import→dispute path     |

---

## AI capability tracker

| AI feature                   | Phase | Version | Status  | Location                            |
| ---------------------------- | ----- | ------- | ------- | ----------------------------------- |
| Risk score (heuristic)       | —     | 4.3     | ✅      | `accounts/intelligence.py`          |
| Readiness score (heuristic)  | —     | 4.3     | ✅      | `accounts/intelligence.py`          |
| Dispute readiness rules      | —     | 4.3     | ✅      | `accounts/intelligence.py`          |
| Next action recommendations  | —     | 4.3     | ✅      | Heuristic text; LLM in 4.5          |
| OCR                          | 1     | 4.3     | ✅      | `worker/jobs/ocr.py`                |
| Document classification      | 1     | 4.3     | 🚧      | `modules/documents/classification/` |
| Metadata / entity extraction | 1     | 4.5     | Planned | Worker                              |
| Case summaries (LLM)         | 2     | 4.5     | Planned | Worker + API                        |
| AI workflow orchestration    | 3     | 5.0     | Planned | —                                   |
| Predictive outcomes          | 3     | 5.0     | Planned | —                                   |
| Autonomous dispute prep      | 4     | 5.0+    | Planned | Compliance gates required           |

See [AI Architecture](../architecture/ai-architecture.md).

---

## Related documents

- [Governance hub](README.md) — lifecycle and build order
- [V5.0 Enterprise Roadmap](../roadmap/v5.0-enterprise.md)
- [Release notes — M2 OCR](../release-notes/v4.3-m2-ocr-pipeline.md)
- [Architecture constitution](../architecture/README.md)
