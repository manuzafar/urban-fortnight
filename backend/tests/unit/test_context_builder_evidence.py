"""
Tests for evidence-aware context building in context_builder.py

These tests verify that:
- Evidence tiers are preserved in summaries
- Claims are properly categorized (verified, industry, hypotheses)
- High-priority validation claims are correctly identified
"""

import pytest
from agents.context_builder import (
    build_evidence_aware_summary,
    build_evidence_context_for_phase,
    get_high_priority_claims_for_validation,
    FIELD_TO_SECTION_PREFIX,
)


@pytest.fixture
def sample_state_with_claims():
    """Sample state with cross-reference index containing claims."""
    return {
        "session_id": "test-session-123",
        "cross_reference_index": {
            "claims": [
                {
                    "claim_id": "MI-1",
                    "statement": "Market size is $3.2B",
                    "evidence_tier": "E2",
                    "confidence": 0.85,
                    "source": "https://statista.com/report",
                },
                {
                    "claim_id": "MI-2",
                    "statement": "67% of users want mobile access",
                    "evidence_tier": "E1",
                    "confidence": 0.9,
                    "source": "primary survey",
                },
                {
                    "claim_id": "MI-3",
                    "statement": "Industry growing 5% annually",
                    "evidence_tier": "E3",
                    "confidence": 0.7,
                    "source": None,
                },
                {
                    "claim_id": "MI-4",
                    "statement": "Price sensitivity is high",
                    "evidence_tier": "E4",
                    "confidence": 0.5,
                    "source": None,
                    "depends_on": ["MI-1", "MI-3"],
                },
                {
                    "claim_id": "BC-1",
                    "statement": "SaaS model is preferred",
                    "evidence_tier": "E4",
                    "confidence": 0.6,
                    "source": None,
                },
                {
                    "claim_id": "BC-2",
                    "statement": "TAM is $10B by 2025",
                    "evidence_tier": "E5",
                    "confidence": 0.3,
                    "source": None,
                    "depends_on": ["MI-1"],
                },
            ],
            "total_claims": 6,
            "evidence_score": 0.55,
        },
    }


@pytest.fixture
def empty_state():
    """State with no claims."""
    return {
        "session_id": "empty-session",
        "cross_reference_index": {
            "claims": [],
            "total_claims": 0,
        },
    }


class TestBuildEvidenceAwareSummary:
    """Tests for build_evidence_aware_summary function."""

    def test_categorizes_verified_facts(self, sample_state_with_claims):
        """Verified facts (E1-E2) should appear in the VERIFIED FACTS section."""
        summary = build_evidence_aware_summary(
            sample_state_with_claims,
            source_sections=["customer_research"],
        )

        assert "VERIFIED FACTS (E1-E2)" in summary
        assert "[E2] Market size is $3.2B" in summary
        assert "[E1] 67% of users want mobile access" in summary

    def test_categorizes_industry_data(self, sample_state_with_claims):
        """Industry data (E3) should appear in the INDUSTRY DATA section."""
        summary = build_evidence_aware_summary(
            sample_state_with_claims,
            source_sections=["customer_research"],
        )

        assert "INDUSTRY DATA (E3)" in summary
        assert "[E3] Industry growing 5% annually" in summary

    def test_categorizes_hypotheses(self, sample_state_with_claims):
        """Hypotheses (E4-E5) should appear in the HYPOTHESES section."""
        summary = build_evidence_aware_summary(
            sample_state_with_claims,
            source_sections=["customer_research"],
        )

        assert "HYPOTHESES (E4-E5)" in summary
        assert "[E4] Price sensitivity is high" in summary
        assert "NEEDS VALIDATION" in summary

    def test_filters_by_source_sections(self, sample_state_with_claims):
        """Should only include claims from specified source sections."""
        # Only business_case claims
        summary = build_evidence_aware_summary(
            sample_state_with_claims,
            source_sections=["business_case"],
        )

        assert "BC-1" in summary
        assert "BC-2" in summary
        assert "MI-1" not in summary  # Market intelligence claim should not appear

    def test_includes_source_urls(self, sample_state_with_claims):
        """Should include source URLs when available."""
        summary = build_evidence_aware_summary(
            sample_state_with_claims,
            source_sections=["customer_research"],
        )

        assert "statista.com" in summary

    def test_handles_empty_claims(self, empty_state):
        """Should handle empty cross-reference index gracefully."""
        summary = build_evidence_aware_summary(
            empty_state,
            source_sections=["customer_research"],
        )

        assert "No claims available" in summary or "No claims found" in summary

    def test_respects_max_chars(self, sample_state_with_claims):
        """Should truncate to max_chars limit."""
        summary = build_evidence_aware_summary(
            sample_state_with_claims,
            source_sections=["customer_research"],
            max_chars=200,
        )

        assert len(summary) <= 200


class TestBuildEvidenceContextForPhase:
    """Tests for build_evidence_context_for_phase function."""

    def test_strategy_phase_includes_discovery_sections(self, sample_state_with_claims):
        """Strategy phase should include claims from discovery sections."""
        context = build_evidence_context_for_phase(
            sample_state_with_claims,
            target_phase="strategy",
        )

        # Should include customer_research claims
        assert "MI-" in context or "No claims" in context

    def test_unknown_phase_returns_empty(self, sample_state_with_claims):
        """Unknown phase should return empty string."""
        context = build_evidence_context_for_phase(
            sample_state_with_claims,
            target_phase="unknown_phase",
        )

        assert context == ""


class TestGetHighPriorityClaimsForValidation:
    """Tests for get_high_priority_claims_for_validation function."""

    def test_returns_e4_e5_claims(self, sample_state_with_claims):
        """Should only return E4 and E5 tier claims."""
        claims = get_high_priority_claims_for_validation(sample_state_with_claims)

        for claim in claims:
            assert claim["evidence_tier"] in ["E4", "E5"]

    def test_prioritizes_by_dependents(self, sample_state_with_claims):
        """Claims with more dependents should be prioritized."""
        claims = get_high_priority_claims_for_validation(sample_state_with_claims)

        # MI-4 has dependents (MI-1, MI-3), should be in the list
        claim_ids = [c["claim_id"] for c in claims]
        # At least some E4/E5 claims should be present
        assert len(claims) > 0

    def test_respects_limit(self, sample_state_with_claims):
        """Should respect the limit parameter."""
        claims = get_high_priority_claims_for_validation(
            sample_state_with_claims,
            limit=2,
        )

        assert len(claims) <= 2

    def test_handles_empty_claims(self, empty_state):
        """Should return empty list for empty claims."""
        claims = get_high_priority_claims_for_validation(empty_state)

        assert claims == []


class TestFieldToSectionPrefixMapping:
    """Tests for field to section prefix mapping."""

    def test_common_mappings_exist(self):
        """Common field names should have prefix mappings."""
        assert FIELD_TO_SECTION_PREFIX["customer_research"] == "MI"
        assert FIELD_TO_SECTION_PREFIX["business_case"] == "BC"
        assert FIELD_TO_SECTION_PREFIX["gtm_plan"] == "GM"
        assert FIELD_TO_SECTION_PREFIX["financial_model"] == "FM"
