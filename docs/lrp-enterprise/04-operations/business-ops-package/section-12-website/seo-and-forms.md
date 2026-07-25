# SEO, Forms & Contact

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

---

## 1. SEO standards

| Item            | Spec                                                                             |
| --------------- | -------------------------------------------------------------------------------- |
| Title pattern   | `{Page} — Lending Readiness Partners` (via `createMetadata`)                     |
| Description     | Readiness / partnership language; never “fix credit fast” or guaranteed approval |
| Canonical       | Prefer production host paths under `apps/lrp-web`                                |
| OG image        | Brand atmosphere; no fake score widgets                                          |
| robots          | Index marketing; noindex thank-you + authenticated apps if not already           |
| Structured data | FAQPage on `/faqs`; Organization on home                                         |

**Keyword posture:** mortgage readiness, lending ready, partner program, borrower preparation — not credit-repair spam clusters.

---

## 2. Contact form — `/contact`

| Field               | Required | Notes                                                                            |
| ------------------- | -------- | -------------------------------------------------------------------------------- |
| Full name           | Yes      |                                                                                  |
| Email               | Yes      |                                                                                  |
| Phone               | Optional | TCPA: consent checkbox if SMS follow-up offered                                  |
| Audience intent     | Yes      | `lender` · `realtor` · `borrower` · `builder` · `attorney` · `advisor` · `other` |
| Company / brokerage | Optional | Strongly encouraged for B2B                                                      |
| Message             | Yes      |                                                                                  |
| Consent             | Yes      | Privacy acknowledgment                                                           |

Prefill intent from query: `/contact?intent=lender`.

**On submit:** create CRM activity (Section 5) + notify Partner Success (Section 14) → thank-you route by intent.

---

## 3. Online referral form

Path: `/resources/partner-kit/referral` (shipped).

Align fields with Section 4 referral tracker + Phase 3 referral packet:

- Referring partner name / org / email / phone
- Borrower name / phone / email (minimum needed)
- Product intent
- Known issues (high-level; **no SSN / full report paste**)
- Preferred LO
- Authorization acknowledgment

**On submit:** `/thank-you/referral` + CRM + case/referral pipeline hooks (productized later).

---

## 4. Briefing / kit request forms

May be embedded on `/lenders` and `/realtors` or route to `/contact?intent=…`.

Minimum fields: name, email, org, role, market, preferred time.

---

## 5. Analytics & UTMs

| Param          | Use                                        |
| -------------- | ------------------------------------------ |
| `utm_source`   | channel (linkedin, event, qr-print)        |
| `utm_medium`   | cpc · organic · print · email · referral   |
| `utm_campaign` | partner-kit · booth-YYYY · section-10-bank |
| `utm_content`  | creative id                                |

Do not put PII in UTMs. Print QR codes (Section 11) should use tracked short paths where possible.

---

## 6. Accessibility & performance

- WCAG 2.2 AA target on marketing pages
- Keyboard-reachable FAQs and forms
- Prefer system-efficient images; hero remains one composition
- Forms: visible labels, error text, no placeholder-only labels

---

## 7. Legal links (footer)

| Link                      | Source     |
| ------------------------- | ---------- |
| Privacy Policy            | Section 3  |
| Terms / E-consent summary | Section 3  |
| Contact                   | `/contact` |

Counsel-review required before first production publish of legal pages.
