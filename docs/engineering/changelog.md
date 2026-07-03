# Engineering Decision Log

This log captures engineering decisions that are too implementation-oriented for release notes and not always large enough for an ADR.

For each sprint or milestone, record:

- Why a technical choice was made
- Alternatives considered
- Technical debt introduced, if any
- Follow-up work
- Performance observations
- Risks

Use ADRs for durable architecture decisions that require formal acceptance. Use release notes for user-facing changes. Use this log for technical context that future maintainers will need when debugging, refactoring, or planning.

## Sprint 4.3.0 — Operational Core

### Decision: Mission Control Aggregates Through One Endpoint

**Decision:** `GET /api/v1/dashboard` returns a single Mission Control snapshot with `overview`, `cases`, `accounts`, `documents`, `timeline`, `tasks`, `processing`, `performance`, and `alerts`.

**Reason:** Reduce frontend chattiness and keep metric ownership in the backend. The frontend should not know whether a metric comes from cases, documents, tasks, timeline, OCR, classification, metadata, or entity resolution.

**Alternatives considered:**

- Multiple frontend API calls to each domain module
- A frontend composition layer that calls domain APIs and merges results
- Separate dashboard endpoints for KPIs, timeline, tasks, alerts, and processing

**Technical debt introduced:** Aggregation query complexity is concentrated in `api/modules/dashboard/repository.py`.

**Follow-up work:**

- Measure dashboard aggregation latency in Sprint 4.3.1.
- Add indexes or query refactors if p95 latency exceeds the `<500 ms` target.
- Consider a denormalized read model if dashboard traffic or metric count grows substantially.

**Performance observations:** Baseline not yet captured. Sprint 4.3.1 owns measurement.

**Risks:** A single aggregation endpoint can become slow or difficult to maintain if it accumulates too much domain-specific logic.

### Decision: Timeline Is the First Event Consumer

**Decision:** Domain services publish platform events, and the timeline subscriber persists append-only `TimelineEvent` rows.

**Reason:** Establish an event-driven foundation without introducing a full workflow engine too early.

**Alternatives considered:**

- Direct timeline writes from each domain service
- Full event-stream infrastructure before timeline requirements were proven
- No event bus until workflow automation

**Technical debt introduced:** The event bus is currently lightweight and in-process; future durable delivery semantics are not yet defined.

**Follow-up work:**

- Validate event publishing in cross-module workflow tests.
- Decide whether workflow automation in 4.5 needs durable queue semantics.
- Add delivery metrics when job orchestration is introduced.

**Performance observations:** Timeline query speed target for Sprint 4.3.1 is `<250 ms` for common recent activity/filter queries.

**Risks:** If event consumers expand without orchestration and metrics, retry and ordering behavior may become inconsistent.

### Decision: Task Management Is a First-Class Operational Module

**Decision:** Tasks have their own model, repository, service, router, API client, validation types, and UI rather than remaining a placeholder.

**Reason:** Automation and dashboard alerts need a durable work queue with RBAC, timeline events, filters, assignment, due dates, and lifecycle transitions.

**Alternatives considered:**

- Keep tasks as a simple case sub-resource
- Generate tasks only from future workflow automation
- Store task-like items as timeline metadata

**Technical debt introduced:** Automatic task creation rules are not yet centralized. Sprint 4.3.1 should verify current event-driven task behavior and document gaps.

**Follow-up work:**

- Add cross-module tests for task creation from events.
- Feed high-priority overdue tasks into Mission Control alerts.
- Use tasks as the target primitive for 4.5 workflow automation.

**Performance observations:** Task query baseline should include list, overdue, due-today, and high-priority filters.

**Risks:** If automation creates tasks without idempotency guarantees, duplicate operational work items may appear.

### Decision: Stabilize Before Starting Version 4.5

**Decision:** Sprint 4.3.1 is a stabilization sprint before new automation features begin.

