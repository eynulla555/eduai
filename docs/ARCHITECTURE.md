# EduAI Platform Blueprint

Concrete, buildable plan for a primary-school Q&A and practice platform (grades 1–4) that works with image-heavy textbooks and OpenAI 4o mini.

## 1. Product pillars
- **Fast answers for parents**: upload or pick an indexed page → ask → get cited answer or hints.
- **Kid-friendly practice**: child mode with large buttons, stars, streaks, and audio read-out.
- **Curriculum alignment**: grade/subject/unit tagging; avoid off-topic/unsafe responses.
- **Low-friction onboarding**: start with one grade + subject to validate.

## 2. User flows
1. **Onboarding**: pick grade → pick subject → choose sample page or upload → guided first question.
2. **Page viewer**: view page image, see detected exercises, tap an exercise, ask or request hints.
3. **Q&A thread**: per page/exercise; show cited snippets + optional cropped images; modes: short answer, explain like I’m 7, step-by-step hint.
4. **Child practice mode**: limited navigation, big touch targets, rewards; “Try similar problem” button.

## 3. Architecture overview
- **Frontend**: React/Next.js web (responsive) or Flutter if mobile-first; design system with cards for subjects and bottom navigation on mobile.
- **Backend**: FastAPI (Python) with Celery/RQ for background jobs. REST endpoints plus optional WebSocket for streaming answers.
- **Data layer**: Postgres for metadata + pgvector for embeddings; Redis for queues and rate limits.
- **Storage**: S3-compatible bucket (MinIO in dev) for page images, thumbnails, and cropped exercise regions.
- **AI**: OpenAI 4o mini for generation; OpenAI embeddings (or text-embedding-3-small) for indexing.

## 4. Ingestion & OCR pipeline
- `POST /upload` enqueues processing for PDF or image uploads.
- PDFs: extract pages via `pypdf` or `pdfplumber`; images: `pytesseract` + `opencv` for text/region detection.
- Store per-exercise metadata: grade, subject, unit, page number, region coordinates, OCR text, OCR confidence.
- Generate thumbnails and per-exercise crops; cache in object storage.
- `GET /page/{id}` returns structured page data (image URL + exercise list with bounding boxes).

## 5. Retrieval-Augmented Generation (RAG)
- Chunk content by exercise; embed text + captions; store in pgvector with exercise/page IDs.
- `/ask` endpoint: question + page/exercise ref → retrieve top-k chunks → call 4o mini with safety/age-appropriate system prompt → return answer + cited snippets.
- Modes: short answer, explain-like-7yo, step-by-step hints, multiple-choice distractors.
- Include cropped image URLs in the prompt when available; note OCR confidence so the model can ask for clarification if low.

### Prompt scaffold (system)
“You are a patient primary-school tutor. Keep language simple and age-appropriate. Prefer step-by-step hints unless the user explicitly requests the full answer. Stay on curriculum, avoid unsafe/off-topic topics. If information is missing or OCR looks unsure, ask a brief clarifying question.”

### Prompt scaffold (user/context bundle)
- Grade, subject, unit, page, exercise number
- Extracted exercise text and caption
- OCR confidence flag and any manual corrections
- Retrieved snippets with citations + optional image crop URLs
- Requested mode (hint vs. full answer, explain-like-7yo, multiple-choice)

## 6. Safety & quality
- Input filters for profanity/PII; enforce per-mode behavior (don’t reveal full solution in hint mode).
- Rate limiting per parent account/IP.
- Logging + feedback buttons (helpful? report) feeding an internal review queue.
- Weekly review of answers and retrieval to improve prompts and chunking.

## 7. Data model (starter)
- `grades` (id, label)
- `subjects` (id, grade_id, name)
- `units` (id, subject_id, title)
- `pages` (id, unit_id, page_number, image_url, thumbnail_url)
- `exercises` (id, page_id, exercise_number, bbox, ocr_text, ocr_confidence, crop_url)
- `vectors` (exercise_id, embedding vector)
- `threads` (id, user_id, exercise_id, created_at)
- `messages` (id, thread_id, role, content, citations, created_at)

### Minimal DDL sketch
```sql
CREATE TABLE pages (
  id SERIAL PRIMARY KEY,
  unit_id INT REFERENCES units(id),
  page_number INT,
  image_url TEXT,
  thumbnail_url TEXT
);

CREATE TABLE exercises (
  id SERIAL PRIMARY KEY,
  page_id INT REFERENCES pages(id),
  exercise_number TEXT,
  bbox JSONB,
  ocr_text TEXT,
  ocr_confidence NUMERIC,
  crop_url TEXT
);

CREATE TABLE vectors (
  exercise_id INT PRIMARY KEY REFERENCES exercises(id),
  embedding VECTOR(1536)
);
```

## 8. API surface (initial)
- `POST /upload` – upload PDF/image; returns job id and detected metadata.
- `GET /page/{id}` – page metadata + exercises + image URLs.
- `POST /exercise/{id}/ask` – question + mode; returns answer + citations.
- `GET /threads/{id}` – Q&A history for that exercise/page.
- `POST /feedback` – message_id + rating/reason.

### Example: ask endpoint
```http
POST /exercise/42/ask
{
  "question": "Bu tapşırığın cavabı nədir?",
  "mode": "hint",
  "language": "az"
}
```
Response
```json
{
  "answer": "Əvvəlcə sözün hecalara bölündüyünə bax...",
  "mode": "hint",
  "citations": [
    {"page_id": 10, "exercise_id": 42, "snippet": "..."}
  ]
}
```

## 9. Frontend modules
- **Home**: grade/subject grid, recent pages.
- **Unit/Page selector**: search by page number; lazy-load thumbnails.
- **Page viewer**: tiled image, exercise hotspots, “Ask about this”, “Auto-extract questions”.
- **Chat/Q&A**: thread with cited snippets, “Show steps”, “Try similar problem”, TTS playback.
- **Child mode**: simplified nav, stars/badges, dark/high-contrast themes.

## 10. Roadmap (phased)
1. **MVP (weeks 1–3)**: scaffold FastAPI + Next.js; implement `/upload`, OCR pipeline, `/page/{id}`, basic RAG `/ask`; seed with sample pages; simple page viewer + Q&A chat.
2. **UX polish (weeks 4–6)**: exercise hotspots, hint vs. answer toggle, citations, TTS, child mode skin.
3. **Quality & safety (weeks 6–8)**: rate limits, abuse filters, feedback loop, prompt refinements, low-confidence OCR correction UI.
4. **Scale (post-MVP)**: more subjects/grades, admin tagging tools, analytics dashboards, offline-ready packs.

## 11. Operational checklist
- Python + Node toolchains; create `.env` with OpenAI key and storage/DB credentials.
- Run `docker compose up` for Postgres + MinIO + Redis.
- Seed DB with sample grade/subject/unit and a few pages; run background worker.
- Start frontend, point at API base URL, and test end-to-end on sample pages.
- Set up monitoring for worker queue depth, OCR failures, and latency of `/ask`.

## 12. Success metrics
- Response latency and answer helpfulness (thumbs up/down rate).
- Percentage of questions answered without clarifications.
- Child mode engagement: streaks completed, stars earned, repeat sessions.
- OCR quality: low-confidence rate and manual correction usage.
