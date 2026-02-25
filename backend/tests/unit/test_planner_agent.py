"""
Comprehensive unit tests for the Planning Agent.

Tests cover:
- Domain classification (B2B_SaaS, Fintech, Healthcare, Marketplace, Consumer)
- Competitor identification
- Regulatory scope detection
- Fallback plan generation
- Plan context extraction for downstream agents
- Error handling and edge cases
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.planner import (
    run_planner_agent,
    _create_fallback_plan,
    get_plan_context_for_agent,
)
from agents.state import create_initial_state, DiscoveryState
from models.schemas import SessionStatus


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def base_state():
    """Create a base state for testing."""
    return create_initial_state(
        session_id="test-session-123",
        product_idea="A comprehensive test product idea",
    )


@pytest.fixture
def b2b_saas_state():
    """Create a state for B2B SaaS domain detection."""
    return create_initial_state(
        session_id="test-b2b-saas",
        product_idea="Enterprise collaboration software for B2B teams with SaaS delivery",
        industry="SaaS",
        target_market="Enterprise businesses",
    )


@pytest.fixture
def healthcare_state():
    """Create a state for Healthcare domain detection."""
    return create_initial_state(
        session_id="test-healthcare",
        product_idea="Patient monitoring system for clinical environments and hospitals",
        industry="Healthcare",
    )


@pytest.fixture
def fintech_state():
    """Create a state for Fintech domain detection."""
    return create_initial_state(
        session_id="test-fintech",
        product_idea="Banking payment processing solution with financial APIs",
        industry="Fintech",
    )


@pytest.fixture
def marketplace_state():
    """Create a state for Marketplace domain detection."""
    return create_initial_state(
        session_id="test-marketplace",
        product_idea="Two-sided marketplace connecting buyers and sellers",
        industry="E-commerce",
    )


@pytest.fixture
def consumer_state():
    """Create a state for Consumer domain detection."""
    return create_initial_state(
        session_id="test-consumer",
        product_idea="Consumer mobile app for lifestyle and personal wellness tracking",
    )


@pytest.fixture
def mock_successful_llm_response():
    """Mock a successful LLM response."""
    return {
        "success": True,
        "data": {
            "domain_type": "B2B_SaaS",
            "key_research_questions": [
                "What is the total addressable market size?",
                "Who are the main competitors?",
                "What are the primary customer pain points?",
            ],
            "competitors_to_analyze": [
                {"name": "Slack", "threat_level": "high"},
                {"name": "Microsoft Teams", "threat_level": "high"},
            ],
            "regulatory_domains": [
                {"regulation": "GDPR", "impact": "high"},
                {"regulation": "SOC 2", "impact": "medium"},
            ],
            "financial_benchmarks": {
                "typical_cac": "$500-1500",
                "typical_ltv": "$5000-15000",
            },
        },
        "tokens_used": 500,
        "duration_seconds": 2.5,
    }


@pytest.fixture
def mock_failed_llm_response():
    """Mock a failed LLM response."""
    return {
        "success": False,
        "error": "API rate limit exceeded",
        "tokens_used": 0,
        "duration_seconds": 0.1,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN CLASSIFICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDomainClassification:
    """Tests for domain classification in fallback plan."""

    def test_detects_b2b_saas_domain(self, b2b_saas_state):
        """Should correctly detect B2B SaaS domain from keywords."""
        plan = _create_fallback_plan(b2b_saas_state)
        assert plan["domain_type"] == "B2B_SaaS"

    def test_detects_healthcare_domain(self, healthcare_state):
        """Should correctly detect Healthcare domain from keywords."""
        plan = _create_fallback_plan(healthcare_state)
        assert plan["domain_type"] == "Healthcare"

    def test_detects_fintech_domain(self, fintech_state):
        """Should correctly detect Fintech domain from keywords."""
        plan = _create_fallback_plan(fintech_state)
        assert plan["domain_type"] == "Fintech"

    def test_detects_marketplace_domain(self, marketplace_state):
        """Should correctly detect Marketplace domain from keywords."""
        plan = _create_fallback_plan(marketplace_state)
        assert plan["domain_type"] == "Marketplace"

    def test_detects_consumer_domain(self, consumer_state):
        """Should correctly detect Consumer domain from keywords."""
        plan = _create_fallback_plan(consumer_state)
        assert plan["domain_type"] == "Consumer"

    def test_defaults_to_general_domain(self, base_state):
        """Should default to 'general' when no specific keywords match."""
        state = create_initial_state(
            session_id="test-generic",
            product_idea="A widget maker tool with various features",
        )
        plan = _create_fallback_plan(state)
        assert plan["domain_type"] == "general"

    def test_healthcare_takes_priority_over_saas(self):
        """Healthcare keywords should take priority over B2B/SaaS keywords."""
        state = create_initial_state(
            session_id="test-priority",
            product_idea="B2B SaaS platform for patient health monitoring",
            industry="Healthcare SaaS",
        )
        plan = _create_fallback_plan(state)
        # Healthcare is checked before B2B_SaaS in the order
        assert plan["domain_type"] == "Healthcare"

    def test_fintech_keywords_detection(self):
        """Should detect fintech from various financial keywords."""
        test_cases = [
            "Payment processing system",
            "Banking application for finance",
            "Financial planning tool",
        ]
        for idea in test_cases:
            state = create_initial_state(session_id="test-fin", product_idea=idea)
            plan = _create_fallback_plan(state)
            assert plan["domain_type"] == "Fintech", f"Failed for: {idea}"


# ═══════════════════════════════════════════════════════════════════════════════
# FALLBACK PLAN STRUCTURE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestFallbackPlanStructure:
    """Tests for fallback plan structure and completeness."""

    def test_includes_all_required_fields(self, base_state):
        """Fallback plan should include all required fields."""
        plan = _create_fallback_plan(base_state)

        required_fields = [
            "domain_type",
            "key_research_questions",
            "competitors_to_analyze",
            "regulatory_domains",
            "financial_benchmarks",
        ]

        for field in required_fields:
            assert field in plan, f"Missing required field: {field}"

    def test_has_minimum_research_questions(self, base_state):
        """Should have at least 5 default research questions."""
        plan = _create_fallback_plan(base_state)
        assert len(plan["key_research_questions"]) >= 5

    def test_includes_fallback_marker(self, base_state):
        """Fallback plan should be marked as a fallback."""
        plan = _create_fallback_plan(base_state)
        assert plan.get("fallback") is True

    def test_competitors_list_is_empty_initially(self, base_state):
        """Competitors should be empty in fallback (discovered later)."""
        plan = _create_fallback_plan(base_state)
        assert plan["competitors_to_analyze"] == []

    def test_regulatory_domains_is_empty_initially(self, base_state):
        """Regulatory domains should be empty in fallback."""
        plan = _create_fallback_plan(base_state)
        assert plan["regulatory_domains"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN CONTEXT EXTRACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetPlanContextForAgent:
    """Tests for extracting plan context for specific agents."""

    def test_returns_empty_for_none_plan(self):
        """Should return empty string when plan is None."""
        result = get_plan_context_for_agent(None, "customer_research")
        assert result == ""

    def test_includes_domain_type_for_all_agents(self):
        """Should include domain type in context for all agents."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": [],
            "competitors_to_analyze": [],
            "regulatory_domains": [],
        }

        agents = ["customer_research", "business_strategy", "legal_regulatory", "technical_architect"]
        for agent in agents:
            result = get_plan_context_for_agent(plan, agent)
            assert "B2B_SaaS" in result

    def test_includes_questions_for_customer_research(self):
        """Should include research questions for customer research agent."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": [
                "What is the TAM?",
                "Who are the primary users?",
            ],
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
                {"name": "Microsoft Teams"},
            ],
            "regulatory_domains": [],
        }

        result = get_plan_context_for_agent(plan, "customer_research")
        assert "Competitors to Analyze" in result
        assert "Slack" in result

    def test_handles_string_format_competitors(self):
        """Should handle competitors as plain strings."""
        plan = {
            "domain_type": "Fintech",
            "key_research_questions": [],
            "competitors_to_analyze": ["Stripe", "Square", "PayPal"],
            "regulatory_domains": [],
        }

        result = get_plan_context_for_agent(plan, "customer_research")
        assert "Stripe" in result

    def test_includes_regulations_for_legal_agent(self):
        """Should include regulations for legal/regulatory agent."""
        plan = {
            "domain_type": "Healthcare",
            "key_research_questions": [],
            "competitors_to_analyze": [],
            "regulatory_domains": [
                {"regulation": "HIPAA"},
                {"regulation": "FDA"},
            ],
        }

        result = get_plan_context_for_agent(plan, "legal_regulatory")
        assert "Regulatory Domains" in result
        assert "HIPAA" in result

    def test_includes_benchmarks_for_business_strategy(self):
        """Should include financial benchmarks for business strategy agent."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": [],
            "competitors_to_analyze": [],
            "regulatory_domains": [],
            "financial_benchmarks": {
                "typical_cac": "$500",
                "typical_ltv": "$5000",
            },
        }

        result = get_plan_context_for_agent(plan, "business_strategy")
        assert "Financial Benchmarks" in result

    def test_includes_tech_considerations_for_architect(self):
        """Should include technical considerations for technical architect."""
        plan = {
            "domain_type": "Healthcare",
            "key_research_questions": [],
            "competitors_to_analyze": [],
            "regulatory_domains": [],
            "technical_considerations": [
                "HIPAA compliance required",
                "High availability needed",
            ],
        }

        result = get_plan_context_for_agent(plan, "technical_architect")
        assert "Technical Considerations" in result
        assert "HIPAA" in result


