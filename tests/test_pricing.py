"""Tests for pricing tiers and access control."""

from __future__ import annotations

import pytest

from src.creator_ai.pricing import (
    TIER_FEATURES,
    TIER_PRICING,
    Tier,
    check_feature_access,
    get_tier_description,
)


class TestTierDefinitions:
    def test_all_four_tiers_exist(self):
        assert Tier.FOUNDATION in Tier
        assert Tier.CREATOR in Tier
        assert Tier.PROFESSIONAL in Tier
        assert Tier.ENTERPRISE in Tier

    def test_foundation_price_is_9_99(self):
        assert TIER_PRICING[Tier.FOUNDATION] == 9.99

    def test_creator_price_is_24_99(self):
        assert TIER_PRICING[Tier.CREATOR] == 24.99

    def test_professional_price_is_49_99(self):
        assert TIER_PRICING[Tier.PROFESSIONAL] == 49.99

    def test_enterprise_price_is_99_99(self):
        assert TIER_PRICING[Tier.ENTERPRISE] == 99.99

    def test_tiers_increase_in_price(self):
        prices = [
            TIER_PRICING[Tier.FOUNDATION],
            TIER_PRICING[Tier.CREATOR],
            TIER_PRICING[Tier.PROFESSIONAL],
            TIER_PRICING[Tier.ENTERPRISE],
        ]
        for i in range(len(prices) - 1):
            assert prices[i] < prices[i + 1]


class TestTierFeatures:
    def test_foundation_includes_layer1_and_layer2_only(self):
        features = TIER_FEATURES[Tier.FOUNDATION]
        assert "layer1" in features
        assert "layer2" in features
        assert len(features) == 2

    def test_creator_includes_foundation_features_plus_analytics(self):
        features = TIER_FEATURES[Tier.CREATOR]
        assert "layer1" in features
        assert "layer2" in features
        assert "layer2_5" in features

    def test_professional_includes_platform_mini_apps(self):
        features = TIER_FEATURES[Tier.PROFESSIONAL]
        assert "layer3" in features

    def test_enterprise_includes_all_layers(self):
        features = TIER_FEATURES[Tier.ENTERPRISE]
        required = ["layer1", "layer2", "layer2_5", "layer3", "layer4", "layer5", "layer6", "layer6_5"]
        for layer in required:
            assert layer in features, f"{layer} missing from Enterprise tier"

    def test_enterprise_has_most_features(self):
        enterprise_count = len(TIER_FEATURES[Tier.ENTERPRISE])
        for tier in Tier:
            assert len(TIER_FEATURES[tier]) <= enterprise_count

    def test_higher_tiers_include_all_lower_tier_features(self):
        """Each tier should be a superset of all lower tiers."""
        tiers_ordered = [Tier.FOUNDATION, Tier.CREATOR, Tier.PROFESSIONAL, Tier.ENTERPRISE]
        for i, lower_tier in enumerate(tiers_ordered[:-1]):
            for higher_tier in tiers_ordered[i + 1:]:
                lower_features = set(TIER_FEATURES[lower_tier])
                higher_features = set(TIER_FEATURES[higher_tier])
                assert lower_features.issubset(higher_features), (
                    f"{higher_tier} should include all features from {lower_tier}"
                )


class TestCheckFeatureAccess:
    def test_foundation_can_access_layer1(self):
        assert check_feature_access(Tier.FOUNDATION, "layer1") is True

    def test_foundation_can_access_layer2(self):
        assert check_feature_access(Tier.FOUNDATION, "layer2") is True

    def test_foundation_cannot_access_layer3(self):
        assert check_feature_access(Tier.FOUNDATION, "layer3") is False

    def test_foundation_cannot_access_layer4(self):
        assert check_feature_access(Tier.FOUNDATION, "layer4") is False

    def test_creator_can_access_analytics(self):
        assert check_feature_access(Tier.CREATOR, "layer2_5") is True

    def test_creator_cannot_access_layer3(self):
        assert check_feature_access(Tier.CREATOR, "layer3") is False

    def test_professional_can_access_layer3(self):
        assert check_feature_access(Tier.PROFESSIONAL, "layer3") is True

    def test_professional_cannot_access_layer4(self):
        assert check_feature_access(Tier.PROFESSIONAL, "layer4") is False

    def test_enterprise_can_access_all_layers(self):
        all_layers = ["layer1", "layer2", "layer2_5", "layer3", "layer4", "layer5", "layer6", "layer6_5"]
        for layer in all_layers:
            assert check_feature_access(Tier.ENTERPRISE, layer) is True, (
                f"Enterprise should have access to {layer}"
            )

    def test_nonexistent_feature_returns_false(self):
        assert check_feature_access(Tier.ENTERPRISE, "layer99") is False

    def test_empty_feature_string_returns_false(self):
        assert check_feature_access(Tier.ENTERPRISE, "") is False


class TestGetTierDescription:
    def test_returns_dict(self):
        result = get_tier_description(Tier.FOUNDATION)
        assert isinstance(result, dict)

    def test_includes_price(self):
        result = get_tier_description(Tier.CREATOR)
        assert "price_per_month" in result
        assert result["price_per_month"] == 24.99

    def test_includes_features_list(self):
        result = get_tier_description(Tier.PROFESSIONAL)
        assert "features" in result
        assert isinstance(result["features"], list)
        assert len(result["features"]) > 0

    def test_includes_description_text(self):
        result = get_tier_description(Tier.ENTERPRISE)
        assert "description" in result
        assert len(result["description"]) > 0

    def test_includes_tier_name(self):
        result = get_tier_description(Tier.FOUNDATION)
        assert "tier" in result
        assert result["tier"] == "foundation"

    @pytest.mark.parametrize("tier", list(Tier))
    def test_all_tiers_return_complete_description(self, tier: Tier):
        result = get_tier_description(tier)
        assert "tier" in result
        assert "price_per_month" in result
        assert "features" in result
        assert "description" in result
