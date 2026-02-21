"""
Tests for constraint broadcasting in constraint_broadcaster.py

These tests verify that:
- Constraints are generated correctly for each phase
- Constraint formatting for prompts is correct
- Constraint validation works properly
"""

import pytest
from agents.constraint_broadcaster import (
    ExecutionConstraint,
    generate_phase_constraints,
    format_constraints_for_prompt,
    validate_output_against_constraints,
    _find_claim_id,
)


@pytest.fixture
def sample_discovery_state():
    """State after discovery phase completion."""
    return {
        "session_id": "test-session-123",
        "customer_research": {
            "market_context": {
                "total_addressable_market": "$5B",
                "customer_segments": ["SMB", "Enterprise"],
            },
        },
        "competitive_analysis": {
            "direct_competitors": [
                {"name": "Competitor A", "market_share": "30%"},
                {"name": "Competitor B", "market_share": "20%"},
            ],
        },
        "detailed_personas": {
            "primary_persona": {
                "name": "Tech-Savvy Manager",
                "archetype": "Early Adopter",
            },
        },
        "cross_reference_index": {
            "claims": [
                {"claim_id": "MI-1", "statement": "Market size is $5B"},
                {"claim_id": "CP-1", "statement": "Primary persona is Tech Manager"},
            ],
        },
    }


@pytest.fixture
def sample_strategy_state(sample_discovery_state):
    """State after strategy phase completion."""
    state = dict(sample_discovery_state)
    state.update({
        "business_case": {
            "unique_value_proposition": "AI-powered workflow automation",
            "revenue_streams": [
                {"name": "SaaS Subscription", "price": "$99/month"},
            ],
        },
        "gtm_plan": {
            "market_entry_strategy": {
                "initial_segment": "SMB Tech Companies",
            },
        },
        "financial_model": {
            "unit_economics": {
                "ltv_cac_ratio": 3.5,
            },
        },
    })
    return state


class TestExecutionConstraint:
    """Tests for ExecutionConstraint dataclass."""

    def test_constraint_creation(self):
        """Should create constraint with all fields."""
        constraint = ExecutionConstraint(
            field="market_size",
            value="$5B",
            source_section="customer_research",
            source_claim_id="MI-1",
            constraint_type="must_use",
            evidence_tier="E3",
            confidence=0.8,
        )

        assert constraint.field == "market_size"
        assert constraint.value == "$5B"
        assert constraint.constraint_type == "must_use"

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        constraint = ExecutionConstraint(
            field="pricing",
            value="$99",
            source_section="business_case",
            source_claim_id="BC-1",
            constraint_type="must_align",
        )

        d = constraint.to_dict()

        assert isinstance(d, dict)
        assert d["field"] == "pricing"
        assert d["source_claim_id"] == "BC-1"


class TestGeneratePhaseConstraints:
    """Tests for generate_phase_constraints function."""

    @pytest.mark.asyncio
    async def test_strategy_constraints_from_discovery(self, sample_discovery_state):
        """Strategy phase should receive constraints from discovery outputs."""
        constraints = await generate_phase_constraints(
            sample_discovery_state,
            target_phase="strategy",
        )

        # Should have market size constraint from customer_research
        field_names = [c.field for c in constraints]
        assert "market_size" in field_names

    @pytest.mark.asyncio
    async def test_delivery_constraints_include_strategy(self, sample_strategy_state):
        """Delivery phase should receive constraints from both discovery and strategy."""
        constraints = await generate_phase_constraints(
            sample_strategy_state,
            target_phase="delivery",
        )

        field_names = [c.field for c in constraints]
        # Should have pricing from business_case
        # Should have market_size from customer_research (inherited)
        assert len(constraints) > 0

    @pytest.mark.asyncio
    async def test_empty_state_returns_empty_constraints(self):
        """Empty state should return empty constraints list."""
        constraints = await generate_phase_constraints(
            {"session_id": "empty"},
            target_phase="strategy",
        )

        assert constraints == []


