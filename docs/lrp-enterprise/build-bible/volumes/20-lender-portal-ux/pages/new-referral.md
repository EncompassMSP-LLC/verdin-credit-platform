# Page spec — New referral

| Field       | Value                      |
| ----------- | -------------------------- |
| Page name   | New referral               |
| Route       | `/lender/referrals/new`    |
| Volume      | 20                         |
| Status      | `review`                   |
| Actors      | LO submitter, branch admin |
| Permissions | Can create referral        |

## 1. Purpose

Capture a mortgage-intent borrower referral into the readiness program.

## 2. Entry / exit

- Entered from: Pipeline CTA
- Navigates to: Pipeline / detail on success

## 3. Layout

Single form + consent acknowledgment + submit.

## 4. Fields

| ID          | Label          | Type     | Required | Source | Validation | PII |
| ----------- | -------------- | -------- | -------- | ------ | ---------- | --- |
| first_name  | First name     | text     | y        | form   | —          | Y   |
| last_name   | Last name      | text     | y        | form   | —          | Y   |
| email       | Email          | email    | y        | form   | email      | Y   |
| phone       | Phone          | tel      | n        | form   | —          | Y   |
| notes       | Notes to ops   | textarea | n        | form   | max len    | Y   |
| consent_ack | Borrower aware | checkbox | y        | form   | must true  | N   |

## 5. Actions

| ID     | Control         | Result | API           | Audit | Errors  |
| ------ | --------------- | ------ | ------------- | ----- | ------- |
| submit | Submit referral | create | POST referral | yes   | 400/409 |

## 6. States

Validation errors / submitting / success

## 7. Compliance copy

“You confirm the borrower expects contact about a readiness program. This is not a loan application approval.”

## 8. Analytics events

`lender_referral_submit`

## 9. Open questions

- Duplicate detection UX
