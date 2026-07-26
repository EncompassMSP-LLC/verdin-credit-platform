# Lending Readiness Platform™ — Version 1.0 Release Plan

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field                | Value                                                                                                                        |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Status               | `ready-for-build`                                                                                                            |
| Preceded by          | Phase 3 Business Ops Package (signed off) · Version 29.0 foundation slices                                                   |
| Target               | Production-capable LRP edition on shared monorepo                                                                            |
| Apps                 | `apps/api` · `apps/lrp-web` · `apps/worker` · `apps/web` (CRO admin)                                                         |
| Executable checklist | [`../../development/lrp-platform-v1.0-completion-checklist.md`](../../development/lrp-platform-v1.0-completion-checklist.md) |
| Ops contract         | [`../04-operations/business-ops-package/`](../04-operations/business-ops-package/)                                           |
| Claim library        | [`../build-bible/CLAIM-LIBRARY.md`](../build-bible/CLAIM-LIBRARY.md)                                                         |

---

## 1. Purpose

Phase 3 documented **how the company runs**. Version 1.0 turns those runbooks into **working software** on the existing Verdin platform — not a product fork and not more parallel documentation.

This plan:

1. Maps every major ops requirement to a platform module
2. Records **shipped / partial / missing** vs today
3. Sequences work into milestones with acceptance criteria and test plans
4. Keeps compliance gates (advisory readiness, staff-mediated disputes, no unsupervised bureau filing)

---

## 2. Architecture lock (non-negotiable)

| Decision          | Rule                                                           |
| ----------------- | -------------------------------------------------------------- |
| Edition, not fork | Same monorepo, API, DB, packages                               |
| LRP UI            | Prefer `apps/lrp-web` (`/`, `/portal`, `/lender`, `/crm`)      |
| CRO admin         | `apps/web` for staff operations already on Verdin              |
| Feature gate      | `ENABLE_MORTGAGE_PARTNER` (+ org partnership)                  |
| AI                | ADR-012 / `require_llm_ready()` — no unsupervised filing tools |
| Marketing claims  | Claim-library locked in all UI strings                         |

---

## 3. Capability gap matrix

Legend: **Shipped** = live API + primary UI path · **Partial** = UI and/or API exists with demo fallback / scaffold · **Missing** = spec only or stub · **Deferred** = out of V1.0 / never

### 3.1 Core modules (Phase 4.1)

| Module                    | Ops source      | Today                                                                                                                                    | V1.0 target                                                        |
| ------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Partner CRM               | §5, §14         | **Partial** — `/crm/*` routes; borrowers/referrals wired to clients/mortgage APIs; much of partners/pipeline/automations still demo data | Live CRM for partners, contacts, activities, tasks, health score   |
| Borrower Portal           | §2, §12, §14    | **Partial** — `/portal/*` with platform auth; docs/messages/analysis hooks; some screens still thin                                      | Production portal: tasks, docs, readiness, messages, notifications |
| Loan Officer Portal       | §1, §4, §6      | **Partial** — `/lender/*` dashboard/pipeline/readiness live; messages/docs often demo-mode                                               | Full LO book: referrals, milestones, reports, notifications        |
| Realtor Portal            | §12 landings    | **Missing** as authenticated product (public `/realtors` marketing only)                                                                 | Partner-scoped realtor workspace (own referrals + progress)        |
| Admin Dashboard           | CRO + CRM admin | **Partial** — `apps/web` + `/crm/admin` scaffolds                                                                                        | Org settings, RBAC, automation toggles, audit views                |
| Case Management           | Verdin core     | **Shipped** — cases/accounts/documents in API; CRM/portal consume selectively                                                            | LRP surfaces fully wired to case lifecycle                         |
| Mortgage Readiness Engine | §7, v29 slice 4 | **Partial** — readiness report + export APIs + lender UI                                                                                 | Dimensions, timeline, blockers, export consistently in portal + LO |
| Report Generation         | §6, §7          | **Partial** — readiness/credit-analysis export; status digests not automated                                                             | Staff-gated publish + partner/borrower distribution                |
| Referral Tracking         | §4, §14         | **Partial** — partner referrals + pipeline stages; intake orchestrator not wired                                                         | End-to-end referral form → assign → pipeline → notify              |
| Notification Center       | §14             | **Partial** — notifications module + portal/lender pages; matrix not fully implemented                                                   | Matrix-complete email/in-app (+ SMS where consented)               |

