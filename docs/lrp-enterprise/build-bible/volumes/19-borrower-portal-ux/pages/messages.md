# Page spec — Messages

| Field       | Value                 |
| ----------- | --------------------- |
| Page name   | Messages              |
| Route       | `/portal/messages`    |
| Volume      | 19                    |
| Status      | `review`              |
| Actors      | Borrower              |
| Permissions | Own thread with staff |

## 1. Purpose

Secure messaging between borrower and operating staff (not LO chat by default).

## 2. Entry / exit

- Entered from: nav, Dashboard, Notifications
- Navigates to: linked Tasks/Documents

## 3. Layout

Thread list (if multi) + conversation + composer.

## 4. Fields

| ID          | Label   | Type     | Required | Source | Validation | PII        |
| ----------- | ------- | -------- | -------- | ------ | ---------- | ---------- |
| body        | Message | textarea | y        | client | max length | Y possible |
| attachments | Files   | file[]   | n        | client | type/size  | Y          |

## 5. Actions

| ID     | Control | Result           | API  | Audit | Errors |
| ------ | ------- | ---------------- | ---- | ----- | ------ |
| send   | Send    | append message   | POST | yes   | 429    |
| attach | Attach  | upload then send | POST | yes   | —      |

## 6. States

- Loading / empty thread CTA / send error / success

## 7. Compliance copy

Composer helper: staff cannot guarantee loan approval. Macros on staff side (Vol 09).

## 8. Analytics events

`portal_message_send`

## 9. Open questions

- [x] Single thread vs topics → **single thread with staff** (P2-5)
