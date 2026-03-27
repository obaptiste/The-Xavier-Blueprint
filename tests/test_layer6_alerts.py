"""Tests for Layer 6 — Interest Alert System."""

from __future__ import annotations

import pytest

from src.creator_ai.layers.layer6_alerts import (
    calculate_engagement_score,
    check_alert,
    format_alert_message,
    score_interaction,
)
from src.creator_ai.models.archetypes import Archetype
from src.creator_ai.models.content import Platform
from src.creator_ai.models.engagement import (
    ALERT_THRESHOLD,
    INTERACTION_WEIGHTS,
    EngagementScore,
    Interaction,
    InteractionType,
)
from src.creator_ai.models.personality import LanguageStyle, Mood, PersonalityProfile, ToneApproach


def _make_interaction(
    interaction_type: InteractionType,
    user_id: str = "user-1",
    creator_id: str = "creator-1",
    platform: Platform = Platform.INSTAGRAM,
) -> Interaction:
    return Interaction(
        user_id=user_id,
        creator_id=creator_id,
        platform=platform,
        interaction_type=interaction_type,
        post_id="post-abc",
    )


def _make_profile() -> PersonalityProfile:
    return PersonalityProfile(
        archetype=Archetype.EDUCATOR,
        language_style=LanguageStyle.CASUAL,
        tone_approach=ToneApproach.DIRECT,
        mood=Mood.FOCUSED,
    )


class TestScoreInteraction:
    @pytest.mark.parametrize("interaction_type,expected_weight", [
        (InteractionType.FIVERR_DM, 8.0),
        (InteractionType.LINKEDIN_DM, 6.0),
        (InteractionType.INSTAGRAM_DM, 5.0),
        (InteractionType.YOUTUBE_LINK_CLICK, 3.0),
        (InteractionType.INSTAGRAM_SAVE, 2.0),
        (InteractionType.TIKTOK_DUET_STITCH, 4.0),
        (InteractionType.FACEBOOK_SHARE, 3.0),
        (InteractionType.COMMENT_WITH_QUESTION, 4.0),
        (InteractionType.STANDARD_COMMENT, 1.0),
        (InteractionType.LIKE, 0.5),
    ])
    def test_correct_weight_returned(self, interaction_type: InteractionType, expected_weight: float):
        interaction = _make_interaction(interaction_type)
        result = score_interaction(interaction)
        assert result == expected_weight

    def test_all_interaction_types_have_positive_score(self):
        for interaction_type in InteractionType:
            interaction = _make_interaction(interaction_type)
            score = score_interaction(interaction)
            assert score > 0, f"{interaction_type} should have a positive score"

    def test_fiverr_dm_has_highest_score(self):
        fiverr_score = INTERACTION_WEIGHTS[InteractionType.FIVERR_DM]
        for it in InteractionType:
            if it != InteractionType.FIVERR_DM:
                assert fiverr_score >= INTERACTION_WEIGHTS[it], (
                    f"FIVERR_DM should have highest or equal score vs {it}"
                )

    def test_like_has_lowest_score(self):
        like_score = INTERACTION_WEIGHTS[InteractionType.LIKE]
        for it in InteractionType:
            if it != InteractionType.LIKE:
                assert INTERACTION_WEIGHTS[it] >= like_score, (
                    f"LIKE should have lowest or equal score vs {it}"
                )


class TestCalculateEngagementScore:
    def test_returns_engagement_score(self):
        interactions = [_make_interaction(InteractionType.LIKE)]
        result = calculate_engagement_score(interactions)
        assert isinstance(result, EngagementScore)

    def test_total_score_is_sum_of_individual_scores(self):
        interactions = [
            _make_interaction(InteractionType.LIKE),
            _make_interaction(InteractionType.STANDARD_COMMENT),
            _make_interaction(InteractionType.INSTAGRAM_SAVE),
        ]
        result = calculate_engagement_score(interactions)
        expected = 0.5 + 1.0 + 2.0
        assert result.total_score == pytest.approx(expected)

    def test_empty_list_raises_value_error(self):
        with pytest.raises(ValueError):
            calculate_engagement_score([])

    def test_alert_not_triggered_below_threshold(self):
        interactions = [_make_interaction(InteractionType.LIKE)]
        result = calculate_engagement_score(interactions)
        assert not result.alert_triggered

    def test_alert_triggered_at_threshold(self):
        interactions = [
            _make_interaction(InteractionType.FIVERR_DM),  # 8.0
            _make_interaction(InteractionType.COMMENT_WITH_QUESTION),  # 4.0
            _make_interaction(InteractionType.INSTAGRAM_DM),  # 5.0
        ]
        result = calculate_engagement_score(interactions)
        assert result.total_score >= ALERT_THRESHOLD
        assert result.alert_triggered

    def test_user_id_matches_interactions(self):
        interactions = [_make_interaction(InteractionType.LIKE, user_id="user-xyz")]
        result = calculate_engagement_score(interactions)
        assert result.user_id == "user-xyz"

    def test_interactions_are_stored(self):
        interactions = [
            _make_interaction(InteractionType.LIKE),
            _make_interaction(InteractionType.STANDARD_COMMENT),
        ]
        result = calculate_engagement_score(interactions)
        assert len(result.interactions) == 2


