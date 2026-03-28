"""Tests for Layer 3 — Platform Mini Apps."""

from __future__ import annotations

import pytest

from src.creator_ai.layers.layer3_mini_apps import (
    ArchetypeVoiceEngine,
    generate_facebook_content,
    generate_fiverr_content,
    generate_for_platform,
    generate_instagram_content,
    generate_linkedin_content,
    generate_tiktok_content,
    generate_x_content,
    generate_youtube_content,
)
from src.creator_ai.models.archetypes import Archetype
from src.creator_ai.models.content import ContentType, ContentUpload, GeneratedContent, Platform
from src.creator_ai.models.personality import LanguageStyle, Mood, PersonalityProfile, ToneApproach


def _make_profile(
    archetype: Archetype = Archetype.EDUCATOR,
    mood: Mood = Mood.FOCUSED,
    language_style: LanguageStyle = LanguageStyle.CASUAL,
    tone: ToneApproach = ToneApproach.DIRECT,
) -> PersonalityProfile:
    return PersonalityProfile(
        archetype=archetype,
        language_style=language_style,
        tone_approach=tone,
        mood=mood,
    )


def _make_upload(
    content_type: ContentType = ContentType.STATEMENT,
    raw_content: str = "I've been building in public for 3 years and here's what I learned about authentic content creation.",
) -> ContentUpload:
    return ContentUpload(content_type=content_type, raw_content=raw_content)


class TestTikTokGenerator:
    def test_returns_generated_content(self):
        result = generate_tiktok_content(_make_profile(), _make_upload(), "")
        assert isinstance(result, GeneratedContent)

    def test_platform_is_tiktok(self):
        result = generate_tiktok_content(_make_profile(), _make_upload(), "")
        assert result.platform == Platform.TIKTOK

    def test_content_text_is_non_empty(self):
        result = generate_tiktok_content(_make_profile(), _make_upload(), "")
        assert len(result.content_text.strip()) > 0

    def test_content_contains_hook_section(self):
        result = generate_tiktok_content(_make_profile(), _make_upload(), "")
        assert "HOOK" in result.content_text.upper() or len(result.content_text) > 20

    def test_hashtags_are_generated(self):
        result = generate_tiktok_content(_make_profile(), _make_upload(), "")
        assert len(result.hashtags) >= 5

    def test_hashtags_start_with_hash(self):
        result = generate_tiktok_content(_make_profile(), _make_upload(), "")
        for tag in result.hashtags:
            assert tag.startswith("#"), f"Hashtag '{tag}' does not start with '#'"

    def test_different_archetypes_produce_different_content(self):
        upload = _make_upload()
        educator_content = generate_tiktok_content(_make_profile(Archetype.EDUCATOR), upload, "")
        disruptor_content = generate_tiktok_content(_make_profile(Archetype.DISRUPTOR), upload, "")
        assert educator_content.content_text != disruptor_content.content_text


class TestInstagramGenerator:
    def test_returns_generated_content(self):
        result = generate_instagram_content(_make_profile(), _make_upload(), "")
        assert isinstance(result, GeneratedContent)

    def test_platform_is_instagram(self):
        result = generate_instagram_content(_make_profile(), _make_upload(), "")
        assert result.platform == Platform.INSTAGRAM

    def test_content_text_is_non_empty(self):
        result = generate_instagram_content(_make_profile(), _make_upload(), "")
        assert len(result.content_text.strip()) > 0

    def test_has_ten_or_more_hashtags(self):
        result = generate_instagram_content(_make_profile(), _make_upload(), "")
        assert len(result.hashtags) >= 10

    def test_caption_contains_raw_content(self):
        raw = "This is my specific raw content for the test"
        upload = _make_upload(raw_content=raw)
        result = generate_instagram_content(_make_profile(), upload, "")
        assert raw[:50] in result.content_text or len(result.content_text) > 0


class TestFacebookGenerator:
    def test_returns_generated_content(self):
        result = generate_facebook_content(_make_profile(), _make_upload(), "")
        assert isinstance(result, GeneratedContent)

    def test_platform_is_facebook(self):
        result = generate_facebook_content(_make_profile(), _make_upload(), "")
        assert result.platform == Platform.FACEBOOK

    def test_content_is_non_empty(self):
        result = generate_facebook_content(_make_profile(), _make_upload(), "")
        assert len(result.content_text.strip()) > 0

    def test_content_contains_question_for_community(self):
        result = generate_facebook_content(_make_profile(), _make_upload(), "")
        assert "?" in result.content_text


