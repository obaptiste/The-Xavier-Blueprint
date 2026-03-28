"""Tests for Layer 1 — Personality Archive."""

from __future__ import annotations

import pytest

from src.creator_ai.layers.layer1_personality import (
    QUIZ_QUESTIONS,
    apply_mood_modulation,
    calculate_archetype,
    create_personality_profile,
)
from src.creator_ai.models.archetypes import Archetype
from src.creator_ai.models.personality import (
    LanguageStyle,
    Mood,
    PersonalityProfile,
    QuizAnswer,
    ToneApproach,
)


class TestQuizQuestions:
    def test_exactly_ten_questions_exist(self):
        assert len(QUIZ_QUESTIONS) == 10

    def test_all_questions_have_four_or_more_options(self):
        for q in QUIZ_QUESTIONS:
            assert len(q.options) >= 4, f"Question {q.id} has fewer than 4 options"

    def test_all_questions_have_non_empty_text(self):
        for q in QUIZ_QUESTIONS:
            assert q.question.strip(), f"Question {q.id} has empty text"

    def test_all_options_have_archetype_weights(self):
        for q in QUIZ_QUESTIONS:
            for i, opt in enumerate(q.options):
                assert opt.archetype_weights, f"Question {q.id} option {i} has no weights"

    def test_question_ids_are_unique(self):
        ids = [q.id for q in QUIZ_QUESTIONS]
        assert len(ids) == len(set(ids))

    def test_archetype_weights_reference_valid_archetypes(self):
        valid = {a.value for a in Archetype}
        for q in QUIZ_QUESTIONS:
            for opt in q.options:
                for key in opt.archetype_weights:
                    assert key in valid, f"Unknown archetype '{key}' in question {q.id}"

    def test_weights_are_positive(self):
        for q in QUIZ_QUESTIONS:
            for opt in q.options:
                for key, weight in opt.archetype_weights.items():
                    assert weight > 0, f"Non-positive weight for {key} in question {q.id}"


class TestCalculateArchetype:
    def _all_answers_for_option(self, option_index: int) -> list[QuizAnswer]:
        return [
            QuizAnswer(question_id=q.id, selected_option_index=option_index)
            for q in QUIZ_QUESTIONS
            if option_index < len(q.options)
        ]

    def test_returns_valid_archetype(self):
        answers = self._all_answers_for_option(0)
        archetype, scores = calculate_archetype(answers)
        assert isinstance(archetype, Archetype)

    def test_returns_scores_for_all_archetypes(self):
        answers = self._all_answers_for_option(0)
        _, scores = calculate_archetype(answers)
        assert len(scores) == len(Archetype)

    def test_top_archetype_has_highest_score(self):
        answers = self._all_answers_for_option(0)
        archetype, scores = calculate_archetype(answers)
        assert scores[archetype] == max(scores.values())

    def test_empty_answers_returns_archetype(self):
        archetype, scores = calculate_archetype([])
        assert isinstance(archetype, Archetype)

    def test_educator_archetype_reachable(self):
        """Selecting the educator-weighted option in every question should produce Educator."""
        educator_answers = []
        for q in QUIZ_QUESTIONS:
            best_idx = 0
            best_weight = -1.0
            for i, opt in enumerate(q.options):
                w = opt.archetype_weights.get(Archetype.EDUCATOR.value, 0.0)
                if w > best_weight:
                    best_weight = w
                    best_idx = i
            educator_answers.append(QuizAnswer(question_id=q.id, selected_option_index=best_idx))
        archetype, scores = calculate_archetype(educator_answers)
        assert archetype == Archetype.EDUCATOR

    def test_disruptor_archetype_reachable(self):
        disruptor_answers = []
        for q in QUIZ_QUESTIONS:
            best_idx = 0
            best_weight = -1.0
            for i, opt in enumerate(q.options):
                w = opt.archetype_weights.get(Archetype.DISRUPTOR.value, 0.0)
                if w > best_weight:
                    best_weight = w
                    best_idx = i
            disruptor_answers.append(QuizAnswer(question_id=q.id, selected_option_index=best_idx))
        archetype, scores = calculate_archetype(disruptor_answers)
        assert archetype == Archetype.DISRUPTOR

    def test_builder_archetype_reachable(self):
        builder_answers = []
        for q in QUIZ_QUESTIONS:
            best_idx = 0
            best_weight = -1.0
            for i, opt in enumerate(q.options):
                w = opt.archetype_weights.get(Archetype.BUILDER.value, 0.0)
                if w > best_weight:
                    best_weight = w
                    best_idx = i
            builder_answers.append(QuizAnswer(question_id=q.id, selected_option_index=best_idx))
        archetype, scores = calculate_archetype(builder_answers)
        assert archetype == Archetype.BUILDER

    def test_invalid_question_id_is_skipped(self):
        answers = [QuizAnswer(question_id="nonexistent", selected_option_index=0)]
        archetype, _ = calculate_archetype(answers)
        assert isinstance(archetype, Archetype)

    def test_out_of_range_option_is_skipped(self):
        answers = [QuizAnswer(question_id="q1", selected_option_index=999)]
        archetype, _ = calculate_archetype(answers)
        assert isinstance(archetype, Archetype)


