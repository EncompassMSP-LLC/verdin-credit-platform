# Page spec — Tasks (Action plan)

| Field       | Value             |
| ----------- | ----------------- |
| Page name   | Tasks             |
| Route       | `/portal/tasks`   |
| Volume      | 19                |
| Status      | `ready-for-build` |
| Actors      | Borrower          |
| Permissions | Own tasks         |

## 1. Purpose

Let the borrower complete and track personalized action-plan tasks.

## 2. Entry / exit

- Entered from: Dashboard, Readiness drivers, nav
- Navigates to: Documents (if task requires upload), Messages

## 3. Layout

1. Filters: Open / Done / All
2. Task list (priority, due, owner)
3. Detail drawer/page: description, steps, complete control

## 4. Fields

| ID           | Label        | Type      | Required | Source    | Validation        | PII |
| ------------ | ------------ | --------- | -------- | --------- | ----------------- | --- |
| title        | Title        | text      | y        | tasks API | —                 | N   |
| status       | Status       | enum      | y        | tasks     | open/done/blocked | N   |
| due_at       | Due          | date      | n        | tasks     | —                 | N   |
| priority     | Priority     | enum      | n        | tasks     | —                 | N   |
| body         | Instructions | rich text | n        | tasks     | —                 | N   |
| requires_doc | Needs upload | bool      | n        | tasks     | —                 | N   |

## 5. Actions

| ID       | Control         | Result                 | API        | Audit | Errors            |
| -------- | --------------- | ---------------------- | ---------- | ----- | ----------------- |
| complete | Mark complete   | status=done            | PATCH task | yes   | 409 if staff-only |
| upload   | Upload for task | → Documents w/ context | —          | —     | —                 |
| ask      | Ask a question  | → Messages compose     | —          | —     | —                 |

Borrower cannot complete staff-only tasks.

## 6. States

- Loading / empty (“No tasks yet”) / error / success toast on complete

## 7. Compliance copy

Task copy must not promise bureau outcomes.

## 8. Analytics events

`portal_task_view` · `portal_task_complete`

## 9. Open questions

- [x] Due dates borrower-editable → **no** (P2-7)
