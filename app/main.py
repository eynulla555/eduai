from __future__ import annotations

from typing import Dict, List

from fastapi import FastAPI, HTTPException, UploadFile

from . import data
from .models import AskRequest, AskResponse, HealthResponse, PageResponse, UploadResponse

app = FastAPI(
    title="EduAI Demo API",
    description="Minimal FastAPI scaffold showing the textbook page + Q&A loop",
    version="0.1.0",
)


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    dependencies = {
        "database": "mock",
        "redis": "mock",
        "storage": "mock",
    }
    return HealthResponse(status="ok", dependencies=dependencies)


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile) -> UploadResponse:
    job_id = f"demo-job-{file.filename}"
    message = "Accepted. In a real deployment this would OCR and index the file asynchronously."
    return UploadResponse(job_id=job_id, message=message, accepted=True)


@app.get("/page/{page_id}", response_model=PageResponse)
def get_page(page_id: int) -> PageResponse:
    page = data.find_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    return PageResponse(
        id=page.id,
        unit_id=page.unit_id,
        page_number=page.page_number,
        image_url=page.image_url,
        thumbnail_url=page.thumbnail_url,
        exercises=[
            {
                "id": ex.id,
                "page_id": ex.page_id,
                "exercise_number": ex.exercise_number,
                "bbox": ex.bbox,
                "ocr_text": ex.ocr_text,
                "ocr_confidence": ex.ocr_confidence,
                "crop_url": ex.crop_url,
            }
            for ex in page.exercises
        ],
    )


@app.post("/exercise/{exercise_id}/ask", response_model=AskResponse)
def ask_question(exercise_id: int, payload: AskRequest) -> AskResponse:
    exercise = data.find_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    thread = _build_mock_thread(exercise, payload)
    citations = [
        {
            "page_id": exercise.page_id,
            "exercise_id": exercise.id,
            "snippet": exercise.ocr_text,
            "bbox": exercise.bbox,
        }
    ]

    answer = _compose_answer(exercise, payload.mode)

    return AskResponse(
        answer=answer,
        mode=payload.mode,
        citations=citations,
        thread=thread,
    )


def _build_mock_thread(exercise: data.Exercise, payload: AskRequest) -> List[Dict[str, str]]:
    base_messages = data.build_thread_seed(exercise)
    user_message = {"role": "user", "content": payload.question}
    assistant_message = {
        "role": "assistant",
        "content": _compose_answer(exercise, payload.mode),
    }
    return [
        message.__dict__
        for message in base_messages
        if message.role in {"system", "assistant"}
    ] + [user_message, assistant_message]


def _compose_answer(exercise: data.Exercise, mode: str) -> str:
    intro = f"Tapşırıq {exercise.exercise_number}: "
    if mode == "hint":
        return intro + "Öncə şəkilə bax və əsas sözləri seç. Sonra bir cümlə qurmağa cəhd et."
    if mode == "similar":
        return intro + "Oxşar tapşırıq: şəkli təsvir edən 2 yeni cümlə yaz və hər cümlədə fərqli bir söz vurğula."
    if mode == "explain_like_7yo":
        return intro + "Bu tapşırıqda sadəcə gördüklərini sözlərlə de və bir dostuna danışırmış kimi izah et."
    return intro + "Cümləni addım-addım qur: əvvəl mövzu, sonra fel, sonra tamamlıq əlavə et."


@app.get("/unit/{unit_id}/pages", response_model=List[PageResponse])
def list_pages(unit_id: int) -> List[PageResponse]:
    unit = data.find_unit(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    return [
        PageResponse(
            id=page.id,
            unit_id=page.unit_id,
            page_number=page.page_number,
            image_url=page.image_url,
            thumbnail_url=page.thumbnail_url,
            exercises=[
                {
                    "id": ex.id,
                    "page_id": ex.page_id,
                    "exercise_number": ex.exercise_number,
                    "bbox": ex.bbox,
                    "ocr_text": ex.ocr_text,
                    "ocr_confidence": ex.ocr_confidence,
                    "crop_url": ex.crop_url,
                }
                for ex in page.exercises
            ],
        )
        for page in unit.pages
    ]
