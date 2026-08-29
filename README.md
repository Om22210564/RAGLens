# RAGLens

RAGLens is a secure, multi-tenant Retrieval-Augmented Generation platform with
an engineering console for building and inspecting grounded AI workflows.

## Features

- **Hybrid retrieval** combining dense semantic search with BM25 sparse search.
- **Query transformation and reranking** for stronger retrieval on complex questions.
- **Grounded answers and citations** tied to tenant-scoped document chunks.
- **Security guardrails** for prompt injection, secrets, unsafe context, and output checks.
- **Tracing** for retrieval stages, latency, answerability, and security events.
- **Evaluation** with Recall@K, Precision@K, Hit Rate@K, MRR, and nDCG@K.
- TXT, Markdown, HTML, and PDF ingestion with background processing.
- Optional sentence-transformer embeddings and Groq generation.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker with Docker Compose
- Node.js 20+
- pnpm

## Setup

```bash
cp .env.example .env
uv sync
docker compose up -d postgres redis
uv run alembic upgrade head
```

The configured host ports are PostgreSQL `5434` and Redis `6381`.

Start the backend API:

```bash
uv run uvicorn app.main:app --reload
```

Start the ingestion worker in another terminal:

```bash
uv run dramatiq app.workers.ingestion
```

Start the frontend:

```bash
cd frontend
cp .env.example .env.local
pnpm install
pnpm dev
```

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

## Important commands

```bash
# Infrastructure
docker compose up -d postgres redis
docker compose ps
docker compose logs -f
docker compose down

# Database migrations
uv run alembic upgrade head
uv run alembic current
uv run alembic history
uv run alembic check
docker compose exec postgres psql -U rag -d rag

# Backend quality checks
make format
make lint
make type-check
make test

# Frontend quality checks
cd frontend
pnpm lint
pnpm type-check
pnpm build
```

To remove containers and permanently delete the local PostgreSQL volume:

```bash
docker compose down -v
```

## Provider configuration

The default configuration uses sentence-transformer embeddings and Groq. Add a
valid key to your local `.env`; never commit it.

```env
APP_EMBEDDING_PROVIDER=sentence_transformer
APP_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
APP_LLM_PROVIDER=groq
APP_GROQ_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=your_groq_api_key
```

After changing the embedding model for an existing database, apply migrations
and rebuild stored embeddings:

```bash
uv run alembic upgrade head
uv run python -m app.ingestion.reindex
```

Restart the API and ingestion worker afterward.

## Development authentication

Protected API requests use development headers while
`APP_DEV_AUTH_ENABLED=true`:

```http
X-User-Id: user-demo
X-Tenant-Id: tenant-demo
```

This header adapter is for local development only.

## Evaluation

Score retrieval results against a JSONL dataset:

```bash
uv run python -m app.evaluation score \
  --dataset datasets/rag_eval.jsonl \
  --results reports/retrieval_results.jsonl \
  --k 5 \
  --output reports/evaluation.json
```

Dataset rows require `id` and `relevant_chunk_ids`; result rows require the
matching `id` and `retrieved_chunk_ids`.
