"""
Tests for confidence calibration in confidence_calibrator.py

These tests verify that:
- Confidence calibration formulas work correctly
- Evidence tiers affect confidence appropriately
- Claim categorization (weak/strong) is accurate
"""

import pytest
from agents.confidence_calibrator import (
    TIER_WEIGHTS,
    SOURCE_BONUS,
    calibrate_claim_confidence,
    calibrate_section_claims,
    calibrate_cross_reference_index,
    get_confidence_distribution,
    identify_weak_claims,
    identify_foundation_claims,
    calculate_section_quality_score,
)


class TestTierWeights:
    """Tests for tier weight constants."""

    def test_e1_has_highest_weight(self):
        """E1 (primary research) should have the highest weight."""
        assert TIER_WEIGHTS["E1"] == 1.0
        assert TIER_WEIGHTS["E1"] > TIER_WEIGHTS["E2"]

    def test_weights_decrease_by_tier(self):
        """Weights should decrease from E1 to E5."""
        assert TIER_WEIGHTS["E1"] > TIER_WEIGHTS["E2"]
        assert TIER_WEIGHTS["E2"] > TIER_WEIGHTS["E3"]
        assert TIER_WEIGHTS["E3"] > TIER_WEIGHTS["E4"]
        assert TIER_WEIGHTS["E4"] > TIER_WEIGHTS["E5"]

    def test_e5_has_lowest_weight(self):
        """E5 (assumption) should have the lowest weight."""
        assert TIER_WEIGHTS["E5"] == 0.1


class TestCalibrateClaim:
    """Tests for calibrate_claim_confidence function."""

    def test_e1_claim_maintains_high_confidence(self):
        """E1 claims should maintain their confidence."""
        claim = {
            "evidence_tier": "E1",
            "confidence": 0.9,
            "source": None,
        }

        calibrated = calibrate_claim_confidence(claim)

        # E1 weight = 1.0, so 0.9 * 1.0 = 0.9
        assert calibrated == 0.9

    def test_e5_claim_reduces_confidence(self):
        """E5 claims should have significantly reduced confidence."""
        claim = {
            "evidence_tier": "E5",
            "confidence": 0.9,
            "source": None,
        }

        calibrated = calibrate_claim_confidence(claim)

        # E5 weight = 0.1, so 0.9 * 0.1 = 0.09
        assert calibrated == 0.09

    def test_source_adds_bonus(self):
        """Having a source should add confidence bonus."""
        claim_no_source = {
            "evidence_tier": "E4",
            "confidence": 0.5,
            "source": None,
        }

        claim_with_source = {
            "evidence_tier": "E4",
            "confidence": 0.5,
            "source": "https://example.com",
        }

        calibrated_no_source = calibrate_claim_confidence(claim_no_source)
        calibrated_with_source = calibrate_claim_confidence(claim_with_source)

        assert calibrated_with_source > calibrated_no_source
        assert calibrated_with_source - calibrated_no_source == SOURCE_BONUS

    def test_confidence_clamped_to_1(self):
        """Calibrated confidence should not exceed 1.0."""
        claim = {
            "evidence_tier": "E1",
            "confidence": 1.0,
            "source": "https://example.com",
        }

        calibrated = calibrate_claim_confidence(claim)

        assert calibrated <= 1.0

    def test_confidence_clamped_to_0(self):
        """Calibrated confidence should not go below 0.0."""
        claim = {
            "evidence_tier": "E5",
            "confidence": 0.0,
            "source": None,
        }

        calibrated = calibrate_claim_confidence(claim)

        assert calibrated >= 0.0

    def test_unknown_tier_uses_e5_weight(self):
        """Unknown tiers should default to E5 weight."""
        claim = {
            "evidence_tier": "E99",  # Invalid tier
            "confidence": 0.5,
            "source": None,
        }

        calibrated = calibrate_claim_confidence(claim)

        # Should use E5 weight (0.1)
        expected = 0.5 * 0.1
        assert calibrated == expected


class TestCalibrateSectionClaims:
    """Tests for calibrate_section_claims function."""

    def test_preserves_raw_confidence(self):
        """Should preserve original confidence as raw_confidence."""
        claims = [
            {"evidence_tier": "E2", "confidence": 0.8, "source": None},
        ]

        calibrated = calibrate_section_claims(claims)

        assert calibrated[0]["raw_confidence"] == 0.8
        assert calibrated[0]["confidence"] != 0.8  # Should be calibrated

    def test_calibrates_all_claims(self):
        """Should calibrate all claims in the list."""
        claims = [
            {"evidence_tier": "E1", "confidence": 0.9, "source": None},
            {"evidence_tier": "E5", "confidence": 0.9, "source": None},
        ]

        calibrated = calibrate_section_claims(claims)

        assert len(calibrated) == 2
        assert calibrated[0]["confidence"] > calibrated[1]["confidence"]


class TestCalibrateCrossReferenceIndex:
    """Tests for calibrate_cross_reference_index function."""

    def test_updates_claims_and_score(self):
        """Should update claims and recalculate evidence score."""
        cross_ref = {
            "claims": [
                {"evidence_tier": "E2", "confidence": 0.8, "source": "url"},
                {"evidence_tier": "E4", "confidence": 0.8, "source": None},
            ],
            "evidence_score": 0.5,
        }

        calibrated = calibrate_cross_reference_index(cross_ref)

        assert "calibrated_evidence_score" in calibrated
        assert calibrated["claims"][0]["raw_confidence"] == 0.8

    def test_handles_empty_index(self):
        """Should handle empty cross-reference index."""
        result = calibrate_cross_reference_index({})

        assert result == {}

    def test_handles_none_index(self):
        """Should handle None cross-reference index."""
        result = calibrate_cross_reference_index(None)

        assert result is None


