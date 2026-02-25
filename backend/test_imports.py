#!/usr/bin/env python3
"""Quick test to validate imports work."""

try:
    from models.constraint_schemas import (
        ConstraintPayload,
        ConstraintType,
        EvidenceTier,
        LegalConstraint,
        ConstraintAcknowledgment,
        ConstraintViolation,
        ConstraintPropagationLog,
    )
    print("✓ models.constraint_schemas imports successful")

    from agents.constraint_broadcaster import (
        ExecutionConstraint,
        validate_constraint_payload,
        validate_legal_constraints,
        create_constraint_acknowledgment,
        log_constraint_propagation,
        validate_all_constraints,
    )
    print("✓ agents.constraint_broadcaster imports successful")

    # Test basic constraint creation
    constraint = ConstraintPayload(
        field="test_field",
        value="test_value",
        source_section="test_section",
        source_claim_id="TS-1",
        constraint_type=ConstraintType.MUST_USE,
        evidence_tier=EvidenceTier.E2,
        confidence=0.8,
    )
    print(f"✓ Created ConstraintPayload: {constraint.field}")

    # Test legal constraint
    legal = LegalConstraint(
        regulation_name="GDPR",
        requirement="Data encryption required for EU user data",
        applicability="Product processes EU user personal data",
        impact_level="high",
        compliance_timeline="6 months",
    )
    print(f"✓ Created LegalConstraint: {legal.regulation_name}")

    # Test acknowledgment
    ack = ConstraintAcknowledgment(
        agent_name="test_agent",
        phase="strategy",
        constraints_received_count=1,
        constraint_fields=["test_field"],
    )
    print(f"✓ Created ConstraintAcknowledgment: {ack.agent_name}")

    print("\n✅ All imports and basic validations successful!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
