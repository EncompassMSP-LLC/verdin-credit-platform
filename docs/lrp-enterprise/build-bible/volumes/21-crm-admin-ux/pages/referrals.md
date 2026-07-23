# Page spec — Referral queue

| Field       | Value                          |
| ----------- | ------------------------------ |
| Page name   | Referrals                      |
| Route       | `/crm/referrals`               |
| Volume      | 21                             |
| Status      | `ready-for-build`              |
| Actors      | Partner success, case managers |
| Permissions | Referral accept/decline        |

## 1. Purpose

Triage inbound lender/realtor referrals into cases.

## 2. Entry / exit

- Entered from: nav, dashboard
- Navigates to: Borrower workspace after accept

## 3. Layout

Queue tabs: New · Accepted · Declined · All; detail drawer.

## 4. Fields

| ID             | Label          | Type | Required   | Source   | Validation | PII |
| -------------- | -------------- | ---- | ---------- | -------- | ---------- | --- |
| borrower_name  | Name           | text | y          | referral | —          | Y   |
| partner        | Partner        | text | y          | referral | —          | N   |
| status         | Status         | enum | y          | referral | —          | N   |
| decline_reason | Decline reason | enum | if decline | form     | —          | N   |

## 5. Actions

| ID      | Control      | Result           | API  | Audit   | Errors |
| ------- | ------------ | ---------------- | ---- | ------- | ------ |
| accept  | Accept       | link/create case | POST | **yes** | 409    |
| decline | Decline      | notify partner   | POST | **yes** | —      |
| assign  | Assign owner | PATCH            | yes  | —       |

## 6. States

Loading / empty / error

## 7. Compliance copy

Accept does not mean loan approval.

## 8. Analytics events

`crm_referral_accept` · `crm_referral_decline`

## 9. Open questions

- Auto-create portal user on accept?
