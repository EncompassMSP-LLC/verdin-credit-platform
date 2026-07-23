# Page spec — Profile

| Field       | Value             |
| ----------- | ----------------- |
| Page name   | Profile           |
| Route       | `/portal/profile` |
| Volume      | 19                |
| Status      | `draft`           |
| Actors      | Borrower          |
| Permissions | Own profile       |

## 1. Purpose

View/update contact and identity basics used for the readiness file.

## 2. Entry / exit

- Entered from: nav / settings
- Navigates to: Settings

## 3. Layout

Form sections: identity, contact, mailing address; save bar.

## 4. Fields

| ID         | Label      | Type  | Required | Source  | Validation | PII |
| ---------- | ---------- | ----- | -------- | ------- | ---------- | --- |
| first_name | First name | text  | y        | profile | —          | Y   |
| last_name  | Last name  | text  | y        | profile | —          | Y   |
| email      | Email      | email | y        | profile | email      | Y   |
| phone      | Phone      | tel   | n        | profile | E.164-ish  | Y   |
| address_*  | Address    | text  | n        | profile | —          | Y   |

SSN: never show full; last-4 only if already on file / policy.

## 5. Actions

| ID   | Control | Result         | API   | Audit | Errors |
| ---- | ------- | -------------- | ----- | ----- | ------ |
| save | Save    | update profile | PATCH | yes   | 400    |

## 6. States

- Loading / validation errors / save success

## 7. Compliance copy

“Keep your contact info current so we can reach you about your readiness file.”

## 8. Analytics events

`portal_profile_save`

## 9. Open questions

- Which fields locked after KYC
