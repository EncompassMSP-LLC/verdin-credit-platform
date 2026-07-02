# Version 5.0+ Scope & Deferrals

Formal scope for **Version 5.0+ — Product Hardening** (pilot readiness). Builds on the shipped **v5.0.0** Enterprise Edition release.

**Kickoff date:** 2026-07-02  
**Target:** Staff and portal UI for 5.0 APIs; pilot deployment readiness

## Theme

Close the gap between shipped backend capabilities and usable product surfaces so credit repair shops can run staff and client workflows without API-only features. No new major epics until pilot surfaces are integrated.

## Epic outcomes (planned)

| Epic | Theme                   | 5.0+ target | Summary                                                   |
| ---- | ----------------------- | ----------- | --------------------------------------------------------- |
| 1    | Developer experience    | Partial     | Reliable local web dev (`api-client` build on `pnpm dev`) |
| 2    | Client management UI    | Partial     | Staff clients list, CRUD, contacts, portal provision      |
| 3    | Case–client linking UI  | Partial     | `client_id` picker on case forms                          |
| 4    | Portal product UI       | Partial     | Document upload + messaging on linked cases               |
| 5    | Compliance UI           | Partial     | Staff consent and retention policy management             |
| 6    | Enterprise reporting UI | Partial     | Bureau performance + team productivity dashboards         |
| 7    | Org admin UI            | Partial     | API key lifecycle management                              |
| 8    | LLM assistance UI       | Partial     | Case summary trigger on case detail                       |

## Shipped from 5.0 (foundation — do not regress)

All v5.0.0 backend modules, feature flags, migrations, and `@verdin/api-client` functions remain production capabilities. See [`version-5.0-scope.md`](version-5.0-scope.md).

## Explicit deferrals (still not 5.0+)

| Capability                    | Deferred to | Reason                                   |
| ----------------------------- | ----------- | ---------------------------------------- |
| Autonomous dispute filing     | 5.1+        | Compliance and legal review gates        |
| Full BPM workflow designer    | 5.1+        | Scale beyond pilot                       |
| Multi-tenant billing / Stripe | 5.1+        | Product + finance sign-off               |
| Predictive outcome models     | 5.1+        | Historical data pipeline                 |
| AI autonomous agents          | 5.1+        | Compliance + observability prerequisites |
| IdP / TOTP enrollment         | 5.1+        | Requires security review beyond scaffold |
| API key auth middleware       | 5.1+        | After staff admin UI ships               |
| Native mobile apps            | 5.1+        | Web-first pilot                          |

## Partial capability limits (5.0+ targets)

### Client management UI (Partial)

**Included:** Clients list with search/filters, create/edit, detail with contacts CRUD, portal user provision when `ENABLE_CLIENT_PORTAL`.

**Not included:** Bulk import, CRM sync, intake wizard.

### Portal product UI (Partial)

**Included:** Upload documents and send/view messages on linked cases in portal UI.

**Not included:** Real-time push, attachments, billing, credit score charts.

### Compliance UI (Partial)

**Included:** List/create/withdraw consent records; list/create/edit retention policies.

**Not included:** Enforcement jobs, legal sign-off workflows.

## v5.0+ sign-off

All eight epics ship as **Partial** with written limits above. Staff and portal pilot surfaces are integrated in the web app behind feature flags (`VITE_ENABLE_CLIENT_PORTAL`, `VITE_ENABLE_ENTERPRISE`, `VITE_ENABLE_LLM`). No **Planned** 5.0+ checklist items remain undocumented — billing, IdP enrollment, API key middleware, and autonomous agents are deferred to **5.1+** per the deferrals table.

| Epic                    | 5.0+ status | Notes                                                          |
| ----------------------- | ----------- | -------------------------------------------------------------- |
| Developer experience    | Partial ✅  | `predev` api-client build; package watch deferred              |
| Client management UI    | Partial ✅  | Staff clients list/CRUD, contacts, portal provision            |
| Case–client linking UI  | Partial ✅  | `client_id` picker on case create/edit                         |
| Portal product UI       | Partial ✅  | Upload + messaging on linked cases; real-time push → 5.1+      |
| Compliance UI           | Partial ✅  | Consent + retention staff UI; enforcement → 5.1+               |
| Enterprise reporting UI | Partial ✅  | Operations, bureau, team tabs; materialized views → 5.1+       |
| Org admin UI            | Partial ✅  | API key lifecycle UI; middleware auth → 5.1+                   |
| LLM assistance UI       | Partial ✅  | Case summary trigger on case detail; document summaries → 5.1+ |

## Related documents

- [Version 5.0+ completion checklist](../development/version-5.0-plus-completion-checklist.md)
- [Version 5.0 scope](version-5.0-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
