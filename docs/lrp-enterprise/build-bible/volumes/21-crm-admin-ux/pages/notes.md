# Page spec — Notes

| Field       | Value           |
| ----------- | --------------- |
| Page name   | Notes           |
| Route       | `/crm/notes`    |
| Volume      | 21              |
| Status      | `draft`         |
| Actors      | Staff           |
| Permissions | Case note write |

## 1. Purpose

Org-wide recent notes / activity search (also embedded on borrower workspace).

## 2. Entry / exit

- Entered from: nav
- Navigates to: Borrower workspace

## 3. Layout

Feed + search; filter internal vs partner-visible.

## 4. Fields

| ID         | Label      | Type     | Required | Source | Validation       | PII        |
| ---------- | ---------- | -------- | -------- | ------ | ---------------- | ---------- |
| body       | Note       | textarea | y        | form   | max len          | Y possible |
| visibility | Visibility | enum     | y        | form   | internal/partner | N          |

## 5. Actions

| ID     | Control  | Result | API | Audit | Errors |
| ------ | -------- | ------ | --- | ----- | ------ |
| create | Add note | POST   | yes | —     |

## 6. States

Loading / empty / error

## 7. Compliance copy

Partner-visible notes use claim library.

## 8. Analytics events

`crm_note_create`

## 9. Open questions

—
