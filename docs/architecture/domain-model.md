# Domain Model

Business domains, bounded contexts, and how core entities relate. This document describes **current implementation (4.3)** and **planned domains** through 5.0.

## Domain map

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enterprise Administration                     │
│         (orgs, users, RBAC, SSO, billing, feature flags)        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      Client Management (4.8+)                    │
│              clients, contacts, intake, client portal            │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Case Management │ │ Credit Account  │ │ Document        │
│    (4.3 ✅)     │ │ Intelligence    │ │ Intelligence    │
│                 │ │    (4.3 ✅)     │ │   (4.3 planned) │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
              ┌──────────────────────────┐
              │   Task Management        │
              │   (scaffold → 4.3 full)  │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │ Timeline & Audit Engine  │
              │   (4.3 events → 5.0)     │
              └────────────┬─────────────┘
                           ▼
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
┌─────────┐      ┌─────────────────┐    ┌─────────────────┐
│Workflow │      │ Dispute Gen     │    │ Import Engine   │
│(4.5)    │      │ (4.5)           │    │ (4.5)           │
└─────────┘      └─────────────────┘    └─────────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │ AI Case Assistant (4.5+) │
              │ Reporting (4.8)          │
              │ Compliance Center (5.0)  │
              └──────────────────────────┘
```

## Core aggregate: Case

The **Case** is the central aggregate root for credit repair operations. Most user-facing work flows through a case.

| Related entity          | Relationship            | Purpose                       |
| ----------------------- | ----------------------- | ----------------------------- |
| **Organization**        | Case belongs to org     | Tenant isolation              |
| **User**                | Case assigned to user   | Ownership / workload          |
| **Account** (tradeline) | Many accounts per case  | Bureau tradeline intelligence |
| **Document**            | Many documents per case | Evidence and reports          |
| **Task**                | Many tasks per case     | Operational work items        |
| **Communication**       | Many per case           | Messages and correspondence   |
| **TimelineEvent**       | Many per case           | Audit trail and activity feed |

### Case lifecycle (implemented)

```
intake → review → evidence_gathering → dispute_preparation
      → awaiting_response → monitoring → complete
```

Status (`open`, `active`, `on_hold`, `resolved`, `closed`) operates orthogonally to stage.

## Credit Account Intelligence (implemented)

An **Account** is a credit bureau tradeline linked to a case — not a client company record (legacy v4.2 model removed in migration 003).

| Concept              | Implementation                                         |
| -------------------- | ------------------------------------------------------ |
| Bureau               | equifax, experian, transunion, innovis, unknown        |
| Risk score           | Computed 0–100 from payment/status/past-due heuristics |
| Readiness score      | Dispute readiness from evidence and workflow state     |
| Intelligence summary | Aggregates across org or single case                   |

Accounts inherit organization scope from their parent case.

## Document Intelligence (planned 4.3)

Documents attach to cases. Future capabilities:

- Stored in MinIO with metadata in PostgreSQL
- OCR and classification via worker jobs
- Entity extraction links to Account records
- Version history and duplicate detection

## Timeline & Audit Engine

**TimelineEvent** records what happened, when, and on which case.

| Event category | Examples                                    |
| -------------- | ------------------------------------------- |
| Case           | created, status changed, assigned           |
| Account        | imported, score recalculated, dispute ready |
| Document       | uploaded, OCR completed, classified         |
| Task           | created, completed, escalated               |
| Auth           | user login (org-level audit in 5.0)         |

**Rule:** Any user-visible or compliance-relevant service action should emit a timeline event (4.3 standardization in progress).

## Task Management

Tasks represent actionable work with assignee, due date, priority, and status. Tasks belong to cases and follow the same org-scoping rules.

## Planned domains (summary)

| Domain               | Version | Entry aggregate                      |
| -------------------- | ------- | ------------------------------------ |
| Workflow Automation  | 4.5     | WorkflowDefinition + Case            |
| Credit Report Import | 4.5     | ImportJob + Case                     |
| Dispute Generation   | 4.5     | DisputeLetter + Account              |
| AI Case Assistant    | 4.5–5.0 | Case (context bundle)                |
| Client Portal        | 4.8     | ClientUser + Case (read-only subset) |
| Compliance Center    | 5.0     | Organization + AuditEvent            |

## Bounded context rules

1. **Modules do not reach across repositories casually** — orchestration happens in a service or dedicated application service.
2. **Cross-domain reads** use IDs and explicit service methods (e.g., list case accounts via `AccountService.list_case_accounts`).
3. **Shared kernel** lives in `api/core/` (pagination, permissions, audit helpers) and `packages/shared`.
4. **No circular module imports** — routers are not imported from module `__init__.py` files.

## Module registry (API)

Current domain modules under `apps/api/api/modules/`:

| Module      | Status           |
| ----------- | ---------------- |
| `auth`      | Production       |
| `cases`     | Production (4.3) |
| `accounts`  | Production (4.3) |
| `documents` | Scaffold         |
| `tasks`     | Scaffold         |
| `timeline`  | Scaffold         |
| `imports`   | Planned          |
| `analytics` | Planned          |

See [Data Model](data-model.md) for persistence detail.
