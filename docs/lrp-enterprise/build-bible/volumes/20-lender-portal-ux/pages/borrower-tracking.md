# Page spec — Borrower tracking

| Field       | Value                    |
| ----------- | ------------------------ |
| Page name   | Borrower tracking        |
| Route       | `/lender/borrowers/:id`  |
| Volume      | 20                       |
| Status      | `draft`                  |
| Actors      | LO roles (own or branch) |
| Permissions | Referral access          |

## 1. Purpose

Coarse status view: stage, readiness band, blockers, next date — not full credit file.

## 2. Entry / exit

- Entered from: Pipeline
- Navigates to: Messages, Exports request

## 3. Layout

Header identity (minimal) · stage · band · blocker list · timeline (partner-safe) · actions.

## 4. Fields

| ID           | Label       | Type      | Required | Source      | Validation    | PII |
| ------------ | ----------- | --------- | -------- | ----------- | ------------- | --- |
| display_name | Name        | text      | y        | referral    | —             | Y   |
| stage        | Stage       | enum      | y        | referral    | —             | N   |
| band         | Band        | enum/null | n        | readiness   | —             | N   |
| blockers     | Blockers    | list      | n        | ops summary | no tradelines | N   |
| next_date    | Next update | date      | n        | referral    | —             | N   |

## 5. Actions

| ID             | Control         | Result     | API | Audit             | Errors |
| -------------- | --------------- | ---------- | --- | ----------------- | ------ |
| message        | Message ops     | → Messages | —   | —                 | —      |
| request_export | Request package | POST       | yes | 403 if ineligible |

## 6. States

Loading / 404 / error

## 7. Compliance copy

“Not an underwriting decision.”

## 8. Analytics events

`lender_borrower_view` · `lender_package_request`

## 9. Open questions

- Show task completion %?
