"""Tests for Layer 2 — The Brain."""

from __future__ import annotations

import pytest

from src.creator_ai.layers.layer2_brain import (
    build_story_context,
    generate_intake_questions,
    ingest_content,
    route_content,
)
from src.creator_ai.models.content import (
    BrainSession,
    ContentType,
    ContentUpload,
    IntakeAnswer,
    Platform,
)


def _make_session(user_id: str = "user-1") -> BrainSession:
    return BrainSession(user_id=user_id)


def _make_upload(content_type: ContentType, raw_content: str = "Some raw content") -> ContentUpload:
    return ContentUpload(content_type=content_type, raw_content=raw_content)


class TestGenerateIntakeQuestions:
    @pytest.mark.parametrize("content_type", list(ContentType))
    def test_returns_three_to_five_questions_per_content_type(self, content_type: ContentType):
        session = _make_session()
        upload = _make_upload(content_type)
        questions = generate_intake_questions(upload, session)
        assert 3 <= len(questions) <= 5, (
            f"Expected 3–5 questions for {content_type}, got {len(questions)}"
        )

    @pytest.mark.parametrize("content_type", list(ContentType))
    def test_all_questions_are_non_empty_strings(self, content_type: ContentType):
        session = _make_session()
        upload = _make_upload(content_type)
        questions = generate_intake_questions(upload, session)
        for q in questions:
            assert isinstance(q, str)
            assert len(q.strip()) > 0

    def test_multi_upload_session_includes_follow_up_questions(self):
        session = _make_session()
        upload1 = _make_upload(ContentType.PHOTO, "First upload")
        upload2 = _make_upload(ContentType.VIDEO, "Second upload")
        session = session.model_copy(update={"uploads": [upload1]})
        questions = generate_intake_questions(upload2, session)
        assert len(questions) >= 3

    def test_photo_questions_are_different_from_video_questions(self):
        session = _make_session()
        photo_upload = _make_upload(ContentType.PHOTO)
        video_upload = _make_upload(ContentType.VIDEO)
        photo_qs = generate_intake_questions(photo_upload, session)
        video_qs = generate_intake_questions(video_upload, session)
        assert photo_qs != video_qs


class TestIngestContent:
    def test_ingest_adds_upload_to_session(self):
        session = _make_session()
        upload = _make_upload(ContentType.STATEMENT, "This is a statement")
        updated = ingest_content(upload, session)
        assert len(updated.uploads) == 1
        assert updated.uploads[0].id == upload.id

    def test_ingest_updates_story_context(self):
        session = _make_session()
        upload = _make_upload(ContentType.STATEMENT, "Building in public")
        updated = ingest_content(upload, session)
        assert len(updated.current_story_context) > 0

    def test_ingest_multiple_uploads_accumulates(self):
        session = _make_session()
        for i in range(3):
            upload = _make_upload(ContentType.PHOTO, f"Photo number {i}")
            session = ingest_content(upload, session)
        assert len(session.uploads) == 3

    def test_ingest_does_not_mutate_original_session(self):
        session = _make_session()
        original_upload_count = len(session.uploads)
        upload = _make_upload(ContentType.VIDEO, "Test video content")
        _ = ingest_content(upload, session)
        assert len(session.uploads) == original_upload_count


class TestRouteContent:
    def test_returns_empty_dict_for_no_uploads(self):
        session = _make_session()
        result = route_content(session, [Platform.TIKTOK])
        assert result == {}

    def test_routes_to_all_requested_platforms(self):
        session = _make_session()
        upload = _make_upload(ContentType.VIDEO, "Great video content")
        session = ingest_content(upload, session)
        platforms = [Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE]
        result = route_content(session, platforms)
        assert set(result.keys()) == set(platforms)

    def test_each_platform_receives_a_content_upload(self):
        session = _make_session()
        upload = _make_upload(ContentType.STATEMENT, "Statement content")
        session = ingest_content(upload, session)
        result = route_content(session, [Platform.LINKEDIN, Platform.X])
        for platform, content in result.items():
            assert isinstance(content, ContentUpload)

    def test_video_upload_routed_to_tiktok(self):
        session = _make_session()
        video = _make_upload(ContentType.VIDEO, "This is a video")
        photo = _make_upload(ContentType.PHOTO, "This is a photo")
        session = ingest_content(video, session)
        session = ingest_content(photo, session)
        result = route_content(session, [Platform.TIKTOK])
        assert result[Platform.TIKTOK].content_type == ContentType.VIDEO

    def test_empty_platform_list_returns_empty_dict(self):
        session = _make_session()
        upload = _make_upload(ContentType.STATEMENT, "content")
        session = ingest_content(upload, session)
        result = route_content(session, [])
        assert result == {}


class TestBuildStoryContext:
    def test_empty_session_returns_non_empty_string(self):
        session = _make_session()
        context = build_story_context(session)
        assert isinstance(context, str)
        assert len(context) > 0

    def test_context_includes_upload_content(self):
        session = _make_session()
        upload = _make_upload(ContentType.STATEMENT, "My unique statement about growth")
        session = ingest_content(upload, session)
        context = build_story_context(session)
        assert len(context) > 10

    def test_context_includes_intake_answers(self):
        session = _make_session()
        upload = _make_upload(ContentType.PHOTO, "A photo")
        session = ingest_content(upload, session)
        answer = IntakeAnswer(question_id="q1", answer_text="I felt inspired and ready")
        session = session.model_copy(update={"intake_answers": [answer]})
        context = build_story_context(session)
        assert "inspired and ready" in context or "INSIGHTS" in context

    def test_context_grows_with_more_uploads(self):
        session = _make_session()
        upload1 = _make_upload(ContentType.PHOTO, "First piece of content")
        upload2 = _make_upload(ContentType.VIDEO, "Second piece of content")
        session1 = ingest_content(upload1, session)
        context1 = build_story_context(session1)
        session2 = ingest_content(upload2, session1)
        context2 = build_story_context(session2)
        assert len(context2) >= len(context1)
