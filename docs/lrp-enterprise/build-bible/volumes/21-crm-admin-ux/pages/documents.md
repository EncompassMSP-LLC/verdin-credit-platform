# Page spec — CRM Documents

| Field       | Value                    |
| ----------- | ------------------------ |
| Page name   | Documents                |
| Route       | `/crm/documents`         |
| Volume      | 21                       |
| Status      | `draft`                  |
| Actors      | Case managers, reviewers |
| Permissions | Document read/write      |

## 1. Purpose

Queue for incoming uploads needing classify / review / attach to analysis.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Borrower workspace documents

## 3. Layout

Needs-review queue · filters by type/status.

## 4. Fields

| ID       | Label  | Type | Required | Source | Validation | PII |
| -------- | ------ | ---- | -------- | ------ | ---------- | --- |
| filename | File   | text | y        | docs   | —          | Y   |
| doc_type | Type   | enum | y        | docs   | —          | N   |
| status   | Status | enum | y        | docs   | —          | N   |

## 5. Actions

| ID       | Control         | Result | API | Audit | Errors |
| -------- | --------------- | ------ | --- | ----- | ------ |
| classify | Set type        | PATCH  | yes | —     |
| accept   | Accept          | PATCH  | yes | —     |
| reject   | Reject + reason | PATCH  | yes | —     |

## 6. States

Loading / empty / error

## 7. Compliance copy

Handle ID docs as sensitive PII.

## 8. Analytics events

`crm_docs_queue_view`

## 9. Open questions

—
