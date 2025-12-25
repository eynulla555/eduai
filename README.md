# EduAI

Blueprint for a Duolingo-style Q&A and practice platform for grades 1–4 that works with image-heavy textbooks and OpenAI 4o mini.

## What this repo contains
- `docs/ARCHITECTURE.md`: architecture, data model, API surface, prompts, and roadmap.

## Quick start (recommended stack)
1. Backend: FastAPI + Celery/RQ; Postgres + pgvector; Redis; S3-compatible storage (MinIO in dev).
2. Frontend: React/Next.js (responsive web) with a child-friendly theme; or Flutter if mobile-first.
3. AI: OpenAI 4o mini for generation; OpenAI embeddings for RAG.

## MVP priorities
- Upload + OCR + page/exercise detection for a handful of legally usable pages.
- Page viewer with exercise hotspots and a Q&A thread per exercise.
- RAG `/ask` endpoint with cited snippets, hint/full-answer modes, and safety filters.
- Basic child mode (large buttons, stars) and TTS playback.

See the full blueprint in `docs/ARCHITECTURE.md` for detailed flows and milestones.

## Quick “show me something working” path
1. **Bootstrap the stack**
   - Run `docker compose up -d postgres minio redis` (compose file should expose ports 5432/9000/6379).
   - Create a `.env` with `OPENAI_API_KEY`, `DATABASE_URL`, `REDIS_URL`, `S3_ENDPOINT`, `S3_BUCKET`, `S3_KEY`, `S3_SECRET`.
2. **Scaffold backend (FastAPI)**
   - Create `app/main.py` with `/healthz`, `/upload`, `/page/{id}`, and `/exercise/{id}/ask` routes.
   - Add Celery/RQ worker (`worker.py`) that consumes upload jobs, runs OCR, stores crops to S3, and writes metadata to Postgres/pgvector.
   - Provide a seed script (`scripts/seed_sample_pages.py`) to insert one subject/unit and a few sample pages for manual testing.
3. **Scaffold frontend (Next.js)**
   - Pages: `/` (grade/subject grid), `/unit/[id]/page/[page]` (viewer), `/exercise/[id]` (chat thread).
   - Components: page image viewer with hotspots, chat panel with answer/hint toggle, TTS button using `SpeechSynthesis`.
4. **Prove the loop**
   - Upload a single PDF page; verify OCR regions; issue `curl -X POST /exercise/{id}/ask -d '{"question":"Bu tapşırığın cavabı nədir?"}'` and confirm cited response.
   - Add a “Try similar problem” button that calls `/exercise/{id}/ask` with mode `similar` to generate practice.

See `docs/EXECUTION_PLAYBOOK.md` for a day-by-day build script and validation checks.
