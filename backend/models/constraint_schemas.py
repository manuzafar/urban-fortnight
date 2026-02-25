"""
Pydantic models for constraint validation.

This module defines strict validation schemas for constraints that flow
between agents and phases, ensuring that constraints don't get lost,
corrupted, or misinterpreted during the discovery workflow.

Key concepts:
- ConstraintPayload: Validated constraint with all required fields
- ConstraintAcknowledgment: Proof that an agent received constraints
- LegalConstraint: Specific constraints from legal_preliminary scan
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ConstraintType(str, Enum):
    """Valid constraint types."""
    MUST_USE = "must_use"
    MUST_ALIGN = "must_align"
    MUST_REFERENCE = "must_reference"
    MUST_NOT_EXCEED = "must_not_exceed"


class EvidenceTier(str, Enum):
    """Evidence quality tiers."""
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"
    E5 = "E5"


class ConstraintPayload(BaseModel):
    """
    Validated constraint payload.

    This schema ensures all constraints have required fields and valid values.

    Attributes:
        field: The field being constrained (e.g., "market_size", "primary_customer")
        value: The constrained value (any type, but must not be None)
        source_section: Which section this constraint comes from
        source_claim_id: The claim ID this constraint is based on (must follow pattern)
        constraint_type: Type of constraint (validated enum)
        evidence_tier: Evidence tier (validated enum)
        confidence: Confidence level (0.0-1.0)
        created_at: When this constraint was created (auto-set)
    """

    field: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Field being constrained",
    )
    value: Any = Field(
        ...,
        description="Constrained value (must not be None)",
    )
    source_section: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Source section name",
    )
    source_claim_id: str = Field(
        ...,
        pattern=r"^[A-Z]{2,4}-\d+$",
        description="Claim ID (format: XX-1, XXX-12, etc.)",
    )
    constraint_type: ConstraintType = Field(
        ...,
        description="Type of constraint",
    )
    evidence_tier: EvidenceTier = Field(
        default=EvidenceTier.E4,
        description="Evidence tier",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence level",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )

    @field_validator("value")
    @classmethod
    def value_must_not_be_none(cls, v):
        """Ensure value is not None."""
        if v is None:
            raise ValueError("Constraint value must not be None")
        return v

    @field_validator("field")
    @classmethod
    def field_must_be_valid(cls, v):
        """Ensure field name is alphanumeric with underscores."""
        if not v.replace("_", "").isalnum():
            raise ValueError(
                f"Field name must be alphanumeric with underscores: {v}"
            )
        return v

    @model_validator(mode="after")
    def validate_confidence_matches_evidence(self):
        """
        Validate that confidence level is reasonable for evidence tier.

        Higher evidence tiers (E1, E2) should have higher confidence.
        """
        tier_min_confidence = {
            EvidenceTier.E1: 0.85,
            EvidenceTier.E2: 0.70,
            EvidenceTier.E3: 0.50,
            EvidenceTier.E4: 0.30,
            EvidenceTier.E5: 0.10,
        }

        min_confidence = tier_min_confidence.get(self.evidence_tier, 0.0)
        if self.confidence < min_confidence:
            raise ValueError(
                f"Confidence {self.confidence} too low for evidence tier "
                f"{self.evidence_tier.value} (minimum: {min_confidence})"
            )

        return self


class LegalConstraint(BaseModel):
    """
    Legal/regulatory constraint from preliminary_legal_scan.

    These constraints come from the legal_preliminary agent and must
    be properly formatted and propagated to downstream agents.

    Attributes:
        regulation_name: Name of regulation (e.g., GDPR, HIPAA)
        requirement: Specific requirement text
        applicability: Why this applies
        impact_level: Impact on product (high/medium/low)
        compliance_timeline: Time needed for compliance
        blocking: Whether this blocks product launch
    """

    regulation_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Regulation name",
    )
    requirement: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Specific requirement",
    )
    applicability: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Why this applies",
    )
    impact_level: str = Field(
        ...,
        pattern=r"^(high|medium|low)$",
        description="Impact level (high/medium/low)",
    )
    compliance_timeline: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Timeline for compliance",
    )
    blocking: bool = Field(
        default=False,
        description="Whether this blocks launch",
    )

    @field_validator("regulation_name")
    @classmethod
    def regulation_name_must_be_uppercase_or_titlecase(cls, v):
        """Ensure regulation name follows standard naming."""
        # Allow acronyms (GDPR, HIPAA) or Title Case (Data Protection Act)
        if not (v.isupper() or v.istitle() or any(c.isupper() for c in v)):
            raise ValueError(
                f"Regulation name should be uppercase acronym or title case: {v}"
            )
        return v


class ConstraintAcknowledgment(BaseModel):
    """
    Proof that an agent received and acknowledged constraints.

    This model tracks that constraints were successfully delivered
    to an agent and the agent confirmed receipt.

    Attributes:
        agent_name: Name of the agent
        phase: Phase name (strategy/delivery/design/synthesis)
        constraints_received_count: Number of constraints received
        constraint_fields: List of constraint field names
        acknowledged_at: When constraints were acknowledged
        prompt_injection_confirmed: Whether constraints were in prompt
    """

    agent_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Agent name",
    )
    phase: str = Field(
        ...,
        pattern=r"^(strategy|delivery|design|synthesis)$",
        description="Phase name",
    )
    constraints_received_count: int = Field(
        ...,
        ge=0,
        description="Number of constraints received",
    )
    constraint_fields: list[str] = Field(
        ...,
        min_length=0,
        description="List of constraint field names",
    )
    acknowledged_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Acknowledgment timestamp",
    )
    prompt_injection_confirmed: bool = Field(
        default=False,
        description="Whether constraints were injected into prompt",
    )

    @model_validator(mode="after")
    def validate_counts_match(self):
        """Ensure constraint count matches field list length."""
        if self.constraints_received_count != len(self.constraint_fields):
            raise ValueError(
                f"Constraint count ({self.constraints_received_count}) does not "
                f"match field list length ({len(self.constraint_fields)})"
            )
        return self


class ConstraintViolation(BaseModel):
    """
    A detected constraint violation.

    Attributes:
        field: Field that was constrained
        expected: Expected value from constraint
        actual: Actual value in output
        severity: Violation severity (high/medium/low)
        constraint_type: Type of constraint violated
        detected_at: When violation was detected
    """

    field: str = Field(..., description="Constrained field")
    expected: Any = Field(..., description="Expected value")
    actual: Any = Field(..., description="Actual value")
    severity: str = Field(
        ...,
        pattern=r"^(high|medium|low)$",
        description="Severity level",
    )
    constraint_type: ConstraintType = Field(
        ...,
        description="Type of constraint violated",
    )
    detected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Detection timestamp",
    )


class ConstraintPropagationLog(BaseModel):
    """
    Log of constraint propagation through phases.

    Tracks how constraints flow from one phase to another,
    ensuring nothing gets lost or corrupted.

    Attributes:
        session_id: Session identifier
        source_phase: Phase that generated constraints
        target_phase: Phase receiving constraints
        constraints_generated: Number of constraints generated
        constraints_delivered: Number successfully delivered
        constraints_acknowledged: Number acknowledged by receiving agent
        propagation_status: Status (success/partial/failed)
        errors: Any errors during propagation
        created_at: Log timestamp
    """

    session_id: str = Field(..., description="Session ID")
    source_phase: str = Field(..., description="Source phase")
    target_phase: str = Field(
        ...,
        pattern=r"^(strategy|delivery|design|synthesis)$",
        description="Target phase",
    )
    constraints_generated: int = Field(
        ...,
        ge=0,
        description="Constraints generated",
    )
    constraints_delivered: int = Field(
        ...,
        ge=0,
        description="Constraints delivered",
    )
    constraints_acknowledged: int = Field(
        ...,
        ge=0,
        description="Constraints acknowledged",
    )
    propagation_status: str = Field(
        ...,
        pattern=r"^(success|partial|failed)$",
        description="Propagation status",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Propagation errors",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Log timestamp",
    )

    @model_validator(mode="after")
    def validate_delivery_counts(self):
        """Ensure delivery counts are logical."""
        if self.constraints_delivered > self.constraints_generated:
            raise ValueError(
                f"Cannot deliver more constraints ({self.constraints_delivered}) "
                f"than generated ({self.constraints_generated})"
            )

        if self.constraints_acknowledged > self.constraints_delivered:
            raise ValueError(
                f"Cannot acknowledge more constraints ({self.constraints_acknowledged}) "
                f"than delivered ({self.constraints_delivered})"
            )

        # Set status based on counts
        if self.constraints_delivered == 0 and self.constraints_generated > 0:
            if self.propagation_status != "failed":
                raise ValueError("Status should be 'failed' when no constraints delivered")
        elif self.constraints_delivered < self.constraints_generated:
            if self.propagation_status not in ["partial", "failed"]:
                raise ValueError("Status should be 'partial' or 'failed' when delivery incomplete")
        elif self.constraints_acknowledged < self.constraints_delivered:
            if self.propagation_status != "partial":
                raise ValueError("Status should be 'partial' when acknowledgment incomplete")

        return self