**Reason:** Version 4.3.0 introduced the core operating model. Validating full workflows, performance, security, and coverage before automation reduces the risk of carrying foundational issues into larger AI and workflow features.

**Alternatives considered:**

- Begin 4.5 import wizard immediately
- Fix stabilization issues opportunistically during 4.5 feature work
- Treat dashboard merge as sufficient validation

**Technical debt introduced:** None intentionally; the sprint exists to identify and retire debt.

**Follow-up work:**

- Complete the Sprint 4.3.1 checklist.
- Capture performance baselines.
- Save the v4.3.0 architecture snapshot as the as-built reference.

**Performance observations:** Baseline targets are defined in `docs/sprint-4.3.1/operational-core-stabilization.md`.

**Risks:** If stabilization is skipped, 4.5 automation could amplify hidden workflow or performance defects.

## Version 4.5 Planning

### Decision: Adopt Predictable Release Cadence

**Decision:** Use `main` as always releasable, `feature/*` for individual capabilities, `sprint/*` for stabilization and integration, semantic tags for releases, and GitHub Releases for every tagged version.

**Reason:** The platform has matured from scaffold to Operational Core. A predictable cadence preserves a clean, auditable history while Version 4.5 adds larger automation and AI capabilities.

**Alternatives considered:**

- Continue merging all work directly through feature branches without stabilization branches
- Tag only major releases and skip patch/stabilization tags
- Use release notes in the repo without GitHub Releases

**Technical debt introduced:** None intentionally. The process adds lightweight release ceremony that must be kept current.

**Follow-up work:**

- Tag `v4.3.0` from `main` after Mission Control is merged.
- Publish a GitHub Release for `v4.3.0` using the GA release notes.
- Use a `sprint/4.3.1-stabilization` branch for the stabilization checklist if multiple fixes or test suites are needed.
- Tag `v4.3.1` only after end-to-end workflow tests, baselines, security review, and coverage goals pass consistently in CI.

**Performance observations:** Release tags should reference the baseline metrics captured in Sprint 4.3.1 so future versions can compare dashboard, OCR, entity resolution, timeline, and task performance.

**Risks:** If `main` is allowed to drift from releasable status, tags and GitHub Releases lose trust as audit artifacts. If stabilization work is mixed into broad feature branches, 4.5 may inherit unresolved Operational Core issues.

### Decision: Group 4.5 Into Four Focused Epics

**Decision:** Organize Version 4.5 around four cohesive epics:

1. Credit Report Intelligence
2. Workflow Automation
3. AI Assistance
4. Client Experience

**Reason:** Grouping related capabilities keeps the release cohesive and prevents 4.5 from becoming a collection of unrelated features.

**Alternatives considered:**

- Track each feature as a separate epic
- Start with AI features before import/workflow foundations
- Continue extending foundational CRUD modules

**Technical debt introduced:** Epic boundaries may need refinement after Sprint 4.3.1 reveals workflow or performance constraints.

**Follow-up work:**

- Open a formal Version 4.5 kickoff milestone after Sprint 4.3.1 exits.
- Define success criteria and dependency maps for each epic.
- Verify each epic builds on Operational Core contracts.

**Performance observations:** Automation should be evaluated against 4.3.1 baselines.

**Risks:** If epics modify core contracts rather than leveraging them, 4.5 could create avoidable architectural churn.

### Decision: Plan a Unified Job Orchestration Layer

**Decision:** By the end of Version 4.5, background processing should converge on a unified job orchestration layer, proposed as `packages/job-orchestrator/`.

Potential package shape:

```text
packages/job-orchestrator/
├── job.py
├── queue.py
├── scheduler.py
├── retry.py
├── registry.py
└── metrics.py
```

**Reason:** 4.5 will add many background processes: OCR, classification, metadata extraction, entity resolution, workflow automation, notifications, AI summaries, and report imports. A shared orchestration layer gives them consistent retries, scheduling, metrics, and monitoring.

**Alternatives considered:**

