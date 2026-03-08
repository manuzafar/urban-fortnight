"""
Unit tests for enterprise context integration in constraint_broadcaster.py.

Tests the generate_enterprise_constraints function and its integration
with the phase constraint generation.
"""

import pytest
from agents.constraint_broadcaster import (
    generate_enterprise_constraints,
    generate_phase_constraints,
    ExecutionConstraint,
)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def enterprise_context_full():
    """Full enterprise context with all sections."""
    return {
        "company": "Acme Corporation",
        "industry": "Financial Services",
        "_sources": ["company", "division"],
        "regulatory": {
            "frameworks": ["SOC2", "GDPR", "PCI-DSS"],
            "data_residency": "US-only",
        },
        "strategy": {
            "strategic_constraints": [
                "No acquisitions in 2024",
                "10% cost reduction target",
            ],
            "strategic_priorities": ["Digital transformation", "Customer experience"],
        },
        "technology": {
            "cloud": "AWS",
            "primary_languages": ["Python", "TypeScript"],
            "databases": ["PostgreSQL", "Redis"],
            "deprecated_technologies": ["Oracle", "COBOL"],
        },
        "risk_management": {
            "risk_appetite": "moderate",
        },
    }


@pytest.fixture
def enterprise_context_minimal():
    """Minimal enterprise context with only regulatory."""
    return {
        "company": "Test Corp",
        "_sources": ["company"],
        "regulatory": {
            "frameworks": ["GDPR"],
        },
    }


@pytest.fixture
def state_with_enterprise_context(enterprise_context_full):
    """State with enterprise context."""
    return {
        "session_id": "test-session-123",
        "enterprise_context": enterprise_context_full,
    }


