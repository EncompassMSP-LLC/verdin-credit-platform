# Sprint 4.3.1 — Operational Core Stabilization

**Purpose:** stabilize Version 4.3.0 before opening Version 4.5 automation work.

Version 4.3.0 establishes the Operational Core: cases, accounts, documents, OCR, classification, metadata, entity resolution, timeline, tasks, and Mission Control. Sprint 4.3.1 should validate that those capabilities work as one product, establish performance baselines, and close reliability or security gaps before new automation features build on top.

## Workstreams

Sprint 4.3.1 is organized into measurable workstreams rather than miscellaneous cleanup:

| Workstream            | Goal                                                                              |
| --------------------- | --------------------------------------------------------------------------------- |
| Quality               | E2E workflow tests, cross-module coverage, eliminate flaky tests                  |
| Performance           | Benchmark dashboard aggregation, profile document pipeline, capture baselines     |
| Security              | RBAC coverage, authentication audit, upload/storage validation, dependency review |
| Operational Readiness | Logging, health checks, observability, deployment docs, backup/recovery           |

The execution order below maps to these workstreams.

## Execution Order

### 1. End-to-End Workflow Validation

Automate the complete operational workflow as an integration test suite that can run in CI:

```text
Create Organization
    ↓
Create Case
    ↓
Add Credit Account
    ↓
Upload Credit Report
    ↓
OCR
    ↓
Classification
    ↓
Metadata Extraction
    ↓
Entity Resolution
    ↓
Timeline Events
    ↓
Task Creation
    ↓
Mission Control Dashboard
```

Checklist:

- [ ] Create a dedicated backend integration suite for the full workflow.
- [ ] Seed organization and users with representative roles.
- [ ] Create a case and linked credit account.
- [ ] Upload a credit report fixture and assert document metadata, storage key, hash, and version state.
- [ ] Run or simulate OCR and assert status transitions and extracted text.
- [ ] Run classification and assert document type, confidence, method, and timestamp.
- [ ] Run metadata extraction and assert extracted fields.
- [ ] Run entity resolution and assert matched, ambiguous, and unmatched outcomes where fixtures support them.
- [ ] Assert timeline events exist exactly once for key domain actions.
- [ ] Assert task creation is triggered for operational work items.
- [ ] Assert Mission Control includes the case, document, task, processing, timeline, and alert data.
- [ ] Document gaps, inconsistent statuses, missing events, or data not surfacing in Mission Control.

### 2. Performance Baselines

Capture baseline metrics before optimizing. These numbers become the comparison point for Version 4.5 automation.

| Metric            | Initial Target                         |
| ----------------- | -------------------------------------- |
| Dashboard API     | `<500 ms`                              |
| Case creation     | `<200 ms`                              |
| Document upload   | `<500 ms` excluding OCR                |
| OCR processing    | Record baseline by file type and size  |
| Entity resolution | Record baseline by candidate set size  |
| Timeline query    | `<250 ms` for recent activity/filter   |
| Task query        | Record list/overdue/due-today baseline |

Capture:

- Dataset size and seed shape
- Local versus CI or containerized environment
- Median, p95, and max latency where practical
- Any query plans or indexes needed before Version 4.5

### 3. Security Review

Create and execute a security checklist covering:

- [ ] RBAC verification for all endpoints
- [ ] JWT expiry, refresh, inactive user, and invalid token behavior
- [ ] File upload validation: MIME type, size, extension, duplicate hash, malformed PDF/image handling
- [ ] MinIO bucket policies and object access controls
- [ ] Secret management: `.env.example`, Docker Compose defaults, CI secrets, no committed credentials
- [ ] Dependency audit: `npm audit`, `pip-audit`, or equivalent
- [ ] CORS and security headers
- [ ] Rate limiting for authentication and uploads

Expected output: security findings with severity, affected paths, and recommended fixes.

### 4. Test Coverage

Expand from endpoint coverage into cross-module scenarios:

- [ ] Case → Document → OCR → Timeline
- [ ] OCR failure → Retry → Success
- [ ] Entity resolution ambiguity
- [ ] Task creation from events
- [ ] Dashboard aggregation and alert generation
- [ ] Event bus interactions and timeline persistence
- [ ] RBAC denial paths for dashboard, tasks, documents, and timeline endpoints
- [ ] Failure and retry scenarios for metadata extraction, entity resolution, and task creation

### 5. Architecture Review

Review the current implementation against the architecture and governance docs before introducing Version 4.5 complexity.

For each major module (`auth`, `cases`, `accounts`, `documents`, `timeline`, `tasks`, `dashboard`, worker jobs):

- [ ] Follows router → service → repository; routers do not query SQLAlchemy directly.
- [ ] Business logic lives in services, database access in repositories.
- [ ] Publishes events instead of tightly coupling modules when actions are user-visible or workflow-relevant.
- [ ] Complies with accepted ADRs.
- [ ] Avoids duplicate business logic across modules.
- [ ] Preserves organization scoping and role checks.
- [ ] Has clear test coverage for success, failure, and RBAC paths.

Architecture snapshot:

- [ ] Generate and save [`docs/architecture/v4.3.0-snapshot.md`](../architecture/v4.3.0-snapshot.md).
- [ ] Include module map, package dependencies, event flow, database entities, API surface, active ADRs, and v4.3.0 capability matrix.
- [ ] Treat the snapshot as the as-built reference for regression investigations during Version 4.5.

### 6. Operational Readiness

Confirm the Operational Core is deployable, observable, and recoverable before automation expands the surface area:

- [ ] Verify structured logging is consistent across API, worker, and background jobs.
- [ ] Verify health checks for API, database, Redis, and object storage.
- [ ] Confirm observability for request latency, errors, and job outcomes (metrics or logs).
- [ ] Ensure deployment documentation (Docker Compose and environment setup) is current.
- [ ] Validate PostgreSQL backup and restore procedure.
- [ ] Validate object storage (MinIO) backup and recovery procedure.
- [ ] Document any operational gaps with owners and follow-up actions.

## Definition of Done

- End-to-end workflow has been exercised and documented.
- Performance baselines are recorded for dashboard, OCR, entity resolution, timeline, and tasks.
- Security review findings are triaged.
- New tests cover the highest-risk cross-module and failure paths.
- Architecture review is complete and the v4.3.0 architecture snapshot is saved.
- Operational readiness is verified: logging, health checks, observability, deployment docs, and backup/recovery.
- Any release-blocking defects are fixed or explicitly deferred with owner and rationale.
- Version 4.5 planning starts from stable Operational Core contracts, not foundational rewrites.

## Version 4.5 Opening Focus

Version 4.5 should intentionally shift from foundational CRUD to automation and intelligence. Every 4.5 epic should leverage the Operational Core instead of modifying its core contracts.

Suggested epic order:

1. Credit Report Import Wizard
2. Bureau-specific parsers
3. Workflow Automation Engine
4. Dispute Generation Engine
5. AI Case Assistant
6. Client Portal
7. Notifications

## Recommended 4.5 Principles

- Build on Mission Control and timeline events as the operational source of truth.
- Prefer workflow automation around existing case/task/document primitives.
- Keep AI outputs auditable: model/version, confidence, source document, timestamp.
- Preserve 4.3 public API contracts unless a formal migration is documented.
- Avoid foundational data-model churn during the first automation sprint.
- Establish a dedicated **Job Orchestration** capability early in 4.5 so OCR, automation, AI processing, notifications, and imports share one execution model (see [`docs/engineering/changelog.md`](../engineering/changelog.md)) instead of evolving independently.
