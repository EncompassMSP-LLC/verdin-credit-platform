# Mortgage Partner Marketing Kit (Phase 1)

| Field        | Value                                        |
| ------------ | -------------------------------------------- |
| Status       | `ready-for-build`                            |
| Volume       | 07                                           |
| Brand        | Lending Readiness Partners (LRP)             |
| Tagline      | Helping More Borrowers Become Lending Ready. |
| Last updated | 2026-07-23                                   |

Canonical sales kit for **loan officers, lender partnerships, and realtor co-channel**. Copy is claim-library locked ([CLAIM-LIBRARY.md](../../CLAIM-LIBRARY.md)).

## Package contents

| #   | Asset                        | File                                                                          |
| --- | ---------------------------- | ----------------------------------------------------------------------------- |
| 1   | Cover / welcome letter       | [01-cover-letter.md](01-cover-letter.md)                                      |
| 2   | Trifold brochure copy        | [02-trifold-brochure.md](02-trifold-brochure.md)                              |
| 3   | Referral flyer               | [03-referral-flyer.md](03-referral-flyer.md)                                  |
| 4   | Loan officer one-pager       | [04-loan-officer-one-pager.md](04-loan-officer-one-pager.md)                  |
| 5   | Mortgage readiness checklist | [05-mortgage-readiness-checklist.md](05-mortgage-readiness-checklist.md)      |
| 6   | Social campaign (5 posts)    | [06-social-campaign.md](06-social-campaign.md)                                |
| 7   | Email drip (5)               | [07-email-campaign.md](07-email-campaign.md)                                  |
| 8   | LinkedIn themes              | [08-linkedin-campaign.md](08-linkedin-campaign.md)                            |
| 9   | Landing page spec            | [09-landing-page-spec.md](09-landing-page-spec.md)                            |
| 10  | Realtor co-channel kit       | [10-realtor-version.md](10-realtor-version.md)                                |
| 11  | Phase 2 premium kit          | [11-phase-2-premium-kit.md](11-phase-2-premium-kit.md) · [phase-2/](phase-2/) |

## Phase 2 web

| Path                                        | Purpose                            |
| ------------------------------------------- | ---------------------------------- |
| `/resources/partner-kit/phase-2`            | Premium kit hub                    |
| `/resources/partner-kit/guide`              | Partnership Guide (readable/print) |
| `/resources/partner-kit/referral`           | Fillable referral form             |
| `/resources/partner-kit/print/leave-behind` | Print leave-behind                 |

## Folder insert order (print)

1. Welcome letter
2. Brochure
3. Services / LO one-pager
4. Referral flyer
5. FAQ (use landing FAQ block)
6. Business card
7. QR to referral / partner portal
8. Mortgage readiness checklist

## QR / URL targets

| Asset            | Target URL                               |
| ---------------- | ---------------------------------------- |
| Lender briefing  | `/lenders` or `/contact?intent=lender`   |
| Lender workspace | `/lender/login`                          |
| Realtor kit      | `/realtors` or `/contact?intent=realtor` |
| Partner kit hub  | `/resources/partner-kit`                 |

## Brand rules (every piece)

- Full name **Lending Readiness Partners** before abbreviation **LRP**
- Tagline exact: _Helping More Borrowers Become Lending Ready._
- Short disclaimer on public pieces: _Lending Readiness Score™ is advisory and not a loan approval or underwriting decision._
- Forbidden: guaranteed approval/funding, “we’ll get you a mortgage,” fabricated FICO before/after, unsupervised filing, “mortgage score” as a promise

## Web surfaces

- Lenders: `apps/lrp-web` `/lenders`
- Realtors: `/realtors`
- Kit hub: `/resources/partner-kit`
- Phase 2 hub: `/resources/partner-kit/phase-2`
