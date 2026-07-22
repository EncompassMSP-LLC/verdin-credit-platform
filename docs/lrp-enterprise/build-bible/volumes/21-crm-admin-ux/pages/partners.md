# Page spec — Partners hub

| Field       | Value            |
| ----------- | ---------------- |
| Page name   | Partners hub     |
| Route       | `/crm/partners`  |
| Volume      | 21               |
| Status      | `draft`          |
| Actors      | Partner success  |
| Permissions | Partnership read |

## 1. Purpose

Unified entry to lenders, realtors, and affiliate partners with health signals.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Lenders, Realtors, Referrals

## 3. Layout

Type tiles · recent activity · at-risk SLA partners.

## 4. Fields

Aggregate partner counts and last activity only.

## 5. Actions

| ID        | Control | Result     | API | Audit | Errors |
| --------- | ------- | ---------- | --- | ----- | ------ |
| open_type | Tile    | typed list | —   | —     | —      |

## 6. States

Loading / empty / error

## 7. Compliance copy

—

## 8. Analytics events

`crm_partners_hub_view`

## 9. Open questions

- Affiliate type needed in v1?
