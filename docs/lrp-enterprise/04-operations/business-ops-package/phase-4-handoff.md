# Phase 4 Handoff — Lending Readiness Platform™

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field    | Value                                                                      |
| -------- | -------------------------------------------------------------------------- |
| From     | Phase 3 Business Operations Package (this folder)                          |
| To       | Version 29.0+ Mortgage Partner Edition / Lending Readiness Platform™       |
| Platform | Shared monorepo — `apps/api` + `apps/lrp-web` (+ `apps/web` for CRO admin) |
| Do not   | Fork a separate Mortgage product codebase                                  |

---

## 1. What Phase 3 delivered (ops)

Company runbooks: onboarding, intake, compliance, referrals, CRM, reporting, sales, marketing banks, print, website IA, video scripts, automation specs.

**Source of truth for “how we operate”:**  
`docs/lrp-enterprise/04-operations/business-ops-package/`

---

## 2. What Phase 4 implements (product)

| Ops need                    | Platform home                        | Checklist / notes                                                                                   |
| --------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------- |
| Partner org + RBAC          | `mortgage_partner` + feature flag    | [`version-29.0-completion-checklist.md`](../../../development/version-29.0-completion-checklist.md) |
| Lender dashboard / pipeline | `/lender/*` + pipeline APIs          | v29.0 slices 2–3 (shipped foundation)                                                               |
| Advisory readiness report   | Partner readiness export             | v29.0 slice 4                                                                                       |
| Borrower portal             | `/portal/*`                          | Continue Build Bible / Stage 5                                                                      |
| CRM workspace               | `/crm/*`                             | Vol 21 + Section 5/14 specs                                                                         |
| Referrals                   | Partner referral + Section 4 tracker | Wire Section 14 referral orchestrator                                                               |
| Notifications               | `modules/notifications` + worker     | Section 14 matrix                                                                                   |
| Documents                   | `modules/documents` + worker jobs    | Section 14 document hooks                                                                           |
| Marketing site landings     | `apps/lrp-web` public routes         | Section 12 specs                                                                                    |
| LLM assists                 | `modules/llm` + ADR-012              | Gated chatbot / summaries only                                                                      |

---

## 3. Recommended engineering backlog (from Section 14)

Priority order from [`section-14-automation/platform-job-map.md`](section-14-automation/platform-job-map.md):

1. Referral intake orchestrator + notification matrix
2. Consultation completed pack (staff-gated send)
3. Daily CRM digest
4. Partner nurture drips
5. Scheduled status digests
6. Chatbot after KB corpus + counsel OK

---

## 4. Explicit non-goals (carry forward)

Aligned with Version 29.0 “never / later” table:

- Live unsupervised bureau filing or polling execution
- Automated re-dispute filing without staff gates
- Cross-tenant lender marketplace
- Forked separate Mortgage codebase
- Guaranteed-approval marketing in any channel

---

## 5. Governance links

| Doc                                                                                                 | Role                            |
| --------------------------------------------------------------------------------------------------- | ------------------------------- |
| [`CLAIM-LIBRARY.md`](../../build-bible/CLAIM-LIBRARY.md)                                            | Allowed / forbidden claims      |
| [`version-29.0-completion-checklist.md`](../../../development/version-29.0-completion-checklist.md) | Platform slice tracker          |
| [`version-29.0-scope.md`](../../governance/version-29.0-scope.md)                                   | Edition scope                   |
| Build Bible Vol 07 partner kit                                                                      | Prior marketing kit manuscripts |
| [`99-ops-package-signoff.md`](99-ops-package-signoff.md)                                            | Phase 3 ops complete            |

---

## 6. Handoff statement

Phase 3 Business Operations Package is **signed off** as documentation-complete.  
Phase 4 work proceeds on the **Lending Readiness Platform™** using these runbooks as the ops contract — implement in-product, do not re-specify a parallel company stack.
