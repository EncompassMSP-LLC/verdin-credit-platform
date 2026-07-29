# Lending Readiness Platform™ V1.0 — Completion Checklist

Executable slices for building the platform from the Phase 3 ops package.

Master plan: [`../lrp-enterprise/15-roadmap/lending-readiness-platform-v1.0-release-plan.md`](../lrp-enterprise/15-roadmap/lending-readiness-platform-v1.0-release-plan.md)

Traceability: [`../lrp-enterprise/15-roadmap/v1.0-feature-traceability-matrix.md`](../lrp-enterprise/15-roadmap/v1.0-feature-traceability-matrix.md)

Gap analysis: [`../lrp-enterprise/15-roadmap/v1.0-gap-analysis.md`](../lrp-enterprise/15-roadmap/v1.0-gap-analysis.md)

Sprint loop: `.cursor/rules/lrp-platform-v1-sprint-loop.mdc`

Ops contract: [`../lrp-enterprise/04-operations/business-ops-package/`](../lrp-enterprise/04-operations/business-ops-package/)

## Exit criteria for "LRP Platform V1.0 done"

- [ ] M1 Core Platform production-wired (auth/RBAC, CRM, borrowers, referrals)
- [ ] M2 Readiness (score, timeline, reports, action plans, notifications)
- [ ] M3 Automation (email/SMS/jobs/packs/scheduling per §14)
- [x] M4 Partner Experience UAT (lender + realtor MVP; borrower UAT)
- [ ] M5 Public Experience claim-safe (landings + KB/SEO scope)
- [ ] M6 Production Readiness (security, perf, monitoring, DR, tag)
- [ ] Capability matrix + API reference updated for LRP V1.0 surfaces
- [ ] No unsupervised bureau filing; claim-library locked in UI
- [ ] V1.0 exit criteria in release plan §7 all checked

---

## Recommended order

| Order | Slice                                                 | Milestone | Status |
| ----- | ----------------------------------------------------- | --------- | ------ |
| 1     | Charter — master release plan + living docs + ADR-013 | Kickoff   | ✅     |
| 2     | LRP-108 Kill demo-mode for production orgs            | M1        | ✅     |
| 3     | LRP-101 CRM partners/contacts live API                | M1        | ✅     |
| 4     | LRP-109 Production organization mode (org type/flags) | M1        | ✅     |
| 5     | LRP-102 CRM tasks + daily digest read model           | M1        | ✅     |
| 6     | LRP-103 Referral intake from web form                 | M1        | ✅     |
| 7     | LRP-107 Case documents in CRM borrower workspace      | M1        | ✅     |
| 8     | LRP-104 Borrower portal task/readiness parity         | M2        | ✅     |
| 9     | LRP-106 Readiness report in borrower portal           | M2        | ✅     |
| 10    | LRP-105 LO notifications center live                  | M2        | ✅     |
| 11    | LRP-401 Readiness timeline UI                         | M2        | ✅     |
| 12    | LRP-402 Bureau + Metro2 in readiness blockers         | M2        | ✅     |
| 13    | LRP-204 Consultation completed pack                   | M2        | ✅     |
| 14    | LRP-201 Referral intake orchestrator job              | M3        | ✅     |
| 15    | LRP-202 Notification matrix v1                        | M3        | ✅     |
| 16    | LRP-203 CRM automation rules (persist)                | M3        | ✅     |
| 17    | LRP-205 Appointment reminders                         | M3        | ✅     |
| 18    | LRP-206 Partner nurture drip                          | M3        | ✅     |
| 19    | LRP-207 Weekly status digest job                      | M3        | ✅     |
| 20    | LRP-301 Realtor partner role + login                  | M4        | ✅     |
| 21    | LRP-302 Realtor portal MVP                            | M4        | ✅     |
| 22    | LRP-303 Borrower UAT script + fixes                   | M4        | ✅     |
| 23    | LRP-304 LO UAT script + fixes                         | M4        | ✅     |
| 24    | LRP-403 Dispute strategy suggestions (advisory)       | M4        | ✅     |
| 25    | LRP-208 Case issue explainability + evidence center   | M2/M4     | ✅     |
| 26    | LRP-209 Consumer communication preferences            | M2/M4     | ✅     |
| 27    | LRP-405 FAQ/KB retrieval bot                          | M4        | ✅     |
| 28    | LRP-406 Letter draft augment (staff-gated)            | M4        | ✅     |
| 29    | LRP-305 Planned marketing landings (`/builders` etc.) | M5        | ✅     |
| 30    | LRP-501 Partner isolation audit                       | M6        | ☐      |
| 31    | LRP-502 Automation audit events                       | M6        | ☐      |
| 32    | LRP-503 LRP smoke E2E in CI                           | M6        | ☐      |
| 33    | LRP-504 Perf budgets                                  | M6        | ☐      |
| 34    | LRP-505 Release notes + tag `lrp-platform-v1.0.0`     | M6        | ☐      |

