"""
Unit tests for enterprise context integration in context_builder.py.

Tests the build_enterprise_context_prompt and get_enterprise_context_for_agent functions.
"""

import pytest
from agents.context_builder import (
    build_enterprise_context_prompt,
    get_enterprise_context_for_agent,
)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def full_enterprise_context():
    """Full enterprise context with all sections."""
    return {
        "company": "Acme Corporation",
        "industry": "Financial Services",
        "_sources": ["company", "division"],
        "regulatory": {
            "frameworks": ["SOC2", "GDPR", "PCI-DSS"],
            "jurisdictions": ["US", "EU"],
            "data_residency": "US-only",
        },
        "strategy": {
            "strategic_priorities": ["Digital transformation", "Customer experience"],
            "strategic_constraints": [
                "No acquisitions in 2024",
                "10% cost reduction target",
            ],
            "innovation_stance": "fast follower",
            "investment_thesis": "Focus on core platform",
        },
        "technology": {
            "cloud": "AWS",
            "primary_languages": ["Python", "TypeScript"],
            "databases": ["PostgreSQL", "Redis"],
            "infrastructure": ["Kubernetes", "Terraform"],
            "deprecated_technologies": ["Oracle", "COBOL"],
            "technical_constraints": [
                "Must use microservices",
                "Zero-downtime deployments",
            ],
        },
        "risk_management": {
            "risk_appetite": "moderate",
            "risk_categories": ["Operational", "Compliance", "Technology"],
        },
        "organization": {
            "delivery_model": "agile",
            "budget_cycle": "quarterly",
            "approval_process": "committee review",
        },
    }


@pytest.fixture
def minimal_enterprise_context():
    """Minimal enterprise context."""
    return {
        "company": "Test Corp",
        "regulatory": {
            "frameworks": ["GDPR"],
        },
    }


@pytest.fixture
def state_with_context(full_enterprise_context):
    """State with enterprise context."""
    return {
        "session_id": "test-123",
        "enterprise_context": full_enterprise_context,
    }


@pytest.fixture
def state_with_preformatted_prompt():
    """State with pre-formatted enterprise context prompt."""
    return {
        "session_id": "test-456",
        "enterprise_context": {"company": "Test Corp"},
        "enterprise_context_prompt": "## PRE-FORMATTED CONTEXT\n\nThis is a pre-formatted prompt.",
    }


