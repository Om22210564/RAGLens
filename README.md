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

The default host ports are PostgreSQL `5434` and Redis `6381`, avoiding common
conflicts with local services. Change both the corresponding `*_HOST_PORT` and
the host URL in `.env` if you need different ports.

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

After pulling a Phase 1 update, apply the latest document-ingestion migration:

```bash
uv sync
uv run alembic upgrade head
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

## Upload a document

Start the worker in a second terminal so queued ingestion jobs are processed:

```bash
uv run dramatiq app.workers.ingestion
```

Then upload a supported TXT, Markdown, HTML, or PDF file:

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -H 'X-User-Id: user-demo' \
  -H 'X-Tenant-Id: tenant-demo' \
  -F 'file=@./example.md;type=text/markdown'
```

The response returns a `document_id` and `ingestion_job_id`. Check its state:

```bash
curl http://localhost:8000/api/v1/documents/DOCUMENT_ID \
  -H 'X-User-Id: user-demo' \
  -H 'X-Tenant-Id: tenant-demo'
```

## Ask a grounded question

Once the document state is `ready`, query only the documents available to your
tenant. The response includes an answerability signal, source citations, and a
trace ID.

```bash
curl -X POST http://localhost:8000/api/v1/queries \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: user-demo' \
  -H 'X-Tenant-Id: tenant-demo' \
  -d '{"query":"What is this project for?","top_k":5}'
```

For complex comparison questions, opt into deterministic decomposition and the
local reranker. Both run only after tenant-scoped retrieval has applied access
filters.

```bash
curl -X POST http://localhost:8000/api/v1/queries \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: user-demo' \
  -H 'X-Tenant-Id: tenant-demo' \
  -d '{"query":"Compare dense retrieval and BM25","transform":true,"rerank":true}'
```

The response includes `rewritten_queries` so transformed retrieval can be
inspected. The local lexical reranker is a baseline; its interface supports a
cross-encoder or external reranking provider later.

The initial generator is an extractive, local baseline. It only returns text
from retrieved evidence and citations; a provider-backed LLM adapter can be
configured in a later phase without changing the API.

## Traces and evaluation

Apply the Phase 5 trace migration before using the query endpoint:

```bash
uv run alembic upgrade head
```

Every successful query response includes a `trace_id`. Retrieve its sanitized,
tenant- and owner-scoped inspection record with:

```bash
curl http://localhost:8000/api/v1/traces/TRACE_ID \
  -H 'X-User-Id: user-demo' \
  -H 'X-Tenant-Id: tenant-demo'
```

The offline evaluation CLI scores JSONL retrieval output. Dataset rows need an
`id` and `relevant_chunk_ids`; result rows need the matching `id` and
`retrieved_chunk_ids`.

```bash
uv run python -m app.evaluation score \
  --dataset datasets/rag_eval.jsonl \
  --results reports/retrieval_results.jsonl \
  --k 5 \
  --output reports/evaluation.json
```

The report contains Recall@K, Precision@K, Hit Rate@K, MRR, and nDCG@K.
