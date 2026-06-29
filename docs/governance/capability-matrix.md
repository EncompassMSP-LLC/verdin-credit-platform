# Platform Capability Matrix

**Executive view** of Verdin platform capabilities — what exists, what version introduced it, readiness by layer, and dependencies.

**Last updated:** 2026-06-28  
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

## Version 4.2 — Platform Foundation

| Capability                 | Version | Status | Backend | Frontend | API | AI  | Tests | Dependencies | Notes                              |
| -------------------------- | ------- | ------ | ------- | -------- | --- | --- | ----- | ------------ | ---------------------------------- |
| Monorepo & CI/CD           | 4.2     | ✅     | ✅      | ✅       | ✅  | —   | ✅    | —            | pnpm, Turborepo, GitHub Actions    |
| Authentication (JWT)       | 4.2     | ✅     | ✅      | ✅       | ✅  | —   | ✅    | —            | Login, refresh, `/auth/me`         |
| RBAC (5 roles)             | 4.2     | ✅     | ✅      | ✅       | ✅  | —   | ✅    | Auth         | Enforced in services               |
| Organization tenancy       | 4.2     | ✅     | ✅      | —        | ✅  | —   | ✅    | Auth         | `organization_id` scoping          |
| Domain module pattern      | 4.2     | ✅     | —       | —        | —   | —   | —     | —            | router → service → repository      |
| Background worker scaffold | 4.2     | ✅     | —       | —        | —   | —   | —     | Redis        | Job registry; placeholder jobs     |
| Feature flags              | 4.2     | ✅     | ✅      | —        | —   | —   | —     | —            | `ENABLE_AI`, `ENABLE_IMPORTS`      |
| Shared packages            | 4.2     | ✅     | —       | ✅       | ✅  | —   | —     | —            | shared, ui, validation, api-client |

---

## Version 4.3 — Operational Core

| Capability                      | Version | Status | Backend | Frontend | API | AI      | Tests | Dependencies                     | Notes                                                                         |
| ------------------------------- | ------- | ------ | ------- | -------- | --- | ------- | ----- | -------------------------------- | ----------------------------------------------------------------------------- |
| **Case Management**             | 4.3     | ✅     | ✅      | ✅       | ✅  | Planned | ✅    | Auth, Org                        | CRUD, filters, RBAC, full UI                                                  |
| **Credit Account Intelligence** | 4.3     | ✅     | ✅      | ✅       | ✅  | Partial | ✅    | Cases                            | Risk/readiness scoring, intelligence summary, heuristics in `intelligence.py` |
| Timeline & Audit Engine         | 4.3     | 🚧     | 🚧      | —        | —   | —       | —     | Cases                            | `TimelineEvent` model; no API yet                                             |
| Task Management                 | 4.3     | 🚧     | 🚧      | 🚧       | 🚧  | —       | —     | Cases                            | Model + seed data; no router/tests                                            |
| Operational Dashboard           | 4.3     | 🚧     | —       | 🚧       | —   | —       | —     | Cases, Accounts, Tasks, Timeline | Placeholder stats; no live metrics                                            |
| Client Management               | 4.3     | —      | —       | —        | —   | —       | —     | Org                              | Clients/contacts deferred to 4.8                                              |

### Document Intelligence Platform (4.3 epic)

Epic plan: [`docs/epics/document-intelligence-platform.md`](../epics/document-intelligence-platform.md)

| Milestone                    | Version | Status  | Backend | Frontend | API | AI      | Tests | Branch                            |
| ---------------------------- | ------- | ------- | ------- | -------- | --- | ------- | ----- | --------------------------------- |
| **M1 — Document Foundation** | 4.3     | ✅      | ✅      | ✅       | ✅  | —       | ✅    | `feature/document-foundation`     |
| M2 — OCR Pipeline            | 4.3     | 🚧      | 🚧      | 🚧       | 🚧  | 🚧      | 🚧    | `feature/document-ocr`            |
| M3 — AI Classification       | 4.3     | Planned | —       | —        | —   | Planned | —     | `feature/document-classification` |
| M4 — Metadata Extraction     | 4.3     | Planned | —       | —        | —   | Planned | —     | `feature/document-metadata`       |
| M5 — Timeline Integration    | 4.3     | Planned | —       | —        | —   | —       | —     | `feature/document-timeline`       |
| M6 — Intelligence Dashboard  | 4.3     | Planned | —       | —        | —   | Partial | —     | `feature/document-dashboard`      |

### 4.3 completion checklist

- [x] Case Management
- [x] Credit Account Intelligence
- [ ] Document Intelligence Platform (M1 ✅ — M2–M6 remaining)
- [ ] Timeline & Audit Engine
- [ ] Task Management (full module)
- [ ] Operational Dashboard (live metrics)

---

## Version 4.5 — Automation

| Capability                      | Version | Status  | Backend | Frontend | API | AI      | Tests | Dependencies        | Notes                                          |
| ------------------------------- | ------- | ------- | ------- | -------- | --- | ------- | ----- | ------------------- | ---------------------------------------------- |
| Workflow Automation             | 4.5     | Planned | —       | —        | —   | —       | —     | Timeline, Tasks     | —                                              |
| Credit Report Import Wizard     | 4.5     | Planned | —       | —        | —   | Planned | —     | Documents, OCR      | —                                              |
| OCR Pipeline                    | 4.5     | Planned | —       | —        | —   | ✅      | —     | Documents, Worker   | Phase 1 AI                                     |
| Document Classification         | 4.5     | Planned | —       | —        | —   | ✅      | —     | OCR                 | Phase 1 AI                                     |
| Entity Extraction               | 4.5     | Planned | —       | —        | —   | ✅      | —     | OCR, Accounts       | Links tradelines to accounts                   |
| AI Case Summaries               | 4.5     | Planned | —       | —        | —   | ✅      | —     | Cases, Documents    | Phase 2 AI                                     |
| AI Recommendation Engine        | 4.5     | Partial | 🚧      | —        | —   | Partial | ✅    | Accounts            | Heuristic recommendations shipped; LLM planned |
| Dispute Generation (foundation) | 4.5     | Planned | —       | —        | —   | ✅      | —     | Accounts, Documents | Templates + AI draft                           |