Deferred follow-ups (preserve queue; do not absorb informally):

| ID       | Slice                                                   | Status |
| -------- | ------------------------------------------------------- | ------ |
| LRP-208A | Evidence vault issue association + case action timeline | ☐      |
| LRP-209A | Unwanted-call complaint workflow + follow-up tracking   | ☐      |

Deferred to [product backlog](../lrp-enterprise/15-roadmap/product-backlog.md): LRP-404 educational simulator (PB-006); authenticated builder/attorney/advisor portals; full public KB depth.

---

## Slice notes

### Slice 1 — Kickoff (2026-07-26)

- Initial release plan (#378)
- Master plan remapped to M1–M6 with traceability matrix, gap analysis, DoD, exit criteria
- Living docs: backlog, roadmap, tech debt, risk register
- ADR-013 — LRP edition on shared platform

### LRP-204 — Consultation completed pack (2026-07-27)

- `POST /cases/{id}/consultation-pack/runs` creates staff-gated **draft** artifacts (readiness snapshot, illustrative timeline, action plan, status stub, partner notification draft)
- Export text/ZIP; `send_guardrails.auto_transmit=false`; partner notification stays `draft_never_sent`
- CRM borrower workspace: Generate draft pack + Download ZIP
- Migration `103_consultation_pack`; tests: `apps/api/tests/cases/test_consultation_pack.py`

### LRP-402 — Bureau + Metro2 in readiness blockers (2026-07-27)

- Lending Readiness compose (`lrs.v1.1`) adds cross-bureau mismatch + high-severity Metro 2 consistency blockers alongside tradeline blockers
- Payload includes `compliance_summary` counts (`metro2_total`, `cross_bureau_total`); advisory only — no bureau I/O or filing
- Portal readiness copy mentions bureau/Metro 2 packaging blockers
- Tests: `apps/api/tests/accounts/test_credit_analysis.py`

### LRP-401 — Readiness timeline UI (2026-07-27)

- `GET /portal/cases/{id}/timeline` composes borrower-safe milestones (case opened, published readiness, documents, completed checklist tasks); optional `?event_type=`
- `apps/lrp-web` `/portal/timeline` loads the API with type filters + deep links (no staff notes / tradeline dumps)
- Tests: `apps/api/tests/client_portal/test_portal_timeline.py`

### LRP-105 — LO notifications center live (2026-07-27)

- `apps/lrp-web` `/lender/notifications` loads platform `listNotifications` / mark-read APIs (demo seed retained for local demo auth)
- Shell badge + dashboard unread strip use `getUnreadNotificationCount` + unread list in platform mode
- Matrix-complete notification producers shipped in LRP-202

### LRP-202 — Notification matrix v1 (2026-07-27)

- Codified Section 14 matrix (`notification-matrix.v1`) with event → audience → channel routes
- Idempotent dispatch audit table `notification_matrix_dispatches` (migration `105_notification_matrix`)
- Staff APIs: `GET /notifications/matrix`, `/matrix/dispatches`, `/matrix/dispatches/{id}`
- Referral intake orchestrator fans out `referral_submitted` + `referral_assigned` via the matrix (SMS TCPA-gated; realtor optional/deferred)
- Tests: `apps/api/tests/notifications/test_notification_matrix.py` (+ referral intake coverage)

### LRP-203 — CRM automation rules persist (2026-07-27)

- Table `crm_automation_rules` (migration `106_crm_automation_rules`) with trigger/channel enums
- `GET/POST/PATCH /mortgage-partner/automation-rules` — seeds default catalog when empty; admin toggle/create
- `apps/lrp-web` `/crm/automations` loads live rules with enable/disable (demo seed fallback retained)
- Rules are configuration only — no unsupervised bureau filing or auto-execution of dispute tools
- Tests: `apps/api/tests/mortgage_partner/test_automation_rules.py`

### LRP-205 — Appointment reminders (2026-07-27)

- Tables `crm_appointments` + `appointment_reminder_runs` (migration `107_appointment_reminders`)
- Create/list/patch appointments; schedule confirmation via matrix `consultation_scheduled`
- Idempotent T-24h / T-1h reminder processor fans out through matrix events (SMS TCPA-gated)
- Staff `POST /mortgage-partner/appointments/reminders/process` + reminder audit list
- `apps/lrp-web` `/crm/calendar` loads live appointments + process-reminders action
- Tests: `apps/api/tests/mortgage_partner/test_appointment_reminders.py`

### LRP-206 — Partner nurture drip (2026-07-28)

- Tables `partner_nurture_programs` / `steps` / `enrollments` / `delivery_runs` (migration `108_partner_nurture_drip`)
- Default 5-step lender drip seeded on first list; enroll requires marketing opt-in
- Idempotent `POST /mortgage-partner/nurture/process`; SMS deferred without TCPA; email consent-gated
- Pause / resume / exit / opt-out; delivery audit history; org isolation
- `apps/lrp-web` `/crm/nurture` live enroll + process + status controls
- Tests: `apps/api/tests/mortgage_partner/test_nurture_drip.py`

### LRP-207 — Weekly status digest job (2026-07-28)

- Tables `partner_weekly_digest_subscriptions` + `partner_weekly_digest_runs` (migration `109_weekly_partner_digest`)
- Opt-in LO subscriptions; PII-minimized §6 weekly snapshot (stage counts, movement, needs attention)
- Idempotent `POST /mortgage-partner/weekly-digests/process` per subscription+ISO week; claim-safe body
- CRM archive list + `/crm/digests` subscribe/process UI
- Tests: `apps/api/tests/mortgage_partner/test_weekly_digest.py`

### LRP-106 — Readiness report in borrower portal (2026-07-27)

- `GET /portal/cases/{id}/readiness-report` + `/export?format=text|pdf` — band-first borrower report (no numeric overall score)
- `apps/lrp-web` `/portal/reports` view + PDF/text download; nav entry
- Tests: `apps/api/tests/client_portal/test_portal_readiness_report.py`

### LRP-104 — Borrower portal task/readiness parity (2026-07-27)

- `GET /portal/cases/{id}/checklist` + `PATCH /portal/checklist/{item_id}` — action plan from baseline items + published readiness blockers
- Completions persisted in `portal_checklist_completions` (migration `102_portal_checklist`)
- `/portal/tasks` shows descriptions + doc/message/readiness deep links; readiness blockers link back to tasks
- Tests: `apps/api/tests/client_portal/test_portal_checklist.py`

### LRP-107 — Case documents in CRM borrower workspace (2026-07-27)

- `apps/lrp-web` borrower workspace Documents panel lists/uploads/downloads case documents via existing Documents API
- Hooks: `useCrmCaseDocuments` / `useCrmUploadCaseDocument` / `downloadCrmDocument` (`listDocuments`, `uploadDocument`, `getDocumentDownloadUrl`)
- Upload gated by `documents.manage`; demo seed docs retained for local demo auth
- No new API endpoints (reuse platform Documents module)

### LRP-101 — CRM partners/contacts live API (2026-07-26)

- `partner_contacts` table + migration `099_partner_contacts`
- Endpoints: list/create/patch contacts under `/mortgage-partner/partnerships/{id}/contacts`
- Partnership list/get enriched with primary contact + active referral count
- `apps/lrp-web` `/crm/partners` loads live partnerships/contacts (demo fallback retained for local)
- Tests: `apps/api/tests/mortgage_partner/test_partner_contacts.py`

### LRP-108 — Kill demo-mode for production orgs (2026-07-26)

- `resolveDemoAuthEnabled` / `isDemoAuthEnabled`: always off when `NODE_ENV=production`
- CRM + lender providers clear stale demo sessions when demo auth is off
- Login forms hide demo credential hints in production
- Tests: `pnpm --filter @verdin/lrp-web test:auth`
- Docs: AUTH-REALMS.md, `.env.example`, traceability matrix

### LRP-103 — Referral intake from web form (2026-07-27)

- Public `POST /mortgage-partner/referral-intake` + `GET .../status` (requires `ENABLE_MORTGAGE_PARTNER` + `REFERRAL_INTAKE_ENABLED`)
- Creates client, intake case, partner referral (default milestones), and ops task; audit row in `partner_referral_intake_runs`
- Quarantines free-text containing SSN patterns; duplicate email/phone → `duplicate_review` + high-priority task
- `apps/lrp-web` `/resources/partner-kit/referral` posts live (optional `?partnership_id=`); thanks page at `/referral/thanks`
- Tests: `apps/api/tests/mortgage_partner/test_referral_intake.py`
- Orchestrator notifications (thank-you emails, round-robin assign) shipped in LRP-201

### LRP-201 — Referral intake orchestrator job (2026-07-27)

- Post-accept `ReferralIntakeOrchestrator`: round-robin assign among case_manager/admin/owner; in-app staff notify; consultation schedule task; thank-you email drafts (or `deferred_email_not_ready`)
- Audit table `partner_referral_intake_orchestrator_runs` (migration `104_referral_intake_orchestrator`)
- `GET /mortgage-partner/referral-intake/{intake_id}/orchestrator` staff read; intake response includes `orchestrator_run_id` + `assigned_user_id`
- Quarantined intakes skip orchestrator; no auto-filing / underwriting decisions
- Tests extended in `apps/api/tests/mortgage_partner/test_referral_intake.py`

### LRP-102 — CRM tasks + daily digest (2026-07-27)

- `GET /tasks/digest/daily` — org-scoped counts (open/overdue/due today/completed today/assigned to me) + sample item lists
- `apps/lrp-web` `/crm/tasks` loads live `listTasks` + digest strip (demo seed fallback retained)
- `@verdin/api-client` `getDailyTaskDigest`
- Tests: `test_daily_task_digest` in `apps/api/tests/tasks/test_tasks.py`
- Partner health scoring / full CRM activity taxonomy remain deferred (backlog / LRP-203+)

### LRP-109 — Production organization mode (2026-07-27)

- `organizations.organization_type` enum: `demo|internal|partner|production` (migration `100_organization_type_flags`; existing orgs default PRODUCTION; `verdin-demo` → DEMO)
- Per-org feature flags table + `/org-context` resolve path (auth → org → flags)
- Demo APIs reject PRODUCTION; `ALLOW_DEMO_ORGS` / `ENABLE_SAMPLE_DATA` / `ENABLE_DEMO_LOGIN` (forced off when `APP_ENV=production`)
- Dedicated seeds: `scripts/seed_demo/seed_demo_{org,users,borrowers,referrals}.py` (refuse production)
- CRM Admin hides Generate Demo Data / Reset Workspace for production orgs
- Tests: `apps/api/tests/org_context/test_production_org_mode.py`

### LRP-301 — Realtor partner role + login (2026-07-28)

- `PartnerRole.realtor` + limited permission matrix; migration `110_realtor_partner_role` (invites + password-reset tokens)
- Staff invite / accept / disable; public preview + password reset; `GET /mortgage-partner/realtor/me` enforces active realtor membership + partnership isolation
- `apps/lrp-web` `/realtor/*` realm: login, activate, forgot/reset password, shell + dashboard; middleware isolates from lender/CRM/portal
- Demo auth: `NEXT_PUBLIC_LRP_REALTOR_DEMO_AUTH` (off in production builds)
- Tests: `apps/api/tests/mortgage_partner/test_realtor_role_login.py`

### LRP-302 — Realtor portal MVP (2026-07-28)

- `GET /mortgage-partner/realtor/dashboard|referrals|pipeline` — partnership-scoped, PII-minimized borrower initials + coarse stage (no notes/tradelines/exports)
- `apps/lrp-web` dashboard / referrals / pipeline wired to live APIs (demo seed fallback retained)
- Capability `realtor_portal_mvp`; tests: `test_realtor_portal_mvp.py`

### LRP-303 — Borrower UAT script + fixes (2026-07-28)

- Manual UAT script: `docs/development/lrp-borrower-uat-script.md` (happy path + isolation + claim-library gates)
- Automated happy path: `apps/api/tests/client_portal/test_borrower_uat_happy_path.py` (login → me → cases → readiness → checklist → timeline → report → documents → messages + isolation)
- Fix: remove hardcoded fake portal nav badges (tasks/messages/notifications) that could mislead UAT
- Capability `borrower_uat_script`; no new API surface

### LRP-304 — LO UAT script + fixes (2026-07-28)

- Manual UAT script: `docs/development/lrp-lo-uat-script.md` (dashboard → referrals → stage → milestones → pipeline → readiness → notifications + deferred surfaces)
- Automated happy path: `apps/api/tests/mortgage_partner/test_lo_uat_happy_path.py` (referral → milestone → report + tenant isolation)
- Fixes: hide seed message threads in platform mode; admin panel clearly marked preview-only for platform UAT
- Capability `lo_uat_script`; no new API surface

### LRP-403 — Dispute strategy suggestions (advisory) (2026-07-28)

- `GET /portal/cases/{id}/dispute-strategy-suggestions` — borrower-safe projection of latest staff strategy run (`auto_send=false`, staff-mediated)
- `/portal/disputes` shows advisory suggestions (no prepare/send controls)
- Tests: `test_portal_dispute_strategy_suggestions.py`; `@verdin/api-client` helper

### LRP-208 — Case issue explainability + evidence center (2026-07-28)

- `GET /cases/{id}/issue-explainability` — plain-language cards from ranked litigation-strength findings
- Fields: what we found / why disputable / possible outcomes / evidence recommendations / finding strength + credit & mortgage impact categories
- CRO Case Workspace panel + CRM borrower workspace panel; disclaimer forbids score-point promises
- Tests: `apps/api/tests/documents/test_issue_explainability.py`; `@verdin/api-client` helper
- Follow-up: evidence vault document↔issue association, action timeline persistence
- Next planned: LRP-209 consumer communication preferences (Do Not Call guided enrollment + creditor/collector prefs; never silent third-party registration)

### LRP-209 — Consumer communication preferences (2026-07-28)

- `client_communication_preferences` table (migration `111_client_comm_prefs`)
- `GET/PUT /clients/{id}/communication-preferences` + DNC `open-registry` / `mark-completed`
- Explicit consent, phone ownership, telemarketing-limitation disclosure; never silent FTC registration
- Communication-request letter draft (staff-gated text only; never auto-sent)
- CRM borrower workspace panel; tests: `test_communication_preferences.py`

### LRP-405 — FAQ/KB retrieval bot (2026-07-28)

- Approved KB catalog + deterministic retrieval (no generative external model required)
- `POST /llm/faq-kb/ask`, conversation audit list, staff feedback
- Audience-aware answers; citations; injection/unsupported-claim refusals
- CRM `/crm/faq-assistant`; migration `112_faq_kb_retrieval`
- Tests: `apps/api/tests/llm/test_faq_kb_retrieval.py`

### LRP-406 — Intelligent Letter Draft Builder (2026-07-29)

- Template catalog (bureau/furnisher/CFPB/FTC/debt validation/goodwill/pay-for-delete/comm prefs/cease/mortgage explanation/custom)
- Deterministic sectioned drafts with fact classifications + evidence refs from LRP-208 issue cards
- Validation checklist blocks score guarantees / auto-removal promises; pay-for-delete requires “not guaranteed”
- Workflow: `ai_draft_created` → staff/client review → approved → ready_to_send; `mark-sent` records external transmission only (`auto_transmit=false`)
- `GET/POST /cases/{id}/letter-drafts`, section PATCH, validate, advance, mark-sent
- Migration `113_letter_draft_bldr`; CRO + CRM panels; Generate letter on issue cards
- Tests: `apps/api/tests/accounts/test_letter_draft_builder.py`

### LRP-305 — Planned marketing landings (2026-07-29)

- Public audience pages: `/builders`, `/attorneys`, `/advisors` (+ `/financial-planners` → `/advisors`)
- `/partners` hub chooser tiles for all audiences; footer audience links updated
- Claim-safe copy only — no approval/funding/score guarantees; advisory disclaimer on heroes
- Next planned: LRP-501 partner isolation audit; deferred LRP-208A / LRP-209A remain queued

### Definition of Done (every slice)

See release plan §6. Checklist row may be marked ✅ only when DoD items are satisfied or explicitly N/A in the PR.

---

## Verify (each implementation PR)

- `python -m pytest` for touched API tests (`DATABASE_URL` → `verdin_credit_test`)
- `pnpm --filter @verdin/api-client build` before web typecheck
- `pnpm --filter @verdin/web` and/or `@verdin/lrp-web` typecheck/lint when UI changes
- Claim-library: no approval/funding/fabricated FICO language
- No unsupervised bureau filing or dispute auto-send
- Update traceability matrix status when shipping a High/Critical row
