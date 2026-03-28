"""Layer 2.5 — Personal Creative Analytics: track patterns, productivity, and mood quality."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..models.archetypes import Archetype
from ..models.content import ContentType
from ..models.personality import Mood, PersonalityProfile
from ..models.content import BrainSession


@dataclass
class CreativePattern:
    """Aggregated creative pattern data for a single creator."""

    user_id: str
    productivity_peaks: list[str] = field(default_factory=list)
    preferred_content_types: dict[str, int] = field(default_factory=dict)
    mood_quality_correlation: dict[str, float] = field(default_factory=dict)
    archetype_evolution: list[tuple[datetime, str]] = field(default_factory=list)
    total_sessions: int = 0
    total_uploads: int = 0


def track_session(session: BrainSession, profile: PersonalityProfile) -> CreativePattern:
    """Record a completed session against the creator's creative pattern."""
    pattern = CreativePattern(user_id=session.user_id)
    pattern.total_sessions = 1
    pattern.total_uploads = len(session.uploads)

    hour = session.created_at.hour
    if hour < 6:
        time_label = "late_night"
    elif hour < 12:
        time_label = "morning"
    elif hour < 17:
        time_label = "afternoon"
    elif hour < 21:
        time_label = "evening"
    else:
        time_label = "night"
    pattern.productivity_peaks = [time_label]

    for upload in session.uploads:
        ct = upload.content_type.value
        pattern.preferred_content_types[ct] = pattern.preferred_content_types.get(ct, 0) + 1

    mood_key = profile.mood.value
    upload_count = len(session.uploads)
    quality_score = min(1.0, upload_count / 5.0) if upload_count > 0 else 0.0
    pattern.mood_quality_correlation[mood_key] = quality_score

    pattern.archetype_evolution = [(session.created_at, profile.archetype.value)]

    return pattern


def get_productivity_insights(pattern: CreativePattern) -> dict:
    """Return actionable productivity insights from a creator's pattern data."""
    if not pattern.productivity_peaks:
        peak = "unknown"
    else:
        from collections import Counter
        peak = Counter(pattern.productivity_peaks).most_common(1)[0][0]

    top_type: str | None = None
    if pattern.preferred_content_types:
        top_type = max(pattern.preferred_content_types, key=lambda k: pattern.preferred_content_types[k])

    peak_labels = {
        "morning": "You do your best work in the morning (6am–12pm). Schedule creation blocks before noon.",
        "afternoon": "Your peak window is the afternoon (12pm–5pm). Protect that time from meetings.",
        "evening": "You create best in the evening (5pm–9pm). Night owls often produce the rawest, most authentic work.",
        "night": "You're a night creator (9pm–midnight). Your content likely carries that unfiltered late-night energy.",
        "late_night": "You work late night (midnight–6am). Your content is probably your most vulnerable and real.",
        "unknown": "Not enough data to identify your peak time yet. Keep creating.",
    }

    return {
        "peak_time": peak,
        "peak_insight": peak_labels.get(peak, peak_labels["unknown"]),
        "top_content_type": top_type,
        "total_sessions": pattern.total_sessions,
        "total_uploads": pattern.total_uploads,
        "archetype_consistency": (
            "Consistent" if len(set(a[1] for a in pattern.archetype_evolution)) == 1
            else "Evolving"
        ),
    }


def get_mood_recommendations(pattern: CreativePattern) -> str:
    """Return a recommendation string about which mood states produce the best output."""
    if not pattern.mood_quality_correlation:
        return (
            "Not enough mood data yet. Create content across different emotional states "
            "to discover when your work is most powerful."
        )

    best_mood = max(pattern.mood_quality_correlation, key=lambda k: pattern.mood_quality_correlation[k])
    worst_mood = min(pattern.mood_quality_correlation, key=lambda k: pattern.mood_quality_correlation[k])
    best_score = pattern.mood_quality_correlation[best_mood]

    mood_advice = {
        "fired_up": "Your fired-up state produces high-volume, high-energy content. Batch create when you feel this.",
        "happy": "Joy translates directly to warmth and connection in your content. Don't waste happy days.",
        "focused": "Focused mode is your most structured output. Perfect for educational and tutorial content.",
        "pissed_off": "Your frustration drives your most contrarian and provocative content. Channel it intentionally.",
        "reflective": "Reflective moods produce your deepest, most shareable wisdom. Slow down and write more.",
        "confident": "Confidence mode produces your most authoritative work. Record videos when you feel this.",
        "playful": "Playful energy makes your content accessible and shareable. Don't skip these creative days.",
        "serious": "Serious mode drives your most impactful long-form content. Use it for manifestos and statements.",
    }

    recommendation = mood_advice.get(
        best_mood,
        f"Your {best_mood} state appears to be your most productive."
    )

    lines = [
        f"BEST CREATIVE MOOD: {best_mood.upper().replace('_', ' ')} (quality score: {best_score:.0%})",
        f"INSIGHT: {recommendation}",
    ]

    if best_mood != worst_mood:
        worst_score = pattern.mood_quality_correlation[worst_mood]
        lines.append(
            f"LOWEST OUTPUT MOOD: {worst_mood.upper().replace('_', ' ')} (score: {worst_score:.0%}) — "
            "consider consuming rather than creating on these days."
        )

    return "\n".join(lines)
