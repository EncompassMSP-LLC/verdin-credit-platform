# Audience Landing Pages

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field | Value                                                                                                         |
| ----- | ------------------------------------------------------------------------------------------------------------- |
| App   | `apps/lrp-web`                                                                                                |
| Rule  | First viewport = brand + one headline + one support + one CTA group + one dominant visual. No guarantee CTAs. |

Phase 3 companion: [`19-website-landing-pages.md`](../../../build-bible/volumes/07-marketing-launch/partner-kit/phase-3/19-website-landing-pages.md).

**Long disclaimer (under every hero):**

> Lending Readiness Score™ is an advisory tool for organizing credit and documentation work toward a mortgage conversation. It is not a credit score from a consumer reporting agency, not an underwriting decision, and not a guarantee of loan approval or terms.

---

## 1. Mortgage partner — `/lenders` (shipped)

| Element  | Spec                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------- |
| Brand    | Lending Readiness Partners (hero)                                                                   |
| Headline | Help more borrowers become lending ready                                                            |
| Support  | Advisory readiness plans and partner visibility—without underwriting confusion.                     |
| CTAs     | Book a briefing · Open partner kit · Lender login                                                   |
| Sections | Problem · Process (Refer → Plan → Update → Return) · Benefits · Compliance boundary · FAQ · Contact |
| Intent   | `?intent=lender` on contact                                                                         |

**Never claim:** We get files approved / funded / scored to a number.

---

## 2. Realtor — `/realtors` (shipped)

| Element  | Spec                                                          |
| -------- | ------------------------------------------------------------- |
| Headline | Keep buyers engaged when financing needs more time            |
| Support  | Dignity-first readiness path alongside your preferred lender. |
| CTAs     | Realtor kit · Contact                                         |
| Sections | What agents can say / not say · Shared stages · FAQ           |
| Intent   | `?intent=realtor`                                             |

---

## 3. Borrower — `/borrowers` (shipped)

| Element  | Spec                                                              |
| -------- | ----------------------------------------------------------------- |
| Headline | A clear plan for “not yet”                                        |
| Support  | Education and next steps toward your next financing conversation. |
| CTAs     | Ask your LO · Contact                                             |
| Sections | What to expect · Portal (invite via LO) · Dignity · FAQ           |
| Intent   | `?intent=borrower`                                                |

**Forbidden CTAs:** Get approved · Fix your score fast · Guaranteed mortgage.

---

## 4. Builder — `/builders` (planned)

| Element  | Spec                                                                                                       |
| -------- | ---------------------------------------------------------------------------------------------------------- |
| Headline | Preparing buyers for the financing conversation                                                            |
| Support  | Help community buyers organize credit and documentation habits—while your preferred lenders stay informed. |
| CTAs     | Partner briefing · Contact                                                                                 |
| Sections | Why builders partner · Referral flow · Claim-safe language for sales offices · FAQ                         |
| Intent   | `?intent=builder`                                                                                          |

---

## 5. Attorney — `/attorneys` (planned)

| Element  | Spec                                                                                                                      |
| -------- | ------------------------------------------------------------------------------------------------------------------------- |
| Headline | Readiness support that stays in its lane                                                                                  |
| Support  | Advisory education and documentation habits for clients with financing goals—separate from legal advice and underwriting. |
| CTAs     | Partner briefing · Contact                                                                                                |
| Sections | Boundary of services · Referral path · Privacy · FAQ                                                                      |
| Intent   | `?intent=attorney`                                                                                                        |

---

## 6. Financial planner / insurance — `/advisors` (planned)

| Element  | Spec                                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------------- |
| Headline | When clients’ home goals need more preparation                                                          |
| Support  | Coordinate with lenders through an advisory readiness partner—visibility without confusing your advice. |
| CTAs     | Partner briefing · Contact                                                                              |
| Sections | Who we serve · How referrals work · What we never claim · FAQ                                           |
| Intent   | `?intent=advisor`                                                                                       |

Alias: `/financial-planners` → redirect to `/advisors`.

---

## 7. Partners hub — `/partners` (shipped / extend)

Overview chooser linking to `/lenders`, `/realtors`, `/builders`, `/attorneys`, `/advisors`.  
One composition: brand, short support, audience tiles (not a dashboard of stats).

---

## 8. Shared section blocks

| Block      | Content rule                                  |
| ---------- | --------------------------------------------- |
| Process    | Refer → Plan → Update → Return                |
| Boundary   | We support readiness. Partners underwrite.    |
| Compliance | Staff-mediated disputes; claim-safe marketing |
| CTA band   | Single primary action + secondary kit/login   |

---

## 9. Implementation notes

- Prefer extending existing `PageHero` / `Section` / `CtaBand` patterns in `apps/lrp-web`.
- Metadata via `createMetadata` — titles emphasize readiness / partnership, not “fix credit fast.”
- Map planned routes before Stage 5 marketing freeze; until then keep Phase 3 print QR pointing at live `/lenders` / `/realtors` / `/contact`.