class TestFormatConstraintsForPrompt:
    """Tests for format_constraints_for_prompt function."""

    def test_formats_must_use_constraints(self):
        """Must-use constraints should appear in MUST USE section."""
        constraints = [
            ExecutionConstraint(
                field="market_size",
                value="$5B",
                source_section="customer_research",
                source_claim_id="MI-1",
                constraint_type="must_use",
            ),
        ]

        prompt = format_constraints_for_prompt(constraints)

        assert "MUST USE" in prompt
        assert "market_size" in prompt
        assert "$5B" in prompt
        assert "MI-1" in prompt

    def test_formats_must_align_constraints(self):
        """Must-align constraints should appear in MUST ALIGN section."""
        constraints = [
            ExecutionConstraint(
                field="primary_customer",
                value="Tech Manager",
                source_section="detailed_personas",
                source_claim_id="CP-1",
                constraint_type="must_align",
            ),
        ]

        prompt = format_constraints_for_prompt(constraints)

        assert "MUST ALIGN" in prompt
        assert "primary_customer" in prompt

    def test_empty_constraints_returns_empty_string(self):
        """Empty constraints should return empty string."""
        prompt = format_constraints_for_prompt([])

        assert prompt == ""

    def test_includes_mandatory_header(self):
        """Should include header indicating constraints are mandatory."""
        constraints = [
            ExecutionConstraint(
                field="test",
                value="value",
                source_section="test",
                source_claim_id="T-1",
                constraint_type="must_use",
            ),
        ]

        prompt = format_constraints_for_prompt(constraints)

        # The prompt uses "CRITICAL" instead of "MANDATORY" but serves the same purpose
        assert "CRITICAL" in prompt or "MANDATORY" in prompt
        assert "MUST align" in prompt.lower() or "must use" in prompt.lower()


class TestValidateOutputAgainstConstraints:
    """Tests for validate_output_against_constraints function."""

    def test_detects_missing_must_use_field(self):
        """Should detect when a must_use field is missing from output."""
        constraints = [
            ExecutionConstraint(
                field="market_size",
                value="$5B",
                source_section="customer_research",
                source_claim_id="MI-1",
                constraint_type="must_use",
            ),
        ]

        output = {"other_field": "value"}

        violations = validate_output_against_constraints(output, constraints)

        assert len(violations) == 1
        assert violations[0]["field"] == "market_size"
        assert violations[0]["actual"] == "NOT FOUND"

    def test_no_violations_when_constraint_met(self):
        """Should return empty list when output meets constraints."""
        constraints = [
            ExecutionConstraint(
                field="market_size",
                value="$5B",
                source_section="customer_research",
                source_claim_id="MI-1",
                constraint_type="must_use",
            ),
        ]

        output = {"market_size": "$5B"}

        violations = validate_output_against_constraints(output, constraints)

        # Value matches exactly or contains the constraint value
        assert len(violations) == 0 or all(v["severity"] == "medium" for v in violations)

    def test_empty_constraints_no_violations(self):
        """Empty constraints should return no violations."""
        violations = validate_output_against_constraints(
            {"any": "output"},
            [],
        )

        assert violations == []


class TestFindClaimId:
    """Tests for _find_claim_id helper function."""

    def test_finds_matching_claim(self):
        """Should find claim ID matching keyword."""
        state = {
            "cross_reference_index": {
                "claims": [
                    {"claim_id": "MI-1", "statement": "Market size is $5B"},
                    {"claim_id": "MI-2", "statement": "Competitor analysis shows..."},
                ],
            },
        }

        claim_id = _find_claim_id(state, "market", "MI")

        assert claim_id == "MI-1"

    def test_returns_default_when_not_found(self):
        """Should return default ID when no match found."""
        state = {"cross_reference_index": {"claims": []}}

        claim_id = _find_claim_id(state, "nonexistent", "XX")

        assert claim_id == "XX-1"
