# Lending Readiness Platform™ — Version 1.0 Release Plan

**Master implementation document.** Every Phase 3 ops requirement traces to working software via the matrix, gap analysis, and checklist.

**Lending Readiness Partners** · Helping More Borrowers Become Lending Ready.

| Field                | Value                                                                                                                        |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Status               | `ready-for-build`                                                                                                            |
| Preceded by          | Phase 3 Ops Package (complete) · Version 29.0 foundation                                                                     |
| Apps                 | `apps/api` · `apps/lrp-web` · `apps/worker` · `apps/web`                                                                     |
| Traceability matrix  | [`v1.0-feature-traceability-matrix.md`](v1.0-feature-traceability-matrix.md)                                                 |
| Gap analysis         | [`v1.0-gap-analysis.md`](v1.0-gap-analysis.md)                                                                               |
| Executable checklist | [`../../development/lrp-platform-v1.0-completion-checklist.md`](../../development/lrp-platform-v1.0-completion-checklist.md) |
| Ops contract         | [`../04-operations/business-ops-package/`](../04-operations/business-ops-package/)                                           |
| Sprint loop          | `.cursor/rules/lrp-platform-v1-sprint-loop.mdc`                                                                              |

### Living product documents

| Document                    | Path                                                                                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Product backlog (post-V1.0) | [`product-backlog.md`](product-backlog.md)                                                                                                     |
| Release roadmap (v1.1+)     | [`release-roadmap.md`](release-roadmap.md)                                                                                                     |
| Technical debt register     | [`technical-debt-register.md`](technical-debt-register.md)                                                                                     |
| Risk register               | [`risk-register.md`](risk-register.md)                                                                                                         |
| ADRs                        | [`../../adr/`](../../adr/) · LRP edition: [`../../adr/013-lrp-edition-on-shared-platform.md`](../../adr/013-lrp-edition-on-shared-platform.md) |

---

## 1. Purpose

Phase 3 documented **how the company runs**. V1.0 turns those runbooks into **production software** on the shared Verdin monorepo — not a fork and not more parallel marketing docs.

This plan is the **single source of truth** for implementation priority until `lrp-platform-v1.0.0` is tagged.

---

## 2. Architecture lock

| Decision          | Rule                                               |
| ----------------- | -------------------------------------------------- |
| Edition, not fork | Same monorepo, API, DB, packages                   |
| LRP UI            | `apps/lrp-web` (`/`, `/portal`, `/lender`, `/crm`) |
| CRO admin         | `apps/web`                                         |
| Feature gate      | `ENABLE_MORTGAGE_PARTNER` + org partnership        |
| AI                | ADR-012 — no unsupervised filing tools             |
| Claims            | CLAIM-LIBRARY locked in all UI strings             |

---

## 3. Feature traceability (summary)

Full matrix: [`v1.0-feature-traceability-matrix.md`](v1.0-feature-traceability-matrix.md)

| Module               | Ops Spec       | Implemented | Gap                                              | Priority |
| -------------------- | -------------- | ----------- | ------------------------------------------------ | -------- |
| Partner CRM          | Section 5      | Partial     | Partner health scoring, live contacts/activities | High     |
| Borrower Portal      | Sections 2 & 7 | Partial     | Action plan UX, readiness parity                 | High     |
| Loan Officer Portal  | Sections 1 & 4 | Partial     | Referral analytics, live notifications           | High     |
| Realtor Portal       | Section 4      | Partial     | Authenticated dashboard                          | Medium   |
| Reports              | Sections 6 & 7 | Partial     | Digests + publish workflow (PDF export partial)  | High     |
| Automation           | Section 14     | Planned     | Workflow engine / orchestrators                  | High     |
| Website              | Section 12     | Partial     | Public KB & SEO                                  | Medium   |
| Auth / RBAC          | Section 5.8    | Partial     | Demo-off for prod; realtor role                  | Critical |
| Production readiness | Platform       | Partial     | Security, perf, UAT, tag                         | Critical |

---

## 4. Gap analysis

Detailed per-feature: existing implementation, missing APIs/UI/tests/docs, security, dependencies, effort — see [`v1.0-gap-analysis.md`](v1.0-gap-analysis.md).

---

## 5. Milestone-based release plan

### Milestone 1 – Core Platform

**Goal:** Auth, RBAC hardening, Partner CRM, borrower management, referral pipeline wired without demo data for production orgs.

| Slice   | Deliverable                              |
| ------- | ---------------------------------------- |
| LRP-108 | Kill demo-mode for production orgs       |
| LRP-101 | CRM partners/contacts live API           |
| LRP-102 | CRM tasks + daily digest read model      |
| LRP-103 | Referral intake from web form            |
| LRP-107 | Case documents in CRM borrower workspace |

**Exit:** Production session required for CRM/lender/portal; referral create path live; partner/borrower records not demo-only.

### Milestone 2 – Readiness

**Goal:** Readiness score, timeline, reports, action plans, notifications visible to borrower + LO + CRM.

| Slice   | Deliverable                                 |
| ------- | ------------------------------------------- |
| LRP-104 | Borrower portal task/readiness parity       |
| LRP-106 | Readiness report in borrower portal         |
| LRP-105 | LO notifications center live                |
| LRP-401 | Readiness timeline UI                       |
| LRP-402 | Bureau + Metro2 in readiness blockers       |
| LRP-204 | Consultation completed pack (staff-gated)   |
| LRP-208 | Case issue explainability + evidence center |
| LRP-209 | Consumer communication preferences          |

