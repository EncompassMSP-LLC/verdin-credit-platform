# Fillable referral form — digital & printable

**Digital:** `/resources/partner-kit/referral`  
**Print:** browser Print on that page (or PDF export).

## Fields

| ID             | Label                                                  | Required | Notes                                  |
| -------------- | ------------------------------------------------------ | -------- | -------------------------------------- |
| partner_org    | Partner / branch name                                  | y        |                                        |
| lo_name        | Loan officer name                                      | y        |                                        |
| lo_email       | LO email                                               | y        |                                        |
| lo_phone       | LO phone                                               | n        |                                        |
| borrower_name  | Borrower display name                                  | y        | Minimal PII                            |
| borrower_email | Borrower email                                         | n        |                                        |
| borrower_phone | Borrower phone                                         | n        |                                        |
| intent         | Mortgage intent notes                                  | n        | Product interest—not eligibility claim |
| gaps           | Known credit/doc gaps                                  | n        | Free text                              |
| consent        | Partner attests borrower consented to referral contact | y        | Checkbox                               |
| notes          | Internal notes                                         | n        |                                        |

## Submit behavior (Phase 2 web)

1. Validate required fields + consent.
2. Prefill `/contact?intent=lender&resource=referral` with summary query params **or** `mailto:` partnerships with encoded body.
3. Show confirmation: referral request recorded for follow-up—not an underwriting decision.
4. Print stylesheet hides chrome; shows LRP header + disclaimer.

## API follow-up (later)

Wire to `POST /mortgage-partner/.../referrals` when partnership id + client id exist; until then contact handoff is intentional.
