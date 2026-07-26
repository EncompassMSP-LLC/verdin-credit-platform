# Platform Job Map

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

Crosswalk from ops automations to likely platform homes. Spec-before-code: implement in Version 29.0+ / worker backlog without forking a separate Mortgage product.

---

## 1. API modules

| Automation area         | Module / surface                                |
| ----------------------- | ----------------------------------------------- |
| Email / SMS / in-app    | `apps/api` `modules/notifications`              |
| Referrals / pipeline    | `mortgage_partner`, cases, accounts             |
| CRM activities / tasks  | CRM APIs backing `/crm`                         |
| Documents               | `modules/documents`                             |
| Readiness / reports     | accounts / reporting / partner readiness export |
| LLM-gated features      | `modules/llm` + ADR-012                         |
| Org settings / consents | `org_admin`, compliance                         |

---

## 2. Worker jobs (existing + proposed)

| Job                                     | Status           | Ops use             |
| --------------------------------------- | ---------------- | ------------------- |
| OCR / classify / parse / entity resolve | Existing         | Document automation |
| AI summary / batch summary              | Existing (gated) | Case assist         |
| SMS marketing delivery                  | Existing         | SMS campaigns       |
| Overdue investigation scan              | Existing         | Ops SLA             |
| Reporting MV refresh                    | Existing         | Analytics           |
| Retention enforcement                   | Existing         | Compliance          |
| Partner nurture drip                    | Proposed         | Email automation    |
| Referral intake orchestrator            | Proposed         | Referral automation |
| Daily CRM digest                        | Proposed         | CRM command center  |
| Consultation completed pack             | Proposed         | Advisory artifacts  |
| Weekly/monthly report assemble          | Proposed         | Status automation   |

---

## 3. UI surfaces

| Automation UX             | Route                                                       |
| ------------------------- | ----------------------------------------------------------- |
| CRM digests / tasks       | `/crm`                                                      |
| Borrower notifications    | `/portal/notifications`                                     |
| Lender notifications      | `/lender/notifications`                                     |
| Automation admin (future) | `/crm/automations` (scaffold exists — wire rules carefully) |

---

## 4. Build order (recommended)

1. Referral intake orchestrator + notification matrix (highest ops leverage)
2. Consultation completed pack (staff-gated send)
3. Daily CRM digest
4. Partner nurture drips
5. Scheduled status digests
6. Chatbot (after KB corpus + counsel OK)

---

## 5. Explicit non-goals (this package)

- Unsupervised bureau filing loops
- Auto-approve marketplace listings
- Cross-tenant data sync
- Guaranteed-outcome messaging in any channel