- Let each worker job manage its own queue and retry policy
- Adopt Celery/RabbitMQ/Kafka immediately
- Keep the current lightweight Redis job helpers indefinitely

**Technical debt introduced:** None yet; this is planned architecture. If delayed too long, duplicated retry and scheduling logic may emerge across worker jobs.

**Follow-up work:**

- During 4.3.1, inventory current worker job patterns and retry behavior.
- In 4.5 kickoff, decide whether `packages/job-orchestrator/` is introduced before or during the Workflow Automation epic.
- Define metrics required for Mission Control and future operational dashboards.

**Performance observations:** Job orchestration should emit queue depth, duration, retry count, failure count, and throughput metrics.

**Risks:** Introducing orchestration too early could over-abstract current needs; introducing it too late could leave 4.5 with fragmented job semantics.

## Version 4.5.0 — Automation release candidate sign-off

### Decision: Formal scope limits and deferrals for v4.5.0

**Decision:** Version 4.5.0 ships as a **release candidate** with three **Partial** epics (workflow auto-tasks, dispute foundation, rules AI) and explicit deferral of client experience, LLM assistance, BPM/cron, and job-orchestrator package to 4.8+.

**Reason:** The sprint loop delivered import intelligence, dispute lifecycle, and event-driven tasks with E2E coverage. Remaining roadmap items (portal, notifications, LLM) require infrastructure or compliance gates not in scope for this RC.

**Alternatives considered:**

- Hold v4.5.0 until LLM features ship (blocked on provider/PII approval)
- Mark Partial capabilities as ✅ without written limits (rejected — governance requires scope notes)
- Defer dispute generation entirely to 4.8 (rejected — foundation lifecycle is production-usable)

**Technical debt introduced:** Overdue investigation uses read-time escalation on account GET rather than a scheduled worker job.

**Follow-up work:**

- Release notes and `v4.5.0` tag (slice 5.5–5.6)
- 4.8 kickoff: notifications, LLM policy, `job-orchestrator` evaluation

**Documentation:** [`docs/governance/version-4.5-scope.md`](../governance/version-4.5-scope.md), capability matrix epic sign-off table.

**Risks:** Stakeholders may expect full workflow engine or LLM in 4.5 — scope doc is the source of truth for what shipped vs deferred.

## Version 4.8.0 — Operations kickoff

### Decision: In-app notifications as first 4.8 slice

**Decision:** Ship persisted per-user in-app notifications (API + staff bell UI) before email/SMS delivery or client portal auth.

**Reason:** Notifications are a dependency for workflow reminders, dispute updates, and future client messaging. In-app delivery requires no external provider.

**Alternatives considered:**

- Start with client portal (rejected — needs client model + auth partition first)
- Start with LLM summaries (rejected — policy ADR gate not yet merged)
- Defer notifications to email-first (rejected — no delivery infra in 4.5)

**Technical debt introduced:** Notification creation is admin-only HTTP for now; workflow modules should call `NotificationService.notify_user()` in follow-up slices.

**Follow-up work:**

- Wire auto-task and dispute lifecycle events to `notify_user`
- Scheduled overdue investigation worker (checklist slice 4)
- Email delivery scaffold (checklist slice 9)

**Documentation:** [`docs/governance/version-4.8-scope.md`](../governance/version-4.8-scope.md), [`docs/development/version-4.8-completion-checklist.md`](../development/version-4.8-completion-checklist.md)

**Risks:** Users may expect email/SMS in the same slice — scope doc limits 4.8 notifications to in-app for RC.

## Version 4.8 — Overdue investigation worker

### Decision: Worker scan replaces GET auto-escalation

**Decision:** Add `overdue_investigation_scan` worker job to scan eligible accounts and create escalation tasks. Remove read-time escalation from `GET /accounts/{id}`; retain explicit `POST /accounts/{id}/dispute-investigation-overdue` for staff.

**Reason:** 4.5 technical debt used account GET as a pseudo-cron. A dedicated worker job is schedulable and auditable without side effects on read paths.