# ═══════════════════════════════════════════════════════════════════════════════
# PLANNER AGENT EXECUTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRunPlannerAgent:
    """Tests for the planner agent execution."""

    @pytest.mark.asyncio
    async def test_successful_llm_response(self, base_state, mock_successful_llm_response):
        """Should use LLM response when call succeeds."""
        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_successful_llm_response

            result = await run_planner_agent(base_state)

            assert result["research_plan"] is not None
            assert result["research_plan"]["domain_type"] == "B2B_SaaS"
            assert len(result["research_plan"]["competitors_to_analyze"]) == 2
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_fallback_on_llm_failure(self, b2b_saas_state, mock_failed_llm_response):
        """Should create fallback plan when LLM call fails."""
        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_failed_llm_response

            result = await run_planner_agent(b2b_saas_state)

            assert result["research_plan"] is not None
            assert result["research_plan"]["domain_type"] == "B2B_SaaS"
            assert result["research_plan"].get("fallback") is True
            assert len(result.get("errors", [])) > 0
            assert "Planning Agent" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_updates_state_tracking_fields(self, base_state, mock_successful_llm_response):
        """Should update token and duration tracking."""
        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_successful_llm_response

            result = await run_planner_agent(base_state)

            assert result["total_tokens_used"] == 500
            assert result["total_duration_seconds"] == 2.5
            assert result["current_agent"] == "Planning Agent"

    @pytest.mark.asyncio
    async def test_sets_status_to_in_progress(self, base_state, mock_successful_llm_response):
        """Should set status to IN_PROGRESS during execution."""
        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_successful_llm_response

            result = await run_planner_agent(base_state)

            assert result["status"] == SessionStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_handles_missing_fields_in_llm_response(self, base_state):
        """Should add defaults for missing fields in LLM response."""
        incomplete_response = {
            "success": True,
            "data": {
                "domain_type": "Consumer",
                # Missing other required fields
            },
            "tokens_used": 100,
            "duration_seconds": 1.0,
        }

        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = incomplete_response

            result = await run_planner_agent(base_state)

            assert result["research_plan"]["domain_type"] == "Consumer"
            assert "key_research_questions" in result["research_plan"]
            assert "competitors_to_analyze" in result["research_plan"]
            assert "regulatory_domains" in result["research_plan"]

    @pytest.mark.asyncio
    async def test_accumulates_tokens_across_calls(self, base_state, mock_successful_llm_response):
        """Should accumulate tokens if state already has token usage."""
        base_state["total_tokens_used"] = 100
        base_state["total_duration_seconds"] = 1.0

        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_successful_llm_response

            result = await run_planner_agent(base_state)

            assert result["total_tokens_used"] == 600  # 100 + 500
            assert result["total_duration_seconds"] == 3.5  # 1.0 + 2.5

    @pytest.mark.asyncio
    async def test_updates_timestamp(self, base_state, mock_successful_llm_response):
        """Should update the updated_at timestamp."""
        original_updated = base_state["updated_at"]

        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_successful_llm_response

            result = await run_planner_agent(base_state)

            assert result["updated_at"] != original_updated


