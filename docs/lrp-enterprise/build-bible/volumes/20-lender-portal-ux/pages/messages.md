# Page spec — Lender messages

| Field       | Value                        |
| ----------- | ---------------------------- |
| Page name   | Messages                     |
| Route       | `/lender/messages`           |
| Volume      | 20                           |
| Status      | `draft`                      |
| Actors      | LO roles                     |
| Permissions | Partnership threads with ops |

## 1. Purpose

LO ↔ ops messaging about referrals (not borrower direct chat unless product later allows).

## 2. Entry / exit

- Entered from: nav, borrower tracking
- Navigates to: referral detail

## 3. Layout

Threads linked to referral IDs + composer.

## 4. Fields

| ID          | Label    | Type     | Required | Source  | Validation | PII        |
| ----------- | -------- | -------- | -------- | ------- | ---------- | ---------- |
| body        | Message  | textarea | y        | form    | max len    | Y possible |
| referral_id | Referral | uuid     | y        | context | —          | N          |

## 5. Actions

| ID   | Control | Result       | API | Audit | Errors |
| ---- | ------- | ------------ | --- | ----- | ------ |
| send | Send    | POST message | yes | 429   |

## 6. States

Loading / empty / error

## 7. Compliance copy

Claim library; no guarantee language.

## 8. Analytics events

`lender_message_send`

## 9. Open questions

- Email bridge vs in-app only for v1