@pytest.fixture
def state_without_context():
    """State without enterprise context."""
    return {
        "session_id": "test-789",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD ENTERPRISE CONTEXT PROMPT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildEnterpriseContextPrompt:
    """Tests for build_enterprise_context_prompt function."""

    def test_empty_context_returns_empty(self):
        """Test that empty context returns empty string."""
        result = build_enterprise_context_prompt({})
        assert result == ""

    def test_none_context_returns_empty(self):
        """Test that None context returns empty string."""
        result = build_enterprise_context_prompt(None)
        assert result == ""

    def test_includes_header(self, full_enterprise_context):
        """Test that prompt includes organizational context header."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "ORGANIZATIONAL CONTEXT" in result
        assert "Guidelines" in result

    def test_includes_company_info(self, full_enterprise_context):
        """Test that prompt includes company information."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "Acme Corporation" in result
        assert "Financial Services" in result

    def test_includes_regulatory_section(self, full_enterprise_context):
        """Test that prompt includes regulatory requirements."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "Compliance Requirements" in result
        assert "Non-negotiable" in result
        assert "SOC2" in result
        assert "GDPR" in result
        assert "PCI-DSS" in result

    def test_includes_data_residency(self, full_enterprise_context):
        """Test that prompt includes data residency."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "US-only" in result

    def test_includes_jurisdictions(self, full_enterprise_context):
        """Test that prompt includes jurisdictions."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "US" in result
        assert "EU" in result

    def test_includes_strategy_section(self, full_enterprise_context):
        """Test that prompt includes strategic alignment."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "Strategic Alignment" in result
        assert "Digital transformation" in result
        assert "Customer experience" in result
        assert "No acquisitions in 2024" in result

    def test_includes_innovation_stance(self, full_enterprise_context):
        """Test that prompt includes innovation stance."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "fast follower" in result

    def test_includes_technology_section(self, full_enterprise_context):
        """Test that prompt includes technology standards."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "Technology Standards" in result
        assert "AWS" in result
        assert "Python" in result
        assert "TypeScript" in result
        assert "PostgreSQL" in result

    def test_includes_deprecated_technologies(self, full_enterprise_context):
        """Test that prompt includes deprecated technologies."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "Deprecated" in result or "deprecated" in result
        assert "Oracle" in result
        assert "COBOL" in result

    def test_includes_technical_constraints(self, full_enterprise_context):
        """Test that prompt includes technical constraints."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "microservices" in result
        assert "Zero-downtime" in result

    def test_includes_risk_management_section(self, full_enterprise_context):
        """Test that prompt includes risk management."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "Risk" in result
        assert "moderate" in result

    def test_includes_organization_section(self, full_enterprise_context):
        """Test that prompt includes organizational context."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "Organizational Context" in result
        assert "agile" in result
        assert "quarterly" in result

    def test_includes_deviation_note(self, full_enterprise_context):
        """Test that prompt includes note about deviation."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "deviat" in result.lower()
        assert "reason" in result.lower()

    def test_respects_max_chars(self, full_enterprise_context):
        """Test that prompt respects max_chars limit."""
        result = build_enterprise_context_prompt(full_enterprise_context, max_chars=500)
        assert len(result) <= 500

    def test_truncation_indicator(self, full_enterprise_context):
        """Test that truncated prompt includes indicator."""
        result = build_enterprise_context_prompt(full_enterprise_context, max_chars=500)
        if len(result) >= 470:  # Close to limit
            assert "truncated" in result.lower()

    def test_minimal_context_works(self, minimal_enterprise_context):
        """Test that minimal context produces valid prompt."""
        result = build_enterprise_context_prompt(minimal_enterprise_context)
        assert "ORGANIZATIONAL CONTEXT" in result
        assert "Test Corp" in result
        assert "GDPR" in result


# ═══════════════════════════════════════════════════════════════════════════════
# GET ENTERPRISE CONTEXT FOR AGENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetEnterpriseContextForAgent:
    """Tests for get_enterprise_context_for_agent function."""

    def test_uses_preformatted_prompt(self, state_with_preformatted_prompt):
        """Test that pre-formatted prompt is used when available."""
        result = get_enterprise_context_for_agent(
            state_with_preformatted_prompt, "customer_research"
        )
        assert result == "## PRE-FORMATTED CONTEXT\n\nThis is a pre-formatted prompt."

    def test_builds_prompt_from_context(self, state_with_context):
        """Test that prompt is built from context when no pre-formatted."""
        result = get_enterprise_context_for_agent(state_with_context, "customer_research")
        assert "ORGANIZATIONAL CONTEXT" in result
        assert "Acme Corporation" in result

    def test_returns_empty_when_no_context(self, state_without_context):
        """Test that empty string returned when no context."""
        result = get_enterprise_context_for_agent(state_without_context, "customer_research")
        assert result == ""

    def test_same_result_for_different_agents(self, state_with_context):
        """Test that all agents get the same enterprise context."""
        result1 = get_enterprise_context_for_agent(state_with_context, "customer_research")
        result2 = get_enterprise_context_for_agent(state_with_context, "business_strategy")
        result3 = get_enterprise_context_for_agent(state_with_context, "technical_architect")

        assert result1 == result2 == result3


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT FORMAT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestPromptFormat:
    """Tests for prompt formatting quality."""

    def test_uses_markdown_headers(self, full_enterprise_context):
        """Test that prompt uses markdown headers."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "##" in result or "###" in result

    def test_uses_bold_for_labels(self, full_enterprise_context):
        """Test that prompt uses bold for labels."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "**" in result

    def test_uses_bullet_points(self, full_enterprise_context):
        """Test that prompt uses bullet points."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        assert "- " in result

    def test_has_separator(self, full_enterprise_context):
        """Test that prompt has separator at end."""
        result = build_enterprise_context_prompt(full_enterprise_context)
        # Uses box drawing separator instead of simple "---"
        assert "────" in result or "---" in result

    def test_readable_structure(self, full_enterprise_context):
        """Test that prompt has readable structure with sections."""
        result = build_enterprise_context_prompt(full_enterprise_context)

        # Should have clear section breaks
        lines = result.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]

        # Should have multiple sections
        header_lines = [l for l in lines if l.startswith("#")]
        assert len(header_lines) >= 3  # At least header + 2 sections


# ═══════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases."""

    def test_context_with_empty_sections(self):
        """Test context with empty sections."""
        context = {
            "company": "Test",
            "regulatory": {},
            "strategy": {},
            "technology": {},
        }
        result = build_enterprise_context_prompt(context)
        assert "Test" in result
        # Should not crash on empty sections

    def test_context_with_none_values(self):
        """Test context with None values."""
        context = {
            "company": "Test",
            "regulatory": {
                "frameworks": None,
                "data_residency": None,
            },
        }
        result = build_enterprise_context_prompt(context)
        assert "Test" in result
        # Should not crash on None values

    def test_context_with_single_item_lists(self):
        """Test context with single-item lists."""
        context = {
            "company": "Test",
            "regulatory": {
                "frameworks": ["GDPR"],
            },
        }
        result = build_enterprise_context_prompt(context)
        assert "GDPR" in result

    def test_context_with_special_characters(self):
        """Test context with special characters."""
        context = {
            "company": "Test & Co. <LLC>",
            "regulatory": {
                "frameworks": ["GDPR (EU)", "SOC2 Type II"],
            },
        }
        result = build_enterprise_context_prompt(context)
        assert "Test & Co." in result
        assert "GDPR (EU)" in result

    def test_context_with_long_values(self):
        """Test context with very long values."""
        long_value = "A" * 500
        context = {
            "company": long_value,
            "strategy": {
                "strategic_constraints": [long_value],
            },
        }
        result = build_enterprise_context_prompt(context, max_chars=2000)
        # Should handle gracefully without crashing
        assert len(result) > 0
