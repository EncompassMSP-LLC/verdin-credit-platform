# LRP Platform V1.2 Completion Checklist — Customer Experience

Phase 4 Growth · Release train step 1. Master epic: [#419](https://github.com/EncompassMSP-LLC/verdin-credit-platform/issues/419).

**Prior:** [`lrp-platform-v1.1.0`](../release-notes/lrp-platform-v1.1.0.md) · **Phases:** [`lrp-platform-maturity-phases.md`](lrp-platform-maturity-phases.md)

## Intent

Extend the **existing** borrower client portal (`/portal/*` + `/api/v1/portal/*`) — do not rebuild. Partner builder/attorney/advisor portals remain backlog (PB-001–003) for a later train if not absorbed here.

## Exit criteria

- [ ] Ordered V1.2 slices merged
- [ ] Capability matrix + API reference updated
- [ ] Tenant isolation + portal realm tests green
- [ ] No autonomous filing / score promises
- [ ] Release notes + tag `lrp-platform-v1.2.0`

## Ordered slices

| Order | ID       | Slice                                            | Status | PR      |
| ----- | -------- | ------------------------------------------------ | ------ | ------- |
| 1     | LRP-301A | Portal self-serve password reset                 | ✅     | #420    |
| 2     | LRP-301B | Portal invite email on staff provision           | ✅     | #421    |
| 3     | LRP-302A | Dedicated portal notifications feed + read state | ✅     | this PR |
| 4     | LRP-302B | Portal message attachments (staff-gated)         | ☐      | —       |
| 5     | LRP-303A | Borrower dashboard UX polish (Vol 19 parity)     | ☐      | —       |
| 6     | LRP-303B | Progress / checklist empty-states + deep links   | ☐      | —       |
| —     | Closeout | Release notes + tag `lrp-platform-v1.2.0`        | ☐      | —       |

## Ranking notes

1. **301A first** — `/portal/forgot-password` is a stub; realtor already has the pattern.
2. **301B** — closes invite loop (`PORTAL_INVITE` matrix event).
3. **302A/B** — notifications + messaging depth before dashboard polish.
4. Partner authenticated portals (builder/attorney/advisor) stay PB-001–003 unless product reprioritizes.

## Slice notes

### LRP-301A — Portal self-serve password reset

- Migration `117_portal_credential_tokens`
- `POST /portal/auth/forgot-password` (generic response; token returned only in development/test)
- `POST /portal/auth/reset-password` → new password + portal session tokens
- Wire `apps/lrp-web` forgot + reset pages
- Never emails secrets in responses outside app_env development/test
- Status: **shipped** (#420)

### LRP-301B — Portal invite email on staff provision

- Reuses `client_portal_credential_tokens` with `purpose=invite` (no migration 118)
- Provision creates portal user + one-time hashed invite; **never emails a password**
- Dispatches notification matrix `PORTAL_INVITE` (email deferred when delivery not ready)
- `POST /clients/{id}/portal-user/resend-invite` (staff-gated, 2-minute cooldown)
- `POST /portal/auth/accept-invite` + `/portal/accept-invite` UI
- Timeline: `PORTAL_USER_INVITED` / `PORTAL_INVITE_ACCEPTED`
- Status: **shipped** (#421)

### LRP-302A — Dedicated portal notifications feed + read state

- Migration `118_portal_notifications` (`recipient_portal_user_id` → `client_portal_users`; reuses `notification_category` enum)
- Credential tokens remain migration **117 only** (invite/reset purposes)
- `GET /portal/notifications`, `GET /portal/notifications/unread-count`, `POST …/read`, `POST …/mark-all-read`
- Matrix `BORROWER` + `IN_APP` writes portal rows (not staff `notifications`)
- lrp-web `/portal/notifications` page + shell unread badge; optimistic mark-read with rollback
- Deep links sanitized to relative `/portal/*`; no staff metadata on responses
- Mark-read idempotent; no per-read audit noise (creation audited via matrix dispatches)
- Status: **this PR**
