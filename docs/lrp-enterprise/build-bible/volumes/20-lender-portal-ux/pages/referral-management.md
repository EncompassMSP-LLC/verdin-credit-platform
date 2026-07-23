# Page spec — Referral management

| Field       | Value               |
| ----------- | ------------------- |
| Page name   | Referral management |
| Route       | `/lender/referrals` |
| Volume      | 20                  |
| Status      | `ready-for-build`   |
| Actors      | LO roles            |
| Permissions | Partnership-scoped  |

## 1. Purpose

Search/filter all referrals; bulk-safe list actions (no mass PII export).

## 2. Entry / exit

- Entered from: nav
- Navigates to: detail, new

## 3. Layout

Filter bar + table + pagination.

## 4. Fields

| ID    | Label        | Type | Required | Source | Validation | PII |
| ----- | ------------ | ---- | -------- | ------ | ---------- | --- |
| q     | Search       | text | n        | query  | min 2      | Y   |
| stage | Stage filter | enum | n        | query  | —          | N   |
| lo_id | LO filter    | uuid | n        | query  | admin      | N   |

## 5. Actions

| ID     | Control | Result       | API | Audit | Errors |
| ------ | ------- | ------------ | --- | ----- | ------ |
| filter | Apply   | refresh list | GET | —     | —      |
| open   | Row     | detail       | —   | —     | —      |

## 6. States

Loading / empty / error

## 7. Compliance copy

Same advisory banner as pipeline.

## 8. Analytics events

`lender_referrals_list`

## 9. Open questions

- CSV export? Only via Exports page with gate
