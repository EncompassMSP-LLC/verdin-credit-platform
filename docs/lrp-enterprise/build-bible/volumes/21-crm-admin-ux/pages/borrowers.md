# Page spec — Borrower list

| Field       | Value            |
| ----------- | ---------------- |
| Page name   | Borrower list    |
| Route       | `/crm/borrowers` |
| Volume      | 21               |
| Status      | `draft`          |
| Actors      | Case managers+   |
| Permissions | Case read        |

## 1. Purpose

Search and filter all borrowers in the org.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Borrower workspace; create borrower

## 3. Layout

Search · filters · table · pagination · “New borrower.”

## 4. Fields

| ID       | Label    | Type | Required | Source | Validation | PII |
| -------- | -------- | ---- | -------- | ------ | ---------- | --- |
| q        | Search   | text | n        | query  | min 2      | Y   |
| stage    | Stage    | enum | n        | query  | —          | N   |
| assignee | Assignee | uuid | n        | query  | —          | N   |

## 5. Actions

| ID     | Control | Result      | API  | Audit | Errors |
| ------ | ------- | ----------- | ---- | ----- | ------ |
| open   | Row     | workspace   | —    | —     | —      |
| create | New     | create flow | POST | yes   | 400    |

## 6. States

Loading / empty / error

## 7. Compliance copy

List shows least PII needed (name + stage).

## 8. Analytics events

`crm_borrowers_list`

## 9. Open questions

- Soft-deleted visibility
