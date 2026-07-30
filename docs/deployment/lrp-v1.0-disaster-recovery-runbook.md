# LRP Platform V1.0 — Disaster Recovery Runbook

**Edition:** Lending Readiness Platform™ on the shared Verdin stack  
**Tag:** `lrp-platform-v1.0.0`  
**Audience:** On-call engineering / Ops  
**Related:** [`production.md`](production.md) · Vol 24 architecture · [`lrp-v1.0-security-officer-signoff.md`](../quality/security/lrp-v1.0-security-officer-signoff.md)

---

## 1. Objectives

| Metric  | Draft target (founder may tighten) | Notes                                      |
| ------- | ---------------------------------- | ------------------------------------------ |
| **RPO** | ≤ 24 hours                         | Nightly Postgres dump; object storage sync |
| **RTO** | ≤ 24 hours for core API + LRP web  | Single-region pilot; no hot standby yet    |

LRP shares Postgres, Redis, object storage, API, and worker with the platform. There is **no separate LRP database**. Recovery restores the shared stack, then validates LRP-specific smoke.

---

## 2. Critical components

| Component        | Role for LRP                                               | Data criticality      |
| ---------------- | ---------------------------------------------------------- | --------------------- |
| PostgreSQL       | Orgs, partnerships, referrals, automations, readiness runs | **Critical**          |
| Object storage   | Case documents, exports, letter drafts                     | **Critical**          |
| Redis            | Job queue (ephemeral OK if jobs can re-enqueue)            | Important             |
| API (`apps/api`) | Mortgage-partner + portal APIs                             | **Critical**          |
| Worker           | Reminders, nurture, digests, OCR                           | Important             |
| `apps/lrp-web`   | CRM / lender / portal / marketing                          | Important (stateless) |

Feature flag: `ENABLE_MORTGAGE_PARTNER=true` must be set in the recovered environment.

---

## 3. Backup inventory

Align with [`production.md` §7](production.md):

| Data       | Method                                            | Cadence          | Retention (draft) |
| ---------- | ------------------------------------------------- | ---------------- | ----------------- |
| PostgreSQL | `pg_dump` (or managed backup)                     | Nightly          | ≥ 14 days         |
| Objects    | Volume snapshot or `mc mirror` / S3 versioning    | Nightly or cont. | ≥ 14 days         |
| Secrets    | Secret manager / sealed `.env.production` offline | On change        | N/A               |
| Images     | Container registry tags matching release          | Per deploy       | Keep V1.0 tag     |

### 3.1 Nightly Postgres dump (example)

```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U verdin verdin_credit | gzip > /backups/verdin-$(date -u +%F).sql.gz
```

Store dumps off-box (S3 / encrypted disk). Record path + checksum in the ops log.

### 3.2 Object storage

```bash
# Example: mirror MinIO bucket to durable S3
mc mirror minio/verdin-documents s3/verdin-documents-backup
```

Prefer provider versioning once off local MinIO volumes.

---

## 4. Restore procedures

### 4.1 Postgres restore (staging first)

1. Provision empty Postgres matching major version.
2. Stop API/worker writers (`docker compose stop api worker` or scale to 0).
3. Restore:

```bash
gunzip -c verdin-YYYY-MM-DD.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U verdin verdin_credit
```

4. Confirm migration head: `alembic current` should match release expectations (V1.0 includes through `114_crm_automation_audit`).
5. Start API/worker; hit `/api/v1/health` and `/api/v1/health/ready`.

**Never** test first restore against production. Use staging with anonymized or scrubbed dump when possible.

### 4.2 Object storage restore

1. Restore bucket/prefix from snapshot or mirror.
2. Spot-check a known document download via authenticated Documents API for a restored case.
3. Confirm CRM borrower workspace documents list for that case.

### 4.3 Application rollback to tagged release

```bash
git fetch --tags
git checkout lrp-platform-v1.0.0
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Pin images/tags to the release commit when using a registry.

---

## 5. LRP post-restore smoke (required)

Run after API is ready (`ENABLE_MORTGAGE_PARTNER=true`):

| #   | Check                                                   | Pass criteria                    |
| --- | ------------------------------------------------------- | -------------------------------- |
| 1   | `GET /api/v1/health` + `/health/ready`                  | 200                              |
| 2   | Staff login                                             | Tokens issued                    |
| 3   | `GET /api/v1/mortgage-partner/status`                   | `mortgage_partner_enabled: true` |
| 4   | List partnerships / pipeline for a known org            | 200; no cross-tenant leakage     |
| 5   | Readiness report for a known referral (if data present) | 200; disclaimer present          |
| 6   | Automation rules list + dry-run fire                    | 200/201; audit event written     |
| 7   | `apps/lrp-web` login → CRM partners or lender pipeline  | UI loads without demo-only path  |

Optional: re-run harness `docs/quality/performance/measure_lrp_perf_budgets.py` in observe mode against staging.

CI reference smoke: `tests/e2e/test_lrp_smoke.py` (requires full stack).

---

## 6. Incident roles & communication

| Role               | Responsibility                                     |
| ------------------ | -------------------------------------------------- |
| Incident commander | Founder or designated eng on-call                  |
| Tech lead          | Execute restore; decide cutover                    |
| Comms              | Partner/status email; no score/approval guarantees |
| Compliance         | If PII exposure suspected, start breach checklist  |

Comms rules (claim library):

- Do **not** promise restored FICO outcomes or underwriting decisions.
- State operational status only (API degraded / restored).

---

## 7. Failover notes (V1.0 pilot)

- Single-region / single-node compose is the documented pilot posture.
- No automated multi-AZ failover in V1.0.
- If region loss: provision new host → restore backups → smoke → update DNS.
- Track cloud region lock + signed RPO/RTO in Vol 24 founder checklist.

---

## 8. Backup restore test log (Ops)

Perform at least **monthly** in staging. Record here or link to ticket:

| Date | Environment | Dump used | RTO observed | Issues | Operator |
| ---- | ----------- | --------- | ------------ | ------ | -------- |
|      |             |           |              |        |          |

---

## 9. Monitoring verification (post-incident / monthly)

| Signal                     | Check                                             |
| -------------------------- | ------------------------------------------------- |
| Uptime                     | External probe on `/api/v1/health/ready`          |
| Disk                       | Alerts on Postgres + object volumes               |
| Errors                     | Error tracker / log spike review                  |
| LRP feature flag           | Confirm `ENABLE_MORTGAGE_PARTNER` in prod secrets |
| Perf observe artifact (CI) | Spot-check latest `lrp-perf-budgets` artifact     |

---

## 10. Approval

| Role                  | Name | Date       | Sign-off        |
| --------------------- | ---- | ---------- | --------------- |
| Engineering           |      | 2026-07-30 | Runbook drafted |
| Ops / on-call lead    |      |            | ☐               |
| Founder (RPO/RTO ack) |      |            | ☐               |