**Follow-up work:** Wire daily enqueue via external cron or `JobScheduler` registry (slice 5 scaffold).

## Version 4.8 — Job orchestration package scaffold

### Decision: Extract shared orchestration into `packages/job-orchestrator/`

**Decision:** Introduce `verdin-job-orchestrator` with job contracts, registry, Redis queue, retry/scheduler/metrics scaffolds, and ADR-011. API and worker import shared `JobType` / queue primitives via thin re-export modules.

**Reason:** Duplicated enqueue code and enums between API and worker blocked consistent retries, scheduling, and observability.

**Alternatives considered:**

- Full Celery migration in 4.8 (rejected — ops cost)
- Defer package to 5.0 (rejected — overdue scan and future jobs need a convergence point now)

**Technical debt introduced:** Retry policy and metrics recorders are not yet wired into `worker/runner.py`; cron evaluation in `JobScheduler` is a placeholder.

**Follow-up work:**

- Wire runner retries and metrics export
- Register scheduled jobs (overdue scan daily cron) when scheduler executes expressions
- PostgreSQL job persistence per ADR-008 Sprint 2 plan

**Documentation:** [`docs/adr/011-job-orchestrator.md`](../adr/011-job-orchestrator.md)

## Version 4.8 — Client and contact model

### Decision: First-class Client aggregate with nested contacts

**Decision:** Add `clients` and `client_contacts` tables with staff CRUD API (`/clients`, `/clients/{id}/contacts`). Cases retain inline `client_name` / `client_email` for backward compatibility; optional `client_id` FK deferred.

**Reason:** Client portal auth (slice 7) requires a durable client identity separate from case denormalized fields.

**Follow-up work:** Link cases to clients, read-only progress view (slice 11).

## Version 4.8 — Client portal auth partition

### Decision: Separate JWT realm for portal users

**Decision:** Add `client_portal_users` table, `/portal/auth/*` endpoints, and JWT `realm=portal` claims. Staff provisions portal credentials via `/clients/{id}/portal-user`. Feature-flagged with `ENABLE_CLIENT_PORTAL`.

**Reason:** Portal users must not share staff RBAC tokens or access staff APIs.

**Follow-up work:** Client portal case progress view (slice 11), dedicated portal token storage in web app.

## Version 4.8 — LLM provider policy and gates

### Decision: `ENABLE_LLM` + `packages/llm-gateway/` before external calls

**Decision:** Add ADR-012, `verdin-llm-gateway` package with provider config, PII scrubbing, and `require_llm_ready()` gate. Separate `ENABLE_LLM` from heuristic `ENABLE_AI`. Expose `GET /llm/status` for staff readiness checks.

**Reason:** 4.5 deferred all LLM work pending compliance gates; implementation slices must not call providers without policy merged.

**Follow-up work:** Actual LLM summary endpoints and worker integration behind gate.

## Version 4.8 — Email delivery scaffold (feature-flagged)

### Decision: Add non-sending readiness gate before provider integration

**Decision:** Add `ENABLE_EMAIL_DELIVERY`, email provider config env vars, and `GET /notifications/email/status` to report readiness (`enabled`, `ready`, provider metadata, blockers). No external provider calls are executed in this slice.

**Reason:** Notifications epic requires an email/SMS scaffold in 4.8, but production delivery wiring needs a later slice and provider selection.

**Follow-up work:** Implement provider adapters (`smtp` / `sendgrid`), enqueue delivery attempts from notification workflows, and add retry/metrics via `job-orchestrator`.

## Version 4.8 — Operations reporting read model

### Decision: Dedicated reporting endpoint + dashboard embedding

**Decision:** Add `GET /reporting/operations` with org-scoped aggregates for clients, dispute account/letter status counts, and notification backlog. Embed the same read model in `GET /dashboard` as an `operations` section.

**Reason:** 4.8 reporting epic needs read-optimized operational KPIs without bloating the core Mission Control aggregation queries.

