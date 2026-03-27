"""Layer 2 — The Brain: content ingestion, intake questions, routing, story context."""

from __future__ import annotations

from ..models.content import (
    BrainSession,
    ContentType,
    ContentUpload,
    IntakeAnswer,
    Platform,
)

# ---------------------------------------------------------------------------
# Intake question templates by content type
# ---------------------------------------------------------------------------

_INTAKE_QUESTIONS: dict[ContentType, list[str]] = {
    ContentType.PHOTO: [
        "What emotion were you feeling — or trying to capture — when you created this image?",
        "What story does this photo tell that isn't visible on the surface?",
        "Who specifically do you want to reach with this, and why do they need to see it right now?",
        "What do you want people to feel in the first three seconds of seeing this?",
        "What conversation or action do you want this image to spark?",
    ],
    ContentType.VIDEO: [
        "What's the single most important thing you need the viewer to remember after watching?",
        "What inspired this video at this specific moment in your life or business?",
        "What transformation do you want someone to experience from start to finish?",
        "How does this connect to the bigger narrative you're building over time?",
        "If only one type of person watched this — who is that person and what do they do next?",
    ],
    ContentType.STATEMENT: [
        "What triggered this statement — was it a personal experience, an observation, or a long-held belief?",
        "Who needs to hear this most, and what would change for them if they truly absorbed it?",
        "What do you want people to do, think, or feel immediately after reading this?",
        "How vulnerable are you willing to be with this message — and what would happen if you went further?",
        "What's the real risk you're taking by saying this publicly, and is that risk worth it?",
    ],
    ContentType.CALENDAR_EVENT: [
        "What transformation will someone experience by attending this — not just information, but real change?",
        "What's the emotional journey you're designing from the moment they register to the moment they leave?",
        "Who is the exact person this event is built for — describe them in detail?",
        "What would make someone lie awake the night before regretting that they didn't sign up?",
        "What's the one non-obvious thing people will take away that they won't find anywhere else?",
    ],
}

_FOLLOW_UP_QUESTIONS: list[str] = [
    "Is there anything about your current situation — professional or personal — that gives this content more context?",
    "What's the relationship between this content and the last thing you shared publicly?",
    "What are you afraid people might misunderstand about this — and is that fear worth addressing directly?",
]


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def generate_intake_questions(
    upload: ContentUpload,
    session: BrainSession,
) -> list[str]:
    """Generate adaptive psychological intake questions based on upload type and session history."""
    base_questions = _INTAKE_QUESTIONS.get(upload.content_type, _INTAKE_QUESTIONS[ContentType.STATEMENT])

    if len(session.uploads) > 1:
        return base_questions[:3] + _FOLLOW_UP_QUESTIONS[:2]

    return base_questions[:5]


def ingest_content(upload: ContentUpload, session: BrainSession) -> BrainSession:
    """Ingest an upload into the Brain session and update story context."""
    updated_uploads = session.uploads + [upload]
    updated_session = session.model_copy(update={"uploads": updated_uploads})
    new_context = build_story_context(updated_session)
    return updated_session.model_copy(update={"current_story_context": new_context})


def route_content(
    session: BrainSession,
    platforms: list[Platform],
) -> dict[Platform, ContentUpload]:
    """Route content from the Brain to the appropriate platform mini apps.

    Each platform receives the upload best suited to its format. When multiple
    uploads are present the routing prefers uploads whose content_type maps
    most naturally to the platform.
    """
    _PLATFORM_PREFERRED_TYPES: dict[Platform, list[str]] = {
        Platform.TIKTOK: ["video", "statement"],
        Platform.INSTAGRAM: ["photo", "video", "statement"],
        Platform.FACEBOOK: ["statement", "photo", "calendar_event"],
        Platform.LINKEDIN: ["statement", "photo"],
        Platform.YOUTUBE: ["video"],
        Platform.FIVERR: ["statement"],
        Platform.X: ["statement", "photo"],
    }

    if not session.uploads:
        return {}

    routing: dict[Platform, ContentUpload] = {}
    for platform in platforms:
        preferred = _PLATFORM_PREFERRED_TYPES.get(platform, [])
        selected: ContentUpload | None = None
        for pref_type in preferred:
            for upload in session.uploads:
                if upload.content_type.value == pref_type:
                    selected = upload
                    break
            if selected:
                break
        routing[platform] = selected or session.uploads[0]

    return routing


def build_story_context(session: BrainSession) -> str:
    """Synthesise all uploads and intake answers into a cohesive story context string."""
    parts: list[str] = []

    if session.uploads:
        parts.append(f"CONTENT ({len(session.uploads)} upload(s)):")
        for i, upload in enumerate(session.uploads, 1):
            snippet = upload.raw_content[:120].replace("\n", " ")
            if len(upload.raw_content) > 120:
                snippet += "…"
            parts.append(f"  [{i}] {upload.content_type.value.upper()}: {snippet}")

    if session.intake_answers:
        parts.append("\nCREATOR INSIGHTS:")
        for answer in session.intake_answers:
            answer_snippet = answer.answer_text[:100].replace("\n", " ")
            if len(answer.answer_text) > 100:
                answer_snippet += "…"
            parts.append(f"  Q{answer.question_id} → {answer_snippet}")

    if not parts:
        return "No content or insights captured yet."

    return "\n".join(parts)
