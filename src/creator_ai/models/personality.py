"""Personality models: quiz, language style, tone, mood, and profile."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .archetypes import Archetype


class LanguageStyle(str, Enum):
    STREET_RAW = "street_raw"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"
    INSPIRATIONAL = "inspirational"


class ToneApproach(str, Enum):
    AUTHORITATIVE = "authoritative"
    PLAYFUL = "playful"
    VULNERABLE = "vulnerable"
    DIRECT = "direct"
    STORYTELLING = "storytelling"
    PROVOCATIVE = "provocative"


class Mood(str, Enum):
    FIRED_UP = "fired_up"
    HAPPY = "happy"
    FOCUSED = "focused"
    PISSED_OFF = "pissed_off"
    REFLECTIVE = "reflective"
    CONFIDENT = "confident"
    PLAYFUL = "playful"
    SERIOUS = "serious"


class QuizOption(BaseModel):
    """A single selectable option in a quiz question."""

    model_config = {"frozen": True}

    text: str
    archetype_weights: dict[str, float] = Field(
        description="Map of archetype value to weight (0–5). Primary ~3, secondary ~1."
    )


class QuizQuestion(BaseModel):
    """A single quiz question with weighted options."""

    model_config = {"frozen": True}

    id: str
    question: str
    options: list[QuizOption] = Field(min_length=4)


class QuizAnswer(BaseModel):
    """A user's answer to a single quiz question."""

    question_id: str
    selected_option_index: int = Field(ge=0)


class QuizResult(BaseModel):
    """The computed result of a completed quiz submission."""

    archetype: Archetype
    scores: dict[str, float] = Field(
        description="Raw weighted score per archetype value."
    )
    language_style: LanguageStyle
    tone_approach: ToneApproach
    mood: Mood


class PersonalityProfile(BaseModel):
    """Full personality profile for a creator."""

    archetype: Archetype
    language_style: LanguageStyle
    tone_approach: ToneApproach
    mood: Mood
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def with_mood(self, new_mood: Mood) -> "PersonalityProfile":
        """Return a copy of this profile with an updated mood and timestamp."""
        return self.model_copy(
            update={"mood": new_mood, "updated_at": datetime.now(timezone.utc)}
        )