**Follow-up work:** Materialized views or read replicas if aggregate latency exceeds dashboard targets; bureau performance and revenue metrics deferred to 5.0.

## Version 4.8 — Client portal case progress view

### Decision: Read-only portal case endpoints with interim case matching

**Decision:** Add `GET /portal/cases` and `GET /portal/cases/{id}` for portal JWT users, plus a minimal client portal UI (`/portal/login`, `/portal`, `/portal/cases/:id`). Cases match the portal client via email/name heuristics until optional `cases.client_id` linking ships.

**Reason:** 4.8 client experience epic requires read-only progress without exposing staff APIs or internal notes.

**Follow-up work:** Add `client_id` FK on cases, dedicated portal token storage isolation from staff session, secure messaging.

## Version 4.8.0 — Operations release sign-off

### Decision: Partial epic delivery with explicit deferrals to 5.0

**Decision:** Ship `v4.8.0` with all five Operations epics marked **Partial** and documented limits in scope doc, capability matrix epic sign-off table, and release notes. LLM summary endpoints and production email/SMS delivery remain deferred post-gate.

**Reason:** 4.8 delivers operational foundations (notifications, portal, reporting, workflow jobs, LLM policy) without over-promising enterprise or compliance features.

**Documentation:** [`docs/governance/version-4.8-scope.md`](../governance/version-4.8-scope.md), [`docs/release-notes/v4.8.0.md`](../release-notes/v4.8.0.md)

## Version 5.0.0 — Enterprise kickoff

### Decision: Formal scope and ordered checklist before implementation slices

**Decision:** Publish `version-5.0-scope.md`, `version-5.0-completion-checklist.md`, capability matrix 5.0 planned rows, and Version 5.0 sprint loop rule. First implementation slice is `cases.client_id` linking.

**Reason:** 4.8 deferred enterprise identity, compliance, production comms, and post-gate LLM work to 5.0; kickoff docs are the source of truth for slice order.

**Follow-up work:** Slice 2 — Alembic migration + API for case–client FK.

### Decision: Optional `cases.client_id` FK with portal FK-first matching

**Decision:** Add nullable `cases.client_id` FK to `clients`, staff create/update/list support with org-scoped validation, and portal case queries that match on FK first with email/name heuristics as fallback for unlinked cases.

**Reason:** Durable case–client relationships replace fragile heuristic-only portal matching while preserving backward compatibility for legacy inline client fields.

**Follow-up work:** Slice 3 — production email delivery adapters.

### Decision: Production email delivery with SMTP/SendGrid adapters and audit trail

**Decision:** Wire `smtp` and `sendgrid` provider adapters behind `ENABLE_EMAIL_DELIVERY`, persist `email_delivery_logs`, expose `POST /notifications/email/send` and `GET /notifications/email/deliveries`, and add optional `deliver_email` on notification create.

**Reason:** Communications epic requires production email beyond the 4.8 readiness scaffold, with auditable sends for compliance and workflow integration.

**Follow-up work:** Slice 4 — LLM case summary endpoint (post-gate).

### Decision: Post-gate LLM case summary endpoint with PII scrubbing and audit trail

**Decision:** Add `verdin_llm_gateway` completion clients (OpenAI-compatible, Anthropic), `POST /cases/{case_id}/llm-summary` for case managers, scrubbed context via `scrub_payload()`, and timeline event `CASE_LLM_SUMMARY_GENERATED` with model and prompt hash metadata.

**Reason:** 5.0 AI epic requires at least one staff-authenticated LLM endpoint after ADR-012 gates; case summaries are the highest-value first surface.

**Follow-up work:** Slice 5 — job orchestrator runner wiring + overdue cron.

### Decision: Wire job orchestrator retry/metrics and in-process overdue scan cron

**Decision:** Implement cron evaluation in `JobScheduler` (croniter), wire `RetryPolicy` and `JobMetricsRecorder` into `worker/orchestrator.py`, and register `overdue_investigation_scan` at `0 6 * * *` UTC with in-process scheduler ticks.