# ═══════════════════════════════════════════════════════════════════════════════
# EDGE CASES AND ERROR HANDLING TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCasesAndErrorHandling:
    """Tests for edge cases and error handling."""

    def test_empty_product_idea(self):
        """Should handle empty product idea gracefully."""
        state = create_initial_state(
            session_id="test-empty",
            product_idea="",
        )
        plan = _create_fallback_plan(state)
        assert plan["domain_type"] == "general"

    def test_very_long_product_idea(self):
        """Should handle very long product idea."""
        long_idea = "AI-powered enterprise " * 100
        state = create_initial_state(
            session_id="test-long",
            product_idea=long_idea,
        )
        plan = _create_fallback_plan(state)
        assert plan["domain_type"] == "B2B_SaaS"

    def test_special_characters_in_product_idea(self):
        """Should handle special characters in product idea."""
        state = create_initial_state(
            session_id="test-special",
            product_idea="B2B SaaS platform with AI/ML & cloud-native features ($100M market)",
        )
        plan = _create_fallback_plan(state)
        assert plan["domain_type"] == "B2B_SaaS"

    def test_case_insensitive_keyword_matching(self):
        """Should match keywords case-insensitively."""
        state = create_initial_state(
            session_id="test-case",
            product_idea="HEALTHCARE SAAS PLATFORM FOR HOSPITALS",
        )
        plan = _create_fallback_plan(state)
        assert plan["domain_type"] == "Healthcare"

    def test_industry_field_contributes_to_detection(self):
        """Industry field should contribute to domain detection."""
        state = create_initial_state(
            session_id="test-industry",
            product_idea="Platform for managing team tasks",
            industry="Healthcare",
        )
        plan = _create_fallback_plan(state)
        assert plan["domain_type"] == "Healthcare"

    @pytest.mark.asyncio
    async def test_handles_none_in_optional_fields(self, base_state, mock_successful_llm_response):
        """Should handle None values in optional fields."""
        base_state["industry"] = None
        base_state["target_market"] = None
        base_state["constraints"] = None
        base_state["additional_context"] = None

        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_successful_llm_response

            result = await run_planner_agent(base_state)

            assert result["research_plan"] is not None
            mock_llm.assert_called_once()

    def test_context_with_empty_plan_fields(self):
        """Should handle plan with empty lists/dicts."""
        plan = {
            "domain_type": "B2B_SaaS",
            "key_research_questions": [],
            "competitors_to_analyze": [],
            "regulatory_domains": [],
            "financial_benchmarks": {},
        }

        result = get_plan_context_for_agent(plan, "customer_research")
        assert "B2B_SaaS" in result
        # Should not crash or include empty sections
        assert "Key Research Questions" not in result or "1." not in result


