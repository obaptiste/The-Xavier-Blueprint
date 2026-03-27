"""Layer 6 — Interest Alert System: score interactions and fire creator alerts."""

from __future__ import annotations

from ..models.archetypes import ARCHETYPE_METADATA
from ..models.content import Platform
from ..models.engagement import (
    ALERT_THRESHOLD,
    INTERACTION_WEIGHTS,
    EngagementScore,
    Interaction,
    InteractionType,
)
from ..models.personality import PersonalityProfile


def score_interaction(interaction: Interaction) -> float:
    """Return the weighted score for a single interaction."""
    return INTERACTION_WEIGHTS.get(interaction.interaction_type, 0.0)


def calculate_engagement_score(interactions: list[Interaction]) -> EngagementScore:
    """Aggregate interaction scores and determine if alert threshold is crossed.

    Groups by (user_id, creator_id) pair — assumes all interactions share the same pair.
    """
    if not interactions:
        raise ValueError("interactions list must not be empty")

    total = sum(score_interaction(i) for i in interactions)
    triggered = check_alert_from_score(total)

    return EngagementScore(
        user_id=interactions[0].user_id,
        creator_id=interactions[0].creator_id,
        total_score=total,
        interactions=interactions,
        alert_triggered=triggered,
    )


def check_alert(score: EngagementScore) -> bool:
    """Return True if the score has crossed the alert threshold."""
    return score.total_score >= ALERT_THRESHOLD


def check_alert_from_score(total_score: float) -> bool:
    """Utility: check threshold from a raw float score."""
    return total_score >= ALERT_THRESHOLD


_INTERACTION_LABELS: dict[InteractionType, str] = {
    InteractionType.FIVERR_DM: "sent you a direct message on Fiverr",
    InteractionType.LINKEDIN_DM: "sent you a direct message on LinkedIn",
    InteractionType.INSTAGRAM_DM: "sent you a direct message on Instagram",
    InteractionType.YOUTUBE_LINK_CLICK: "clicked through from your YouTube content",
    InteractionType.INSTAGRAM_SAVE: "saved your Instagram post",
    InteractionType.TIKTOK_DUET_STITCH: "dueted or stitched your TikTok",
    InteractionType.FACEBOOK_SHARE: "shared your content on Facebook",
    InteractionType.COMMENT_WITH_QUESTION: "left a question in your comments",
    InteractionType.STANDARD_COMMENT: "commented on your content",
    InteractionType.LIKE: "liked your content",
}

_INTENT_LEVELS = [
    (20.0, "🔥 EXTREMELY HIGH INTENT — respond immediately"),
    (15.0, "⚡ HIGH INTENT — prioritise this person"),
    (10.0, "📈 GROWING INTEREST — worth engaging"),
    (5.0, "👀 EARLY SIGNAL — warming up"),
    (0.0, "💡 INITIAL CONTACT — new audience member"),
]


def format_alert_message(score: EngagementScore, profile: PersonalityProfile) -> str:
    """Format a human-readable alert for the creator: who, what, where, how much intent."""
    archetype_meta = ARCHETYPE_METADATA.get(profile.archetype, {})
    archetype_name = archetype_meta.get("name", profile.archetype.value.title())

    intent_label = _INTENT_LEVELS[-1][1]
    for threshold, label in _INTENT_LEVELS:
        if score.total_score >= threshold:
            intent_label = label
            break

    platform_summary: dict[str, list[str]] = {}
    for interaction in score.interactions:
        p = interaction.platform.value
        label = _INTERACTION_LABELS.get(interaction.interaction_type, interaction.interaction_type.value)
        platform_summary.setdefault(p, []).append(label)

    platform_lines = []
    for platform, actions in platform_summary.items():
        platform_lines.append(f"  • {platform.upper()}: {', '.join(actions)}")

    lines = [
        f"🚨 CREATOR ALERT — {archetype_name} Mode",
        f"",
        f"User ID: {score.user_id}",
        f"Engagement Score: {score.total_score:.1f} / {ALERT_THRESHOLD:.0f} threshold",
        f"Intent Level: {intent_label}",
        f"",
        f"Activity across platforms:",
        *platform_lines,
        f"",
        f"Total touchpoints: {len(score.interactions)}",
        f"Recommendation: This person is signalling real interest. Engage them now.",
    ]
    return "\n".join(lines)
