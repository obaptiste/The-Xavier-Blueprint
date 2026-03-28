"""Tier definitions and access control for Creator AI pricing."""

from __future__ import annotations

from enum import Enum


class Tier(str, Enum):
    FOUNDATION = "foundation"
    CREATOR = "creator"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


TIER_PRICING: dict[Tier, float] = {
    Tier.FOUNDATION: 9.99,
    Tier.CREATOR: 24.99,
    Tier.PROFESSIONAL: 49.99,
    Tier.ENTERPRISE: 99.99,
}

TIER_FEATURES: dict[Tier, list[str]] = {
    Tier.FOUNDATION: ["layer1", "layer2"],
    Tier.CREATOR: ["layer1", "layer2", "layer2_5"],
    Tier.PROFESSIONAL: ["layer1", "layer2", "layer2_5", "layer3"],
    Tier.ENTERPRISE: [
        "layer1",
        "layer2",
        "layer2_5",
        "layer3",
        "layer4",
        "layer5",
        "layer6",
        "layer6_5",
    ],
}

TIER_DESCRIPTIONS: dict[Tier, str] = {
    Tier.FOUNDATION: (
        "Everything you need to discover your archetype and start feeding content into your Brain. "
        "Your personality DNA and content ingestion engine."
    ),
    Tier.CREATOR: (
        "Foundation plus Personal Creative Analytics — understand when you create best, "
        "what moods drive your best work, and how your archetype is evolving."
    ),
    Tier.PROFESSIONAL: (
        "Creator plus Platform Mini Apps — generate archetype-voiced, platform-native "
        "content for TikTok, Instagram, Facebook, LinkedIn, YouTube, Fiverr, and X."
    ),
    Tier.ENTERPRISE: (
        "The full system — every layer unlocked. Intelligent scheduling, live response engine, "
        "interest alerts, and audience engagement intelligence. For creators serious about scale."
    ),
}


def check_feature_access(tier: Tier, feature: str) -> bool:
    """Return True if the given tier includes access to the given feature layer."""
    return feature in TIER_FEATURES.get(tier, [])


def get_tier_description(tier: Tier) -> dict:
    """Return full tier description with price and included features."""
    return {
        "tier": tier.value,
        "price_per_month": TIER_PRICING[tier],
        "features": TIER_FEATURES[tier],
        "description": TIER_DESCRIPTIONS[tier],
    }