# ═══════════════════════════════════════════════════════════════════════════════
# REGULATORY SCOPE DETECTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegulatoryScope:
    """Tests for regulatory scope implications based on domain."""

    @pytest.mark.asyncio
    async def test_healthcare_implies_hipaa_regulatory_scope(self, healthcare_state):
        """Healthcare domain should trigger HIPAA-related regulatory focus."""
        mock_response = {
            "success": True,
            "data": {
                "domain_type": "Healthcare",
                "key_research_questions": ["What HIPAA requirements apply?"],
                "competitors_to_analyze": [],
                "regulatory_domains": [
                    {"regulation": "HIPAA", "impact": "critical"},
                    {"regulation": "FDA", "impact": "high"},
                ],
                "financial_benchmarks": {},
            },
            "tokens_used": 300,
            "duration_seconds": 2.0,
        }

        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await run_planner_agent(healthcare_state)

            regulations = result["research_plan"]["regulatory_domains"]
            reg_names = [r.get("regulation", r) if isinstance(r, dict) else r for r in regulations]
            assert "HIPAA" in reg_names

    @pytest.mark.asyncio
    async def test_fintech_implies_pci_regulatory_scope(self, fintech_state):
        """Fintech domain should trigger PCI/financial regulatory focus."""
        mock_response = {
            "success": True,
            "data": {
                "domain_type": "Fintech",
                "key_research_questions": ["What PCI compliance is required?"],
                "competitors_to_analyze": [],
                "regulatory_domains": [
                    {"regulation": "PCI DSS", "impact": "critical"},
                    {"regulation": "SOX", "impact": "high"},
                ],
                "financial_benchmarks": {},
            },
            "tokens_used": 300,
            "duration_seconds": 2.0,
        }

        with patch("agents.planner.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await run_planner_agent(fintech_state)

            regulations = result["research_plan"]["regulatory_domains"]
            reg_names = [r.get("regulation", r) if isinstance(r, dict) else r for r in regulations]
            assert "PCI DSS" in reg_names
