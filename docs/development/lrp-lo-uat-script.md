# LRP Loan Officer Portal UAT Script (LRP-304)

Manual acceptance script for Lending Readiness Partners **loan officer / lender workspace** (`apps/lrp-web` `/lender/*`) against the shared Mortgage Partner + notifications APIs. Pair with automated coverage in `apps/api/tests/mortgage_partner/test_lo_uat_happy_path.py`.

| Field        | Value                                         |
| ------------ | --------------------------------------------- |
| Slice        | LRP-304                                       |
| Audience     | Loan officer / lender partner operator        |
| Auth         | Platform JWT (`/auth/login`) — not portal JWT |
| Demo auth    | **Off** for production UAT (LRP-108)          |
| Last updated | 2026-07-28                                    |

## Preconditions

1. `ENABLE_MORTGAGE_PARTNER=true` on the API.
2. CRO org has an **active lender partnership** with at least one referral linked to a client (and preferably a case with a **published** credit-analysis / readiness run).
3. Use a staff/partner platform user with Mortgage Partner access (admin or case manager on the CRO org for V1.0 interim mapping).
4. Confirm `NODE_ENV=production` or lender demo flags off when validating production-like behavior.

## Happy path (must pass)

| #   | Step             | Route / action                         | Expected                                                                             |
| --- | ---------------- | -------------------------------------- | ------------------------------------------------------------------------------------ |
| 1   | Open login       | `/lender/login`                        | Form loads; no demo credential prefill in production builds                          |
| 2   | Sign in          | Platform email + password              | Redirect to `/lender/dashboard`; platform session cookie set                         |
| 3   | Dashboard        | `/lender/dashboard`                    | Live partnership summary (referral counts / stages); advisory readiness copy visible |
| 4   | Referrals        | `/lender/referrals`                    | Partnership-scoped referral list; borrower display names; no cross-org rows          |
| 5   | Advance stage    | Referral detail / patch stage          | `pipeline_stage` updates (e.g. referred → intake); stage timestamp changes           |
| 6   | Milestones       | Referral milestones                    | Default 5 milestones; can view completions                                           |
| 7   | Pipeline         | `/lender/pipeline`                     | Board cards match stage; days-in-stage present                                       |
| 8   | Readiness report | `/lender/readiness` or referral report | Band + disclaimer; score is advisory (not underwriting / CRA FICO claim)             |
| 9   | Readiness export | Text or PDF download                   | File downloads; disclaimer in payload; never auto-transmitted                        |
| 10  | Notifications    | `/lender/notifications`                | Live inbox loads (may be empty); mark-read works when items exist                    |
| 11  | Sign out         | Shell → Sign out                       | Returns to `/lender/login`; protected routes redirect                                |

## Explicitly deferred / demo-only (document, do not fail UAT)

| Surface             | Status for V1.0 UAT                                      |
| ------------------- | -------------------------------------------------------- |
| `/lender/messages`  | Demo-local threads until partner messaging APIs connect  |
| `/lender/documents` | May remain seed/demo until partner document APIs connect |
| `/lender/admin`     | Local/demo settings only — not production org admin      |
| `/lender/analytics` | Referral analytics aggregates remain backlog             |
| Realtor realm       | Separate `/realtor/*` UAT (LRP-301/302)                  |

## Negative / isolation checks

| #   | Check                                           | Expected                          |
| --- | ----------------------------------------------- | --------------------------------- |
| N1  | Call Mortgage Partner APIs with portal JWT only | 401/403                           |
| N2  | Access another CRO org’s `partnership_id`       | 404                               |
| N3  | Visit `/portal/*` or `/realtor/*` with LO only  | Redirect to that realm’s login    |
| N4  | Readiness copy                                  | No “approved” / funding guarantee |

## Claim-library / copy gates

- Dashboard and readiness surfaces keep advisory disclaimer language.
- Pipeline “funded” / “mortgage ready” are **operational stage labels**, not underwriting outcomes.
- No fabricated credit bureau score as a funding decision.

## Sign-off

| Role            | Name | Date | Pass? | Notes |
| --------------- | ---- | ---- | ----- | ----- |
| Product / PO    |      |      | ☐     |       |
| Partner success |      |      | ☐     |       |
| QA              |      |      | ☐     |       |

Automated suite reference: `python -m pytest apps/api/tests/mortgage_partner/test_lo_uat_happy_path.py` (`DATABASE_URL` → `verdin_credit_test`).