**Exit:** Advisory readiness report viewable/exportable with disclaimer; action plan tasks drive portal UX.

### Milestone 3 – Automation

**Goal:** Email, SMS (consented), background jobs, document packs, scheduling per Section 14.

| Slice   | Deliverable                      |
| ------- | -------------------------------- |
| LRP-201 | Referral intake orchestrator job |
| LRP-202 | Notification matrix v1           |
| LRP-203 | CRM automation rules (persist)   |
| LRP-205 | Appointment reminders            |
| LRP-206 | Partner nurture drip             |
| LRP-207 | Weekly status digest job         |

**Exit:** Referral submit triggers matrix notifications + CRM tasks idempotently; no unsupervised filing.

### Milestone 4 – Partner Experience

**Goal:** Production lender portal; realtor portal MVP; builder/attorney as marketing or backlog.

| Slice         | Deliverable                             |
| ------------- | --------------------------------------- |
| LRP-301       | Realtor partner role + login            |
| LRP-302       | Realtor portal MVP                      |
| LRP-303       | Borrower UAT script + fixes             |
| LRP-304       | LO UAT script + fixes                   |
| LRP-403       | Dispute strategy suggestions (advisory) |
| LRP-405 / 406 | Gated FAQ bot + letter draft augment    |

**Exit:** Borrower + LO UAT signed; realtor can see own referrals only. Builder/attorney **authenticated** portals → [product backlog](product-backlog.md) unless pulled in.

### Milestone 5 – Public Experience

**Goal:** Website completeness — KB, blog/stories process, FAQ, SEO, planned landings.

| Slice     | Deliverable                                         |
| --------- | --------------------------------------------------- |
| LRP-305   | Planned marketing landings (`/builders`, etc.)      |
| (backlog) | Public KB index, success-story composites, SEO pass |

**Exit:** Claim-safe public site matches Section 12 IA for V1.0 scope; KB MVP published or explicitly deferred with date.

### Milestone 6 – Production Readiness

**Goal:** Performance, security, monitoring, backups/DR, compliance review, launch tag.

| Slice   | Deliverable                               |
| ------- | ----------------------------------------- |
| LRP-501 | Partner isolation audit                   |
| LRP-502 | Automation audit events                   |
| LRP-503 | LRP smoke E2E in CI                       |
| LRP-504 | Perf budgets                              |
| LRP-505 | Release notes + tag `lrp-platform-v1.0.0` |

**Exit:** All V1.0 exit criteria below checked.

---

## 6. Definition of Done (every feature / slice)

A slice is **Done** only when:

- [ ] Backend API implemented (or explicitly N/A)
- [ ] UI complete for the stated audience (or explicitly N/A)
- [ ] Unit tests passing for new logic
- [ ] Integration / API tests passing for new endpoints
- [ ] Accessibility validated for new interactive UI (keyboard + labels)
- [ ] Documentation updated (`docs/api/reference.md`, capability matrix, checklist)
- [ ] Security implications reviewed (tenant scope, consent, PII)
- [ ] Claim-library check for user-visible copy
- [ ] Product Owner approval (or documented owner sign-off in PR)
- [ ] Ready for production (no demo-only path for the feature)

---

## 7. V1.0 exit criteria

Before declaring Version 1.0 complete:

- [ ] All **Critical** and **High** rows in the traceability matrix are **Shipped** (or explicitly waived with PO + compliance sign-off)
- [ ] All required CI/CD checks passing on `main`
- [ ] No open **blocker** defects
- [ ] Security review complete (partner isolation + auth) — automated denial suite shipped (LRP-501); formal officer sign-off open
- [x] Performance targets documented + observe harness in CI (dashboard + readiness export p95; LRP-504)
- [x] UAT sign-off received (borrower + LO; realtor if MVP in scope) — LRP-303 / LRP-304
- [ ] Production deployment checklist completed
- [ ] Operations handoff completed (runbooks → on-call + §14 job map) — LRP DR runbook open
- [x] Tag `lrp-platform-v1.0.0` + release notes published

---

## 8. Explicit non-goals (V1.0)

| Item                                           | Defer                             |
| ---------------------------------------------- | --------------------------------- |
| Live bureau soft-pull for lenders              | Never\*                           |
| Unsupervised dispute filing                    | Never\*                           |
| Cross-tenant marketplace                       | Never                             |
| Forked Mortgage codebase                       | Never                             |
| Full white-label custom domains                | v1.1+                             |
| LOS deep sync                                  | v1.1+                             |
| Authenticated builder/attorney/advisor portals | v1.1 (backlog) unless prioritized |

---

## 9. After V1.0 — product lifecycle

Maintain these living documents (do not let them go stale):

1. [Product backlog](product-backlog.md)
2. [Release roadmap](release-roadmap.md)
3. [Technical debt register](technical-debt-register.md)
4. [Risk register](risk-register.md)
5. [ADRs](../../adr/) for durable decisions

---

## 10. How to execute

1. Pick next unchecked slice from the [completion checklist](../../development/lrp-platform-v1.0-completion-checklist.md).
2. One LRP-xxx ID per PR; satisfy Definition of Done.
3. Update traceability matrix status when merging.
4. Prefer extending `mortgage_partner`, `clients`, `notifications`, `documents`, `llm`.

**Success:** A lender refers a borrower; staff runs the case in CRM; the borrower completes tasks; an advisory readiness report is shared; partners see progress; automations notify the right people — without demo data and without unsupervised filing.
