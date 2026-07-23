# Volume 21 — CRM and admin UX specification

| Field        | Value                             |
| ------------ | --------------------------------- |
| Status       | `draft`                           |
| Stage        | 2 — Product Blueprint             |
| Owner        | Product + Ops                     |
| Last updated | 2026-07-22                        |
| Depends on   | Vol 14 · Vol 18 · Vol 19 · Vol 20 |

---

## 1. Scope

Operator **Enterprise CRM** surfaces (`/crm/*` in `apps/lrp-web`) used by staff to run readiness operations, partners, and compliance-safe workflows.

**Non-goals:** Borrower portal (Vol 19); lender self-serve (Vol 20); visual tokens (Vol 23).

## 2. Actors & RBAC (draft)

| Role            | Typical access                                 |
| --------------- | ---------------------------------------------- |
| Owner / Admin   | All modules + permissions + billing hooks      |
| Ops lead        | Cases, pipeline, reporting, automations config |
| Case manager    | Borrowers, tasks, documents, notes, messages   |
| Reviewer        | Dispute / findings review queues               |
| Partner success | Referrals, lenders, realtors, digests          |
| Read only       | Dashboards / reporting view                    |

Prototype may use demo auth; production maps to platform RBAC.

## 3. Global rules

- Staff-mediated disputes only; no unsupervised bureau filing controls
- Claim library (Vol 18) in all outbound macros
- Every mutation audited (who/when/what)
- Impersonation / “view as borrower” if present: banner + audit

## 4. IA / routes (draft — align with prototype)

| Route                      | Page                     |
| -------------------------- | ------------------------ |
| `/crm/login`               | Login                    |
| `/crm` or `/crm/dashboard` | Ops dashboard            |
| `/crm/pipeline`            | Readiness pipeline board |
| `/crm/borrowers`           | Borrower list            |
| `/crm/borrowers/:id`       | Borrower workspace       |
| `/crm/referrals`           | Referral queue           |
| `/crm/lenders`             | Lender partners          |
| `/crm/realtors`            | Realtor partners         |
| `/crm/partners`            | Partner hub              |
| `/crm/tasks`               | Task queue               |
| `/crm/documents`           | Document queue           |
| `/crm/notes`               | Notes / activity         |
| `/crm/email`               | Email workspace          |
| `/crm/sms`                 | SMS workspace            |
| `/crm/calendar`            | Calendar                 |
| `/crm/workflow`            | Workflow board           |
| `/crm/automations`         | Automations (gated)      |
| `/crm/reporting`           | Reporting                |
| `/crm/permissions`         | Roles & permissions      |
| `/crm/admin`               | Org admin                |

## 5. Inventory

[PAGE-INVENTORY.md](./PAGE-INVENTORY.md) · specs in [`pages/`](./pages/)

## 6. Exit gate

Inventory rows ≥ `review`; ops + compliance sign-off on borrower workspace + dispute actions.

## Approval

| Role       | Name | Date | Sign-off |
| ---------- | ---- | ---- | -------- |
| Product    |      |      | ☐        |
| Ops        |      |      | ☐        |
| Compliance |      |      | ☐        |
