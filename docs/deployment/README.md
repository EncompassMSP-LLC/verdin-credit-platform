# Deployment docs

| Document                                       | Purpose                                        |
| ---------------------------------------------- | ---------------------------------------------- |
| [guide.md](guide.md)                           | Primary deployment guide                       |
| [production.md](production.md)                 | Production notes                               |
| [local-docker-pilot.md](local-docker-pilot.md) | Local pilot stack (Mailpit, `.env.production`) |

## Compose files (repo root)

| File                             | Use                                                                             |
| -------------------------------- | ------------------------------------------------------------------------------- |
| `docker-compose.yml`             | Day-to-day local stack (nginx `:80`, web `:3000`, api `:8000`)                  |
| `docker-compose.local-pilot.yml` | Pilot-like stack (Mailpit, production-ish env via `--env-file .env.production`) |
| `docker-compose.prod.yml`        | Production-oriented compose                                                     |

```bash
# Default local
docker compose up

# Local pilot (uses .env.production)
docker compose -f docker-compose.local-pilot.yml --env-file .env.production up -d
```

See also: [root README — Environment files](../README.md).
