"""
Tests for the Planning Agent functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch

from agents.planner import (
    run_planner_agent,
    _create_fallback_plan,
    get_plan_context_for_agent,
)
from agents.state import create_initial_state


class TestCreateFallbackPlan:
    """Tests for the fallback plan creation."""

    def test_detects_b2b_saas_domain(self):
        """Should detect B2B SaaS domain from keywords."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Enterprise collaboration software for B2B teams",
            industry="SaaS",
        )

        plan = _create_fallback_plan(state)

        assert plan["domain_type"] == "B2B_SaaS"

    def test_detects_healthcare_domain(self):
        """Should detect Healthcare domain from keywords."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Patient monitoring system for clinical use",
            industry="Healthcare",
        )

        plan = _create_fallback_plan(state)

        assert plan["domain_type"] == "Healthcare"

    def test_detects_fintech_domain(self):
        """Should detect Fintech domain from keywords."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Banking payment processing solution",
            industry="Fintech",
        )

        plan = _create_fallback_plan(state)

        assert plan["domain_type"] == "Fintech"

    def test_detects_consumer_domain(self):
        """Should detect Consumer domain from keywords."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Consumer mobile app for lifestyle tracking",
        )

        plan = _create_fallback_plan(state)

        assert plan["domain_type"] == "Consumer"

    def test_defaults_to_general_domain(self):
        """Should default to general when no keywords match."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Widget maker tool",
        )

        plan = _create_fallback_plan(state)

        assert plan["domain_type"] == "general"

    def test_includes_required_fields(self):
        """Fallback plan should include all required fields."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )

        plan = _create_fallback_plan(state)

        assert "domain_type" in plan
        assert "key_research_questions" in plan
        assert "competitors_to_analyze" in plan
        assert "regulatory_domains" in plan
        assert "financial_benchmarks" in plan
        assert len(plan["key_research_questions"]) >= 5


class TestGetPlanContextForAgent:
    """Tests for extracting plan context for specific agents."""

    def test_returns_empty_for_no_plan(self):
        """Should return empty string when no plan exists."""
        result = get_plan_context_for_agent(None, "customer_research")
        assert result == ""

    def test_includes_domain_type_for_all_agents(self):
        """Should include domain type for all agents."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": ["Q1", "Q2"],
            "competitors_to_analyze": [{"name": "Competitor A"}],
            "regulatory_domains": [{"regulation": "GDPR"}],
        }

        result = get_plan_context_for_agent(plan, "customer_research")
        assert "B2B_SaaS" in result

    def test_includes_questions_for_customer_research(self):
        """Should include research questions for customer research agent."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": ["What is the TAM?", "Who are competitors?"],
            "competitors_to_analyze": [],
            "regulatory_domains": [],
        }

        result = get_plan_context_for_agent(plan, "customer_research")

        assert "Key Research Questions" in result
        assert "TAM" in result

    def test_includes_competitors_for_customer_research(self):
        """Should include competitors for customer research agent."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": [],
            "competitors_to_analyze": [
                {"name": "Slack"},
                {"name": "Teams"},
            ],
            "regulatory_domains": [],
        }

        result = get_plan_context_for_agent(plan, "customer_research")

        assert "Competitors to Analyze" in result
        assert "Slack" in result

    def test_includes_regulations_for_legal_agent(self):
        """Should include regulations for legal agent."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": [],
            "competitors_to_analyze": [],
            "regulatory_domains": [
                {"regulation": "GDPR"},
                {"regulation": "CCPA"},
            ],
        }

        result = get_plan_context_for_agent(plan, "legal_regulatory")

        assert "Regulatory Domains" in result
        assert "GDPR" in result


class TestRunPlannerAgent:
    """Tests for the planner agent execution."""

    @pytest.mark.asyncio
    async def test_creates_fallback_on_llm_failure(self):
        """Should create fallback plan when LLM call fails."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="B2B SaaS product",
        )

        with patch("agents.planner.call_llm") as mock_llm:
            mock_llm.return_value = {
                "success": False,
                "error": "API error",
                "tokens_used": 0,
                "duration_seconds": 0.1,
            }

            result = await run_planner_agent(state)

            assert result["research_plan"] is not None
            assert result["research_plan"]["domain_type"] == "B2B_SaaS"
            assert "Planning Agent" in result.get("errors", [""])[0]

    @pytest.mark.asyncio
    async def test_uses_llm_response_on_success(self):
        """Should use LLM response when successful."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )

        mock_plan = {
            "domain_type": "Marketplace",
            "key_research_questions": ["Q1"],
            "competitors_to_analyze": [{"name": "eBay"}],
            "regulatory_domains": [{"regulation": "GDPR"}],
            "financial_benchmarks": {},
        }

        with patch("agents.planner.call_llm") as mock_llm:
            mock_llm.return_value = {
                "success": True,
                "data": mock_plan,
                "tokens_used": 100,
                "duration_seconds": 1.0,
            }

            result = await run_planner_agent(state)

            assert result["research_plan"]["domain_type"] == "Marketplace"
            assert result["research_plan"]["competitors_to_analyze"][0]["name"] == "eBay"
