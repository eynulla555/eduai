from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Exercise:
    id: int
    page_id: int
    exercise_number: str
    bbox: Dict[str, int]
    ocr_text: str
    ocr_confidence: float
    crop_url: Optional[str] = None


@dataclass
class Page:
    id: int
    unit_id: int
    page_number: int
    image_url: str
    thumbnail_url: str
    exercises: List[Exercise]


@dataclass
class Unit:
    id: int
    subject_id: int
    title: str
    pages: List[Page]


@dataclass
class Subject:
    id: int
    grade_id: int
    name: str
    units: List[Unit]


@dataclass
class Grade:
    id: int
    label: str
    subjects: List[Subject]


@dataclass
class ThreadMessage:
    role: str
    content: str
    citations: Optional[List[Dict[str, str]]] = None


grade_one_language = Grade(
    id=1,
    label="Grade 1",
    subjects=[
        Subject(
            id=1,
            grade_id=1,
            name="Azerbaijani Language",
            units=[
                Unit(
                    id=1,
                    subject_id=1,
                    title="Unit 1: Salam, məktəb!",
                    pages=[
                        Page(
                            id=1,
                            unit_id=1,
                            page_number=50,
                            image_url="https://example.com/page50.png",
                            thumbnail_url="https://example.com/page50-thumb.png",
                            exercises=[
                                Exercise(
                                    id=1,
                                    page_id=1,
                                    exercise_number="1",
                                    bbox={"x": 120, "y": 210, "w": 320, "h": 180},
                                    ocr_text="Şəkli izah et və suallara cavab ver.",
                                    ocr_confidence=0.92,
                                    crop_url="https://example.com/page50-ex1.png",
                                ),
                                Exercise(
                                    id=2,
                                    page_id=1,
                                    exercise_number="2",
                                    bbox={"x": 120, "y": 430, "w": 320, "h": 160},
                                    ocr_text="Hekayəni oxu və altından xətt çəkilən sözləri izah et.",
                                    ocr_confidence=0.88,
                                    crop_url="https://example.com/page50-ex2.png",
                                ),
                            ],
                        ),
                        Page(
                            id=2,
                            unit_id=1,
                            page_number=51,
                            image_url="https://example.com/page51.png",
                            thumbnail_url="https://example.com/page51-thumb.png",
                            exercises=[
                                Exercise(
                                    id=3,
                                    page_id=2,
                                    exercise_number="1",
                                    bbox={"x": 90, "y": 180, "w": 340, "h": 160},
                                    ocr_text="Şəkilə bax və 3 cümlə qur.",
                                    ocr_confidence=0.9,
                                )
                            ],
                        ),
                    ],
                )
            ],
        )
    ],
)

grades = [grade_one_language]


def find_page(page_id: int) -> Optional[Page]:
    for grade in grades:
        for subject in grade.subjects:
            for unit in subject.units:
                for page in unit.pages:
                    if page.id == page_id:
                        return page
    return None


def find_exercise(exercise_id: int) -> Optional[Exercise]:
    for grade in grades:
        for subject in grade.subjects:
            for unit in subject.units:
                for page in unit.pages:
                    for exercise in page.exercises:
                        if exercise.id == exercise_id:
                            return exercise
    return None


def find_unit(unit_id: int) -> Optional[Unit]:
    for grade in grades:
        for subject in grade.subjects:
            for unit in subject.units:
                if unit.id == unit_id:
                    return unit
    return None


def build_thread_seed(exercise: Exercise) -> List[ThreadMessage]:
    return [
        ThreadMessage(
            role="system",
            content=(
                "You are a patient primary-school tutor. Keep language simple. "
                "Prefer step-by-step hints unless the user explicitly asks for the full answer. "
                "Stay age-appropriate and encourage the student to try a step before revealing the solution."
            ),
        ),
        ThreadMessage(
            role="assistant",
            content=(
                "Tap the exercise area to ask a question. You can request a hint, a full answer, or a similar practice problem."
            ),
        ),
    ]
