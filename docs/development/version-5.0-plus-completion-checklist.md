# Version 5.0+ Completion Checklist

Ordered path to **pilot-ready product surfaces** — **in progress**. Preceded by shipped **v5.0.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.0+ pilot done”

- [ ] All eight epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.0-plus-scope.md`](../governance/version-5.0-plus-scope.md)
- [ ] Capability matrix **Frontend** column updated for 5.0+ UI slices
- [ ] Staff can manage clients and link cases without API calls
- [ ] Portal users can upload documents and view/send messages on linked cases (when flags enabled)
- [ ] `pnpm dev` in `apps/web` works without manual `api-client` build

---

## Phase 1 — Recommended order

| Order | Slice                             | Epic             | Status |
| ----- | --------------------------------- | ---------------- | ------ |
| 1     | 5.0+ scope + completion checklist | Kickoff          | ✅     |
| 2     | Web `predev` api-client build     | DX               | ✅     |
| 3     | Staff client management UI        | Client Mgmt      | ✅     |
| 4     | Case form `client_id` picker      | Client Mgmt      | ✅     |
| 5     | Portal document upload UI         | Client Portal    | ✅     |
| 6     | Portal secure messaging UI        | Client Portal    | —      |
| 7     | Staff case messaging UI           | Client Portal    | —      |
| 8     | Compliance center staff UI        | Compliance       | —      |
| 9     | Enterprise reporting staff UI     | Reporting        | —      |
| 10    | Org admin staff UI                | Enterprise Admin | —      |
| 11    | LLM case summary UI               | AI               | —      |
| 12    | Capability matrix 5.0+ sign-off   | Governance       | —      |

Portal slices require `VITE_ENABLE_CLIENT_PORTAL=true`. LLM UI slice requires `VITE_ENABLE_LLM=true` and ADR-012 gates.

---

## Explicitly not 5.0+ (→ 5.1+)

| Capability              | Version | Why defer         |
| ----------------------- | ------- | ----------------- |
| Autonomous dispute file | 5.1+    | Compliance        |
| Billing / Stripe        | 5.1+    | Product + finance |
| Predictive analytics    | 5.1+    | Data pipeline     |
| IdP enrollment          | 5.1+    | Security review   |
| API key auth middleware | 5.1+    | After admin UI    |
