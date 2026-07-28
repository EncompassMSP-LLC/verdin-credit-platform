# LRP Borrower Portal UAT Script (LRP-303)

Manual acceptance script for Lending Readiness Partners **borrower portal** (`apps/lrp-web` `/portal/*`) against the shared platform API. Pair with automated coverage in `apps/api/tests/client_portal/test_borrower_uat_happy_path.py`.

| Field        | Value                         |
| ------------ | ----------------------------- |
| Slice        | LRP-303                       |
| Audience     | Borrower / client portal user |
| Auth         | Portal JWT (`/portal/auth/*`) |
| Demo auth    | **Off** for production UAT    |
| Last updated | 2026-07-28                    |

## Preconditions

1. `ENABLE_CLIENT_PORTAL=true` on the API.
2. Staff has created a Client, linked an open Case, and provisioned a portal user (`POST /clients/{id}/portal-user`).
3. Prefer a **published** credit-analysis / readiness run so readiness + report surfaces are non-empty.
4. Use a dedicated UAT borrower email (not `owner@verdin.demo` staff credentials).
5. Confirm `NODE_ENV=production` or demo flags off when validating production-like behavior (LRP-108).

## Happy path (must pass)

| #   | Step              | Route / action          | Expected                                                                   |
| --- | ----------------- | ----------------------- | -------------------------------------------------------------------------- |
| 1   | Open login        | `/portal/login`         | Form loads; no demo credential hints in production builds                  |
| 2   | Sign in           | Portal email + password | Redirect to `/portal/dashboard`; session cookie set                        |
| 3   | Me / identity     | Dashboard header        | Shows borrower display name or email; no staff CRM chrome                  |
| 4   | Cases             | Dashboard / progress    | At least one case for this client only                                     |
| 5   | Readiness         | `/portal/readiness`     | Band-first score; advisory disclaimer visible; no CRA credit-score claim   |
| 6   | Tasks / checklist | `/portal/tasks`         | Action-plan items load; can complete an open item when present             |
| 7   | Timeline          | `/portal/timeline`      | Case/readiness/document/task milestones; no staff notes or tradeline dumps |
| 8   | Reports           | `/portal/reports`       | Readiness report JSON view; text/PDF export includes disclaimer            |
| 9   | Documents         | `/portal/documents`     | Case document list (empty OK); upload gated to allowed types               |
| 10  | Messages          | `/portal/messages`      | Thread loads for primary case; borrower can send a message                 |
| 11  | Disputes summary  | `/portal/disputes`      | Counts-only / staff-mediated copy; no self-file CTA                        |
| 12  | Sign out          | Shell → Sign out        | Returns to `/portal/login`; protected routes redirect                      |

## Negative / isolation checks

| #   | Check                                                  | Expected                                                          |
| --- | ------------------------------------------------------ | ----------------------------------------------------------------- |
| N1  | Call portal APIs with staff JWT                        | 401/403 (not borrower session)                                    |
| N2  | Request another client’s `case_id`                     | 404/403                                                           |
| N3  | Visit `/lender/*` or `/crm/*` with portal session only | Redirect to that realm’s login (cookies isolated)                 |
| N4  | Forgot password                                        | Copy directs to partner/staff reset (no false self-serve success) |

## Claim-library / copy gates

- No “you are approved”, “guaranteed funding”, or fabricated FICO as underwriting outcome.
- Advisory disclaimer present on readiness and report surfaces.
- Dispute language stays staff-mediated.

## Sign-off

| Role            | Name | Date | Pass? | Notes |
| --------------- | ---- | ---- | ----- | ----- |
| Product / PO    |      |      | ☐     |       |
| Partner success |      |      | ☐     |       |
| QA              |      |      | ☐     |       |

Automated suite reference: `python -m pytest apps/api/tests/client_portal/test_borrower_uat_happy_path.py` (`DATABASE_URL` → `verdin_credit_test`).
