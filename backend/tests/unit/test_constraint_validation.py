"""
Tests for constraint validation system.

These tests verify that:
1. Constraint payloads are properly validated with Pydantic
2. Legal constraints from preliminary_legal_scan are correctly formatted
3. Receiving agents properly acknowledge constraints
4. Constraints don't get lost or corrupted between phases
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from models.constraint_schemas import (
    ConstraintPayload,
    ConstraintType,
    EvidenceTier,
    LegalConstraint,
    ConstraintAcknowledgment,
    ConstraintViolation,
    ConstraintPropagationLog,
)
from agents.constraint_broadcaster import (
    ExecutionConstraint,
    validate_constraint_payload,
    validate_legal_constraints,
    create_constraint_acknowledgment,
    log_constraint_propagation,
    validate_all_constraints,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT PAYLOAD VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstraintPayloadValidation:
    """Tests for ConstraintPayload Pydantic model."""

    def test_valid_constraint_payload(self):
        """Should create valid constraint payload."""
        payload = ConstraintPayload(
            field="market_size",
            value="$5B",
            source_section="customer_research",
            source_claim_id="MI-1",
            constraint_type=ConstraintType.MUST_USE,
            evidence_tier=EvidenceTier.E2,
            confidence=0.8,
        )

        assert payload.field == "market_size"
        assert payload.value == "$5B"
        assert payload.constraint_type == ConstraintType.MUST_USE
        assert payload.evidence_tier == EvidenceTier.E2
        assert payload.confidence == 0.8

    def test_constraint_payload_with_defaults(self):
        """Should use defaults for optional fields."""
        payload = ConstraintPayload(
            field="pricing",
            value="$99",
            source_section="business_case",
            source_claim_id="BC-1",
            constraint_type=ConstraintType.MUST_ALIGN,
        )

        assert payload.evidence_tier == EvidenceTier.E4
        assert payload.confidence == 0.5
        assert isinstance(payload.created_at, datetime)

    def test_constraint_payload_rejects_none_value(self):
        """Should reject None as constraint value."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintPayload(
                field="test_field",
                value=None,
                source_section="test_section",
                source_claim_id="TS-1",
                constraint_type=ConstraintType.MUST_USE,
            )

        assert "must not be none" in str(exc_info.value).lower()

    def test_constraint_payload_validates_claim_id_format(self):
        """Should validate claim_id follows pattern XX-1."""
        # Valid formats
        valid_ids = ["MI-1", "BC-12", "CL-999", "JTBD-1"]
        for claim_id in valid_ids:
            payload = ConstraintPayload(
                field="test",
                value="test",
                source_section="test",
                source_claim_id=claim_id,
                constraint_type=ConstraintType.MUST_USE,
            )
            assert payload.source_claim_id == claim_id

        # Invalid formats
        invalid_ids = ["MI1", "BC_1", "cl-1", "123", "MI-", "-1"]
        for claim_id in invalid_ids:
            with pytest.raises(ValidationError):
                ConstraintPayload(
                    field="test",
                    value="test",
                    source_section="test",
                    source_claim_id=claim_id,
                    constraint_type=ConstraintType.MUST_USE,
                )

    def test_constraint_payload_validates_field_name(self):
        """Should validate field name is alphanumeric with underscores."""
        # Valid field names
        valid_fields = ["market_size", "pricing_model", "ltv_cac_ratio", "year5revenue"]
        for field in valid_fields:
            payload = ConstraintPayload(
                field=field,
                value="test",
                source_section="test",
                source_claim_id="TS-1",
                constraint_type=ConstraintType.MUST_USE,
            )
            assert payload.field == field

        # Invalid field names (with special characters)
        invalid_fields = ["market-size", "pricing.model", "ltv/cac", "year 5"]
        for field in invalid_fields:
            with pytest.raises(ValidationError):
                ConstraintPayload(
                    field=field,
                    value="test",
                    source_section="test",
                    source_claim_id="TS-1",
                    constraint_type=ConstraintType.MUST_USE,
                )

    def test_constraint_payload_validates_confidence_for_evidence_tier(self):
        """Should ensure confidence matches evidence tier."""
        # E1 with high confidence - valid
        payload = ConstraintPayload(
            field="test",
            value="test",
            source_section="test",
            source_claim_id="TS-1",
            constraint_type=ConstraintType.MUST_USE,
            evidence_tier=EvidenceTier.E1,
            confidence=0.95,
        )
        assert payload.confidence == 0.95

        # E1 with low confidence - invalid
        with pytest.raises(ValidationError) as exc_info:
            ConstraintPayload(
                field="test",
                value="test",
                source_section="test",
                source_claim_id="TS-1",
                constraint_type=ConstraintType.MUST_USE,
                evidence_tier=EvidenceTier.E1,
                confidence=0.5,  # Too low for E1
            )

        assert "too low for evidence tier" in str(exc_info.value).lower()

    def test_constraint_payload_confidence_bounds(self):
        """Should enforce confidence between 0.0 and 1.0."""
        # Valid
        payload = ConstraintPayload(
            field="test",
            value="test",
            source_section="test",
            source_claim_id="TS-1",
            constraint_type=ConstraintType.MUST_USE,
            confidence=0.5,
        )
        assert payload.confidence == 0.5

        # Too low
        with pytest.raises(ValidationError):
            ConstraintPayload(
                field="test",
                value="test",
                source_section="test",
                source_claim_id="TS-1",
                constraint_type=ConstraintType.MUST_USE,
                confidence=-0.1,
            )

        # Too high
        with pytest.raises(ValidationError):
            ConstraintPayload(
                field="test",
                value="test",
                source_section="test",
                source_claim_id="TS-1",
                constraint_type=ConstraintType.MUST_USE,
                confidence=1.5,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# LEGAL CONSTRAINT VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestLegalConstraintValidation:
    """Tests for LegalConstraint validation."""

    def test_valid_legal_constraint(self):
        """Should create valid legal constraint."""
        constraint = LegalConstraint(
            regulation_name="GDPR",
            requirement="Data must be encrypted at rest and in transit",
            applicability="Product processes EU user data",
            impact_level="high",
            compliance_timeline="6 months",
            blocking=True,
        )

        assert constraint.regulation_name == "GDPR"
        assert constraint.impact_level == "high"
        assert constraint.blocking is True

    def test_legal_constraint_validates_regulation_name_case(self):
        """Should validate regulation name is properly formatted."""
        # Valid formats
        valid_names = ["GDPR", "HIPAA", "SOC2", "Data Protection Act"]
        for name in valid_names:
            constraint = LegalConstraint(
                regulation_name=name,
                requirement="Test requirement",
                applicability="Test applicability",
                impact_level="medium",
                compliance_timeline="3 months",
            )
            assert constraint.regulation_name == name

        # Invalid format (all lowercase)
        with pytest.raises(ValidationError):
            LegalConstraint(
                regulation_name="gdpr",
                requirement="Test requirement",
                applicability="Test applicability",
                impact_level="medium",
                compliance_timeline="3 months",
            )

    def test_legal_constraint_validates_impact_level(self):
        """Should validate impact_level is high/medium/low."""
        # Valid levels
        for level in ["high", "medium", "low"]:
            constraint = LegalConstraint(
                regulation_name="TEST",
                requirement="Test requirement",
                applicability="Test applicability",
                impact_level=level,
                compliance_timeline="3 months",
            )
            assert constraint.impact_level == level

        # Invalid level
        with pytest.raises(ValidationError):
            LegalConstraint(
                regulation_name="TEST",
                requirement="Test requirement",
                applicability="Test applicability",
                impact_level="critical",  # Not valid
                compliance_timeline="3 months",
            )

    def test_legal_constraint_validates_field_lengths(self):
        """Should validate minimum and maximum field lengths."""
        # Requirement too short
        with pytest.raises(ValidationError):
            LegalConstraint(
                regulation_name="TEST",
                requirement="Short",  # Less than 10 chars
                applicability="Test applicability",
                impact_level="medium",
                compliance_timeline="3 months",
            )

        # Requirement too long
        with pytest.raises(ValidationError):
            LegalConstraint(
                regulation_name="TEST",
                requirement="x" * 1001,  # More than 1000 chars
                applicability="Test applicability",
                impact_level="medium",
                compliance_timeline="3 months",
            )


class TestValidateLegalConstraints:
    """Tests for validate_legal_constraints function."""

    def test_validates_legal_constraints_from_preliminary_scan(self):
        """Should validate legal constraints from preliminary_legal_scan output."""
        preliminary_scan = {
            "applicable_regulations": [
                {
                    "name": "GDPR",
                    "description": "General Data Protection Regulation requires data encryption",
                    "applicability": "Product processes EU user data",
                    "impact_level": "high",
                    "estimated_compliance_timeline": "6 months",
                },
                {
                    "name": "HIPAA",
                    "description": "Health Insurance Portability and Accountability Act",
                    "applicability": "Product handles health information",
                    "impact_level": "medium",
                    "estimated_compliance_timeline": "12 months",
                },
            ],
        }

        valid_constraints, errors = validate_legal_constraints(preliminary_scan)

        assert len(valid_constraints) == 2
        assert len(errors) == 0
        assert valid_constraints[0].regulation_name == "GDPR"
        assert valid_constraints[1].regulation_name == "HIPAA"

    def test_handles_malformed_legal_constraints(self):
        """Should handle malformed legal constraints gracefully."""
        preliminary_scan = {
            "applicable_regulations": [
                {
                    "name": "GDPR",
                    "description": "Valid constraint",
                    "applicability": "Valid applicability",
                    "impact_level": "high",
                    "estimated_compliance_timeline": "6 months",
                },
                {
                    "name": "gdpr",  # Invalid: lowercase
                    "description": "Short",  # Invalid: too short
                    "applicability": "Test",  # Invalid: too short
                    "impact_level": "critical",  # Invalid: not high/medium/low
                    "estimated_compliance_timeline": "soon",
                },
            ],
        }

        valid_constraints, errors = validate_legal_constraints(preliminary_scan)

        assert len(valid_constraints) == 1  # Only first one is valid
        assert len(errors) == 1  # Second one has errors
        assert "validation failed" in errors[0].lower()

    def test_handles_empty_regulations_list(self):
        """Should handle empty regulations list."""
        preliminary_scan = {"applicable_regulations": []}

        valid_constraints, errors = validate_legal_constraints(preliminary_scan)

        assert len(valid_constraints) == 0
        assert len(errors) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT ACKNOWLEDGMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstraintAcknowledgment:
    """Tests for ConstraintAcknowledgment model."""

    def test_valid_constraint_acknowledgment(self):
        """Should create valid constraint acknowledgment."""
        ack = ConstraintAcknowledgment(
            agent_name="business_strategy",
            phase="strategy",
            constraints_received_count=3,
            constraint_fields=["market_size", "primary_customer", "competitive_landscape"],
            prompt_injection_confirmed=True,
        )

        assert ack.agent_name == "business_strategy"
        assert ack.phase == "strategy"
        assert ack.constraints_received_count == 3
        assert len(ack.constraint_fields) == 3
        assert ack.prompt_injection_confirmed is True

    def test_constraint_acknowledgment_validates_phase(self):
        """Should validate phase is one of the valid phases."""
        # Valid phases
        for phase in ["strategy", "delivery", "design", "synthesis"]:
            ack = ConstraintAcknowledgment(
                agent_name="test_agent",
                phase=phase,
                constraints_received_count=1,
                constraint_fields=["test"],
            )
            assert ack.phase == phase

        # Invalid phase
        with pytest.raises(ValidationError):
            ConstraintAcknowledgment(
                agent_name="test_agent",
                phase="discovery",  # Not valid
                constraints_received_count=1,
                constraint_fields=["test"],
            )

    def test_constraint_acknowledgment_validates_count_matches_fields(self):
        """Should ensure constraint count matches field list length."""
        # Valid: count matches
        ack = ConstraintAcknowledgment(
            agent_name="test_agent",
            phase="strategy",
            constraints_received_count=2,
            constraint_fields=["field1", "field2"],
        )
        assert ack.constraints_received_count == 2

        # Invalid: count doesn't match
        with pytest.raises(ValidationError) as exc_info:
            ConstraintAcknowledgment(
                agent_name="test_agent",
                phase="strategy",
                constraints_received_count=3,
                constraint_fields=["field1", "field2"],  # Only 2 fields
            )

        assert "does not match" in str(exc_info.value).lower()

    def test_create_constraint_acknowledgment_function(self):
        """Should create acknowledgment from ExecutionConstraints."""
        constraints = [
            ExecutionConstraint(
                field="market_size",
                value="$5B",
                source_section="customer_research",
                source_claim_id="MI-1",
                constraint_type="must_use",
            ),
            ExecutionConstraint(
                field="pricing",
                value="$99",
                source_section="business_case",
                source_claim_id="BC-1",
                constraint_type="must_align",
            ),
        ]

        ack = create_constraint_acknowledgment(
            agent_name="gtm_agent",
            phase="strategy",
            constraints=constraints,
            prompt_injected=True,
        )

        assert ack.agent_name == "gtm_agent"
        assert ack.phase == "strategy"
        assert ack.constraints_received_count == 2
        assert "market_size" in ack.constraint_fields
        assert "pricing" in ack.constraint_fields
        assert ack.prompt_injection_confirmed is True


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT PROPAGATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstraintPropagationLog:
    """Tests for ConstraintPropagationLog model."""

    def test_valid_propagation_log_success(self):
        """Should create valid propagation log with success status."""
        log = ConstraintPropagationLog(
            session_id="test-session-123",
            source_phase="discovery",
            target_phase="strategy",
            constraints_generated=3,
            constraints_delivered=3,
            constraints_acknowledged=3,
            propagation_status="success",
            errors=[],
        )

        assert log.session_id == "test-session-123"
        assert log.propagation_status == "success"
        assert log.constraints_generated == 3

    def test_propagation_log_validates_delivery_counts(self):
        """Should validate delivery counts are logical."""
        # Invalid: delivered > generated
        with pytest.raises(ValidationError) as exc_info:
            ConstraintPropagationLog(
                session_id="test",
                source_phase="discovery",
                target_phase="strategy",
                constraints_generated=2,
                constraints_delivered=3,  # More than generated
                constraints_acknowledged=2,
                propagation_status="partial",
            )

        assert "cannot deliver more" in str(exc_info.value).lower()

        # Invalid: acknowledged > delivered
        with pytest.raises(ValidationError) as exc_info:
            ConstraintPropagationLog(
                session_id="test",
                source_phase="discovery",
                target_phase="strategy",
                constraints_generated=3,
                constraints_delivered=2,
                constraints_acknowledged=3,  # More than delivered
                propagation_status="partial",
            )

        assert "cannot acknowledge more" in str(exc_info.value).lower()

    def test_propagation_log_validates_status_matches_counts(self):
        """Should validate status matches delivery counts."""
        # Should be 'failed' when nothing delivered
        with pytest.raises(ValidationError):
            ConstraintPropagationLog(
                session_id="test",
                source_phase="discovery",
                target_phase="strategy",
                constraints_generated=3,
                constraints_delivered=0,
                constraints_acknowledged=0,
                propagation_status="success",  # Should be 'failed'
            )

        # Should be 'partial' when delivery incomplete
        with pytest.raises(ValidationError):
            ConstraintPropagationLog(
                session_id="test",
                source_phase="discovery",
                target_phase="strategy",
                constraints_generated=3,
                constraints_delivered=2,
                constraints_acknowledged=2,
                propagation_status="success",  # Should be 'partial'
            )

    def test_log_constraint_propagation_function(self):
        """Should create propagation log from constraints."""
        generated = [
            ExecutionConstraint(
                field="market_size",
                value="$5B",
                source_section="customer_research",
                source_claim_id="MI-1",
                constraint_type="must_use",
            ),
            ExecutionConstraint(
                field="pricing",
                value="$99",
                source_section="business_case",
                source_claim_id="BC-1",
                constraint_type="must_align",
            ),
        ]

        delivered = generated  # All delivered

        ack = ConstraintAcknowledgment(
            agent_name="test_agent",
            phase="strategy",
            constraints_received_count=2,
            constraint_fields=["market_size", "pricing"],
        )

        log = log_constraint_propagation(
            session_id="test-123",
            source_phase="discovery",
            target_phase="strategy",
            generated_constraints=generated,
            delivered_constraints=delivered,
            acknowledgment=ack,
        )

        assert log.session_id == "test-123"
        assert log.constraints_generated == 2
        assert log.constraints_delivered == 2
        assert log.constraints_acknowledged == 2
        assert log.propagation_status == "success"


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT VALIDATION INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidateConstraintPayloadFunction:
    """Tests for validate_constraint_payload function."""

    def test_validates_valid_execution_constraint(self):
        """Should validate ExecutionConstraint successfully."""
        constraint = ExecutionConstraint(
            field="market_size",
            value="$5B",
            source_section="customer_research",
            source_claim_id="MI-1",
            constraint_type="must_use",
            evidence_tier="E2",
            confidence=0.8,
        )

        is_valid, error = validate_constraint_payload(constraint)

        assert is_valid is True
        assert error is None

    def test_rejects_invalid_execution_constraint(self):
        """Should reject ExecutionConstraint with invalid claim ID."""
        constraint = ExecutionConstraint(
            field="market_size",
            value="$5B",
            source_section="customer_research",
            source_claim_id="INVALID",  # Invalid format
            constraint_type="must_use",
            evidence_tier="E2",
            confidence=0.8,
        )

        is_valid, error = validate_constraint_payload(constraint)

        assert is_valid is False
        assert error is not None
        assert "validation failed" in error.lower()


class TestValidateAllConstraints:
    """Tests for validate_all_constraints function."""

    def test_validates_batch_of_constraints(self):
        """Should validate multiple constraints and separate valid from invalid."""
        constraints = [
            ExecutionConstraint(
                field="market_size",
                value="$5B",
                source_section="customer_research",
                source_claim_id="MI-1",
                constraint_type="must_use",
                evidence_tier="E2",
                confidence=0.8,
            ),
            ExecutionConstraint(
                field="pricing",
                value="$99",
                source_section="business_case",
                source_claim_id="BC-1",
                constraint_type="must_align",
                evidence_tier="E3",
                confidence=0.6,
            ),
            ExecutionConstraint(
                field="bad_field",
                value="test",
                source_section="test",
                source_claim_id="INVALID",  # Invalid format
                constraint_type="must_use",
            ),
        ]

        valid_constraints, errors = validate_all_constraints(constraints)

        assert len(valid_constraints) == 2  # First two are valid
        assert len(errors) == 1  # Last one is invalid
        assert "validation failed" in errors[0].lower()

    def test_handles_empty_constraint_list(self):
        """Should handle empty constraint list."""
        valid_constraints, errors = validate_all_constraints([])

        assert len(valid_constraints) == 0
        assert len(errors) == 0
