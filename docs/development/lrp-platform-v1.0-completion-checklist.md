# Lending Readiness Platform™ V1.0 — Completion Checklist

Executable slices for building the platform from the Phase 3 ops package.

Master plan: [`../lrp-enterprise/15-roadmap/lending-readiness-platform-v1.0-release-plan.md`](../lrp-enterprise/15-roadmap/lending-readiness-platform-v1.0-release-plan.md)

Sprint loop: `.cursor/rules/lrp-platform-v1-sprint-loop.mdc`

Ops contract: [`../lrp-enterprise/04-operations/business-ops-package/`](../lrp-enterprise/04-operations/business-ops-package/)

## Exit criteria for "LRP Platform V1.0 done"

- [ ] M1 core modules production-wired (CRM, borrower portal, LO portal, referrals, readiness, notifications)
- [ ] M2 automation workflows live (orchestrator, matrix, CRM rules, consultation pack, digests)
- [ ] M3 partner/borrower portal UAT passed (incl. realtor MVP)
- [ ] M4 intelligence + gated AI assistants shipped
- [ ] M5 production hardening + tag `lrp-platform-v1.0.0`
- [ ] Capability matrix + API reference updated for LRP V1.0 surfaces
- [ ] No unsupervised bureau filing; claim-library locked in UI

---

## Recommended order

| Order | Slice                                                 | Milestone | Status |
| ----- | ----------------------------------------------------- | --------- | ------ |
| 1     | Charter — this checklist + release plan               | Kickoff   | ✅     |
| 2     | LRP-101 CRM partners/contacts live API                | M1        | ☐      |
| 3     | LRP-102 CRM tasks + daily digest read model           | M1        | ☐      |
| 4     | LRP-103 Referral intake from web form                 | M1        | ☐      |
| 5     | LRP-104 Borrower portal task/readiness parity         | M1        | ☐      |
| 6     | LRP-105 LO notifications center live                  | M1        | ☐      |
| 7     | LRP-106 Readiness report in borrower portal           | M1        | ☐      |
| 8     | LRP-107 Case documents in CRM borrower workspace      | M1        | ☐      |
| 9     | LRP-108 Kill demo-mode for production orgs            | M1        | ☐      |
| 10    | LRP-201 Referral intake orchestrator job              | M2        | ☐      |
| 11    | LRP-202 Notification matrix v1                        | M2        | ☐      |
| 12    | LRP-203 CRM automation rules (persist)                | M2        | ☐      |
| 13    | LRP-204 Consultation completed pack                   | M2        | ☐      |
| 14    | LRP-205 Appointment reminders                         | M2        | ☐      |
| 15    | LRP-206 Partner nurture drip                          | M2        | ☐      |
| 16    | LRP-207 Weekly status digest job                      | M2        | ☐      |
| 17    | LRP-301 Realtor partner role + login                  | M3        | ☐      |
| 18    | LRP-302 Realtor portal MVP                            | M3        | ☐      |
| 19    | LRP-303 Borrower UAT script + fixes                   | M3        | ☐      |
| 20    | LRP-304 LO UAT script + fixes                         | M3        | ☐      |
| 21    | LRP-305 Planned marketing landings (`/builders` etc.) | M3        | ☐      |
| 22    | LRP-401 Readiness timeline UI                         | M4        | ☐      |
| 23    | LRP-402 Bureau + Metro2 in readiness blockers         | M4        | ☐      |
| 24    | LRP-403 Dispute strategy suggestions (advisory)       | M4        | ☐      |
| 25    | LRP-404 Educational credit simulator                  | M4        | ☐      |
| 26    | LRP-405 FAQ/KB retrieval bot                          | M4        | ☐      |
| 27    | LRP-406 Letter draft augment (staff-gated)            | M4        | ☐      |
| 28    | LRP-501 Partner isolation audit                       | M5        | ☐      |
| 29    | LRP-502 Automation audit events                       | M5        | ☐      |
| 30    | LRP-503 LRP smoke E2E in CI                           | M5        | ☐      |
| 31    | LRP-504 Perf budgets                                  | M5        | ☐      |
| 32    | LRP-505 Release notes + tag `lrp-platform-v1.0.0`     | M5        | ☐      |

---

## Slice notes

### Slice 1 — Kickoff (2026-07-26)

- Release plan with gap matrix (shipped / partial / missing)
- Milestone map M1–M5 aligned to Phase 4.1–4.6
- Backlog IDs LRP-101…LRP-505 with acceptance criteria

---

## Verify (each implementation PR)

- `python -m pytest` for touched API tests (`DATABASE_URL` → `verdin_credit_test`)
- `pnpm --filter @verdin/api-client build` before web typecheck
- `pnpm --filter @verdin/web` and/or `@verdin/lrp-web` typecheck/lint when UI changes
- Claim-library: no approval/funding/fabricated FICO language
- No unsupervised bureau filing or dispute auto-send
