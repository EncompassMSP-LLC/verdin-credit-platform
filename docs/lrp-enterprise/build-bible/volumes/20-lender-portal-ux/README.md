# Volume 20 — Lender portal UX specification

| Field        | Value                 |
| ------------ | --------------------- |
| Status       | `draft`               |
| Stage        | 2 — Product Blueprint |
| Owner        | Product               |
| Last updated | 2026-07-22            |
| Depends on   | Vol 12 · Vol 18       |

---

## 1. Scope

Lender / LO workspace screens (`/lender/*` in `apps/lrp-web`).

**Non-goals:** Full CRM (Vol 21); borrower portal (Vol 19).

## 2. Actors

| Actor        | Access                             |
| ------------ | ---------------------------------- |
| LO submitter | Create referrals; see own pipeline |
| LO viewer    | Read-only pipeline                 |
| Branch admin | Manage users; exports; digests     |

## 3. Global rules

- Advisory language on all readiness displays
- PII minimization; no full tradeline tables by default
- Exports operator-gated / authorized

## 4. IA / routes (draft)

| Route                   | Page                       |
| ----------------------- | -------------------------- |
| `/lender`               | Pipeline / home            |
| `/lender/referrals`     | Referral management        |
| `/lender/referrals/new` | New referral               |
| `/lender/borrowers/:id` | Borrower tracking (coarse) |
| `/lender/reports`       | Partner reports            |
| `/lender/analytics`     | Analytics (aggregate)      |
| `/lender/messages`      | Messages / requests        |
| `/lender/exports`       | Exports                    |
| `/lender/settings`      | Branch settings            |

## 5. Inventory

[PAGE-INVENTORY.md](./PAGE-INVENTORY.md)

## Approval

| Role       | Name | Date | Sign-off |
| ---------- | ---- | ---- | -------- |
| Product    |      |      | ☐        |
| Compliance |      |      | ☐        |
