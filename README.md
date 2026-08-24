# Advanced RAG Platform

Secure, multi-tenant Retrieval-Augmented Generation (RAG) platform.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker and Docker Compose

## First-time setup

Run these commands from the project root:

```bash
cp .env.example .env
uv sync
docker compose up -d postgres redis
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

The API is then available at `http://localhost:8000`.

## Docker Compose commands

Start all services:

```bash
docker compose up -d
```

Start only PostgreSQL and Redis for local API development:

```bash
docker compose up -d postgres redis
```

Check service status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
docker compose logs -f postgres
docker compose logs -f api
docker compose logs -f worker
```

Stop services while retaining database data:

```bash
docker compose stop
```

Stop and remove containers while retaining database data:

```bash
docker compose down
```

Remove containers **and the local PostgreSQL volume** (this permanently deletes
local database data):

```bash
docker compose down -v
```

## Database commands

Apply all migrations:

```bash
uv run alembic upgrade head
```

Show the current migration revision:

```bash
uv run alembic current
```

Show migration history:

```bash
uv run alembic history
```

Validate that ORM models and migrations are aligned:

```bash
uv run alembic check
```

Open a PostgreSQL shell in the Compose database:

```bash
docker compose exec postgres psql -U rag -d rag
```

Useful commands inside `psql`:

```sql
\dt
SELECT * FROM alembic_version;
\q
```

## Development checks

```bash
make lint
make type-check
make test
```

## Development authentication

While `APP_DEV_AUTH_ENABLED=true`, protected development endpoints require
these headers:

```bash
curl http://localhost:8000/api/v1/me \
  -H 'X-User-Id: user-demo' \
  -H 'X-Tenant-Id: tenant-demo'
```

This header-based adapter is for local development only and will be replaced by
validated bearer-token authentication before production use.