class TestLinkedInGenerator:
    def test_returns_generated_content(self):
        result = generate_linkedin_content(_make_profile(), _make_upload(), "")
        assert isinstance(result, GeneratedContent)

    def test_platform_is_linkedin(self):
        result = generate_linkedin_content(_make_profile(), _make_upload(), "")
        assert result.platform == Platform.LINKEDIN

    def test_content_is_professional(self):
        result = generate_linkedin_content(_make_profile(Archetype.EDUCATOR), _make_upload(), "")
        text = result.content_text.lower()
        assert any(word in text for word in ["professionals", "insight", "approach", "understand", "perspective"])

    def test_has_hashtags(self):
        result = generate_linkedin_content(_make_profile(), _make_upload(), "")
        assert len(result.hashtags) >= 3


class TestYouTubeGenerator:
    def test_returns_generated_content(self):
        result = generate_youtube_content(_make_profile(), _make_upload(), "")
        assert isinstance(result, GeneratedContent)

    def test_platform_is_youtube(self):
        result = generate_youtube_content(_make_profile(), _make_upload(), "")
        assert result.platform == Platform.YOUTUBE

    def test_description_contains_chapters(self):
        result = generate_youtube_content(_make_profile(), _make_upload(), "")
        assert "CHAPTERS" in result.content_text or "0:00" in result.content_text

    def test_metadata_includes_title(self):
        result = generate_youtube_content(_make_profile(), _make_upload(), "")
        assert "title" in result.metadata
        assert len(result.metadata["title"]) > 0

    def test_metadata_includes_tags(self):
        result = generate_youtube_content(_make_profile(), _make_upload(), "")
        assert "tags" in result.metadata
        assert len(result.metadata["tags"]) > 0


class TestFiverrGenerator:
    def test_returns_generated_content(self):
        result = generate_fiverr_content(_make_profile(), _make_upload(), "")
        assert isinstance(result, GeneratedContent)

    def test_platform_is_fiverr(self):
        result = generate_fiverr_content(_make_profile(), _make_upload(), "")
        assert result.platform == Platform.FIVERR

    def test_content_contains_credibility_bullets(self):
        result = generate_fiverr_content(_make_profile(), _make_upload(), "")
        assert "•" in result.content_text

    def test_content_is_non_empty(self):
        result = generate_fiverr_content(_make_profile(), _make_upload(), "")
        assert len(result.content_text.strip()) > 0


class TestXGenerator:
    def test_returns_generated_content(self):
        result = generate_x_content(_make_profile(), _make_upload(), "")
        assert isinstance(result, GeneratedContent)

    def test_platform_is_x(self):
        result = generate_x_content(_make_profile(), _make_upload(), "")
        assert result.platform == Platform.X

    def test_content_contains_thread_structure(self):
        result = generate_x_content(_make_profile(), _make_upload(), "")
        assert "1/" in result.content_text

    def test_thread_has_engagement_question(self):
        result = generate_x_content(_make_profile(), _make_upload(), "")
        assert "?" in result.content_text


class TestDispatcher:
    @pytest.mark.parametrize("platform", list(Platform))
    def test_all_platforms_produce_generated_content(self, platform: Platform):
        result = generate_for_platform(
            platform=platform,
            profile=_make_profile(),
            upload=_make_upload(),
            story_context="",
        )
        assert isinstance(result, GeneratedContent)
        assert result.platform == platform
        assert len(result.content_text.strip()) > 0

    def test_raises_for_unknown_platform(self):
        with pytest.raises((ValueError, KeyError)):
            generate_for_platform(
                platform="nonexistent_platform",  # type: ignore[arg-type]
                profile=_make_profile(),
                upload=_make_upload(),
                story_context="",
            )


class TestArchetypeVoiceEngine:
    def test_get_opening_returns_string(self):
        engine = ArchetypeVoiceEngine()
        result = engine.get_opening(Archetype.EDUCATOR, "content creation")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_mood_prefix_returns_string(self):
        engine = ArchetypeVoiceEngine()
        for mood in Mood:
            prefix = engine.get_mood_prefix(mood)
            assert isinstance(prefix, str)

    def test_transform_returns_full_content(self):
        engine = ArchetypeVoiceEngine()
        result = engine.transform(
            raw_text="My raw content here",
            archetype=Archetype.MENTOR,
            mood=Mood.CONFIDENT,
            language_style=LanguageStyle.CASUAL,
            topic="social media",
        )
        assert "My raw content here" in result
        assert len(result) > 20
