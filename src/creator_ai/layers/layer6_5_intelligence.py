"""Layer 6.5 — Audience Engagement Intelligence: performance analysis and strategy."""

from __future__ import annotations

from collections import defaultdict

from .layer2_5_analytics import CreativePattern
from .layer6_alerts import score_interaction
from ..models.content import Platform
from ..models.engagement import EngagementScore, Interaction, ALERT_THRESHOLD


def analyse_platform_performance(interactions: list[Interaction]) -> dict[Platform, dict]:
    """Return performance metrics per platform: total score, unique engagers, avg score, top content."""
    platform_data: dict[Platform, dict] = {}

    by_platform: dict[str, list[Interaction]] = defaultdict(list)
    for interaction in interactions:
        by_platform[interaction.platform.value].append(interaction)

    for platform_val, items in by_platform.items():
        try:
            platform = Platform(platform_val)
        except ValueError:
            continue

        total_score = sum(score_interaction(i) for i in items)
        unique_engagers = len({i.user_id for i in items})
        avg_score = total_score / len(items) if items else 0.0

        post_scores: dict[str, float] = defaultdict(float)
        for item in items:
            if item.post_id:
                post_scores[item.post_id] += score_interaction(item)

        top_post = max(post_scores, key=lambda k: post_scores[k]) if post_scores else None

        platform_data[platform] = {
            "total_score": round(total_score, 2),
            "interaction_count": len(items),
            "unique_engagers": unique_engagers,
            "avg_score_per_interaction": round(avg_score, 2),
            "top_post_id": top_post,
            "top_post_score": round(post_scores.get(top_post, 0.0), 2) if top_post else 0.0,
        }

    return platform_data


def identify_high_intent_segments(scores: list[EngagementScore]) -> list[dict]:
    """Identify audience segments with highest conversion probability.

    Returns segments sorted by total_score descending, annotated with
    segment type (super_fan, warm_lead, active_follower).
    """
    segments: list[dict] = []
    for score in scores:
        if score.total_score >= ALERT_THRESHOLD * 2:
            segment_type = "super_fan"
            conversion_probability = 0.85
        elif score.total_score >= ALERT_THRESHOLD:
            segment_type = "warm_lead"
            conversion_probability = 0.60
        elif score.total_score >= ALERT_THRESHOLD * 0.5:
            segment_type = "active_follower"
            conversion_probability = 0.30
        else:
            segment_type = "casual_viewer"
            conversion_probability = 0.05

        platform_counts: dict[str, int] = defaultdict(int)
        for interaction in score.interactions:
            platform_counts[interaction.platform.value] += 1
        primary_platform = max(platform_counts, key=lambda k: platform_counts[k]) if platform_counts else "unknown"

        segments.append({
            "user_id": score.user_id,
            "segment_type": segment_type,
            "total_score": round(score.total_score, 2),
            "conversion_probability": conversion_probability,
            "primary_platform": primary_platform,
            "touchpoint_count": len(score.interactions),
            "alert_triggered": score.alert_triggered,
        })

    return sorted(segments, key=lambda s: s["total_score"], reverse=True)


def generate_strategy_recommendations(
    platform_performance: dict,
    creative_pattern: CreativePattern,
) -> list[str]:
    """Return actionable strategy recommendations based on data."""
    recommendations: list[str] = []

    if platform_performance:
        top_platform = max(
            platform_performance,
            key=lambda p: platform_performance[p].get("total_score", 0),
        )
        top_data = platform_performance[top_platform]
        recommendations.append(
            f"📈 DOUBLE DOWN ON {top_platform.value.upper()}: Your highest-performing platform "
            f"(score: {top_data['total_score']}, {top_data['unique_engagers']} unique engagers). "
            f"Increase posting frequency by 20% here first."
        )

        low_performers = [
            p for p, d in platform_performance.items()
            if d.get("avg_score_per_interaction", 0) < 1.0
        ]
        for lp in low_performers[:2]:
            recommendations.append(
                f"⚠️ REVIEW {lp.value.upper()} STRATEGY: Low average engagement score per interaction. "
                f"Test a different content format or post at different peak hours."
            )

    if creative_pattern.mood_quality_correlation:
        best_mood = max(
            creative_pattern.mood_quality_correlation,
            key=lambda k: creative_pattern.mood_quality_correlation[k],
        )
        recommendations.append(
            f"🧠 BATCH CREATE IN '{best_mood.upper().replace('_', ' ')}' MOOD: "
            f"Your data shows this emotional state correlates with your highest-quality output. "
            f"Schedule longer creation blocks when you feel this way."
        )

    if creative_pattern.preferred_content_types:
        top_type = max(
            creative_pattern.preferred_content_types,
            key=lambda k: creative_pattern.preferred_content_types[k],
        )
        recommendations.append(
            f"🎯 LEAN INTO {top_type.upper()} CONTENT: This is your most-created format. "
            f"Build a repeatable production system around it to reduce friction and increase output."
        )

    if creative_pattern.productivity_peaks:
        from collections import Counter
        peak = Counter(creative_pattern.productivity_peaks).most_common(1)[0][0]
        recommendations.append(
            f"⏰ PROTECT YOUR {peak.upper().replace('_', ' ')} BLOCK: "
            f"Your creation data shows this is when you produce the most. "
            f"Block this time in your calendar and treat it as non-negotiable."
        )

    if not recommendations:
        recommendations.append(
            "📊 MORE DATA NEEDED: Keep creating and engaging to build a meaningful pattern. "
            "Recommendations improve significantly after 10+ sessions."
        )

    return recommendations


def get_content_resonance_map(interactions: list[Interaction]) -> dict:
    """Map which content types and posts are generating the most high-value engagement."""
    post_metrics: dict[str, dict] = defaultdict(lambda: {
        "total_score": 0.0,
        "interaction_count": 0,
        "unique_users": set(),
        "platforms": set(),
        "interaction_types": [],
    })

    for interaction in interactions:
        if not interaction.post_id:
            continue
        post_id = interaction.post_id
        s = score_interaction(interaction)
        post_metrics[post_id]["total_score"] += s
        post_metrics[post_id]["interaction_count"] += 1
        post_metrics[post_id]["unique_users"].add(interaction.user_id)
        post_metrics[post_id]["platforms"].add(interaction.platform.value)
        post_metrics[post_id]["interaction_types"].append(interaction.interaction_type.value)

    resonance_map: dict[str, dict] = {}
    for post_id, data in post_metrics.items():
        resonance_map[post_id] = {
            "total_score": round(data["total_score"], 2),
            "interaction_count": data["interaction_count"],
            "unique_engagers": len(data["unique_users"]),
            "platforms": list(data["platforms"]),
            "interaction_types": list(set(data["interaction_types"])),
            "resonance_level": (
                "viral" if data["total_score"] >= 50
                else "high" if data["total_score"] >= 25
                else "medium" if data["total_score"] >= 10
                else "low"
            ),
        }

    return dict(
        sorted(resonance_map.items(), key=lambda x: x[1]["total_score"], reverse=True)
    )