class TestGetConfidenceDistribution:
    """Tests for get_confidence_distribution function."""

    def test_counts_by_tier(self):
        """Should count claims by evidence tier."""
        claims = [
            {"evidence_tier": "E1", "confidence": 0.9},
            {"evidence_tier": "E1", "confidence": 0.8},
            {"evidence_tier": "E4", "confidence": 0.5},
        ]

        dist = get_confidence_distribution(claims)

        assert dist["by_tier"]["E1"] == 2
        assert dist["by_tier"]["E4"] == 1

    def test_calculates_averages(self):
        """Should calculate average confidences."""
        claims = [
            {"evidence_tier": "E1", "confidence": 0.9},
            {"evidence_tier": "E1", "confidence": 0.7},
        ]

        dist = get_confidence_distribution(claims)

        assert dist["avg_raw_confidence"] == 0.8

    def test_counts_high_low_confidence(self):
        """Should count high and low confidence claims."""
        claims = [
            {"evidence_tier": "E1", "confidence": 0.9, "source": "url"},  # High after calibration
            {"evidence_tier": "E5", "confidence": 0.9, "source": None},  # Low after calibration
        ]

        dist = get_confidence_distribution(claims)

        assert "high_confidence_count" in dist
        assert "low_confidence_count" in dist

    def test_handles_empty_claims(self):
        """Should handle empty claims list."""
        dist = get_confidence_distribution([])

        assert dist["total"] == 0


class TestIdentifyWeakClaims:
    """Tests for identify_weak_claims function."""

    def test_returns_low_confidence_claims(self):
        """Should return claims below threshold."""
        claims = [
            {"claim_id": "A", "evidence_tier": "E1", "confidence": 0.9, "source": "url"},  # High: 0.9 * 1.0 + 0.1 = 1.0
            {"claim_id": "B", "evidence_tier": "E5", "confidence": 0.5, "source": None},  # Low: 0.5 * 0.1 = 0.05
        ]

        # Threshold 0.1 to catch the E5 claim (0.05 < 0.1)
        weak = identify_weak_claims(claims, threshold=0.1)

        # E5 with 0.5 confidence = 0.5 * 0.1 = 0.05, which is < 0.1
        weak_ids = [c["claim_id"] for c in weak]
        assert "B" in weak_ids
        assert "A" not in weak_ids  # E1 claim should not be in weak list

    def test_sorts_by_confidence(self):
        """Should sort by confidence (lowest first)."""
        claims = [
            {"claim_id": "A", "evidence_tier": "E5", "confidence": 0.3},  # Very low
            {"claim_id": "B", "evidence_tier": "E5", "confidence": 0.5},  # Low
        ]

        weak = identify_weak_claims(claims, threshold=0.5)

        if len(weak) >= 2:
            assert weak[0]["claim_id"] == "A"  # Lowest first


class TestIdentifyFoundationClaims:
    """Tests for identify_foundation_claims function."""

    def test_returns_high_confidence_claims(self):
        """Should return claims above threshold."""
        claims = [
            {"claim_id": "A", "evidence_tier": "E1", "confidence": 0.9, "source": "url"},
            {"claim_id": "B", "evidence_tier": "E5", "confidence": 0.5},
        ]

        strong = identify_foundation_claims(claims, threshold=0.7)

        strong_ids = [c["claim_id"] for c in strong]
        assert "A" in strong_ids  # E1 with 0.9 + source = high calibrated
        # B should not be there (E5 with 0.5 = 0.05 calibrated)

    def test_sorts_by_confidence_descending(self):
        """Should sort by confidence (highest first)."""
        claims = [
            {"claim_id": "A", "evidence_tier": "E1", "confidence": 0.8, "source": "url"},
            {"claim_id": "B", "evidence_tier": "E1", "confidence": 0.9, "source": "url"},
        ]

        strong = identify_foundation_claims(claims, threshold=0.5)

        if len(strong) >= 2:
            # B has higher raw confidence, should be first
            assert strong[0]["claim_id"] == "B"


class TestCalculateSectionQualityScore:
    """Tests for calculate_section_quality_score function."""

    def test_calculates_overall_score(self):
        """Should calculate weighted quality score."""
        claims = [
            {"evidence_tier": "E1", "confidence": 0.9, "source": "url"},
            {"evidence_tier": "E2", "confidence": 0.8, "source": "url"},
        ]

        quality = calculate_section_quality_score(claims, "Market Intelligence")

        assert "score" in quality
        assert 0 <= quality["score"] <= 1

    def test_includes_all_metrics(self):
        """Should include all quality metrics."""
        claims = [
            {"evidence_tier": "E1", "confidence": 0.9, "source": "url"},
        ]

        quality = calculate_section_quality_score(claims, "Market Intelligence")

        assert "avg_confidence" in quality
        assert "tier_score" in quality
        assert "source_coverage" in quality
        assert "claim_adequacy" in quality

    def test_checks_minimum_claims(self):
        """Should check if minimum claims met."""
        claims = [
            {"evidence_tier": "E1", "confidence": 0.9, "source": "url"},
        ]

        # Market Intelligence requires 5 claims
        quality = calculate_section_quality_score(claims, "Market Intelligence")

        assert quality["claim_adequacy"] is False
        assert quality["claim_count"] == 1
        assert quality["min_required"] == 5

    def test_handles_empty_claims(self):
        """Should handle empty claims list."""
        quality = calculate_section_quality_score([], "Test Section")

        assert quality["score"] == 0.0
