# Page spec — Lender exports

| Field       | Value                          |
| ----------- | ------------------------------ |
| Page name   | Exports                        |
| Route       | `/lender/exports`              |
| Volume      | 20                             |
| Status      | `review`                       |
| Actors      | Branch admin; LO if authorized |
| Permissions | Export entitlement             |

## 1. Purpose

Request and download **readiness packages** / authorized summaries for attorney or loan-file handoff — never auto-filed anywhere.

## 2. Entry / exit

- Entered from: nav, borrower tracking
- Navigates to: download when ready

## 3. Layout

Eligible referrals · request form · history of exports.

## 4. Fields

| ID          | Label    | Type | Required | Source | Validation      | PII |
| ----------- | -------- | ---- | -------- | ------ | --------------- | --- |
| referral_id | Referral | uuid | y        | form   | eligible        | N   |
| purpose     | Purpose  | enum | y        | form   | handoff reasons | N   |

## 5. Actions

| ID       | Control        | Result     | API  | Audit        | Errors  |
| -------- | -------------- | ---------- | ---- | ------------ | ------- |
| request  | Request export | enqueue    | POST | **required** | 403     |
| download | Download       | signed URL | GET  | **required** | 404/410 |

## 6. States

Ineligible explainer / processing / ready / expired link

## 7. Compliance copy

“Advisory package for authorized handoff. Not a credit decision. Not transmitted to bureaus by this action.”

## 8. Analytics events

`lender_export_request` · `lender_export_download`

## 9. Open questions

- [x] Watermark / password → **watermarked PDF + audit; password optional later** (P2-8)
