# Phase 3 — Business Operations Package

Lending Readiness Partners (LRP) operating system for a **lender-ready organization**: onboarding, intake, compliance, referral ops, CRM, reporting, sales enablement, marketing scale, and automation specs.

This is **company operations**, not marketing fluff. Manuscripts here are claim-library locked and counsel-review gated where legal.

| Field                 | Value                                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Brand                 | Lending Readiness Partners (LRP)                                                                                        |
| Tagline               | Helping More Borrowers Become Lending Ready.                                                                            |
| Claim library         | [`../../build-bible/CLAIM-LIBRARY.md`](../../build-bible/CLAIM-LIBRARY.md)                                              |
| Checklist             | [`00-completion-checklist.md`](00-completion-checklist.md)                                                              |
| Sign-off              | [`99-ops-package-signoff.md`](99-ops-package-signoff.md)                                                                |
| Phase 4 handoff       | [`phase-4-handoff.md`](phase-4-handoff.md)                                                                              |
| Marketing kit (prior) | [`../build-bible/volumes/07-marketing-launch/partner-kit/`](../../build-bible/volumes/07-marketing-launch/partner-kit/) |
| Office binaries       | [`../../../../assets/lrp/marketing-package/v2/`](../../../../assets/lrp/marketing-package/v2/)                          |
| Platform (Phase 4)    | Version 29.0+ Mortgage Partner Edition — `apps/api` + `apps/lrp-web`                                                    |
| Package status        | **COMPLETE** (Sections 1–14 + sign-off)                                                                                 |

## Sections

| #   | Section                    | Path                                                                 |
| --- | -------------------------- | -------------------------------------------------------------------- |
| 1   | Partner Onboarding Kit     | [`section-01-partner-onboarding/`](section-01-partner-onboarding/)   |
| 2   | Client Intake Package      | [`section-02-client-intake/`](section-02-client-intake/)             |
| 3   | Compliance Package         | [`section-03-compliance/`](section-03-compliance/)                   |
| 4   | Referral Management System | [`section-04-referral-management/`](section-04-referral-management/) |
| 5   | CRM Package                | [`section-05-crm/`](section-05-crm/)                                 |
| 6   | Status Reports             | [`section-06-status-reports/`](section-06-status-reports/)           |
| 7   | Mortgage Readiness Reports | [`section-07-readiness-reports/`](section-07-readiness-reports/)     |
| 8   | Presentation Package       | [`section-08-presentations/`](section-08-presentations/)             |
| 9   | Sales Package              | [`section-09-sales/`](section-09-sales/)                             |
| 10  | Marketing Expansion        | [`section-10-marketing-expansion/`](section-10-marketing-expansion/) |
| 11  | Print Marketing            | [`section-11-print/`](section-11-print/)                             |
| 12  | Website                    | [`section-12-website/`](section-12-website/)                         |
| 13  | Video Marketing            | [`section-13-video/`](section-13-video/)                             |
| 14  | Automation                 | [`section-14-automation/`](section-14-automation/)                   |

## Phase 4 — Lending Readiness Platform™

After this ops package, product work continues as the **Lending Readiness Platform™** on the shared monorepo (no product fork):

- Lender dashboard / pipeline — shipped foundation in v29.0
- Borrower portal — `apps/lrp-web` `/portal/*`
- Advisory AI credit analysis + Mortgage Readiness Score — credit_analysis + partner readiness export
- Referral management, document vault, white-label partner portals, analytics, APIs

Ops docs here define **how the company runs**; the platform implements **how partners and staff execute** that runbook in software.

## Rules

1. Follow CLAIM-LIBRARY — advisory readiness only; no guaranteed approval/funding; no fabricated FICO; no unsupervised filing.
2. Legal templates require counsel review before use with live partners.
3. Durable docs live under `docs/lrp-enterprise/`; binaries under `assets/lrp/`.
4. Prefer edition on shared platform APIs over inventing a separate Mortgage product.
