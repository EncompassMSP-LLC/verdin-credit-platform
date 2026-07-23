# Page spec — Credit Timeline

| Field       | Value              |
| ----------- | ------------------ |
| Page name   | Credit Timeline    |
| Route       | `/portal/timeline` |
| Volume      | 19                 |
| Status      | `draft`            |
| Actors      | Borrower           |
| Permissions | Own case events    |

## 1. Purpose

Show a chronological, borrower-safe history of readiness milestones (uploads, score publishes, tasks, dispute sends recorded by staff).

## 2. Entry / exit

- Entered from: nav, Dashboard
- Navigates to: related Tasks / Documents / Messages

## 3. Layout

Vertical timeline; filters by type optional.

## 4. Fields

| ID         | Label  | Type     | Required | Source       | Validation             | PII |
| ---------- | ------ | -------- | -------- | ------------ | ---------------------- | --- |
| event_at   | When   | datetime | y        | timeline API | —                      | N   |
| event_type | Type   | enum     | y        | timeline     | —                      | N   |
| title      | Title  | text     | y        | timeline     | borrower-safe          | N   |
| detail     | Detail | text     | n        | timeline     | no raw tradeline dumps | N   |

## 5. Actions

| ID           | Control      | Result    | API | Audit | Errors |
| ------------ | ------------ | --------- | --- | ----- | ------ |
| open_related | View related | deep link | —   | —     | —      |

Read-only for borrower.

## 6. States

- Loading / empty (“No activity yet”) / error

## 7. Compliance copy

Events must not imply creditor decisions.

## 8. Analytics events

`portal_timeline_view`

## 9. Open questions

- Include staff-only internal notes? **No**
