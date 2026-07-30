# Release Notes — Lending Readiness Platform™ V1.0.0

**Edition:** Lending Readiness Platform™ (LRP) on the shared Verdin monorepo  
**Tag:** `lrp-platform-v1.0.0`  
**Date:** 2026-07-30  
**Checklist:** [`docs/development/lrp-platform-v1.0-completion-checklist.md`](../development/lrp-platform-v1.0-completion-checklist.md)

## Summary

`lrp-platform-v1.0.0` marks **feature-complete delivery** of the LRP Platform V1.0 checklist (LRP-101 through LRP-505, plus charter). The edition ships as a **shared-platform Mortgage Partner / lending-readiness surface** — not a forked product — with staff-mediated workflows, claim-safe marketing, and explicit non-goals for unsupervised bureau filing and live soft-pulls.

This tag is the implementation closeout for the V1.0 slice list. Formal security-officer sign-off and LRP-specific DR runbook remain tracked as post-tag operations items (see Known remaining).

## Highlights by milestone

| Milestone            | What shipped                                                                                                                                                                |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **M1 Core platform** | Demo auth kill-switch; production org mode; CRM partners/contacts; tasks + daily digest; referral web intake; CRM case documents                                            |
| **M2 Readiness**     | Portal checklist/tasks; readiness report + timeline; LO notifications; bureau/Metro2 blockers; consultation completed pack; issue explainability; communication preferences |
| **M3 Automation**    | Referral intake orchestrator; notification matrix; CRM automation rules; appointments/reminders; nurture drip; weekly partner digests                                       |
| **M4 Partner UX**    | Realtor role + portal MVP; borrower/LO UAT scripts; advisory dispute strategy; FAQ/KB retrieval; intelligent letter drafts                                                  |
| **M5 Public**        | Claim-safe landings for builders, attorneys, advisors (+ financial-planners alias); partners hub tiles                                                                      |
| **M6 Production**    | Partner isolation denial suite; automation audit events; LRP smoke E2E in CI; perf budgets (observe); **this release + tag**                                                |

## Production readiness (M6)

| Slice   | Deliverable                                                                                      |
| ------- | ------------------------------------------------------------------------------------------------ |
| LRP-501 | Cross-tenant partner isolation denial suite                                                      |
| LRP-502 | Durable CRM automation audit events + staff dry-run/fire                                         |
| LRP-503 | `tests/e2e/test_lrp_smoke.py` in `.github/workflows/e2e.yml` with `ENABLE_MORTGAGE_PARTNER=true` |
| LRP-504 | Product p95 budgets + observe harness (`docs/quality/performance/lrp-v1-perf-budgets.md`)        |
| LRP-505 | These release notes + Git tag / GitHub Release `lrp-platform-v1.0.0`                             |

## Explicit non-goals (unchanged)

- Live bureau soft-pull for lenders
- Unsupervised dispute filing / auto-transmit of letters
- Cross-tenant marketplace / partner JWT realm
- Forked Mortgage codebase
- Full white-label custom domains (v1.1+)

## Deferred follow-ups

| ID        | Item                                   | Notes                                                                                                 |
| --------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| LRP-208A  | Evidence vault depth                   | ✅ Delivered in [`lrp-platform-v1.1.0`](lrp-platform-v1.1.0.md) (#414 / #415)                         |
| LRP-209A  | Unwanted-call complaint workflow       | ✅ Delivered in [`lrp-platform-v1.1.0`](lrp-platform-v1.1.0.md) (#416)                                |
| Ops       | Formal security review sign-off        | Package ready — signature open ([sign-off](../quality/security/lrp-v1.0-security-officer-signoff.md)) |
| Ops       | LRP edition DR / backup runbook        | Drafted — restore drill open ([runbook](../deployment/lrp-v1.0-disaster-recovery-runbook.md))         |
| Hardening | Post-release checklist                 | [`lrp-v1.0-post-release-hardening.md`](../development/lrp-v1.0-post-release-hardening.md)             |
| Perf      | Hard CI enforcement of LRP p95 budgets | Observe-only until CI variance calibrated                                                             |

## Related documents

- [V1.0 release plan](../lrp-enterprise/15-roadmap/lending-readiness-platform-v1.0-release-plan.md)
- [Feature traceability matrix](../lrp-enterprise/15-roadmap/v1.0-feature-traceability-matrix.md)
- [Gap analysis](../lrp-enterprise/15-roadmap/v1.0-gap-analysis.md)
- [Completion checklist](../development/lrp-platform-v1.0-completion-checklist.md)
- [Capability matrix](../governance/capability-matrix.md)
- [API reference](../api/reference.md)
- [LRP perf budgets](../quality/performance/lrp-v1-perf-budgets.md)
- [E2E strategy](../quality/testing/e2e-strategy.md)
- [Security officer sign-off package](../quality/security/lrp-v1.0-security-officer-signoff.md)
- [LRP DR runbook](../deployment/lrp-v1.0-disaster-recovery-runbook.md)
- [Post-release hardening](../development/lrp-v1.0-post-release-hardening.md)