**Reason:** 4.8 deferred runner integration; 5.0 platform slice requires schedulable overdue scan without external cron-only wiring.

**Follow-up work:** Slice 6 — MFA / SSO foundation (feature-flagged).

### Decision: Enterprise identity readiness scaffold behind `ENABLE_ENTERPRISE`

**Decision:** Add `enterprise_identity` settings/gates, `GET /enterprise/status` for SSO (`oidc`/`saml`) and MFA (`totp`) readiness, and `@verdin/api-client` types. Staff and portal auth partitions remain separate.

**Reason:** Enterprise identity epic requires a compliance gate before IdP or TOTP enrollment endpoints ship in later slices.

**Follow-up work:** Slice 7 — compliance center scaffold + consent model.

### Decision: Compliance center scaffold with consent records and retention placeholders

**Decision:** Add `consent_records` and `retention_policies` tables (migration `017`), compliance module with org-scoped consent CRUD + withdrawal, retention policy placeholders (admin), `GET /compliance/status`, and `@verdin/api-client` compliance functions.

**Reason:** Compliance epic requires durable consent history and retention policy foundations before legal sign-off or enforcement workflows ship in later versions.

**Follow-up work:** Slice 8 — portal document upload.

### Decision: Portal document upload scoped to linked cases

**Decision:** Add `POST /portal/cases/{case_id}/documents` and `GET /portal/cases/{case_id}/documents` for portal JWT users, reuse document storage/OCR pipeline, emit `PORTAL_DOCUMENT_UPLOADED` timeline events, and expose `@verdin/api-client` upload helpers.

**Reason:** Client portal epic requires clients to submit evidence on linked cases without staff mediation; uploads remain org-scoped with the same case visibility rules as read-only progress.

**Follow-up work:** Slice 9 — portal secure messaging scaffold.

### Decision: Secure messaging thread scaffold for portal and staff

**Decision:** Add `message_threads` and `thread_messages` tables (migration `018`), one thread per case, portal `GET/POST /portal/cases/{case_id}/messages`, staff `GET/POST /cases/{case_id}/message-thread`, timeline events for portal and staff messages, and `@verdin/api-client` messaging helpers.

**Reason:** Client portal epic requires a durable messaging foundation on linked cases before real-time delivery or attachments ship in later versions.

**Follow-up work:** Slice 10 — enterprise reporting read models.

### Decision: Enterprise bureau performance and team productivity read models

**Decision:** Add `GET /reporting/bureau-performance` and `GET /reporting/team-productivity` org-scoped aggregate endpoints, `GET /reporting/status` capabilities overview, and `@verdin/api-client` reporting helpers.

**Reason:** Reporting epic requires enterprise dashboards beyond 4.8 operations KPIs without materialized views or revenue pipelines in this slice.

**Follow-up work:** Slice 11 — API keys + org admin scaffold.

### Decision: Organization admin scaffold with API key lifecycle

**Decision:** Add `organization_api_keys` table (migration `019`), org-admin module with `GET /org-admin/status`, organization summary, API key create/list/get/revoke endpoints, SHA-256 hashed key storage with `vrd_live_` prefix, and `@verdin/api-client` org-admin helpers. Gated behind `ENABLE_ENTERPRISE`; admin role required.

**Reason:** Enterprise admin epic requires durable API key foundations before SCIM, billing admin, or key-authenticated integrations ship in later versions.

**Follow-up work:** Slice 12 — capability matrix 5.0 sign-off + deferrals.

### Decision: Version 5.0 epic sign-off with explicit deferrals to 5.0+ / 5.1+

**Decision:** Mark all nine Version 5.0 epics **Partial ✅** in `version-5.0-scope.md`, add capability matrix epic sign-off table, document deferred AI workflow orchestration and predictive outcomes in the AI tracker, and update roadmap with v5.0.0 RC outcomes.

