# AI Knowledge Inbox

A small personal tool for saving notes and URLs, then asking questions about them. It's built as a simple RAG (retrieval-augmented generation) pipeline, meant for a single user running it locally, with no login required.

## How it's put together

The frontend is a React + Vite app, written in plain JavaScript and styled with Tailwind. It talks to a FastAPI backend that handles everything else: fetching and cleaning URL content, validating notes, splitting text into chunks, generating embeddings with a local sentence-transformers model, storing everything in SQLite, and calling Groq to generate answers. The backend exposes three main routes: `POST /ingest`, `GET /items`, and `POST /query`.

Each part of the backend has one job. Routers parse requests, hand off to services, and shape responses. Services do the actual work. The only places that write raw SQL are `db.py`, `vector_store.py`, and `items_repository.py`; routers just open a connection and pass it along when a request needs one transaction across two of those services.

## Running it locally

### Backend

Open a terminal in the `backend` folder and set up a virtual environment:

```bash
cd backend
python -m venv venv
./venv/Scripts/activate        # on macOS/Linux use: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # then add your GROQ_API_KEY (get a free one at https://console.groq.com/keys)
uvicorn app.main:app --reload --port 8000
```

The first time you run it, it'll download the embedding model (`all-MiniLM-L6-v2`, about 80MB). After that it's cached locally, so startup is fast.

### Frontend

In a separate terminal:

```bash
cd frontend
npm install
cp .env.example .env           # sets VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev                    # opens at http://localhost:5173
```

## The API

Every error comes back in the same shape: `{"error": {"code": "...", "message": "..."}}`. Requests that don't match the expected schema (wrong types, missing fields) get a 422 from Pydantic; requests that are well-formed but fail a business rule (like a missing `url` for `source_type: "url"`) get a 400 from the app itself.

`POST /ingest` accepts either `{"source_type": "note", "text": "..."}` or `{"source_type": "url", "url": "..."}`. It returns 201 on success, 400 if the input fails validation, and 502 if a URL can't be fetched.

`GET /items` returns everything you've saved so far, newest first, along with a preview and chunk count for each.

`POST /query` takes `{"question": "...", "top_k": 4}` (top_k is optional). It returns 400 for an empty question and 502 if the LLM call fails.

`GET /health` is just a liveness check.

The full request and response schemas are enforced by Pydantic, so `backend/app/models.py` is the source of truth if you want the details.

## Why it's built this way

**Chunking.** Text gets split into roughly 800-character windows with about 120 characters of overlap, and it tries to break on sentence or paragraph boundaries rather than cutting mid-word. This avoids needing a tokenizer and is easy to reason about. A fancier structure-aware chunker would probably retrieve better on long, heavily formatted documents, but that's overkill for short notes and articles at single-user scale.

**Embeddings.** These run locally via sentence-transformers instead of a hosted API. Groq, which handles the LLM side, doesn't offer embeddings, and bringing in a second paid provider just for that didn't seem worth it. The tradeoff is a bit of latency on the first request while the model loads, and encoding happens on CPU, but that's totally fine at the volume one person generates.

**Vector store.** Chunks and their embeddings live in SQLite, and similarity search is just cosine similarity computed in-process with numpy. No extra infrastructure to run, everything is easy to inspect, and it survives restarts. It's a linear scan under the hood, which stays fast up to a few thousand chunks. That comfortably covers a personal inbox.

## Where this would start to creak

This is built for one person, not scale, so a few things would need to change before it could handle more:

The linear scan over embeddings would become the bottleneck somewhere in the tens of thousands of chunks, since query time grows with corpus size. SQLite also doesn't have a real story for concurrent writes, which is fine for one user but not for many. And everything, including the embedding model, runs inside the same process as the API, so a slow embed or LLM call blocks whatever else is happening. There's also no pagination on `/items` yet, so a big inbox just returns everything at once.

If this were headed toward production, the natural next steps would be swapping the linear scan for a proper ANN index like pgvector or Qdrant, moving embedding and URL fetching into a background job queue so `/ingest` can return immediately, adding auth and per-user data if it stops being single-user, adding pagination and rate limiting, and eventually moving off a local SQLite file to a networked database.

## Debugging

Logs are structured JSON (see `backend/app/logging_config.py`), and every request gets an ID that's threaded through its log lines and returned in the `X-Request-Id` header, so a single request's story is easy to follow.

Every expected failure, bad input, an unreachable URL, an embedding failure, an LLM failure, is its own typed `AppError` subclass mapped to a specific status code and error code (see `backend/app/exceptions.py`). Anything unexpected gets caught by a global handler, logged with full detail on the server, and turned into a generic message for the client.