@pytest.fixture
def state_without_enterprise_context():
    """State without enterprise context."""
    return {
        "session_id": "test-session-456",
        "enterprise_context": None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE ENTERPRISE CONSTRAINTS TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGenerateEnterpriseConstraints:
    """Tests for generate_enterprise_constraints function."""

    def test_empty_state_returns_empty(self, state_without_enterprise_context):
        """Test that empty enterprise context returns no constraints."""
        constraints = generate_enterprise_constraints(state_without_enterprise_context)
        assert constraints == []

    def test_extracts_regulatory_frameworks(self, state_with_enterprise_context):
        """Test extraction of regulatory framework constraints."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        compliance_constraints = [
            c for c in constraints if c.field == "compliance_framework"
        ]
        assert len(compliance_constraints) == 3

        values = [c.value for c in compliance_constraints]
        assert "SOC2" in values
        assert "GDPR" in values
        assert "PCI-DSS" in values

        # All should be E1 with confidence 1.0
        for c in compliance_constraints:
            assert c.evidence_tier == "E1"
            assert c.confidence == 1.0
            assert c.constraint_type == "must_use"
            assert c.source_section == "enterprise_context"

    def test_extracts_data_residency(self, state_with_enterprise_context):
        """Test extraction of data residency constraint."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        data_residency = [c for c in constraints if c.field == "data_residency"]
        assert len(data_residency) == 1
        assert data_residency[0].value == "US-only"
        assert data_residency[0].evidence_tier == "E1"
        assert data_residency[0].confidence == 1.0

    def test_extracts_strategic_constraints(self, state_with_enterprise_context):
        """Test extraction of strategic constraints."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        strategic = [c for c in constraints if c.field == "strategic_alignment"]
        assert len(strategic) == 2

        values = [c.value for c in strategic]
        assert "No acquisitions in 2024" in values
        assert "10% cost reduction target" in values

        for c in strategic:
            assert c.constraint_type == "must_align"
            assert c.evidence_tier == "E1"
            assert c.confidence == 0.95

    def test_extracts_strategic_priorities(self, state_with_enterprise_context):
        """Test extraction of strategic priorities."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        priorities = [c for c in constraints if c.field == "strategic_priorities"]
        assert len(priorities) == 1
        assert "Digital transformation" in priorities[0].value
        assert "Customer experience" in priorities[0].value

    def test_extracts_cloud_platform(self, state_with_enterprise_context):
        """Test extraction of cloud platform constraint."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        cloud = [c for c in constraints if c.field == "cloud_platform"]
        assert len(cloud) == 1
        assert cloud[0].value == "AWS"
        assert cloud[0].constraint_type == "must_use"
        assert cloud[0].evidence_tier == "E1"

    def test_extracts_programming_languages(self, state_with_enterprise_context):
        """Test extraction of programming languages constraint."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        languages = [c for c in constraints if c.field == "programming_languages"]
        assert len(languages) == 1
        assert "Python" in languages[0].value
        assert "TypeScript" in languages[0].value

    def test_extracts_databases(self, state_with_enterprise_context):
        """Test extraction of database technologies constraint."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        databases = [c for c in constraints if c.field == "database_technologies"]
        assert len(databases) == 1
        assert "PostgreSQL" in databases[0].value
        assert "Redis" in databases[0].value

    def test_extracts_deprecated_technologies(self, state_with_enterprise_context):
        """Test extraction of deprecated technologies constraint."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        deprecated = [c for c in constraints if c.field == "deprecated_technologies"]
        assert len(deprecated) == 1
        assert "Oracle" in deprecated[0].value
        assert "COBOL" in deprecated[0].value
        # Deprecated should use "must_not_exceed" as proxy for "must_not_use"
        assert deprecated[0].constraint_type == "must_not_exceed"

    def test_extracts_risk_appetite(self, state_with_enterprise_context):
        """Test extraction of risk appetite constraint."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        risk = [c for c in constraints if c.field == "risk_appetite"]
        assert len(risk) == 1
        assert risk[0].value == "moderate"
        assert risk[0].constraint_type == "must_align"

    def test_all_constraints_have_claim_ids(self, state_with_enterprise_context):
        """Test that all constraints have source claim IDs."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        for c in constraints:
            assert c.source_claim_id.startswith("EC-")
            assert c.source_section == "enterprise_context"

    def test_minimal_context_extracts_correctly(self, enterprise_context_minimal):
        """Test that minimal context extracts correctly."""
        state = {
            "session_id": "test",
            "enterprise_context": enterprise_context_minimal,
        }
        constraints = generate_enterprise_constraints(state)

        # Should only have one GDPR constraint
        compliance = [c for c in constraints if c.field == "compliance_framework"]
        assert len(compliance) == 1
        assert compliance[0].value == "GDPR"


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE CONSTRAINTS INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestPhaseConstraintsIntegration:
    """Tests for enterprise constraints integration with phase constraints."""

    @pytest.mark.asyncio
    async def test_enterprise_constraints_prepended_to_strategy(
        self, state_with_enterprise_context
    ):
        """Test that enterprise constraints are prepended to strategy phase."""
        constraints = await generate_phase_constraints(
            state_with_enterprise_context, "strategy"
        )

        # Should include enterprise constraints
        enterprise_constraints = [
            c for c in constraints if c.source_section == "enterprise_context"
        ]
        assert len(enterprise_constraints) > 0

        # Enterprise constraints should come first
        if len(constraints) > len(enterprise_constraints):
            first_n = constraints[: len(enterprise_constraints)]
            for c in first_n:
                assert c.source_section == "enterprise_context"

    @pytest.mark.asyncio
    async def test_enterprise_constraints_prepended_to_delivery(
        self, state_with_enterprise_context
    ):
        """Test that enterprise constraints are prepended to delivery phase."""
        constraints = await generate_phase_constraints(
            state_with_enterprise_context, "delivery"
        )

        enterprise_constraints = [
            c for c in constraints if c.source_section == "enterprise_context"
        ]
        assert len(enterprise_constraints) > 0

    @pytest.mark.asyncio
    async def test_enterprise_constraints_prepended_to_design(
        self, state_with_enterprise_context
    ):
        """Test that enterprise constraints are prepended to design phase."""
        constraints = await generate_phase_constraints(
            state_with_enterprise_context, "design"
        )

        enterprise_constraints = [
            c for c in constraints if c.source_section == "enterprise_context"
        ]
        assert len(enterprise_constraints) > 0

    @pytest.mark.asyncio
    async def test_enterprise_constraints_prepended_to_synthesis(
        self, state_with_enterprise_context
    ):
        """Test that enterprise constraints are prepended to synthesis phase."""
        constraints = await generate_phase_constraints(
            state_with_enterprise_context, "synthesis"
        )

        enterprise_constraints = [
            c for c in constraints if c.source_section == "enterprise_context"
        ]
        assert len(enterprise_constraints) > 0

    @pytest.mark.asyncio
    async def test_no_enterprise_constraints_when_missing(
        self, state_without_enterprise_context
    ):
        """Test no enterprise constraints when context is missing."""
        constraints = await generate_phase_constraints(
            state_without_enterprise_context, "strategy"
        )

        enterprise_constraints = [
            c for c in constraints if c.source_section == "enterprise_context"
        ]
        assert len(enterprise_constraints) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT STRUCTURE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstraintStructure:
    """Tests for constraint structure validity."""

    def test_constraint_is_execution_constraint(self, state_with_enterprise_context):
        """Test that generated constraints are ExecutionConstraint instances."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        for c in constraints:
            assert isinstance(c, ExecutionConstraint)

    def test_constraint_has_required_fields(self, state_with_enterprise_context):
        """Test that constraints have all required fields."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        for c in constraints:
            assert hasattr(c, "field")
            assert hasattr(c, "value")
            assert hasattr(c, "source_section")
            assert hasattr(c, "source_claim_id")
            assert hasattr(c, "constraint_type")
            assert hasattr(c, "evidence_tier")
            assert hasattr(c, "confidence")
            assert hasattr(c, "urgency")  # New field

    def test_evidence_tiers_are_valid(self, state_with_enterprise_context):
        """Test that evidence tiers are valid E1-E5."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        valid_tiers = {"E1", "E2", "E3", "E4", "E5"}
        for c in constraints:
            assert c.evidence_tier in valid_tiers

    def test_confidence_in_valid_range(self, state_with_enterprise_context):
        """Test that confidence is between 0 and 1."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        for c in constraints:
            assert 0.0 <= c.confidence <= 1.0

    def test_constraint_types_are_valid(self, state_with_enterprise_context):
        """Test that constraint types are valid."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        valid_types = {"must_use", "must_align", "must_reference", "must_not_exceed", "guidance"}
        for c in constraints:
            assert c.constraint_type in valid_types

    def test_urgency_levels_are_valid(self, state_with_enterprise_context):
        """Test that urgency levels are valid."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        valid_urgency = {"required", "preferred", "guidance"}
        for c in constraints:
            assert c.urgency in valid_urgency


# ═══════════════════════════════════════════════════════════════════════════════
# URGENCY LEVEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestUrgencyLevels:
    """Tests for urgency level assignment in enterprise constraints."""

    def test_regulatory_constraints_are_required(self, state_with_enterprise_context):
        """Test that regulatory constraints have 'required' urgency."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        compliance_constraints = [
            c for c in constraints if c.field == "compliance_framework"
        ]
        for c in compliance_constraints:
            assert c.urgency == "required"

        data_residency = [c for c in constraints if c.field == "data_residency"]
        for c in data_residency:
            assert c.urgency == "required"

    def test_strategic_constraints_are_required(self, state_with_enterprise_context):
        """Test that strategic constraints have 'required' urgency."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        strategic = [c for c in constraints if c.field in ("strategic_alignment", "strategic_priorities")]
        for c in strategic:
            assert c.urgency == "required"

    def test_technology_constraints_are_preferred(self, state_with_enterprise_context):
        """Test that most technology constraints have 'preferred' urgency."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        tech_fields = {"cloud_platform", "programming_languages", "database_technologies"}
        tech_constraints = [c for c in constraints if c.field in tech_fields]
        for c in tech_constraints:
            assert c.urgency == "preferred"

    def test_deprecated_technologies_are_required(self, state_with_enterprise_context):
        """Test that deprecated technologies have 'required' urgency."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        deprecated = [c for c in constraints if c.field == "deprecated_technologies"]
        for c in deprecated:
            assert c.urgency == "required"

    def test_risk_appetite_is_required(self, state_with_enterprise_context):
        """Test that risk appetite has 'required' urgency."""
        constraints = generate_enterprise_constraints(state_with_enterprise_context)

        risk = [c for c in constraints if c.field == "risk_appetite"]
        for c in risk:
            assert c.urgency == "required"
