"""Router: Layer 1 — Personality Archive endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..layers.layer1_personality import (
    QUIZ_QUESTIONS,
    apply_mood_modulation,
    calculate_archetype,
    create_personality_profile,
)
from ..models.archetypes import ARCHETYPE_METADATA, Archetype
from ..models.personality import (
    LanguageStyle,
    Mood,
    PersonalityProfile,
    QuizAnswer,
    QuizQuestion,
    QuizResult,
    ToneApproach,
)

router = APIRouter(prefix="/personality", tags=["personality"])


class QuizSubmission(BaseModel):
    answers: list[QuizAnswer]
    language_style: LanguageStyle = LanguageStyle.CASUAL
    tone_approach: ToneApproach = ToneApproach.DIRECT
    mood: Mood = Mood.FOCUSED


class ProfileCreateRequest(BaseModel):
    answers: list[QuizAnswer]
    language_style: LanguageStyle
    tone_approach: ToneApproach
    mood: Mood


class MoodUpdateRequest(BaseModel):
    mood: Mood
    profile: PersonalityProfile


@router.get("/quiz", response_model=list[QuizQuestion])
def get_quiz_questions() -> list[QuizQuestion]:
    """Return all 10 archetype quiz questions."""
    return QUIZ_QUESTIONS


@router.post("/quiz/submit", response_model=QuizResult)
def submit_quiz(submission: QuizSubmission) -> QuizResult:
    """Submit quiz answers and receive archetype result with scores."""
    if not submission.answers:
        raise HTTPException(status_code=422, detail="At least one answer is required.")

    archetype, scores = calculate_archetype(submission.answers)
    return QuizResult(
        archetype=archetype,
        scores={k.value: v for k, v in scores.items()},
        language_style=submission.language_style,
        tone_approach=submission.tone_approach,
        mood=submission.mood,
    )


@router.post("/profile", response_model=PersonalityProfile)
def create_profile(request: ProfileCreateRequest) -> PersonalityProfile:
    """Create a full personality profile from quiz answers and style preferences."""
    if not request.answers:
        raise HTTPException(status_code=422, detail="At least one answer is required.")
    return create_personality_profile(
        answers=request.answers,
        language_style=request.language_style,
        tone_approach=request.tone_approach,
        mood=request.mood,
    )


@router.get("/archetypes", response_model=dict)
def list_archetypes() -> dict:
    """List all 10 archetypes with full metadata."""
    return {k.value: v for k, v in ARCHETYPE_METADATA.items()}


@router.put("/profile/mood", response_model=PersonalityProfile)
def update_mood(request: MoodUpdateRequest) -> PersonalityProfile:
    """Update the mood for the current profile and return the updated profile."""
    return request.profile.with_mood(request.mood)
