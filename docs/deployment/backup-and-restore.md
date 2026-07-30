# Staging Backup and Restore

Scripts (run on the droplet from `/opt/lrp/app`):

| Script                          | Purpose                                     |
| ------------------------------- | ------------------------------------------- |
| `scripts/backup-production.sh`  | Dump Postgres + archive MinIO volume        |
| `scripts/restore-production.sh` | Destructive restore with typed confirmation |

## Backup

```bash
cd /opt/lrp/app
./scripts/backup-production.sh
```

Creates `backups/<UTC-timestamp>/`:

- `postgres.sql.gz` — `pg_dump` of the staging database
- `minio-data.tar.gz` — MinIO `/data` directory
- `manifest.txt` — hostname / DB metadata

Copy backups **off the droplet** (Spaces, another region, or encrypted object storage). Droplet-local copies alone are not disaster recovery.

## Restore

```bash
./scripts/restore-production.sh backups/20260730T120000Z
# Prompt: type RESTORE-STAGING
```

Effects:

1. Stops api / worker / web / caddy
2. Reloads Postgres from the dump
3. Replaces MinIO volume contents
4. Restarts the application stack

## Policy

Restored data must remain **staging/demo only**. Do not restore production borrower databases, real credit reports, SSNs, or identity document buckets into staging.

## Schedule (recommended)

- Daily automated backup via cron + offsite sync
- Retain ≥ 7 daily + 4 weekly copies off-droplet
- Test restore quarterly on a scratch path or snapshot