### 3.2 Automation (Phase 4.2)

| Capability             | Today                                                       | V1.0                                             |
| ---------------------- | ----------------------------------------------------------- | ------------------------------------------------ |
| Email workflows        | Notifications + templates exist; LRP drips not orchestrated | Partner lead + referral + consultation sequences |
| SMS workflows          | SMS campaign/deliverability workers exist                   | TCPA-gated appointment + task nudges             |
| Appointment scheduling | CRM calendar UI scaffold                                    | Book/remind/complete → consultation pack         |
| Document generation    | Worker OCR/classify/parse; letter lifecycle in API          | Staff-gated packs; no auto-file                  |
| Status report jobs     | Reporting MV refresh exists                                 | Weekly/monthly digests per §6/§14                |
| CRM task automation    | Automations page is **demo scaffold**                       | Rule engine for §14 CRM triggers                 |
| Referral routing       | Manual / API create                                         | Intake orchestrator (atomic checklist)           |
| AI assistant           | LLM module gated; portal AI analysis partial                | FAQ/KB bot + portal helper (read-only tools)     |
| Scheduled jobs         | Worker registry                                             | Digests, nurture, SLA escalation jobs            |

### 3.3 Audience portals (Phase 4.3)

| Audience                        | Today                                | V1.0                                                      |
| ------------------------------- | ------------------------------------ | --------------------------------------------------------- |
| Borrowers                       | Partial portal                       | Production-ready                                          |
| Loan officers                   | Partial lender app                   | Production-ready                                          |
| Realtors                        | Marketing only                       | Authenticated partner portal (MVP)                        |
| Builders / attorneys / advisors | Marketing specs (§12 planned routes) | **Deferred** to V1.1 unless partnership demand forces MVP |
| Internal staff                  | CRM + `apps/web`                     | CRM production + CRO admin unchanged                      |

### 3.4 Intelligence (Phase 4.4)

| Capability                   | Today                            | V1.0                                                          |
| ---------------------------- | -------------------------------- | ------------------------------------------------------------- |
| Readiness Score              | Partial (partner report)         | Canonical advisory score in portal + LO + CRM                 |
| Readiness Timeline           | Spec / report fields             | First-class timeline UI                                       |
| Bureau comparison            | **Shipped** in CRO stack         | Surface in LRP case/readiness views                           |
| Metro 2 analysis             | **Shipped** in CRO stack         | Surface findings in readiness blockers                        |
| Dispute strategy engine      | Staff-mediated dispute lifecycle | Advisory suggestions only; staff approve send                 |
| Credit simulation            | Limited / analysis runs          | Read-only “what-if” educational simulator (no score promises) |
| Loan qualification estimator | Spec / readiness dimensions      | Advisory estimator — **not** underwriting                     |

### 3.5 AI layer (Phase 4.5)

| Assistant              | V1.0 scope                                     |
| ---------------------- | ---------------------------------------------- |
| Borrower assistant     | Portal helper: tasks, KB, next steps on file   |
| Partner assistant      | LO/realtor: status explanation + kit links     |
| Employee copilot       | CRM: SOP/KB retrieval (no silent mutations)    |
| Letter drafting        | Augment drafts only; staff review/approve/send |
| Credit report analysis | Existing analysis + export paths               |
| KB search              | Index §12 KB + FAQs                            |
| SOP guidance           | Retrieve ops package / training docs           |

### 3.6 Production readiness (Phase 4.6)

