# Platform Governance

This directory is the **governance hub** for the Verdin Credit Platform. It connects product direction, technical design, standards, and delivery status into one traceable system.

## Governance layers

| Layer                 | Document                                                                                                                   | Audience                    | Answers                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------- | -------------------------------------------- |
| **Product roadmap**   | [`../roadmap/v5.0-enterprise.md`](../roadmap/v5.0-enterprise.md)                                                           | Executives, PM, engineering | Where are we going? What domains matter?     |
| **Capability matrix** | [`capability-matrix.md`](capability-matrix.md)                                                                             | All stakeholders            | What exists today? What is production-ready? |
| **Architecture**      | [`../architecture/README.md`](../architecture/README.md)                                                                   | Engineers, architects       | How is it built? What rules apply?           |
| **ADRs**              | [`../adr/README.md`](../adr/README.md)                                                                                     | Engineers                   | Why was it built this way?                   |
| **Engineering log**   | [`../engineering/changelog.md`](../engineering/changelog.md)                                                               | Engineers                   | Why did implementation choices evolve?       |
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

## Release Cadence

Use a predictable release model now that the platform has a stable Operational Core:

| Channel         | Policy                                                                           |
| --------------- | -------------------------------------------------------------------------------- |
| `main`          | Always releasable. Only merge work that has passed CI and is ready to ship.      |
| `feature/*`     | Individual capabilities or tightly scoped product changes.                       |
| `sprint/*`      | Stabilization, integration, and release-hardening work.                          |
| Semantic tags   | Use annotated semantic version tags such as `v4.3.0`, `v4.3.1`, `v4.5.0`.        |
| GitHub Releases | Every tagged version gets release notes and a summary of delivered capabilities. |

Release flow:

1. Complete feature or sprint work on a branch.
2. Merge through PR after CI, review, release notes, and capability matrix updates.
3. Pull `main` locally after merge.
4. Create an annotated tag from `main`.
5. Push the tag.
6. Publish a GitHub Release from the tag with delivered capabilities, upgrade notes, and known risks.

For Version 4.3:

- `v4.3.0` marks Operational Core GA after Mission Control is merged to `main`.
- `v4.3.1` marks the stabilization sprint once all checklist items are complete and passing consistently in CI.
- Version 4.5 begins only after 4.3.1 exit criteria are satisfied.

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

### Phase 1 — Operational Core (Version 4.3)

| Priority | Capability                              | Status     | Branch / Reference                                    |
| -------- | --------------------------------------- | ---------- | ----------------------------------------------------- |
| —        | Platform Foundation                     | ✅ Shipped | `feature/platform-foundation`                         |
| —        | Case Management                         | ✅ Shipped | `feature/case-management`                             |
| —        | Credit Account Intelligence             | ✅ Shipped | `feature/account-intelligence`                        |
| —        | Document Foundation (M1)                | ✅ Shipped | `feature/document-foundation`                         |
| —        | OCR Pipeline (M2)                       | ✅ Shipped | `feature/document-ocr`                                |
| —        | AI Classification (M3)                  | ✅ Shipped | `feature/document-classification`                     |
| —        | Metadata & Entity Resolution (M4)       | ✅ Shipped | `feature/document-entity-resolution`                  |
| —        | Timeline & Audit Engine (M5)            | ✅ Shipped | `feature/document-timeline`                           |
| —        | Task Management                         | ✅ Shipped | `feature/task-management`                             |
| —        | Operational Dashboard (Mission Control) | ✅ Shipped | `GET /dashboard` product API                          |
| **Next** | Operational Core Stabilization (4.3.1)  | Planned    | `docs/sprint-4.3.1/operational-core-stabilization.md` |

> **Version 4.3.0** is the **Operational Core** release. Sprint 4.3.1 is a short stabilization gate for end-to-end validation, performance baselines, security review, and test coverage before **Version 4.5** automation starts.

### Phase 2 — Automation (4.5)

Credit Report Import Wizard → Advanced OCR & bureau parsing → Workflow Automation Engine → Dispute Generation Engine → AI Case Assistant → Client Portal → Notifications & Messaging

4.5 planning should use four release epics: Credit Report Intelligence, Workflow Automation, AI Assistance, and Client Experience. The engineering decision log also records the recommendation to introduce a unified `packages/job-orchestrator/` layer before background automation becomes fragmented.

### Phase 3 — Intelligence (4.8)

Dispute generation (full) → analytics → client portal → notifications

### Phase 4 — Enterprise (5.0)

Multi-tenancy → compliance center → AI case assistant → predictive analytics → enterprise administration

## Quick links

- [Capability matrix (executive view)](capability-matrix.md)
- [Roadmap index](../roadmap/README.md)
- [Engineering Decision Log](../engineering/changelog.md)
- [Sprint 4.3.1 stabilization](../sprint-4.3.1/operational-core-stabilization.md)
- [Release notes — M2 OCR](../release-notes/v4.3-m2-ocr-pipeline.md)
- [Developer guide](../developer-guide.md)
- [ADR 009 — Architecture governance](../adr/009-architecture-governance.md)
