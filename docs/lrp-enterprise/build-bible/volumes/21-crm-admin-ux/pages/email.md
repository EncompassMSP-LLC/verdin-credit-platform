# Page spec — Email workspace

| Field       | Value                          |
| ----------- | ------------------------------ |
| Page name   | Email                          |
| Route       | `/crm/email`                   |
| Volume      | 21                             |
| Status      | `draft`                        |
| Actors      | Case managers, partner success |
| Permissions | Comms send                     |

## 1. Purpose

Send/receive (or log) email tied to borrowers/partners using approved templates.

## 2. Entry / exit

- Entered from: nav, borrower workspace
- Navigates to: thread → case

## 3. Layout

Inbox / sent · template picker · composer with compliance lint.

## 4. Fields

| ID      | Label   | Type      | Required | Source | Validation       | PII |
| ------- | ------- | --------- | -------- | ------ | ---------------- | --- |
| to      | To      | email     | y        | form   | email            | Y   |
| subject | Subject | text      | y        | form   | —                | N   |
| body    | Body    | rich text | y        | form   | template or free | Y   |
| case_id | Case    | uuid      | n        | form   | —                | N   |

## 5. Actions

| ID           | Control  | Result        | API  | Audit   | Errors        |
| ------------ | -------- | ------------- | ---- | ------- | ------------- |
| send         | Send     | enqueue email | POST | **yes** | 400 lint fail |
| log_outbound | Log only | store         | POST | yes     | —             |

## 6. States

Loading / provider down / lint blocked

## 7. Compliance copy

Block send if forbidden phrases detected (Vol 18); staff can override with reason (audited) — product decision TBD.

## 8. Analytics events

`crm_email_send`

## 9. Open questions

- [x] Live provider vs log-only → **templates + lint; block forbidden phrases (no override)** (P2-9); provider when staging ready