**Reason:** Governance slice closes the 5.0 implementation track before release notes and tag; all promised capabilities are either shipped (partial) or explicitly deferred with written limits.

**Documentation:** [`docs/governance/version-5.0-scope.md`](../governance/version-5.0-scope.md), [`docs/governance/capability-matrix.md`](../governance/capability-matrix.md)

**Follow-up work:** Slice 13 — `docs/release-notes/v5.0.0.md`.

### Decision: Publish Version 5.0.0 release notes

**Decision:** Add `docs/release-notes/v5.0.0.md` covering all nine partial epics, feature flags, migrations 015–019, deferrals, and update capability matrix, roadmap, and governance release history.

**Reason:** Release notes are the user-facing summary of the Enterprise Edition RC before the `v5.0.0` git tag.

**Documentation:** [`docs/release-notes/v5.0.0.md`](../release-notes/v5.0.0.md)

**Follow-up work:** Slice 14 — tag `v5.0.0`.

### Decision: Tag `v5.0.0` — Enterprise Edition release

**Decision:** Mark Version 5.0 completion checklist complete and tag `v5.0.0` on `main` with GitHub Release notes sourced from `docs/release-notes/v5.0.0.md`.

**Reason:** Closes the Version 5.0 sprint loop; all nine epics ship as Partial with documented deferrals.

**Documentation:** [`docs/release-notes/v5.0.0.md`](../release-notes/v5.0.0.md), [`docs/development/version-5.0-completion-checklist.md`](../development/version-5.0-completion-checklist.md)

## Version 5.0+ — Product Hardening kickoff

### Decision: Pilot UI checklist after v5.0.0 tag

**Decision:** Publish `version-5.0-plus-scope.md`, `version-5.0-plus-completion-checklist.md`, and Version 5.0+ sprint loop. First implementation slices: web `predev` api-client build and staff client management UI.

**Reason:** v5.0 shipped enterprise APIs without staff UI for clients, compliance, reporting, and org admin; pilot readiness requires product surfaces before 5.1 enterprise hardening.

**Follow-up work:** Slice 4 — case form `client_id` picker.

### Decision: Case form client picker for durable case–client linking

**Decision:** Extend `createCaseSchema` with optional `client_id`, add `ClientPicker` on case create/edit forms, auto-fill client name/email from linked records, and show client profile link on case detail.

**Reason:** 5.0+ pilot requires staff to link cases to client records without API calls; portal matching prefers FK when set.

**Follow-up work:** Slice 5 — portal document upload UI.

### Decision: Portal document upload UI on case detail

**Decision:** Add `PortalCaseDocuments` on portal case detail with document list and multipart upload form using existing portal document API helpers.

**Reason:** 5.0+ pilot requires clients to submit evidence without staff mediation; backend upload endpoints shipped in v5.0.0.

**Follow-up work:** Slice 6 — portal secure messaging UI.

### Decision: Portal secure messaging UI on case detail

**Decision:** Add `PortalCaseMessages` on portal case detail with thread history and send form using portal messaging API helpers.

**Reason:** 5.0+ pilot requires clients to communicate with staff on linked cases without email; backend messaging scaffold shipped in v5.0.0.

**Follow-up work:** Slice 7 — staff case messaging UI.

### Decision: Staff case messaging UI on case detail

**Decision:** Add `CaseMessageThreadPanel` on staff case detail with thread history and reply form using staff messaging API helpers, gated by `VITE_ENABLE_CLIENT_PORTAL`.

**Reason:** 5.0+ pilot requires staff to respond to portal clients without leaving the case workspace.

**Follow-up work:** Slice 8 — compliance center staff UI.

### Decision: Compliance center staff UI

**Decision:** Add `/compliance` page with consent record list/create/withdraw and retention policy list/create, gated by `VITE_ENABLE_ENTERPRISE`.

**Reason:** 5.0+ pilot requires staff to manage compliance artifacts without API calls; backend compliance center shipped in v5.0.0.

