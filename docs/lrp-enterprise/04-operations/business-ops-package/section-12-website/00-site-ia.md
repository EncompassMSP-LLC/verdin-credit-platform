# Site Information Architecture

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field | Value                                                       |
| ----- | ----------------------------------------------------------- |
| App   | `apps/lrp-web`                                              |
| Rule  | One brand, multiple audiences — no forked marketing domains |

---

## 1. Public marketing surface

| Path                              | Primary audience                         | Spec                                       |
| --------------------------------- | ---------------------------------------- | ------------------------------------------ |
| `/`                               | Mixed / brand home                       | Home hero + audience chooser               |
| `/about`                          | All                                      | Company posture                            |
| `/services`                       | All                                      | What we do / don’t                         |
| `/technology`                     | Partners + operators                     | Platform overview (advisory)               |
| `/pricing`                        | Partners                                 | Packages; no outcome pricing               |
| `/partners`                       | Partner overview hub                     | Routes to audience landings                |
| `/lenders`                        | Mortgage companies / LOs / brokers       | [`landing-pages.md`](landing-pages.md)     |
| `/realtors`                       | Real estate agents / teams               | same                                       |
| `/borrowers`                      | Consumers (via LO preferred)             | same                                       |
| `/builders`                       | Builders / community sales (planned)     | same                                       |
| `/attorneys`                      | Consumer / real-estate counsel (planned) | same                                       |
| `/advisors`                       | Financial planners / insurance (planned) | same                                       |
| `/resources`                      | All                                      | Hub for kits + KB                          |
| `/resources/partner-kit`          | Partners                                 | Digital kit                                |
| `/resources/partner-kit/referral` | Partners                                 | Referral form                              |
| `/faqs`                           | All                                      | [`faqs.md`](faqs.md)                       |
| `/blog`                           | All                                      | [`blog.md`](blog.md)                       |
| `/blog/[slug]`                    | All                                      | Article template                           |
| `/stories`                        | All (planned; may live under `/blog`)    | [`success-stories.md`](success-stories.md) |
| `/contact`                        | All                                      | Intent-aware form                          |
| `/thank-you/*`                    | Post-submit                              | [`thank-you-pages.md`](thank-you-pages.md) |

---

## 2. Authenticated product surfaces (not marketing)

| Prefix    | Role                         |
| --------- | ---------------------------- |
| `/portal` | Borrower portal              |
| `/lender` | Partner / LO workspace       |
| `/crm`    | Internal Partner Success CRM |

Marketing CTAs may deep-link to login pages (`/portal/login`, `/lender/login`, `/crm/login`) — never promise outcomes on those entry points.

---

## 3. Global chrome

| Element          | Requirement                                                                         |
| ---------------- | ----------------------------------------------------------------------------------- |
| Header           | Wordmark hero-level; primary nav: Partners · Borrowers · Resources · FAQs · Contact |
| Footer           | Tagline · short advisory disclaimer · legal links · contact                         |
| Cookie / privacy | Link to counsel-approved privacy policy (Section 3)                                 |
| Mobile           | Single composition heroes; no card-clutter first viewport                           |

---

## 4. Audience chooser (home)

One job: route the visitor.

1. I’m a loan officer / lender → `/lenders`
2. I’m a realtor → `/realtors`
3. I’m preparing for a financing conversation → `/borrowers`
4. I’m another referral partner → `/partners`

---

## 5. Content ownership

| Surface         | Owner           | Review                                              |
| --------------- | --------------- | --------------------------------------------------- |
| Landings / FAQ  | Marketing + ops | Claim library                                       |
| Blog / stories  | Marketing       | Claim library + no real testimonial without release |
| KB              | Ops / training  | Compliance for dispute/process articles             |
| Product UI copy | Product         | ADR-012 / claim library                             |

---

## 6. Related

- Section 1 onboarding (partner welcome language)
- Section 3 compliance (privacy / e-consent links)
- Section 10 social (repurpose claim-safe posts into blog seeds)
- Section 14 automation (form → CRM / notification wiring)
