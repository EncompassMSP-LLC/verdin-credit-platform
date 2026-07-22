# Page spec — Learning Center

| Field       | Value                  |
| ----------- | ---------------------- |
| Page name   | Learning Center        |
| Route       | `/portal/learn`        |
| Volume      | 19                     |
| Status      | `review`               |
| Actors      | Borrower               |
| Permissions | Authenticated borrower |

## 1. Purpose

Deliver short education modules that support readiness habits (utilization, collections, timelines, partner process).

## 2. Entry / exit

- Entered from: Dashboard nudge, nav
- Navigates to: Tasks (related), Readiness

## 3. Layout

1. Module catalog (progress)
2. Module player / article
3. Completion check

## 4. Fields

| ID        | Label     | Type    | Required | Source       | Validation | PII |
| --------- | --------- | ------- | -------- | ------------ | ---------- | --- |
| module_id | Module    | id      | y        | CMS/static   | —          | N   |
| progress  | Progress  | percent | n/a      | learning API | —          | N   |
| completed | Completed | bool    | n/a      | learning API | —          | N   |

## 5. Actions

| ID       | Control       | Result          | API           | Audit | Errors |
| -------- | ------------- | --------------- | ------------- | ----- | ------ |
| start    | Start module  | open content    | —             | —     | —      |
| complete | Mark complete | progress update | POST progress | yes   | —      |

## 6. States

- Empty catalog (shouldn’t happen) / loading / error

## 7. Compliance copy

Modules must not claim guaranteed approvals or illegal credit tactics.

## 8. Analytics events

`portal_learn_start` · `portal_learn_complete`

## 9. Open questions

- [x] Content CMS vs static → **static modules in repo for v1** (P2-4)
