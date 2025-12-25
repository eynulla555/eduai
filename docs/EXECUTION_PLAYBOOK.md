# Execution Playbook

Practical, time-boxed plan to stand up a working demo (backend + frontend + OCR/RAG loop) with OpenAI 4o mini.

## Day 1: Repo and infra scaffolding
- Create Python venv, install FastAPI, uvicorn, SQLAlchemy, pgvector, Celery/RQ, boto3/minio, pydantic, pypdf/pytesseract/opencv.
- Add `docker-compose.yml` services: `postgres`, `pgvector extension`, `redis`, `minio`.
- Create `.env.example` with required secrets/URLs; wire `docker compose up -d` to start dependencies.
- Initialize migrations (Alembic) with `grades`, `subjects`, `units`, `pages`, `exercises`, `vectors`, `threads`, `messages` tables.

## Day 2: Backend endpoints and worker
- Implement FastAPI routes:
  - `GET /healthz` (DB + Redis ping).
  - `POST /upload` → enqueue background job with file URL/upload; return job id.
  - `GET /page/{id}` → return page metadata + exercises with bounding boxes/crops.
  - `POST /exercise/{id}/ask` → accepts `{question, mode, language?, thread_id?}`.
- Build worker (`worker.py`):
  - Fetch file, split pages, OCR with `pytesseract`/`opencv`, detect regions, save crops to MinIO.
  - Persist exercises with bbox + OCR text + confidence; generate embeddings and store in `vectors`.
- Add simple rate limiting middleware (per IP/user) using Redis.

## Day 3: Retrieval + prompt wiring
- Implement retrieval helper: fetch exercise context, retrieve top-K similar exercises/snippets from `vectors` via cosine distance.
- Build prompt composer with safety rails:
  - System prompt enforcing kid-safe, hint-first behavior; refuse off-topic/profane asks.
  - User/context bundle: grade, subject, unit, page, exercise text, OCR confidence, retrieved snippets, optional crop URLs, mode.
- Call OpenAI 4o mini; return `{answer, mode, citations, next_actions?, thread_id}`.
- Add `/feedback` endpoint to log thumbs up/down and reasons.

## Day 4: Frontend skeleton (Next.js)
- Pages/components:
  - `/`: grade + subject grid; recent pages list.
  - `/unit/[id]/page/[page]`: page viewer with tiled image/zoom (OpenSeadragon or canvas), exercise hotspots, “Ask about this”.
  - `/exercise/[id]`: chat thread with cited snippets, “Show steps” vs. “Full answer”, TTS button, “Try similar problem”.
- Add shared UI kit: primary button, card grid, chat bubble, badge/star components for child mode.
- Wire API calls with SWR/React Query; show loading states and error toasts.

## Day 5: QA loop and polish
- Seed sample content via `scripts/seed_sample_pages.py` (one grade, two subjects, 3–5 pages each).
- Manual QA script:
  - Upload a page; verify OCR bounding boxes and crops are saved.
  - Call `/page/{id}` and check JSON payload matches viewer expectations.
  - Call `/exercise/{id}/ask` in modes `hint`, `answer`, `similar`, and validate citations + tone.
- Add analytics hooks (screen/ask events) and log prompts/responses with redaction of PII.

## Stretch add-ons (post-demo)
- Admin console for tagging/editing OCR text and bbox corrections.
- Offline-ready “download unit” bundle for child mode (preload pages and cached answers for common asks).
- A/B prompt templates and adjust retrieval chunking per subject (math vs. language).

## Validation checklist before demo
- ✅ Health checks: `/healthz` returns OK with DB + Redis + S3 connectivity.
- ✅ OCR & crops: at least one page with correct exercise boxes and readable crops in MinIO.
- ✅ RAG: `/exercise/{id}/ask` returns cited answers and stays age-appropriate in all modes.
- ✅ UX: can navigate grade → subject → unit → page; ask a question and hear TTS playback.
- ✅ Safety: profanity/PII filter triggers; hint mode never reveals full solution.