| Area            | V1.0 bar                                     |
| --------------- | -------------------------------------------- |
| Security review | Auth paths, partner isolation, portal upload |
| Audit logging   | Referral/automation/report publish events    |
| RBAC validation | Partner / realtor / borrower / CRM roles     |
| Performance     | p95 budgets on dashboard + readiness export  |
| Backup / DR     | Inherit platform standards; document RPO/RTO |
| Monitoring      | Worker failures, notification deliverability |
| Deploy pipeline | Existing CI; LRP smoke E2E                   |
| UAT             | Scripted partner + borrower journeys         |

---

## 4. Milestone plan

| Milestone | Phase     | Goal                             | Exit criteria                                                                                      |
| --------- | --------- | -------------------------------- | -------------------------------------------------------------------------------------------------- |
| **M1**    | 4.1       | Core modules production-wired    | Gap matrix “Partial → Shipped” for CRM, portals (borrower+LO), referrals, readiness, notifications |
| **M2**    | 4.2       | Automation workflows             | Referral orchestrator + notification matrix + CRM task rules + consultation pack                   |
| **M3**    | 4.3       | Partner + borrower portal launch | Realtor MVP portal; borrower/LO UAT pass; marketing landings claim-safe                            |
| **M4**    | 4.4 + 4.5 | Intelligence + AI                | Timeline + bureau/Metro2 in LRP UI; gated assistants; no filing tools                              |
| **M5**    | 4.6       | Production hardening             | Security/RBAC/audit/perf/UAT; tag `lrp-platform-v1.0.0`                                            |

Suggested sequencing: **M1 → M2 → M3** in series; **M4** starts after M1 readiness surfaces are stable; **M5** runs continuously and gates launch.

---

## 5. Prioritized backlog (implementation slices)

One PR-sized slice per row. Prefer wiring existing APIs over new schemas.

### M1 — Core platform

| ID      | Slice                                    | Acceptance criteria                                                          | Tests           |
| ------- | ---------------------------------------- | ---------------------------------------------------------------------------- | --------------- |
| LRP-101 | CRM partners/contacts live API           | Replace demo partners list with org/contact APIs; activity create            | API + CRM UI    |
| LRP-102 | CRM tasks + daily digest read model      | Overdue/today queues match §5 daily workflow                                 | API + CRM       |
| LRP-103 | Referral intake from web form            | `/resources/partner-kit/referral` → partner referral + CRM activity + notify | API e2e         |
| LRP-104 | Borrower portal task/readiness parity    | Tasks + readiness score from case; no demo when authed                       | Portal e2e      |
| LRP-105 | LO notifications center live             | Matrix rows for referral/status use notifications API                        | API + lender UI |
| LRP-106 | Readiness report in borrower portal      | View/export advisory report with disclaimer                                  | Portal + API    |
| LRP-107 | Case documents in CRM borrower workspace | Upload/list via documents API                                                | CRM + API       |
| LRP-108 | Kill demo-mode for production orgs       | Feature flag: demo fallback off when platform session                        | Unit + e2e      |

### M2 — Automation

| ID      | Slice                            | Acceptance criteria                                                  | Tests        |
| ------- | -------------------------------- | -------------------------------------------------------------------- | ------------ |
| LRP-201 | Referral intake orchestrator job | Atomic checklist §14 referral automation                             | Worker + API |
| LRP-202 | Notification matrix v1           | Partner Success / CS / LO / borrower channels for referral + consult | Integration  |
| LRP-203 | CRM automation rules (persist)   | Replace demo automations table with stored rules                     | API + CRM    |
| LRP-204 | Consultation completed pack      | Draft readiness/timeline/action plan; staff gate before partner send | API          |
| LRP-205 | Appointment reminders            | Email + optional SMS (consent) T-24h / T-1h                          | Worker       |
| LRP-206 | Partner nurture drip             | §14 email sequence; stop on Active/unsubscribe                       | Worker       |
| LRP-207 | Weekly status digest job         | §6 weekly fields to opted-in LOs                                     | Worker       |

### M3 — Portals

