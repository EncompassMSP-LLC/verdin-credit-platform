# Page spec — Realtors

| Field       | Value                             |
| ----------- | --------------------------------- |
| Page name   | Realtors                          |
| Route       | `/crm/realtors`                   |
| Volume      | 21                                |
| Status      | `draft`                           |
| Actors      | Partner success                   |
| Permissions | Partnership manage (realtor type) |

## 1. Purpose

Manage realtor teams with **minimized** data access profiles.

## 2. Entry / exit

- Entered from: nav
- Navigates to: detail / referrals filtered

## 3. Layout

Same pattern as Lenders; access preset = coarse status only.

## 4. Fields

| ID            | Label  | Type | Required | Source      | Validation      | PII |
| ------------- | ------ | ---- | -------- | ----------- | --------------- | --- |
| team_name     | Team   | text | y        | partnership | —               | N   |
| access_preset | Access | enum | y        | partnership | realtor_limited | N   |

## 5. Actions

| ID     | Control | Result      | API | Audit | Errors |
| ------ | ------- | ----------- | --- | ----- | ------ |
| create | New     | POST        | yes | —     |
| invite | Invite  | POST member | yes | —     |

## 6. States

Loading / empty / error

## 7. Compliance copy

UI warns: realtors do not see full credit files.

## 8. Analytics events

`crm_realtor_create`

## 9. Open questions

- Always require linked lender?
