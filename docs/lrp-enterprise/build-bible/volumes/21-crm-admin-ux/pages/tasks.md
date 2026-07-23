# Page spec — CRM Tasks

| Field       | Value         |
| ----------- | ------------- |
| Page name   | Tasks         |
| Route       | `/crm/tasks`  |
| Volume      | 21            |
| Status      | `draft`       |
| Actors      | Case managers |
| Permissions | Task write    |

## 1. Purpose

Cross-borrower task queue for staff and borrower-assigned work.

## 2. Entry / exit

- Entered from: nav, dashboard
- Navigates to: Borrower workspace task tab

## 3. Layout

Filters (mine, overdue, staff-only) · table · bulk assign.

## 4. Fields

| ID       | Label    | Type | Required | Source | Validation     | PII |
| -------- | -------- | ---- | -------- | ------ | -------------- | --- |
| title    | Title    | text | y        | task   | —              | N   |
| borrower | Borrower | text | y        | case   | —              | Y   |
| owner    | Owner    | enum | y        | task   | staff/borrower | N   |
| due_at   | Due      | date | n        | task   | —              | N   |
| status   | Status   | enum | y        | task   | —              | N   |

## 5. Actions

| ID       | Control  | Result | API | Audit | Errors |
| -------- | -------- | ------ | --- | ----- | ------ |
| complete | Complete | PATCH  | yes | —     |
| create   | New task | POST   | yes | —     |
| reassign | Reassign | PATCH  | yes | —     |

## 6. States

Loading / empty / error

## 7. Compliance copy

Task titles must not promise outcomes.

## 8. Analytics events

`crm_tasks_queue_view`

## 9. Open questions

—
