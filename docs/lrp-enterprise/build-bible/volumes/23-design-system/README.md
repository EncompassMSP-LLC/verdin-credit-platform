# Volume 23 — Design system

| Field        | Value                                                    |
| ------------ | -------------------------------------------------------- |
| Status       | `ready-for-build`                                        |
| Stage        | 3                                                        |
| Owner        | Product / design                                         |
| Last updated | 2026-07-22                                               |
| Depends on   | Vol 16 · Vol 19–21                                       |
| Brand inputs | `docs/brand/lending-readiness-partners/` · `assets/lrp/` |

---

## 1. Purpose

Lock visual and interaction rules so Stage 5 implements one coherent LRP product across marketing, borrower portal, lender workspace, and CRM.

**Non-goals:** Rewriting platform `apps/web` chrome unless shared tokens are extracted; pixel-perfect mockups for every state (page specs own content).

## 2. Principles

1. **Trust over hype** — calm navy/gold; no “guaranteed approval” visual language
2. **One composition** on marketing heroes; product apps may use denser ops layouts
3. **Clarity first** — readiness band and next action beat decorative chrome
4. **Accessible by default** — WCAG 2.2 AA target
5. **Motion with purpose** — 2–3 intentional patterns, not noise

## 3. Color tokens

| Token                    | Value            | Use                                      |
| ------------------------ | ---------------- | ---------------------------------------- |
| `--lrp-navy`             | `#00133E`        | Brand, headers, primary text on light    |
| `--lrp-gold`             | `#C29E5B`        | Accent, CTAs secondary, score highlights |
| `--lrp-navy-ink`         | `#0A1B3D` approx | Body emphasis                            |
| `--lrp-surface`          | `#F7F8FA`        | App background (not cream cliché)        |
| `--lrp-surface-elevated` | `#FFFFFF`        | Panels                                   |
| `--lrp-border`           | `#D7DCE5`        | Hairlines                                |
| `--lrp-success`          | semantic green   | Completed tasks                          |
| `--lrp-warning`          | semantic amber   | SLA risk                                 |
| `--lrp-danger`           | semantic red     | Errors / critical flags                  |
| `--lrp-info`             | semantic blue    | Advisory callouts                        |

**Bands (draft):** Building / Progressing / Near ready / Lending Ready — map to neutral→gold progression; never pure “stock green = approved.”

## 4. Typography

| Role                | Guidance                                                                           |
| ------------------- | ---------------------------------------------------------------------------------- |
| Display (marketing) | Expressive serif or distinctive sans from brand kit — **not** Inter/Roboto default |
| Product UI          | Readable sans (brand-specified); tabular nums for scores                           |
| Scale               | Display / H1–H3 / body / small / caption                                           |
| Line length         | Product body ~60–80ch                                                              |

Exact font files: lock from brand kit before `ready-for-build`.

## 5. Spacing / grid / breakpoints

| Token       | Value                                             |
| ----------- | ------------------------------------------------- |
| Space scale | 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64               |
| Content max | Portal ~1120–1280px; CRM full width with side nav |
| Breakpoints | `sm` 640 · `md` 768 · `lg` 1024 · `xl` 1280       |

## 6. Component inventory

| Component                 | Notes                                                 |
| ------------------------- | ----------------------------------------------------- |
| Button                    | Primary (navy), secondary (outline), tertiary, danger |
| Input / Select / Textarea | Labels, errors, help                                  |
| Checkbox / Radio / Switch | Consent patterns                                      |
| Alert / Banner            | Advisory (info) mandatory pattern                     |
| Tabs                      | Borrower workspace / CRM                              |
| Table                     | Dense CRM; comfortable portal                         |
| Modal / Drawer            | Confirm destructive; task detail                      |
| Badge                     | Stage + band                                          |
| Empty state               | Illustration optional; clear CTA                      |
| Score meter               | Band-first; optional numeric                          |
| Nav shells                | Portal / Lender / CRM distinct but token-shared       |

Cards: **avoid** decorative cards in marketing heroes; allow for interactive containers in apps when needed.

## 7. Score visualization

- Band label dominant
- Optional ring/bar for numeric (staff or borrower if enabled)
- Driver list with severity dots
- Always adjacent short disclaimer link

## 8. Icons

Single set (e.g. Lucide or brand set) — consistent stroke; no emoji in product chrome.

## 9. Motion

| Pattern        | Use                         |
| -------------- | --------------------------- |
| Fade/slide in  | Page section enter (portal) |
| Progress pulse | Analysis pending            |
| Toast          | Task complete               |

Duration ~150–250ms; respect `prefers-reduced-motion`.

## 10. Accessibility

- Contrast AA for text/icons
- Focus rings visible on navy/gold
- Form errors tied to inputs
- Don’t rely on color alone for band

## 11. Delivery

| Artifact                     | When                  |
| ---------------------------- | --------------------- |
| Token CSS / Tailwind theme   | Stage 5 early         |
| Component stubs in `lrp-web` | Stage 5               |
| Storybook (optional)         | After core components |

## 12. Open decisions

- [ ] Exact display + UI font pairing from brand kit
- [x] Dark mode → **no for v1** (P2-13)
- [x] Tokens → **app-local in `lrp-web` first** (P2-14)

## Approval

| Role             | Name | Date | Sign-off |
| ---------------- | ---- | ---- | -------- |
| Founder / design |      |      | ☐        |
| Product          |      |      | ☐        |
