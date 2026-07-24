# Version 29.0 Completion Checklist

Ordered path for **Mortgage Partner Edition (foundation)** and follow-on governance work.

Preceded by shipped **v28.0.0**. Target tag: **v29.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-29.0-scope.md`](../governance/version-29.0-scope.md)

## Exit criteria for "29.0 done"

- [x] Lender/partner org model + RBAC + `ENABLE_MORTGAGE_PARTNER` gate
- [x] Lender dashboard with client pipeline + loan milestones (shared case data)
- [ ] Mortgage readiness estimator + exportable readiness report
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented (no fork; no live bureau; no cross-tenant marketplace)
- [ ] `docs/release-notes/v29.0.0.md` + tag `v29.0.0`

---

## Phase 1 — Recommended order

| Order | Slice                                              | Epic         | Status |
| ----- | -------------------------------------------------- | ------------ | ------ |
| 1     | 29.0 scope + completion checklist                  | Kickoff      | ✅     |
| 2     | Partner org model + lender RBAC + feature flag     | Platform     | ✅     |
| 3     | Lender dashboard + pipeline + loan milestones      | Partner UI   | ✅     |
| 4     | Mortgage readiness score + readiness report export | Intelligence | ✅     |
| 5     | Capability matrix 29.0 sign-off                    | Governance   | ☐      |

Architecture rule: **edition on the shared platform** — same monorepo/API. Do not clone the product. Optional `apps/lender-web` only if UX divergence requires it.

---

## Slice 3 implementation notes (2026-07-23)

- Migration `097_partner_loan_pipeline`: `loan_pipeline_stage` enum + `pipeline_stage` / `pipeline_stage_changed_at` columns on `partner_referrals`; `partner_loan_milestones` table; `pipeline_view`, `pipeline_update`, `milestone_update` enum values on `partner_access_action`.
- New endpoints: `GET /partnerships/{id}/pipeline`, `GET /partnerships/{id}/dashboard-summary`, `GET/PUT /partnerships/{id}/referrals/{rid}/milestones`.
- Default milestone checklist (5 items) seeded on referral create.
- `PartnerReferralUpdate` now accepts optional `pipeline_stage` (at least one of status/stage/notes required).
- `@verdin/api-client` updated: `LoanPipelineStage`, `PipelineCard`, `PartnerDashboardSummary`, `PartnerLoanMilestone`, `getPartnershipPipeline`, `getPartnerDashboardSummary`, `listReferralMilestones`, `replaceReferralMilestones`.
- `apps/lrp-web` partner-hooks extended with `useLenderPipeline`, `useLenderDashboardSummary`, `useReferralMilestones`, `useReplaceReferralMilestones`; pipeline and dashboard pages wired to live API with demo fallback.

---

## Slice 4 implementation notes (2026-07-24)

- Migration `098_partner_readiness_actions`: adds `readiness_view` and `readiness_export` enum values to `partner_access_action` (idempotent `ADD VALUE IF NOT EXISTS`).
- New `PartnerAccessAction` enum values: `READINESS_VIEW`, `READINESS_EXPORT`.
- `credit_analysis_export.py` (new): pure formatter → `build_credit_analysis_text`, `build_credit_analysis_pdf_bytes`, `build_credit_analysis_export`, `export_filename`, `sanitize_content_disposition_filename`. ADVISORY_DISCLAIMER always leads every export.
- Cases router: `GET /cases/{case_id}/credit-analysis/runs/{run_id}/export?export_format=text|pdf` — operator-gated, disclaimer prominent, never auto-transmitted.
- `CreditAnalysisService.export_run()` wires the cases export.
- Partner readiness schemas: `ReadinessDimension`, `ReadinessBlocker`, `ReadinessPriorityTask`, `MortgageReadinessReportResponse`, `ReadinessReportSummary`.
- `MortgagePartnerRepository`: `get_latest_published_run_for_case`, `list_referrals_with_case`.
- `MortgagePartnerService`: `get_readiness_report`, `export_readiness_report`, `list_readiness_reports`; `get_status` adds `partner_readiness_report` + `partner_readiness_export` capabilities.
- New endpoints:
  - `GET /mortgage-partner/partnerships/{id}/readiness-reports` (list summaries)
  - `GET /mortgage-partner/partnerships/{id}/referrals/{rid}/readiness-report` (full JSON)
  - `GET /mortgage-partner/partnerships/{id}/referrals/{rid}/readiness-report/export?format=text|pdf`
- `@verdin/api-client` `mortgagePartner.ts`: `MortgageReadinessReport`, `ReadinessReportSummary`, `ReadinessDimension`, `ReadinessBlocker`, `ReadinessPriorityTask`, `listPartnershipReadinessReports`, `getReferralReadinessReport`, `getReferralReadinessReportExportUrl`; `PartnerAccessAction` extended.
- `apps/lrp-web`: `lib/lender/readiness-hooks.ts` (new); readiness page wired to live API with demo fallback.
- Tests: `tests/accounts/test_credit_analysis_export.py` (13 tests), `tests/mortgage_partner/test_readiness_report.py` (13 tests). All 26 pass.

---

## Explicitly not 29.0 (→ 30.0+ / never)

| Capability                                     | Version | Why defer                           |
| ---------------------------------------------- | ------- | ----------------------------------- |
| Custom partner domains / full white-label SaaS | 30.0+   | Theme + logo first                  |
| LOS deep sync (Encompass, etc.)                | 30.0+   | Prove partner dashboard value first |
| Consumer mortgage application portal           | 30.0+   | Lender/CRO surfaces first           |
| Live bureau soft-pull for lenders              | Never\* | Compliance gate unchanged           |
| Automated filing / unsupervised loops          | Never\* | Platform policy unchanged           |
| Cross-tenant lender marketplace                | Never   | Applicant data isolation            |
| Forked separate Mortgage codebase              | Never   | Maintenance and compliance cost     |

\*Unless a future compliance-approved program revisits these gates.
