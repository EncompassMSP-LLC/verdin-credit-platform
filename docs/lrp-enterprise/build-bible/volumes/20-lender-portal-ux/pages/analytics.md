# Page spec — Lender analytics

| Field       | Value                       |
| ----------- | --------------------------- |
| Page name   | Analytics                   |
| Route       | `/lender/analytics`         |
| Volume      | 20                          |
| Status      | `draft`                     |
| Actors      | Branch admin (LO optional)  |
| Permissions | Partnership aggregates only |

## 1. Purpose

Trends: referral volume, time-in-stage, readiness-band mix — **no cross-tenant benchmarks**.

## 2. Entry / exit

- Entered from: nav
- Navigates to: Reports

## 3. Layout

Charts + definitions tooltips.

## 4. Fields

Aggregate series only (no client lists on this page).

## 5. Actions

| ID    | Control      | Result  | API | Audit | Errors |
| ----- | ------------ | ------- | --- | ----- | ------ |
| range | Change range | refresh | GET | —     | —      |

## 6. States

Loading / insufficient data / error

## 7. Compliance copy

“Internal to your partnership. Not predictive of loan approval.”

## 8. Analytics events

`lender_analytics_view`

## 9. Open questions

- Chart library later (Vol 23/5)
