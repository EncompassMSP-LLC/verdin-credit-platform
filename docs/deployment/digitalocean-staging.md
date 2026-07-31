# DigitalOcean Staging Deployment

Secure staging for **EncompassMSP-LLC / verdin-credit-platform** on a single Ubuntu 24.04 Droplet using Docker Compose + Caddy.

| Item           | Value                                   |
| -------------- | --------------------------------------- |
| Droplet        | Basic · 2 vCPU · 4 GB RAM · 80 GB SSD   |
| OS             | Ubuntu 24.04 LTS                        |
| App path       | `/opt/lrp/app`                          |
| Hostname       | `app.<DOMAIN>` (platform only)          |
| Marketing site | InfinityFree (separate; not this stack) |
| Public ports   | **22, 80, 443 only**                    |
| Compose file   | `docker-compose.production.yml`         |
| Data policy    | Staging / demo / synthetic **only**     |

Local development continues to use `docker-compose.yml` unchanged.

## Architecture

```
Internet → :80/:443 Caddy (TLS) → web (SPA) + api (FastAPI)
                │
                ├── api → postgres, redis, minio
                └── worker → postgres, redis, minio
```

Internal services **do not** publish host ports.

## One-time server setup

1. Create the Droplet (Ubuntu 24.04, SSH key auth, no password login).
2. Configure UFW:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

3. Install Docker Engine + Compose plugin (official Docker docs for Ubuntu).
4. Point DNS `A`/`AAAA` for `app.<DOMAIN>` at the droplet.
5. Clone the repo:

```bash
sudo mkdir -p /opt/lrp
sudo chown "$USER:$USER" /opt/lrp
git clone git@github.com:EncompassMSP-LLC/verdin-credit-platform.git /opt/lrp/app
cd /opt/lrp/app
```

6. Create secrets file:

```bash
cp .env.production.example .env.production
# Fill SECRET_KEY, DB/MinIO passwords, APP_HOSTNAME, CADDY_ACME_EMAIL, URLs
chmod 600 .env.production
```

Generate secrets:

```bash
openssl rand -hex 32   # SECRET_KEY
openssl rand -hex 24   # passwords
```

7. Deploy:

```bash
chmod +x scripts/*.sh
./scripts/deploy-production.sh
```

8. Confirm:

```bash
curl -fsS "https://app.<DOMAIN>/api/v1/health"
curl -fsS "https://app.<DOMAIN>/api/v1/health/ready"
```

## GitHub Actions (manual)

Workflow: `.github/workflows/staging-deploy.yml` (`workflow_dispatch` only — **not** on every merge).

Required repository secrets:

| Secret             | Purpose                         |
| ------------------ | ------------------------------- |
| `STAGING_HOST`     | Droplet IP or hostname          |
| `STAGING_USER`     | SSH user (e.g. `deploy`)        |
| `STAGING_SSH_KEY`  | Private key (ed25519 preferred) |
| `STAGING_APP_PATH` | Absolute path (`/opt/lrp/app`)  |

Trigger: Actions → **Staging Deploy (DigitalOcean)** → type `deploy-staging` → choose git ref.

The droplet must already contain a configured `.env.production` (secrets are not pushed from GitHub).

## Feature flags (staging defaults)

| Flag                       | Default | Notes                                   |
| -------------------------- | ------- | --------------------------------------- |
| `ENABLE_CLIENT_PORTAL`     | true    | Required for borrower portal staging    |
| `ENABLE_AI` / `ENABLE_LLM` | false   | Unfinished AI surfaces off              |
| `ENABLE_ENTERPRISE`        | false   | Unfinished enterprise surfaces off      |
| `ENABLE_EMAIL_DELIVERY`    | false   | Prefer `EMAIL_PROVIDER=microsoft_graph` |
| `VITE_ENABLE_*` mirrors    | same    | Rebuild `web` after changing Vite flags |

### Microsoft 365 email (Graph / OAuth)

Prefer Graph over SMTP app passwords:

1. Entra ID → App registration → create app (single tenant).
2. Certificates & secrets → create a **client secret**.
3. API permissions → Microsoft Graph → **Application** → `Mail.Send` → **Grant admin consent**.
4. Set on the droplet `.env.production`:

```env
ENABLE_EMAIL_DELIVERY=true
EMAIL_PROVIDER=microsoft_graph
EMAIL_FROM_ADDRESS=info@yourdomain.com
EMAIL_GRAPH_TENANT_ID=<directory-tenant-id>
EMAIL_GRAPH_CLIENT_ID=<application-client-id>
EMAIL_GRAPH_CLIENT_SECRET=<client-secret-value>
```

5. Recreate API: `docker compose -f docker-compose.production.yml --env-file .env.production up -d --force-recreate api`
6. Org Admin → Email delivery → **Send test email**.

`EMAIL_FROM_ADDRESS` must be a real mailbox (user or shared) the app can send as.

## Data policy (mandatory)

**Never** place in staging:

- Real credit reports or bureau pulls
- Real SSNs / ITINs
- Government ID scans or selfies
- Production borrower PII dumps
- Live Stripe / bureau credentials

Use demo orgs, synthetic accounts, and redacted fixtures only. See [security-checklist.md](./security-checklist.md).

## Related docs

- [security-checklist.md](./security-checklist.md)
- [backup-and-restore.md](./backup-and-restore.md)
- [rollback.md](./rollback.md)
- Legacy pilot notes: [production.md](./production.md), [local-docker-pilot.md](./local-docker-pilot.md)