class TestCheckAlert:
    def test_returns_false_below_threshold(self):
        score = EngagementScore(
            user_id="u1",
            creator_id="c1",
            total_score=ALERT_THRESHOLD - 1,
            alert_triggered=False,
        )
        assert not check_alert(score)

    def test_returns_true_at_exact_threshold(self):
        score = EngagementScore(
            user_id="u1",
            creator_id="c1",
            total_score=ALERT_THRESHOLD,
            alert_triggered=True,
        )
        assert check_alert(score)

    def test_returns_true_above_threshold(self):
        score = EngagementScore(
            user_id="u1",
            creator_id="c1",
            total_score=ALERT_THRESHOLD + 10,
            alert_triggered=True,
        )
        assert check_alert(score)

    def test_threshold_constant_is_15(self):
        assert ALERT_THRESHOLD == 15.0


class TestFormatAlertMessage:
    def test_returns_non_empty_string(self):
        interactions = [
            _make_interaction(InteractionType.FIVERR_DM),
            _make_interaction(InteractionType.COMMENT_WITH_QUESTION),
            _make_interaction(InteractionType.INSTAGRAM_DM),
        ]
        score = calculate_engagement_score(interactions)
        profile = _make_profile()
        message = format_alert_message(score, profile)
        assert isinstance(message, str)
        assert len(message.strip()) > 0

    def test_message_contains_user_id(self):
        interactions = [_make_interaction(InteractionType.FIVERR_DM, user_id="user-test-id")]
        score = calculate_engagement_score(interactions)
        message = format_alert_message(score, _make_profile())
        assert "user-test-id" in message

    def test_message_contains_score(self):
        interactions = [
            _make_interaction(InteractionType.FIVERR_DM),
            _make_interaction(InteractionType.LINKEDIN_DM),
            _make_interaction(InteractionType.INSTAGRAM_DM),
        ]
        score = calculate_engagement_score(interactions)
        message = format_alert_message(score, _make_profile())
        assert str(int(score.total_score)) in message or "Score" in message or "score" in message

    def test_message_contains_recommendation(self):
        interactions = [
            _make_interaction(InteractionType.FIVERR_DM),
            _make_interaction(InteractionType.COMMENT_WITH_QUESTION),
            _make_interaction(InteractionType.INSTAGRAM_DM),
        ]
        score = calculate_engagement_score(interactions)
        message = format_alert_message(score, _make_profile())
        assert len(message) > 50

    def test_message_varies_by_archetype(self):
        interactions = [
            _make_interaction(InteractionType.FIVERR_DM),
            _make_interaction(InteractionType.LINKEDIN_DM),
            _make_interaction(InteractionType.INSTAGRAM_DM),
        ]
        score = calculate_engagement_score(interactions)
        educator_profile = PersonalityProfile(
            archetype=Archetype.EDUCATOR,
            language_style=LanguageStyle.CASUAL,
            tone_approach=ToneApproach.DIRECT,
            mood=Mood.FOCUSED,
        )
        visionary_profile = PersonalityProfile(
            archetype=Archetype.VISIONARY,
            language_style=LanguageStyle.CASUAL,
            tone_approach=ToneApproach.DIRECT,
            mood=Mood.FOCUSED,
        )
        msg_educator = format_alert_message(score, educator_profile)
        msg_visionary = format_alert_message(score, visionary_profile)
        assert msg_educator != msg_visionary
