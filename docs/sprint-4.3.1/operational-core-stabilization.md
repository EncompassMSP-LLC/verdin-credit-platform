# Sprint 4.3.1 — Operational Core Stabilization

**Purpose:** stabilize Version 4.3.0 before opening Version 4.5 automation work.

Version 4.3.0 establishes the Operational Core: cases, accounts, documents, OCR, classification, metadata, entity resolution, timeline, tasks, and Mission Control. Sprint 4.3.1 should validate that those capabilities work as one product, establish performance baselines, and close reliability or security gaps before new automation features build on top.

## Objectives

### 1. End-to-End Workflow Validation

Exercise the full operational workflow:

```text
Create Case
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
Automatic Task Creation
    ↓
Mission Control Dashboard
```

Validation outputs:

- Document gaps, inconsistent statuses, missing timeline events, and any data that fails to surface in Mission Control.
- Confirm each module preserves organization scoping and RBAC through the workflow.
- Confirm failed OCR, unresolved entities, review-required documents, and overdue high-priority tasks appear as dashboard alerts.
- Confirm task and timeline events are created exactly once per relevant domain action.

### 2. Performance Baselines

Measure and record baseline metrics before adding more automation:

- Dashboard aggregation latency for `GET /api/v1/dashboard`
- OCR throughput by file count, file size, and document type
- Entity resolution execution time per document and per candidate set
- Timeline query speed for common filters and recent activity feed
- Task query speed for list, overdue, due-today, and high-priority filters

Capture:

- Dataset size and seed shape
- Local versus CI or containerized environment
- Median, p95, and max latency where practical
- Any query plans or indexes needed before Version 4.5

### 3. Security Review

Review the shipped Operational Core for:

- RBAC enforcement on every protected endpoint
- JWT access/refresh lifecycle and inactive-user handling
- File upload validation: MIME type, size, extension, duplicate hash, malformed PDFs/images
- Object storage access: bucket policy, presigned URL scope, storage key predictability
- Dependency updates and known vulnerabilities
- Secrets management: environment variables, examples, Docker Compose defaults, CI secrets

Expected output: security findings with severity, affected paths, and recommended fixes.

### 4. Test Coverage

Raise automated coverage where the Operational Core crosses module boundaries:

- Cross-module workflows from case creation through Mission Control
- Event bus interactions and timeline persistence
- Dashboard aggregation shape and alert generation
- Failure and retry scenarios for OCR, metadata extraction, entity resolution, and task creation
- RBAC denial paths for dashboard, tasks, documents, and timeline endpoints

## Definition of Done

- End-to-end workflow has been exercised and documented.
- Performance baselines are recorded for dashboard, OCR, entity resolution, timeline, and tasks.
- Security review findings are triaged.
- New tests cover the highest-risk cross-module and failure paths.
- Any release-blocking defects are fixed or explicitly deferred with owner and rationale.
- Version 4.5 planning starts from stable Operational Core contracts, not foundational rewrites.

## Version 4.5 Opening Focus

Version 4.5 should intentionally shift from foundational CRUD to automation and intelligence. Every 4.5 epic should leverage the Operational Core instead of modifying its core contracts.

Suggested epic order:

1. Credit Report Import Wizard
2. Advanced OCR & Bureau Parsing
3. Workflow Automation Engine
4. Dispute Generation Engine
5. AI Case Assistant
6. Client Portal
7. Notifications & Messaging

## Recommended 4.5 Principles

- Build on Mission Control and timeline events as the operational source of truth.
- Prefer workflow automation around existing case/task/document primitives.
- Keep AI outputs auditable: model/version, confidence, source document, timestamp.
- Preserve 4.3 public API contracts unless a formal migration is documented.
- Avoid foundational data-model churn during the first automation sprint.
