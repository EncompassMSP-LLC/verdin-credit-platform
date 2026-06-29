# Platform Governance

This directory is the **governance hub** for the Verdin Credit Platform. It connects product direction, technical design, standards, and delivery status into one traceable system.

## Governance layers

| Layer                 | Document                                                                                                                   | Audience                    | Answers                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------- | -------------------------------------------- |
| **Product roadmap**   | [`../roadmap/v5.0-enterprise.md`](../roadmap/v5.0-enterprise.md)                                                           | Executives, PM, engineering | Where are we going? What domains matter?     |
| **Capability matrix** | [`capability-matrix.md`](capability-matrix.md)                                                                             | All stakeholders            | What exists today? What is production-ready? |
| **Architecture**      | [`../architecture/README.md`](../architecture/README.md)                                                                   | Engineers, architects       | How is it built? What rules apply?           |
| **ADRs**              | [`../adr/README.md`](../adr/README.md)                                                                                     | Engineers                   | Why was it built this way?                   |
| **Standards**         | [`../coding-standards.md`](../coding-standards.md), [`../architecture/api-standards.md`](../architecture/api-standards.md) | Engineers                   | What conventions must we follow?             |

## Feature lifecycle

Every feature must follow this lifecycle for consistency and traceability:

```
Roadmap alignment
       ↓
Architecture review (domain + data + API + security)
       ↓
ADR (if significant or irreversible)
       ↓
Feature branch
       ↓
Implementation (router → service → repository)
       ↓
Tests (unit + integration)
       ↓
Documentation (API reference + architecture if changed)
       ↓
Pull request
       ↓
CI/CD (pre-commit, lint, typecheck, pytest, build)
       ↓
Merge
       ↓
Release notes
       ↓
Capability matrix update   ← required before epic is "done"
```

### Definition of done (capability row)

A capability may be marked **✅ Production** in the [capability matrix](capability-matrix.md) only when:

- Backend module complete with RBAC and org scoping
- API documented in `docs/api/reference.md`
- `@verdin/api-client` functions implemented (not stubs)
- Frontend UI integrated (where applicable)
- Integration tests for all endpoints
- Release notes or sprint doc published
- Matrix row updated in the same PR or immediately after merge

## Recommended build order

With governance in place, prioritize features in this order:

### Phase 1 — Operational Core (complete 4.3)

| Priority | Capability                                     | Rationale                                                   |
| -------- | ---------------------------------------------- | ----------------------------------------------------------- |
| **Next** | **M2 — OCR Pipeline** (`feature/document-ocr`) | Async text extraction; unblocks classification and metadata |
| 2        | M3–M4 — Classification & metadata extraction   | Structured fields linked to accounts                        |
| 3        | Timeline & Audit Engine                        | Document events feed audit trail                            |
| 4        | Task Management (full module)                  | Operational queues depend on tasks                          |
| 5        | Operational Dashboard                          | Live metrics from cases, accounts, tasks, timeline          |

> **Note:** Milestone 1 (Document Foundation) is complete. Continue the epic on `feature/document-ocr`.

### Phase 2 — Automation (4.5)

Credit Report Import Wizard → OCR pipeline → entity extraction → AI summaries → recommendation engine

### Phase 3 — Intelligence (4.8)

Dispute generation → analytics → client portal → notifications

### Phase 4 — Enterprise (5.0)

Multi-tenancy → compliance center → AI case assistant → predictive analytics → enterprise administration

## Quick links

- [Capability matrix (executive view)](capability-matrix.md)
- [Roadmap index](../roadmap/README.md)
- [Developer guide](../developer-guide.md)
- [ADR 009 — Architecture governance](../adr/009-architecture-governance.md)