**Follow-up work:** Slice 9 — enterprise reporting staff UI.

### Decision: Enterprise reporting staff UI

**Decision:** Add `/reporting` page with operations, bureau performance, and team productivity tabs using enterprise reporting API helpers, gated by `VITE_ENABLE_ENTERPRISE`.

**Reason:** 5.0+ pilot requires staff to access bureau and team read models without API calls; backend reporting shipped in v5.0.0.

**Follow-up work:** Slice 10 — org admin staff UI.

### Decision: Org admin staff UI

**Decision:** Add `/org-admin` page with organization summary, API key list/create/revoke, and one-time secret display; fix api-client create key body serialization.

**Reason:** 5.0+ pilot requires admins to manage API keys without CLI; backend org admin shipped in v5.0.0.

**Follow-up work:** Slice 11 — LLM case summary UI.

### Decision: LLM case summary UI on case detail

**Decision:** Add `CaseLlmSummaryPanel` on staff case detail with LLM readiness check and generate action using `POST /cases/{id}/llm-summary`, gated by `VITE_ENABLE_LLM`.

**Reason:** 5.0+ pilot requires staff to trigger gated case summaries from the case workspace without API calls.

**Follow-up work:** Slice 12 — capability matrix 5.0+ sign-off.

### Decision: Version 5.0+ pilot sign-off

**Decision:** Mark all eight 5.0+ epics **Partial ✅** in scope doc, add capability matrix 5.0+ epic sign-off table, complete checklist exit criteria, and update roadmap to pilot-ready status.

**Reason:** All twelve 5.0+ UI slices shipped; pilot can run staff and portal workflows behind feature flags without API-only gaps.

**Follow-up work:** 5.1+ planning — billing, IdP enrollment, API key middleware, autonomous agents per deferrals table.

### Decision: Kick off Version 5.1 production hardening

**Decision:** Add `version-5.1-scope.md`, `version-5.1-completion-checklist.md`, and `.cursor/rules/version-51-sprint-loop.mdc`; link 5.1 from product roadmap.

**Reason:** 5.0+ pilot sign-off complete; deferred production integrations need a sequenced delivery path before v5.1.0 release.

**Follow-up work:** Slice 2 — API key auth middleware.

### Decision: API key auth middleware on reporting operations

**Decision:** Add `ApiKeyAuthService` with prefix/hash validation, scope checks, and `last_used_at` audit; wire `GET /reporting/operations` to accept `X-API-Key` or `Authorization: Bearer vrd_live_…` alongside staff JWT. Gated behind `ENABLE_ENTERPRISE`.

**Reason:** 5.1 requires at least one production integration path authenticated by organization API keys before billing and external automation expand.

**Follow-up work:** Slice 3 — production SMS delivery.

### Decision: IdP and TOTP staff enrollment

**Decision:** Add TOTP enrollment (`/enterprise/mfa/totp/*`) with encrypted secret storage and OIDC account linking (`/enterprise/sso/enrollment/*`) with signed state tokens, `user_totp_enrollments` and `user_sso_enrollments` tables, and `@verdin/api-client` enrollment helpers. Gated behind `ENABLE_ENTERPRISE`.

**Reason:** 5.1 identity epic requires staff enrollment beyond the v5.0 readiness scaffold before SCIM or multi-IdP federation.

**Follow-up work:** Slice 5 — Stripe billing scaffold.

### Decision: Stripe billing scaffold

**Decision:** Add `organization_billing_accounts` and `billing_webhook_events` tables, Stripe customer/subscription helpers, admin billing setup/subscribe endpoints, webhook handler at `POST /billing/webhooks/stripe`, and embedded `billing` on `GET /org-admin/organization`. Gated by `ENABLE_BILLING`.

**Reason:** 5.1 billing epic requires a durable Stripe integration foundation before usage metering or invoicing ships in later versions.

**Follow-up work:** Slice 6 — compliance enforcement jobs.
