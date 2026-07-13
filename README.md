# AI Knowledge Inbox

Save notes and URLs, then ask questions over them via a small RAG pipeline.
Single-user, no auth, local-first.

## Architecture

```
frontend/ (React + Vite + Tailwind, TypeScript)
  └── calls → backend/ (FastAPI)
                ├── ingestion.py   fetch + clean URL content, validate notes
                ├── chunking.py    split raw content into overlapping windows
                ├── embeddings.py  local sentence-transformers model
                ├── vector_store.py SQLite storage + in-process cosine search
                ├── llm.py         Groq chat completion for answer generation
                ├── rag.py         orchestrates retrieval → generation
                └── routers/       POST /ingest, GET /items, POST /query
                                   (SQLite file: backend/data/inbox.db)
```

Each concern lives in its own module: routers stay thin (parse → call
service → shape response), services own one job each, and nothing reaches
into SQLite directly except `db.py` / `vector_store.py` / `items_repository.py`.

## Setup

### Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # then set GROQ_API_KEY (free key: https://console.groq.com/keys)
uvicorn app.main:app --reload --port 8000
```

The embedding model (`all-MiniLM-L6-v2`, ~80MB) downloads automatically on
first use and is cached locally afterward.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env           # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev                    # http://localhost:5173
```

## API

All error responses share one shape: `{"error": {"code": "...", "message": "..."}}`.

| Endpoint | Method | Body | Notes |
|---|---|---|---|
| `/ingest` | POST | `{"source_type": "note", "text": "..."}` or `{"source_type": "url", "url": "..."}` | 201 on success, 400 on bad input, 502 if a URL can't be fetched |
| `/items` | GET | — | Returns saved items with preview + chunk count, newest first |
| `/query` | POST | `{"question": "...", "top_k": 4}` | `top_k` optional (defaults to 4); 502 if the LLM call fails |
| `/health` | GET | — | Liveness check |

Full request/response schemas are enforced by Pydantic — see `backend/app/models.py`.

## Design tradeoffs

**Chunking** — fixed ~800-character windows with ~120-character overlap,
preferring to break on sentence/paragraph boundaries over hard character
cuts (`backend/app/services/chunking.py`). No tokenizer dependency, cheap to
reason about, and overlap avoids losing context that straddles a boundary.
A semantic/structure-aware chunker (split by heading, adaptive size) would
retrieve better on long structured documents, but isn't worth the complexity
for short notes and articles at single-user scale.

**Embeddings** — local `sentence-transformers` model instead of a hosted
embeddings API. Groq (the LLM provider used here) doesn't expose embeddings,
and adding a second paid provider just for that would be more moving parts
for no real benefit at this scale. Tradeoff: first-request latency to load
the model, and CPU-bound encoding — both fine for single-user volume, not
fine for high concurrent throughput.

**Vector store** — SQLite for persistence, cosine similarity computed
in-process with numpy at query time (`vector_store.py`). No extra
infrastructure, trivially inspectable, persists across restarts. This is a
linear scan: it stays fast (low milliseconds) up to a few thousand chunks,
which comfortably covers a personal inbox.

**What breaks at scale** —
- Linear scan becomes the bottleneck once chunk count reaches the tens of
  thousands; query latency grows linearly with corpus size.
- SQLite has no built-in concurrent-write scaling story — fine for one user,
  not for many simultaneous ingesters.
- Everything, including the embedding model, runs in the same process as
  the API — a slow embed or LLM call blocks that worker.
- No pagination on `/items` — a large inbox returns everything in one
  response.

**Production changes** —
- Swap the linear scan for an ANN index (pgvector, Qdrant, or a managed
  vector DB) once corpus size or query volume justifies it.
- Move embedding generation and URL fetching to a background job queue so
  `/ingest` returns immediately and heavy work happens asynchronously.
- Add auth + per-user partitioning if this stops being single-user.
- Add pagination/cursoring to `/items` and rate limiting to `/query`.
- Replace the in-process SQLite file with a networked database once more
  than one API instance needs to share state.

## Debuggability

- Structured JSON logs (`backend/app/logging_config.py`) with a per-request
  ID threaded through every log line and returned as `X-Request-Id`.
- Every expected failure mode (bad input, unreachable URL, embedding
  failure, LLM failure) is a typed `AppError` subclass mapped to a specific
  HTTP status and error code — see `backend/app/exceptions.py`.
- Unexpected exceptions are caught by a global handler and logged with
  detail server-side while returning a generic message to the client.
