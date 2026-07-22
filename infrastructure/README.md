# Infrastructure

Supporting config for local and deployed stacks.

| Path        | Purpose                                              |
| ----------- | ---------------------------------------------------- |
| `nginx/`    | Reverse proxy (`default.conf`) and web static config |
| `postgres/` | Init SQL for first container boot                    |
| `scripts/`  | Ops helper scripts                                   |
| `docker/`   | Extra Docker assets (if present)                     |

Compose entrypoints live at the repo root (`docker-compose.yml`, `docker-compose.local-pilot.yml`, `docker-compose.prod.yml`). See [docs/deployment/README.md](../docs/deployment/README.md).
