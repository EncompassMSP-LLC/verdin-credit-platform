# Security Architecture

Authentication, authorization, audit, and compliance-oriented security design for Verdin Credit Platform.

## Security principles

1. **Defense in depth** — network TLS, auth, RBAC, org scoping, audit trails
2. **Least privilege** — default deny; roles grant minimum required access
3. **Tenant isolation** — no cross-organization data access via API
4. **Auditability** — who did what, when, on which record
5. **Secrets never in code** — environment variables and secret managers (5.0)

## Authentication

### Current (4.2–4.3)

| Component        | Implementation                     |
| ---------------- | ---------------------------------- |
| Protocol         | JWT access tokens + refresh tokens |
| Password storage | bcrypt via `hash_password()`       |
| Login            | `POST /api/v1/auth/login`          |
| Refresh          | `POST /api/v1/auth/refresh`        |
| Current user     | `GET /api/v1/auth/me`              |
| Token transport  | `Authorization: Bearer` header     |

Access tokens are short-lived; refresh tokens enable renewal without re-login.

### Planned (5.0)

- MFA (TOTP / WebAuthn)
- SSO (SAML 2.0 / OIDC)
- API keys for integration partners (scoped, rotatable)
- Session revocation list (Redis)

## Authorization (RBAC)

### Role hierarchy

```
owner > admin > case_manager > reviewer > read_only
```

Higher roles inherit lower-role capabilities via `has_permission()` in `api/core/permissions.py`.

### Enforcement points

| Layer      | Responsibility                                       |
| ---------- | ---------------------------------------------------- |
| Router     | `Depends(get_current_user)` on all business routes   |
| Service    | `_require_write()`, `_require_delete()`, role checks |
| Repository | Organization filter on every query                   |

**Never** trust client-supplied `organization_id` — always use `current_user.organization_id`.

### Domain permission pattern

Each module defines constants in `permissions.py`:

```python
DOMAIN_READ_ROLE = UserRole.READ_ONLY
DOMAIN_WRITE_ROLE = UserRole.CASE_MANAGER
DOMAIN_DELETE_ROLE = UserRole.ADMIN
```

## Multi-tenancy & data isolation

- Users belong to one `Organization`
- All case/account/document queries filter by org
- 404 (not 403) when resource exists in another org — prevents enumeration
- Future client portal users (4.8) get a separate auth realm with case-scoped tokens

## Audit trail

### Field-level audit (today)

- `created_by_id`, `updated_by_id` on entities via `apply_audit_on_create/update`
- `created_at`, `updated_at`, `deleted_at`

### Event-level audit (4.3+)

- `TimelineEvent` per case for user-visible actions
- Standard event types documented in domain model

### Immutable audit store (5.0)

- Append-only `audit_events` table or external log store
- Tamper-evident retention for compliance review
- Covers admin actions, consent changes, data exports

## Encryption

| Layer                              | Status                                             |
| ---------------------------------- | -------------------------------------------------- |
| In transit                         | TLS required in production (Nginx / load balancer) |
| At rest (DB)                       | Managed PostgreSQL encryption (deployment concern) |
| At rest (objects)                  | MinIO SSE (4.5+ hardening)                         |
| Application-level field encryption | PII fields TBD for 5.0 (SSN, full account numbers) |

**Rule:** Store masked account identifiers (`account_number_masked`); never persist full PAN/SSN in plaintext.

## Input validation

- Pydantic schemas on all inputs
- SQL injection prevented by SQLAlchemy parameterized queries
- File uploads (4.3+): MIME validation, size limits, virus scan hook (5.0)

## Secrets management

| Environment      | Approach                     |
| ---------------- | ---------------------------- |
| Local dev        | `.env` (gitignored)          |
| CI               | GitHub Actions secrets       |
| Production (5.0) | Vault / cloud secret manager |

Required secrets: `SECRET_KEY`, database URL, Redis URL, MinIO credentials, integration API keys.

## Compliance hooks (5.0 Compliance Center)

| Regulation         | Platform support                                        |
| ------------------ | ------------------------------------------------------- |
| **CROA**           | Consent tracking, disclosure workflows                  |
| **FCRA**           | Dispute timing, investigation status, response tracking |
| **FDCPA**          | Collection account flags, communication limits          |
| **CFPB**           | Complaint generation and tracking                       |
| **Data retention** | Configurable retention policies per org                 |

Account intelligence fields (`dispute_status`, `investigation_status`, `next_eligible_dispute_date`) align with FCRA dispute workflow requirements.

## Security monitoring (5.0)

- Failed login rate limiting
- Anomaly detection on bulk exports
- Alerting on privilege escalation changes

## Incident response

1. Rotate `SECRET_KEY` and invalidate refresh tokens
2. Review audit/timeline logs for affected org
3. Patch and deploy via CI pipeline
4. Document in post-incident ADR if architectural change required

## Related documents

- [API Standards — auth errors](api-standards.md#authentication)
- [ADR 004 — JWT with refresh tokens](../adr/README.md)
- [Data Model — audit fields](data-model.md#global-conventions)
