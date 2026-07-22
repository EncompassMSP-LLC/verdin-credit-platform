# Page spec — CRM Login

| Field       | Value                     |
| ----------- | ------------------------- |
| Page name   | Login                     |
| Route       | `/crm/login`              |
| Volume      | 21                        |
| Status      | `draft`                   |
| Actors      | Staff                     |
| Permissions | Unauthenticated → session |

## 1. Purpose

Authenticate staff into the Enterprise CRM.

## 2. Entry / exit

- Entered from: direct URL, session expiry redirect
- Navigates to: Dashboard on success

## 3. Layout

Centered auth form; brand mark; no borrower marketing hero.

## 4. Fields

| ID       | Label    | Type     | Required | Source | Validation | PII |
| -------- | -------- | -------- | -------- | ------ | ---------- | --- |
| email    | Email    | email    | y        | form   | email      | Y   |
| password | Password | password | y        | form   | min length | Y   |

## 5. Actions

| ID    | Control | Result  | API  | Audit       | Errors |
| ----- | ------- | ------- | ---- | ----------- | ------ |
| login | Sign in | session | auth | login event | 401    |

## 6. States

Loading / invalid credentials / locked account

## 7. Compliance copy

Internal tool notice; no guarantee marketing.

## 8. Analytics events

`crm_login_success` · `crm_login_fail`

## 9. Open questions

- SSO / MFA timing