| ID      | Slice                             | Acceptance criteria                              | Tests         |
| ------- | --------------------------------- | ------------------------------------------------ | ------------- |
| LRP-301 | Realtor partner role + login      | RBAC: own referrals only                         | API           |
| LRP-302 | Realtor portal MVP                | Dashboard, referrals, progress, messages         | e2e           |
| LRP-303 | Borrower UAT script + fixes       | Journey: invite → tasks → docs → report          | UAT checklist |
| LRP-304 | LO UAT script + fixes             | Journey: referral → milestone → report           | UAT checklist |
| LRP-305 | Planned landings `/builders` etc. | Marketing pages per §12 (auth portal still V1.1) | Web           |

### M4 — Intelligence + AI

| ID      | Slice                                 | Acceptance criteria                     | Tests           |
| ------- | ------------------------------------- | --------------------------------------- | --------------- |
| LRP-401 | Readiness timeline UI                 | Portal + LO + CRM share model           | UI + API        |
| LRP-402 | Bureau + Metro2 in readiness blockers | Reuse CRO findings; advisory copy       | API             |
| LRP-403 | Dispute strategy suggestions          | Advisory only; no auto-send             | API             |
| LRP-404 | Educational credit simulator          | Explicitly not a score/approval promise | UI              |
| LRP-405 | FAQ/KB retrieval bot                  | Public + portal; escalate to human      | LLM-gated tests |
| LRP-406 | Letter draft augment                  | Staff must approve before send          | API             |

### M5 — Production

| ID      | Slice                   | Acceptance criteria                        | Tests          |
| ------- | ----------------------- | ------------------------------------------ | -------------- |
| LRP-501 | Partner isolation audit | Cross-tenant tests for referrals/readiness | Security tests |
| LRP-502 | Automation audit events | Every orchestrator write audited           | API            |
| LRP-503 | LRP smoke E2E in CI     | Login + referral + readiness happy paths   | CI             |
| LRP-504 | Perf budgets            | Dashboard + export p95 documented          | Perf harness   |
| LRP-505 | Release notes + tag     | `lrp-platform-v1.0.0`                      | Docs           |

---

## 6. Mapping to your Phase 4.x framing

| Your phase                          | This plan                           |
| ----------------------------------- | ----------------------------------- |
| 4.1 Platform feature completion     | **M1**                              |
| 4.2 Automation implementation       | **M2**                              |
| 4.3 Client & partner portals        | **M3** (+ borrower/LO finish in M1) |
| 4.4 Mortgage readiness intelligence | **M4** (intelligence)               |
| 4.5 AI layer                        | **M4** (AI)                         |
| 4.6 Production readiness            | **M5**                              |

---

## 7. Explicit non-goals (V1.0)

| Item                                            | Defer        |
| ----------------------------------------------- | ------------ |
| Live bureau soft-pull for lenders               | Never\*      |
| Unsupervised dispute filing / bureau submission | Never\*      |
| Cross-tenant marketplace                        | Never        |
| Forked Mortgage codebase                        | Never        |
| Full white-label custom domains                 | V1.1 / 30.0+ |
| LOS deep sync (Encompass, etc.)                 | V1.1 / 30.0+ |
| Authenticated builder/attorney/advisor portals  | V1.1         |
| Guaranteed-approval or fabricated FICO UX       | Never        |

---

## 8. How to execute

1. Use [`lrp-platform-v1.0-completion-checklist.md`](../../development/lrp-platform-v1.0-completion-checklist.md) as the sprint board.
2. One checklist slice per PR (API + tests + api-client + `lrp-web` as needed).
3. Prefer extending existing modules (`mortgage_partner`, `clients`, `notifications`, `documents`, `llm`).
4. Demo fallback allowed in dev only; production orgs must use platform session (LRP-108).
5. Update capability matrix + API reference when shipping user-visible surfaces.

---

## 9. Success definition — LRP Platform V1.0

A lender can refer a borrower, staff can run the case in CRM, the borrower completes tasks in the portal, an advisory readiness report is shared, partners see progress, and automations notify the right people — **without** demo data, **without** unsupervised filing, and **with** claim-safe language throughout.
