from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ExerciseResponse(BaseModel):
    id: int
    page_id: int
    exercise_number: str
    bbox: dict
    ocr_text: str
    ocr_confidence: float
    crop_url: Optional[HttpUrl] = None


class PageResponse(BaseModel):
    id: int
    unit_id: int
    page_number: int
    image_url: HttpUrl
    thumbnail_url: HttpUrl
    exercises: List[ExerciseResponse]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="User question about the exercise")
    mode: str = Field(
        "hint",
        description="hint | answer | similar | explain_like_7yo",
    )
    language: str = Field("az", description="Two-letter language code")
    thread_id: Optional[str] = Field(None, description="Client thread identifier")


class AskResponse(BaseModel):
    answer: str
    mode: str
    citations: List[dict]
    thread: List[dict]
    next_actions: List[str] = Field(
        default_factory=lambda: ["Tap try similar problem", "Ask for a bigger hint", "Switch to full answer"],
        description="Suggested follow-ups for the user",
    )


class UploadResponse(BaseModel):
    job_id: str
    message: str
    accepted: bool


class HealthResponse(BaseModel):
    status: str
    dependencies: dict
