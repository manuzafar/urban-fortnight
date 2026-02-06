"""
Tests for targeted revision routing and multi-model configuration.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.orchestrator import route_revision, prepare_revision_node
from agents.state import create_initial_state
from config import AGENT_MODEL_CONFIG, get_agent_model


class TestRouteRevision:
    """Tests for the route_revision function."""

    def test_routes_to_customer_research_when_it_fails(self):
        """Should route to customer_research when that section scores below threshold."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["quality_assessment"] = {
            "overall_score": 0.65,
            "section_scores": [
                {"section": "Customer Research", "score": 0.5},  # Failing
                {"section": "Business Case", "score": 0.8},
                {"section": "Product Requirements", "score": 0.8},
            ],
        }

        result = route_revision(state)
        assert result == "customer_research"

    def test_routes_to_business_strategy_when_it_fails(self):
        """Should route to business_strategy when business case scores below threshold."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["quality_assessment"] = {
            "overall_score": 0.65,
            "section_scores": [
                {"section": "Customer Research", "score": 0.8},  # Passing
                {"section": "Business Case", "score": 0.5},  # Failing
                {"section": "Product Requirements", "score": 0.8},
            ],
        }

        result = route_revision(state)
        assert result == "business_strategy"

    def test_routes_to_technical_architect_when_it_fails(self):
        """Should route to technical_architect when architecture scores below threshold."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["quality_assessment"] = {
            "overall_score": 0.65,
            "section_scores": [
                {"section": "Customer Research", "score": 0.8},
                {"section": "Business Case", "score": 0.8},
                {"section": "Product Requirements", "score": 0.8},
                {"section": "Technical Architecture", "score": 0.5},  # Failing
            ],
        }

        result = route_revision(state)
        assert result == "technical_architect"

    def test_routes_to_legal_when_it_fails(self):
        """Should route to legal_regulatory when legal section scores below threshold."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["quality_assessment"] = {
            "overall_score": 0.65,
            "section_scores": [
                {"section": "Customer Research", "score": 0.8},
                {"section": "Business Case", "score": 0.8},
                {"section": "Product Requirements", "score": 0.8},
                {"section": "Technical Architecture", "score": 0.8},
                {"section": "Legal Review", "score": 0.5},  # Failing
            ],
        }

        result = route_revision(state)
        assert result == "legal_regulatory"

    def test_fallback_to_customer_research_when_no_section_fails(self):
        """Should fallback to customer_research when no specific section fails."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["quality_assessment"] = {
            "overall_score": 0.65,
            "section_scores": [],  # Empty scores
        }

        result = route_revision(state)
        assert result == "customer_research"

    def test_handles_missing_quality_assessment(self):
        """Should fallback to customer_research when quality_assessment is missing."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        # No quality_assessment set

        result = route_revision(state)
        assert result == "customer_research"


class TestPrepareRevisionNode:
    """Tests for the prepare_revision_node function."""

    @pytest.mark.asyncio
    async def test_clears_only_failing_agent_onwards(self):
        """Should only clear outputs from failing agent onwards."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        # Set all outputs
        state["customer_research"] = {"data": "research"}
        state["business_case"] = {"data": "business"}
        state["product_requirements"] = {"data": "prd"}
        state["technical_architecture"] = {"data": "tech"}
        state["legal_regulatory_review"] = {"data": "legal"}
        state["quality_assessment"] = {
            "overall_score": 0.65,
            "section_scores": [
                {"section": "Customer Research", "score": 0.8},
                {"section": "Business Case", "score": 0.8},
                {"section": "Product Requirements", "score": 0.5},  # Failing
                {"section": "Technical Architecture", "score": 0.8},
            ],
        }

        result = await prepare_revision_node(state)

        # Customer research and business case should be preserved
        assert result["customer_research"] == {"data": "research"}
        assert result["business_case"] == {"data": "business"}

        # PRD onwards should be cleared
        assert result["product_requirements"] is None
        assert result["technical_architecture"] is None
        assert result["legal_regulatory_review"] is None

    @pytest.mark.asyncio
    async def test_increments_iteration(self):
        """Should increment the iteration counter."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["iteration"] = 1
        state["quality_assessment"] = {
            "overall_score": 0.65,
            "section_scores": [
                {"section": "Customer Research", "score": 0.5},
            ],
        }

        result = await prepare_revision_node(state)

        assert result["iteration"] == 2


class TestMultiModelConfig:
    """Tests for multi-model routing configuration."""

    def test_agent_model_config_has_expected_agents(self):
        """Config should have entries for all main agents."""
        expected_agents = [
            "customer_research",
            "business_strategy",
            "prd_generator",
            "prd_critic",
            "technical_architect",
            "legal_regulatory",
            "critique",
            "executive_summary",
        ]

        for agent in expected_agents:
            assert agent in AGENT_MODEL_CONFIG, f"Missing config for {agent}"

    def test_get_agent_model_returns_configured_model(self):
        """get_agent_model should return the configured model for an agent."""
        # These should use Pro for deeper reasoning
        assert "pro" in get_agent_model("critique").lower()
        assert "pro" in get_agent_model("legal_regulatory").lower()
        assert "pro" in get_agent_model("business_strategy").lower()

        # These should use Flash for speed
        assert "flash" in get_agent_model("customer_research").lower()
        assert "flash" in get_agent_model("executive_summary").lower()

    def test_get_agent_model_returns_default_for_unknown(self):
        """get_agent_model should return default model for unknown agents."""
        result = get_agent_model("unknown_agent")
        # Should return the default llm_model from settings
        assert result is not None
        assert len(result) > 0
