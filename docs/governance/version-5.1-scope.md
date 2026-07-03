# Version 5.1 Scope & Deferrals

Formal scope for **Version 5.1 — Production Hardening**. Builds on shipped **v5.0.0** backend and **5.0+ pilot-ready** product surfaces.

**Kickoff date:** 2026-07-02  
**Target:** Production integrations deferred from 5.0/5.0+ — API key auth, identity enrollment, billing, and expanded AI/compliance automation

## Theme

Move from pilot-ready UI to production-grade enterprise operations: authenticated integrations, billable multi-tenant usage, stronger identity, and the next tier of AI and compliance automation — without autonomous filing or mobile apps in this release.

## Epic outcomes (planned)

| Epic | Theme                     | 5.1 target | Summary                                                 |
| ---- | ------------------------- | ---------- | ------------------------------------------------------- |
| 1    | API integrations          | Partial    | API key auth middleware for machine clients             |
| 2    | Identity enrollment       | Partial    | IdP / TOTP enrollment beyond SSO/MFA readiness scaffold |
| 3    | Billing                   | Partial    | Stripe subscription scaffold + org billing status       |
| 4    | Communications production | Partial    | Production SMS delivery alongside existing email        |
| 5    | Compliance enforcement    | Partial    | Retention enforcement job placeholders + audit          |
| 6    | LLM expansion             | Partial    | Document summary endpoint + staff UI                    |
| 7    | Portal real-time          | Partial    | Push notification scaffold for portal messaging         |
| 8    | Reporting depth           | Partial    | Materialized reporting views for bureau/team metrics    |

## Shipped from 5.0 / 5.0+ (foundation — do not regress)

All v5.0.0 APIs, 5.0+ staff/portal UI, feature flags, migrations, and `@verdin/api-client` functions remain production capabilities. See [`version-5.0-scope.md`](version-5.0-scope.md) and [`version-5.0-plus-scope.md`](version-5.0-plus-scope.md).

## Explicit deferrals (not 5.1)

| Capability                 | Deferred to | Reason                                   |
| -------------------------- | ----------- | ---------------------------------------- |
| Autonomous dispute filing  | 5.2+        | Legal/compliance review beyond 5.1       |
| Full BPM workflow designer | 5.2+        | Scale beyond integration hardening       |
| Predictive outcome models  | 5.2+        | Historical data pipeline not ready       |
| AI autonomous agents       | 5.2+        | Observability + compliance prerequisites |
| Native mobile apps         | 5.2+        | Web-first production                     |
| SCIM provisioning          | 5.2+        | After IdP enrollment stabilizes          |
| Revenue analytics          | 5.2+        | After billing scaffold ships             |

## Partial capability limits (5.1 targets)

### API key auth middleware (Partial)

**Included:** Validate `OrganizationApiKey` on selected routes; scope checks (`read`/`write`); last-used audit.

**Not included:** Per-route rate limiting UI, key rotation automation, public developer portal.

### Identity enrollment (Partial)

**Included:** Staff enrollment flows for TOTP and one IdP provider behind `ENABLE_ENTERPRISE`.

**Not included:** SCIM, multiple IdP federation, passwordless.

### Billing (Partial)

**Included:** Stripe customer + subscription scaffold, webhook handler, org billing status on admin summary.

**Not included:** Usage-based metering, invoicing PDFs, dunning automation.

## v5.1 sign-off

Six of eight epics ship as **Partial ✅**; **Communications production** (SMS) and **LLM expansion** (document summary UI) are **explicitly deferred** to **5.2+**. All shipped capabilities are gated behind `ENABLE_*` feature flags documented in `.env.example`. Release notes: [`v5.1.0.md`](../release-notes/v5.1.0.md).

| Epic                      | 5.1 status | Notes                                                                 |
| ------------------------- | ---------- | --------------------------------------------------------------------- |
| API integrations          | Partial ✅ | `GET /reporting/operations` accepts org API keys                      |
| Identity enrollment       | Partial ✅ | TOTP + OIDC staff enrollment behind `ENABLE_ENTERPRISE`               |
| Billing                   | Partial ✅ | Stripe customer + subscription scaffold behind `ENABLE_BILLING`       |
| Communications production | Deferred   | Production SMS delivery → 5.2+                                        |
| Compliance enforcement    | Partial ✅ | Retention enforcement jobs behind `ENABLE_COMPLIANCE_ENFORCEMENT`     |
| LLM expansion             | Deferred   | Document summary endpoint + staff UI → 5.2+                           |
| Portal real-time          | Partial ✅ | Push notification scaffold behind `ENABLE_PORTAL_PUSH`                |
| Reporting depth           | Partial ✅ | Materialized bureau/team views behind `ENABLE_MATERIALIZED_REPORTING` |

## Related documents

- [Version 5.1 completion checklist](../development/version-5.1-completion-checklist.md)
- [Version 5.0+ scope](version-5.0-plus-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