---

## Version 4.8 — Operations

| Capability                | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies     | Notes                        |
| ------------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ---------------- | ---------------------------- |
| Reporting & Analytics     | 4.8     | Planned | —       | —        | —   | —   | —     | All 4.3 domains  | Dashboards, resolution rates |
| Client Portal             | 4.8     | Planned | —       | —        | —   | —   | —     | Cases, Documents | Separate auth realm          |
| Notifications             | 4.8     | Planned | —       | —        | —   | —   | —     | Timeline, Worker | Email/SMS                    |
| Communications Center     | 4.8     | Planned | 🚧      | —        | —   | —   | —     | Cases            | `Communication` model only   |
| Dispute Generation (full) | 4.8     | Planned | —       | —        | —   | ✅  | —     | 4.5 foundation   | Bureau, furnisher, CFPB      |

---

## Version 5.0 — Enterprise Edition

| Capability                | Version | Status  | Backend | Frontend | API | AI  | Tests | Dependencies      | Notes                                               |
| ------------------------- | ------- | ------- | ------- | -------- | --- | --- | ----- | ----------------- | --------------------------------------------------- |
| Enterprise Multi-tenancy  | 5.0     | Partial | ✅      | —        | ✅  | —   | ✅    | Auth              | Single org per user today; 5.0 enhancements planned |
| Compliance Center         | 5.0     | Planned | —       | —        | —   | —   | —     | Timeline, Audit   | CROA, FCRA, FDCPA, retention                        |
| AI Case Assistant         | 5.0     | Planned | —       | —        | —   | 🚧  | —     | 4.5 AI, Documents | Phase 3–4 AI                                        |
| Predictive Analytics      | 5.0     | Planned | —       | —        | —   | ✅  | —     | Analytics, AI     | Dispute success, prioritization                     |
| Enterprise Administration | 5.0     | Planned | —       | —        | —   | —   | —     | Auth              | SSO, API keys, billing                              |
| MFA / SSO                 | 5.0     | Planned | —       | —        | —   | —   | —     | Auth              | —                                                   |
| Immutable Audit Store     | 5.0     | Planned | —       | —        | —   | —   | —     | Timeline          | Append-only compliance log                          |
| Enterprise Integrations   | 5.0     | Planned | —       | —        | —   | —   | —     | API gateway       | Bureaus, Twilio, Stripe, etc.                       |

---

## Dependency graph (simplified)

```
Platform Foundation (4.2)
        │
        ├── Case Management ──┬── Credit Account Intelligence
        │                     │
        │                     ├── Document Intelligence ◄── NEXT EPIC
        │                     │         │
        │                     │         ├── OCR / Classification (4.5)
        │                     │         ├── Import Wizard (4.5)
        │                     │         └── Entity Extraction (4.5)
        │                     │
        │                     ├── Timeline Engine
        │                     │         │
        │                     │         └── Workflow Automation (4.5)
        │                     │
        │                     └── Task Management
        │                               │
        └───────────────────────────────┴── Dashboard (4.3)
                                              │
                                              └── Analytics (4.8)
                                                        │
                                                        └── Enterprise (5.0)
```

---

## AI capability tracker

| AI feature                   | Phase | Version | Status  | Location                   |
| ---------------------------- | ----- | ------- | ------- | -------------------------- |
| Risk score (heuristic)       | —     | 4.3     | ✅      | `accounts/intelligence.py` |
| Readiness score (heuristic)  | —     | 4.3     | ✅      | `accounts/intelligence.py` |
| Dispute readiness rules      | —     | 4.3     | ✅      | `accounts/intelligence.py` |
| Next action recommendations  | —     | 4.3     | ✅      | Heuristic text; LLM in 4.5 |
| OCR                          | 1     | 4.5     | Planned | Worker                     |
| Document classification      | 1     | 4.5     | Planned | Worker                     |
| Metadata / entity extraction | 1     | 4.5     | Planned | Worker                     |
| Case summaries (LLM)         | 2     | 4.5     | Planned | Worker + API               |
| AI workflow orchestration    | 3     | 5.0     | Planned | —                          |
| Predictive outcomes          | 3     | 5.0     | Planned | —                          |
| Autonomous dispute prep      | 4     | 5.0+    | Planned | Compliance gates required  |

See [AI Architecture](../architecture/ai-architecture.md).

---

## How to update this matrix

1. Open or create the epic PR.
2. When the capability reaches **Definition of done** ([governance README](README.md#definition-of-done-capability-row)), update the row.
3. Set **Status** to ✅ only when all applicable layer columns are ✅ (or — where N/A).
4. Add a note if status is **Partial** or **🚧**.
5. Update the **4.3 completion checklist** if relevant.

---

## Related documents

- [Governance hub](README.md) — lifecycle and build order
- [V5.0 Enterprise Roadmap](../roadmap/v5.0-enterprise.md)
- [Architecture constitution](../architecture/README.md)
- [ADR index](../adr/README.md)
