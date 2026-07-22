# Page spec — Lenders

| Field       | Value                  |
| ----------- | ---------------------- |
| Page name   | Lenders                |
| Route       | `/crm/lenders`         |
| Volume      | 21                     |
| Status      | `draft`                |
| Actors      | Partner success, admin |
| Permissions | Partnership manage     |

## 1. Purpose

Manage lender partnerships, LO seats, and digest settings.

## 2. Entry / exit

- Entered from: nav, Partners hub
- Navigates to: lender detail / members

## 3. Layout

Partner table · create · detail drawer (members, SLA, status).

## 4. Fields

| ID           | Label    | Type  | Required  | Source      | Validation          | PII |
| ------------ | -------- | ----- | --------- | ----------- | ------------------- | --- |
| name         | Org name | text  | y         | partnership | —                   | N   |
| status       | Status   | enum  | y         | partnership | active/pilot/paused | N   |
| member_email | LO email | email | on invite | form        | email               | Y   |

## 5. Actions

| ID     | Control    | Result           | API | Audit | Errors |
| ------ | ---------- | ---------------- | --- | ----- | ------ |
| create | New lender | POST partnership | yes | 409   |
| invite | Invite LO  | POST member      | yes | —     |
| pause  | Pause      | PATCH            | yes | —     |

## 6. States

Loading / empty / error

## 7. Compliance copy

Partner kit disclaimer link.

## 8. Analytics events

`crm_lender_create` · `crm_lender_invite`

## 9. Open questions

- Map to `mortgage_partner` API module
