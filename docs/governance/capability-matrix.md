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

## Version 4.3 — Operational Core (in progress)

| Capability                      | Version | Status | Backend | Frontend | API | AI      | Tests | Notes                                                                |
| ------------------------------- | ------- | ------ | ------- | -------- | --- | ------- | ----- | -------------------------------------------------------------------- |
| Platform Foundation             | 4.2     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | Shipped in 4.2 — monorepo, auth, RBAC, CI                            |
| **Case Management**             | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | CRUD, filters, RBAC, full UI                                         |
| **Credit Account Intelligence** | 4.3     | ✅     | ✅      | ✅       | ✅  | Partial | ✅    | Heuristic risk/readiness scoring in `intelligence.py`                |
| **Document Foundation**         | 4.3     | ✅     | ✅      | ✅       | ✅  | —       | ✅    | Upload, versioning, MinIO, duplicate detection                       |
| **OCR Pipeline**                | 4.3     | ✅     | ✅      | ✅       | ✅  | ✅      | ✅    | Async worker extraction; pypdf + tesseract                           |
| **AI Classification**           | 4.3     | 🚧     | 🚧      | —        | 🚧  | 🚧      | 🚧    | Rule-based classifier framework on `feature/document-classification` |
| **Metadata Extraction**         | 4.3     | 🚧     | —       | —        | —   | Planned | —     | Milestone 4 — `feature/document-metadata`                            |
| Timeline & Audit Engine         | 4.3     | 🚧     | 🚧      | —        | —   | —       | —     | `TimelineEvent` model; no API yet                                    |
| Task Management                 | 4.3     | 🚧     | 🚧      | 🚧       | 🚧  | —       | —     | Model + seed data; no router/tests                                   |
| Operational Dashboard           | 4.3     | 🚧     | —       | 🚧       | —   | —       | —     | Placeholder stats; no live metrics                                   |
| Client Management               | 4.3     | —      | —       | —        | —   | —       | —     | Deferred to 4.8                                                      |

### Document Intelligence Platform (4.3 epic)

Epic plan: [`docs/epics/document-intelligence-platform.md`](../epics/document-intelligence-platform.md)

| Milestone                    | Version | Status  | Backend | Frontend | API | AI      | Tests | Branch                            |
| ---------------------------- | ------- | ------- | ------- | -------- | --- | ------- | ----- | --------------------------------- |
| **M1 — Document Foundation** | 4.3     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | `feature/document-foundation`     |
| **M2 — OCR Pipeline**        | 4.3     | ✅      | ✅      | ✅       | ✅  | ✅      | ✅    | `feature/document-ocr`            |
| M3 — AI Classification       | 4.3     | 🚧      | 🚧      | —        | 🚧  | 🚧      | 🚧    | `feature/document-classification` |
| M4 — Metadata Extraction     | 4.3     | Planned | —       | —        | —   | Planned | —     | `feature/document-metadata`       |
| M5 — Timeline Integration    | 4.3     | Planned | —       | —        | —   | —       | —     | `feature/document-timeline`       |
| M6 — Intelligence Dashboard  | 4.3     | Planned | —       | —        | —   | Partial | —     | `feature/document-dashboard`      |

### 4.3 completion checklist

- [x] Case Management
- [x] Credit Account Intelligence
- [x] Document Foundation (M1)
- [x] OCR Pipeline (M2)
- [ ] AI Classification (M3 — in progress)
- [ ] Metadata Extraction (M4)
- [ ] Timeline & Audit Engine
- [ ] Task Management (full module)
- [ ] Operational Dashboard (live metrics)

> **Release strategy:** Version 4.3 is the **Operational Core** milestone. Freeze 4.3 as a stable production release once classification, metadata extraction, timeline, tasks, and dashboard are complete. Version 4.5 then focuses on automation (import wizard, AI summaries, workflow, dispute generation) without revisiting platform architecture.

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

| Capability                      | Version | Status  | Backend | Frontend | API | AI      | Tests | Dependencies        | Notes                                          |
| ------------------------------- | ------- | ------- | ------- | -------- | --- | ------- | ----- | ------------------- | ---------------------------------------------- |
| Workflow Automation             | 4.5     | Planned | —       | —        | —   | —       | —     | Timeline, Tasks     | —                                              |
| Credit Report Import Wizard     | 4.5     | Planned | —       | —        | —   | Planned | —     | Documents, OCR      | —                                              |
| OCR Pipeline                    | 4.3     | ✅      | ✅      | ✅       | ✅  | ✅      | ✅    | Documents, Worker   | Shipped in 4.3 Operational Core                |
| Document Classification         | 4.3     | 🚧      | 🚧      | —        | 🚧  | 🚧      | 🚧    | OCR                 | Rules engine in 4.3; LLM augmentation in 4.5   |
| Entity Extraction               | 4.5     | Planned | —       | —        | —   | ✅      | —     | OCR, Accounts       | Links tradelines to accounts                   |
| AI Case Summaries               | 4.5     | Planned | —       | —        | —   | ✅      | —     | Cases, Documents    | Phase 2 AI                                     |
| AI Recommendation Engine        | 4.5     | Partial | 🚧      | —        | —   | Partial | ✅    | Accounts            | Heuristic recommendations shipped; LLM planned |
| Dispute Generation (foundation) | 4.5     | Planned | —       | —        | —   | ✅      | —     | Accounts, Documents | Templates + AI draft                           |

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
