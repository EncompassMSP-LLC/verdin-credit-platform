# Page spec — Lender Pipeline

| Field       | Value                              |
| ----------- | ---------------------------------- |
| Page name   | Pipeline                           |
| Route       | `/lender`                          |
| Volume      | 20                                 |
| Status      | `ready-for-build`                  |
| Actors      | LO submitter, viewer, branch admin |
| Permissions | Partnership-scoped referrals       |

## 1. Purpose

Show open referrals by stage so LOs know who is moving toward Lending Ready.

## 2. Entry / exit

- Entered from: login, nav
- Navigates to: Borrower tracking, New referral, Exports

## 3. Layout

**Table** default (P2-1); filters (mine / branch, stage); SLA badges. Kanban deferred.

## 4. Fields

| ID               | Label       | Type      | Required | Source    | Validation | PII |
| ---------------- | ----------- | --------- | -------- | --------- | ---------- | --- |
| borrower_display | Borrower    | text      | y        | referral  | masked ok  | Y   |
| stage            | Stage       | enum      | y        | referral  | —          | N   |
| readiness_band   | Band        | enum/null | n        | readiness | advisory   | N   |
| updated_at       | Updated     | datetime  | y        | referral  | —          | N   |
| next_date        | Next update | date      | n        | referral  | —          | N   |

## 5. Actions

| ID              | Control         | Result              | API  | Audit | Errors |
| --------------- | --------------- | ------------------- | ---- | ----- | ------ |
| open            | Row             | → Borrower tracking | —    | —     | —      |
| new             | New referral    | → New referral      | —    | —     | —      |
| request_package | Request package | create request      | POST | yes   | 403    |

## 6. States

- Loading / empty CTA to refer / error

## 7. Compliance copy

Banner: readiness is advisory; not underwriting.

## 8. Analytics events

`lender_pipeline_view` · `lender_pipeline_open_referral`

## 9. Open questions

- [x] Kanban vs table → **table** (P2-1)
