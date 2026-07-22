# Volume 19 — Borrower portal UX specification

| Field        | Value                    |
| ------------ | ------------------------ |
| Status       | `draft`                  |
| Stage        | 2 — Product Blueprint    |
| Owner        | Product                  |
| Last updated | 2026-07-22               |
| Depends on   | Vol 11 · Vol 18 · Vol 22 |

---

## 1. Scope

Every borrower-facing screen in `apps/lrp-web` (borrower portal). Specs are the contract for Stage 5 implementation / refactor.

**Non-goals:** Lender UI (Vol 20); CRM (Vol 21); visual tokens (Vol 23).

## 2. Actors

| Actor                           | Access                                 |
| ------------------------------- | -------------------------------------- |
| Borrower (client)               | Own case data only                     |
| Staff (impersonation / support) | Via CRM — not this volume’s primary UX |

## 3. Global rules

- Advisory disclaimer available from shell (link to “What Lending Ready means”)
- No “approved” / “guaranteed” copy anywhere
- PII: show full only to authenticated borrower on own record
- Empty/loading/error required on every page

## 4. IA / routes (draft)

| Route                            | Page            |
| -------------------------------- | --------------- |
| `/portal` or `/portal/dashboard` | Dashboard       |
| `/portal/timeline`               | Credit Timeline |
| `/portal/readiness`              | Readiness Score |
| `/portal/documents`              | Documents       |
| `/portal/tasks`                  | Tasks           |
| `/portal/learn`                  | Learning Center |
| `/portal/notifications`          | Notifications   |
| `/portal/reports`                | Reports         |
| `/portal/messages`               | Messages        |
| `/portal/profile`                | Profile         |
| `/portal/settings`               | Settings        |

Exact path prefix may match existing `lrp-web` routing — update when locking `ready-for-build`.

## 5. Page inventory

[PAGE-INVENTORY.md](./PAGE-INVENTORY.md) · specs in [`pages/`](./pages/)

## 6. Exit gate

All inventory rows ≥ `review`; founder/product sign-off.

## Approval

| Role       | Name | Date | Sign-off |
| ---------- | ---- | ---- | -------- |
| Product    |      |      | ☐        |
| Compliance |      |      | ☐        |