class TestCreatePersonalityProfile:
    def test_creates_profile_with_correct_language_style(self):
        answers = [QuizAnswer(question_id="q1", selected_option_index=0)]
        profile = create_personality_profile(
            answers=answers,
            language_style=LanguageStyle.STREET_RAW,
            tone_approach=ToneApproach.DIRECT,
            mood=Mood.FIRED_UP,
        )
        assert profile.language_style == LanguageStyle.STREET_RAW

    def test_creates_profile_with_correct_mood(self):
        answers = [QuizAnswer(question_id="q1", selected_option_index=0)]
        profile = create_personality_profile(
            answers=answers,
            language_style=LanguageStyle.CASUAL,
            tone_approach=ToneApproach.PLAYFUL,
            mood=Mood.HAPPY,
        )
        assert profile.mood == Mood.HAPPY

    def test_returns_personality_profile_instance(self):
        answers = [QuizAnswer(question_id="q1", selected_option_index=0)]
        profile = create_personality_profile(
            answers=answers,
            language_style=LanguageStyle.PROFESSIONAL,
            tone_approach=ToneApproach.AUTHORITATIVE,
            mood=Mood.CONFIDENT,
        )
        assert isinstance(profile, PersonalityProfile)

    def test_profile_has_created_at_timestamp(self):
        answers = [QuizAnswer(question_id="q1", selected_option_index=0)]
        profile = create_personality_profile(
            answers=answers,
            language_style=LanguageStyle.CASUAL,
            tone_approach=ToneApproach.DIRECT,
            mood=Mood.FOCUSED,
        )
        assert profile.created_at is not None


class TestMoodModulation:
    def _make_profile(self, mood: Mood) -> PersonalityProfile:
        return PersonalityProfile(
            archetype=Archetype.EDUCATOR,
            language_style=LanguageStyle.CASUAL,
            tone_approach=ToneApproach.DIRECT,
            mood=mood,
        )

    def test_returns_non_empty_string(self):
        profile = self._make_profile(Mood.FIRED_UP)
        result = apply_mood_modulation(profile, "creating content about social media")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_different_moods_produce_different_instructions(self):
        context = "content about building an audience"
        moods = list(Mood)
        results = {mood: apply_mood_modulation(self._make_profile(mood), context) for mood in moods}
        unique_results = set(results.values())
        assert len(unique_results) == len(moods), "Each mood should produce a unique instruction"

    def test_content_context_included_in_output(self):
        profile = self._make_profile(Mood.FOCUSED)
        context = "my unique content context abc123"
        result = apply_mood_modulation(profile, context)
        assert context in result

    def test_archetype_voice_referenced_in_output(self):
        profile = self._make_profile(Mood.CONFIDENT)
        result = apply_mood_modulation(profile, "test context")
        assert "VOICE" in result

    def test_all_archetypes_produce_non_empty_instructions(self):
        for archetype in Archetype:
            profile = PersonalityProfile(
                archetype=archetype,
                language_style=LanguageStyle.CASUAL,
                tone_approach=ToneApproach.DIRECT,
                mood=Mood.FOCUSED,
            )
            result = apply_mood_modulation(profile, "test")
            assert len(result) > 0
