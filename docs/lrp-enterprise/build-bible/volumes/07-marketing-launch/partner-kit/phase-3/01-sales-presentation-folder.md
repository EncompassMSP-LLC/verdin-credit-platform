# 01 — Sales Presentation Folder (print-ready)

| Field     | Value                           |
| --------- | ------------------------------- |
| Status    | `ready-for-build`               |
| Spec size | 9" × 12" presentation folder    |
| Finish    | Matte navy + optional gold foil |
| Extends   | Phase 2 leave-behind (`17`)     |

Physical leave-behind for lender visits, LO desks, and chamber/networking follow-ups. Designers produce press PDFs from this spec; binaries land in `assets/lrp/brochures/` when delivered.

---

## 1. Construction

| Element             | Spec                                                        |
| ------------------- | ----------------------------------------------------------- |
| Flat size           | Per vendor die (standard 9×12 two-pocket)                   |
| Closed size         | 9" W × 12" H                                                |
| Stock               | 100–120 lb cover, matte laminate                            |
| Pockets             | Left + right, 4" deep, glued; capacity ~25 sheets each      |
| Business card slits | Right pocket, horizontal, holds one standard 3.5" × 2" card |
| Card orientation    | Logo out, QR visible when pocket filled                     |
| Spine (optional)    | Narrow gold rule + “Mortgage Readiness Partnership”         |
| Reinforcement       | Soft-touch laminate; avoid high-gloss “retail flyer” look   |

---

## 2. Front cover (outside)

**Visual plane:** Full-bleed navy (`#0B1F3A`) with subtle paper/architectural texture (low opacity). No photo collage. No floating badges.

**Composition (top → bottom):**

1. Wordmark — Lending Readiness Partners (hero)
2. Program line — Mortgage Readiness Partnership
3. Tagline — Helping More Borrowers Become Lending Ready.
4. Thin gold rule
5. Optional partner co-brand lockup area (bottom-left, “In partnership with”)

**QR placement (front, lower-right):**

| Field      | Value                                              |
| ---------- | -------------------------------------------------- |
| Size       | 0.85" × 0.85" minimum                              |
| Target     | `/resources/partner-kit` (or co-branded short URL) |
| Caption    | Scan for digital partner kit                       |
| Quiet zone | White or warm-paper square under code              |

**Do not** place detached promo stickers on the cover.

---

## 3. Back cover (outside)

**Layout:**

| Zone        | Content                                                                                                   |
| ----------- | --------------------------------------------------------------------------------------------------------- |
| Top         | Wordmark (small) + tagline                                                                                |
| Middle      | Three partner benefits (icons optional, sparse): Clear plan · Partner visibility · Staff-mediated process |
| Lower third | Contact block + QR to `/contact?intent=lender`                                                            |
| Footer      | Short advisory disclaimer + © year                                                                        |

**Contact block (fill per market):**

```
Partnerships
hello@lendingreadinesspartners.com
[Phone]
[City / MSA beachhead]
lendingreadinesspartners.com
```

---

## 4. Inside left flap / pocket face

**Headline:** What’s inside  
**Body (short):** Everything your team needs to evaluate a Mortgage Readiness Partnership—without guarantee culture or score hype.

**Pocket insert checklist (printed on flap):**

1. Welcome letter
2. Company brochure
3. Loan officer quick reference
4. Partnership guide excerpt or full guide
5. Referral flyer / form
6. Mortgage readiness checklist
7. Business card

**Disclaimer strip (inner flap bottom):** short advisory disclaimer.

---

## 5. Inside right flap / pocket face

**Headline:** How partnership works

Process strip (four steps, horizontal):

1. **Refer** — LO sends near-miss borrower
2. **Plan** — Staff builds advisory readiness plan
3. **Update** — Partner sees progress (portal / digest)
4. **Return** — Borrower resumes financing conversation when prepared

**Callout well:** “We support readiness. Your team underwrites.”

**Business card holder:** die-cut slits; place LRP card with QR to `/lender/login` or kit hub.

---

## 6. Inside pocket inserts (standard pack)

| Pocket  | Insert                                | Source manuscript                  |
| ------- | ------------------------------------- | ---------------------------------- |
| Left 1  | Welcome / cover letter                | Phase 1 `01` + Phase 3 `02` letter |
| Left 2  | Tri-fold or bi-fold brochure          | Phase 3 `03`                       |
| Left 3  | Referral flyer                        | Phase 1 `03` / Phase 3 `08`        |
| Right 1 | LO quick reference                    | Phase 3 `05`                       |
| Right 2 | Readiness checklist                   | Phase 1 `05`                       |
| Right 3 | Partnership guide (or 4-page excerpt) | Phase 3 `04`                       |
| Card    | Business card                         | Phase 3 Canva kit                  |

---

## 7. QR code map

| Placement            | Destination                       | Caption             |
| -------------------- | --------------------------------- | ------------------- |
| Front cover          | `/resources/partner-kit`          | Digital partner kit |
| Back cover           | `/contact?intent=lender`          | Book a briefing     |
| Inside right (small) | `/resources/partner-kit/referral` | Send a referral     |
| Business card        | `/lenders` or `/lender/login`     | Partner resources   |

Export QR as vector; embed in print PDF; re-test after URL changes.

---

## 8. Print-ready artwork checklist (vendor)

- [ ] CMYK PDF/X-1a or PDF/X-4
- [ ] Bleeds 0.125" all sides
- [ ] Fonts outlined or licensed package
- [ ] Foil (optional) on separate spot layer
- [ ] Die-line layer for pockets + card slits
- [ ] Soft-proof against brand palette
- [ ] Disclaimer legible at ≥ 7 pt
- [ ] QR scanned from physical proof at final size

**File names:**

- `LRP_Folder_Lender_FrontBack_YYYYMM_v#.pdf`
- `LRP_Folder_Lender_Inside_YYYYMM_v#.pdf`
- `LRP_Folder_Lender_Die_YYYYMM_v#.pdf`

---

## 9. White-label variant

| Element        | LRP-branded                    | Partner-forward                                        |
| -------------- | ------------------------------ | ------------------------------------------------------ |
| Front wordmark | LRP                            | Partner logo primary; LRP secondary                    |
| Program name   | Mortgage Readiness Partnership | [Partner] Mortgage Readiness Program (powered by LRP)  |
| QR targets     | LRP URLs                       | Co-branded short links / partner vanity where approved |
| Disclaimer     | Always LRP claim library       | Always required                                        |

---

## 10. Copy blocks (exact)

**Front program line:** Mortgage Readiness Partnership

**Front tagline:** Helping More Borrowers Become Lending Ready.

**Back benefit 1:** A clear plan when the answer today is “not yet.”  
**Back benefit 2:** Progress visibility for loan officers—without underwriting confusion.  
**Back benefit 3:** Staff-mediated process with claim-safe communication.

**Inside process closer:** We help borrowers prepare for the next financing conversation. Lending decisions stay with you.
