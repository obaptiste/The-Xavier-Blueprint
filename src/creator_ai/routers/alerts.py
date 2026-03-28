"""Router: Layers 6 & 6.5 — Alert System and Audience Engagement Intelligence endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..layers.layer6_alerts import (
    calculate_engagement_score,
    check_alert,
    format_alert_message,
    score_interaction,
)
from ..layers.layer6_5_intelligence import (
    analyse_platform_performance,
    generate_strategy_recommendations,
    get_content_resonance_map,
    identify_high_intent_segments,
)
from ..layers.layer2_5_analytics import CreativePattern
from ..models.engagement import EngagementScore, Interaction
from ..models.personality import PersonalityProfile

router = APIRouter(tags=["alerts"])

_SCORES: dict[str, EngagementScore] = {}
_INTERACTIONS: list[Interaction] = []


class ScoreRequest(BaseModel):
    interaction: Interaction
    profile: PersonalityProfile


class AlertRequest(BaseModel):
    interactions: list[Interaction]
    profile: PersonalityProfile


@router.post("/alerts/score", response_model=dict)
def score_new_interaction(request: ScoreRequest) -> dict:
    """Score a single interaction and return its weight."""
    weight = score_interaction(request.interaction)
    _INTERACTIONS.append(request.interaction)
    return {
        "interaction_id": request.interaction.id,
        "interaction_type": request.interaction.interaction_type.value,
        "score": weight,
        "user_id": request.interaction.user_id,
    }


@router.get("/alerts/engagement/{user_id}", response_model=EngagementScore)
def get_engagement_score(user_id: str, creator_id: str) -> EngagementScore:
    """Get the aggregated engagement score for a (user, creator) pair."""
    matching = [
        i for i in _INTERACTIONS
        if i.user_id == user_id and i.creator_id == creator_id
    ]
    if not matching:
        raise HTTPException(
            status_code=404,
            detail=f"No interactions found for user '{user_id}' with creator '{creator_id}'.",
        )
    return calculate_engagement_score(matching)


@router.get("/alerts/high-intent", response_model=list[dict])
def get_high_intent_engagers(creator_id: str, threshold: float = 15.0) -> list[dict]:
    """Get list of high-intent engagers above the specified threshold."""
    by_user: dict[str, list[Interaction]] = {}
    for interaction in _INTERACTIONS:
        if interaction.creator_id == creator_id:
            by_user.setdefault(interaction.user_id, []).append(interaction)

    scores = [calculate_engagement_score(items) for items in by_user.values() if items]
    high_intent = [s for s in scores if s.total_score >= threshold]
    return identify_high_intent_segments(high_intent)


@router.get("/analytics/platform-performance", response_model=dict)
def get_platform_performance(creator_id: str) -> dict:
    """Get platform performance analysis for a creator."""
    creator_interactions = [i for i in _INTERACTIONS if i.creator_id == creator_id]
    if not creator_interactions:
        return {}
    perf = analyse_platform_performance(creator_interactions)
    return {p.value: data for p, data in perf.items()}


@router.get("/analytics/recommendations", response_model=list[str])
def get_recommendations(creator_id: str) -> list[str]:
    """Get strategy recommendations for a creator based on their interaction data."""
    creator_interactions = [i for i in _INTERACTIONS if i.creator_id == creator_id]
    platform_perf = analyse_platform_performance(creator_interactions) if creator_interactions else {}
    pattern = CreativePattern(user_id=creator_id)
    return generate_strategy_recommendations(platform_perf, pattern)
