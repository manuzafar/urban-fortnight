# Constraint Validation System

## Overview

The constraint validation system ensures that constraints passed between agents and phases don't get lost, corrupted, or misinterpreted during the discovery workflow.

## Problem Statement

Before this system, constraints could:
- Be malformed or missing required fields
- Get lost during phase transitions
- Have incorrect evidence tier/confidence mappings
- Never be acknowledged by receiving agents
- Violate logical consistency rules

## Solution Architecture

### 1. Pydantic Validation Schemas

**Location**: `backend/models/constraint_schemas.py`

All constraints are validated using strict Pydantic models:

```python
from models.constraint_schemas import (
    ConstraintPayload,          # Validated constraint with all required fields
    LegalConstraint,            # Legal/regulatory constraints
    ConstraintAcknowledgment,   # Proof that agent received constraints
    ConstraintPropagationLog,   # Log of constraint flow between phases
    ConstraintViolation,        # Detected constraint violations
)
```

### 2. Validation Functions

**Location**: `backend/agents/constraint_broadcaster.py`

Key validation functions:

```python
# Validate a single constraint
is_valid, error = validate_constraint_payload(constraint)

# Validate legal constraints from preliminary_legal_scan
valid_constraints, errors = validate_legal_constraints(preliminary_scan)

# Create acknowledgment when agent receives constraints
ack = create_constraint_acknowledgment(
    agent_name="business_strategy",
    phase="strategy",
    constraints=constraints,
    prompt_injected=True
)

# Log constraint propagation between phases
log = log_constraint_propagation(
    session_id="session-123",
    source_phase="discovery",
    target_phase="strategy",
    generated_constraints=generated,
    delivered_constraints=delivered,
    acknowledgment=ack
)

# Validate batch of constraints
valid, errors = validate_all_constraints(constraints)
```

## Validation Rules

### ConstraintPayload Validation

**Required Fields:**
- `field`: Alphanumeric with underscores (e.g., `market_size`, `ltv_cac_ratio`)
- `value`: Any non-None value
- `source_section`: Source agent/section name
- `source_claim_id`: Pattern `XX-1` (e.g., `MI-1`, `BC-12`, `JTBD-999`)
- `constraint_type`: One of `must_use`, `must_align`, `must_reference`, `must_not_exceed`
- `evidence_tier`: One of `E1`, `E2`, `E3`, `E4`, `E5`
- `confidence`: Float between 0.0 and 1.0

**Validation Rules:**
1. `value` must not be None
2. `field` must be alphanumeric with underscores only
3. `source_claim_id` must match pattern `[A-Z]{2,4}-\d+`
4. `confidence` must match evidence tier minimum:
   - E1: min 0.85
   - E2: min 0.70
   - E3: min 0.50
   - E4: min 0.30
   - E5: min 0.10

**Examples:**

```python
# Valid
constraint = ConstraintPayload(
    field="market_size",
    value="$5B",
    source_section="customer_research",
    source_claim_id="MI-1",
    constraint_type=ConstraintType.MUST_USE,
    evidence_tier=EvidenceTier.E2,
    confidence=0.8,  # >= 0.70 for E2
)

# Invalid: confidence too low for E1
constraint = ConstraintPayload(
    field="market_size",
    value="$5B",
    source_section="customer_research",
    source_claim_id="MI-1",
    constraint_type=ConstraintType.MUST_USE,
    evidence_tier=EvidenceTier.E1,
    confidence=0.5,  # ❌ Should be >= 0.85 for E1
)
```

### LegalConstraint Validation

**Required Fields:**
- `regulation_name`: Uppercase acronym or Title Case (e.g., `GDPR`, `Data Protection Act`)
- `requirement`: 10-1000 characters
- `applicability`: 10-500 characters
- `impact_level`: One of `high`, `medium`, `low`
- `compliance_timeline`: Timeline string
- `blocking`: Boolean (whether this blocks launch)

**Validation Rules:**
1. `regulation_name` must be uppercase or title case
2. `requirement` must be 10-1000 characters
3. `applicability` must be 10-500 characters
4. `impact_level` must be exactly `high`, `medium`, or `low`

**Examples:**

```python
# Valid
legal = LegalConstraint(
    regulation_name="GDPR",
    requirement="Data must be encrypted at rest and in transit",
    applicability="Product processes EU user data",
    impact_level="high",
    compliance_timeline="6 months",
    blocking=True,
)

# Invalid: lowercase regulation name
legal = LegalConstraint(
    regulation_name="gdpr",  # ❌ Should be uppercase
    requirement="Data encryption required",
    applicability="EU data processing",
    impact_level="high",
    compliance_timeline="6 months",
)
```

### ConstraintAcknowledgment Validation

**Required Fields:**
- `agent_name`: Agent name
- `phase`: One of `strategy`, `delivery`, `design`, `synthesis`
- `constraints_received_count`: Number of constraints
- `constraint_fields`: List of field names
- `prompt_injection_confirmed`: Whether constraints were in prompt

**Validation Rules:**
1. `phase` must be one of the valid phases
2. `constraints_received_count` must match `len(constraint_fields)`
3. Count must be >= 0

**Examples:**

```python
# Valid
ack = ConstraintAcknowledgment(
    agent_name="business_strategy",
    phase="strategy",
    constraints_received_count=2,
    constraint_fields=["market_size", "primary_customer"],
    prompt_injection_confirmed=True,
)

# Invalid: count doesn't match fields
ack = ConstraintAcknowledgment(
    agent_name="business_strategy",
    phase="strategy",
    constraints_received_count=3,  # ❌ Says 3 but only 2 fields
    constraint_fields=["market_size", "primary_customer"],
)
```

### ConstraintPropagationLog Validation

**Required Fields:**
- `session_id`: Session identifier
- `source_phase`: Source phase name
- `target_phase`: One of `strategy`, `delivery`, `design`, `synthesis`
- `constraints_generated`: Number generated
- `constraints_delivered`: Number delivered
- `constraints_acknowledged`: Number acknowledged
- `propagation_status`: One of `success`, `partial`, `failed`
- `errors`: List of error messages

**Validation Rules:**
1. `constraints_delivered` <= `constraints_generated`
2. `constraints_acknowledged` <= `constraints_delivered`
3. Status must match delivery counts:
   - `failed`: when `delivered == 0` and `generated > 0`
   - `partial`: when `delivered < generated` or `acknowledged < delivered`
   - `success`: when all constraints delivered and acknowledged

**Examples:**

```python
# Valid: Success
log = ConstraintPropagationLog(
    session_id="session-123",
    source_phase="discovery",
    target_phase="strategy",
    constraints_generated=3,
    constraints_delivered=3,
    constraints_acknowledged=3,
    propagation_status="success",
    errors=[],
)

# Invalid: delivered > generated
log = ConstraintPropagationLog(
    session_id="session-123",
    source_phase="discovery",
    target_phase="strategy",
    constraints_generated=2,
    constraints_delivered=3,  # ❌ Can't deliver more than generated
    constraints_acknowledged=2,
    propagation_status="partial",
)
```

## Usage Examples

### Example 1: Validating Legal Constraints from preliminary_legal_scan

```python
from agents.constraint_broadcaster import validate_legal_constraints

# Output from legal_preliminary agent
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
            "name": "hipaa",  # ❌ Invalid: lowercase
            "description": "Short",  # ❌ Invalid: too short
            "applicability": "Test",  # ❌ Invalid: too short
            "impact_level": "critical",  # ❌ Invalid: not high/medium/low
            "estimated_compliance_timeline": "soon",
        },
    ],
}

valid_constraints, errors = validate_legal_constraints(preliminary_scan)

print(f"Valid: {len(valid_constraints)}")  # 1
print(f"Errors: {len(errors)}")  # 1
print(f"Error: {errors[0]}")  # Details about second regulation
```

### Example 2: Creating and Validating Constraint Acknowledgment

```python
from agents.constraint_broadcaster import (
    ExecutionConstraint,
    create_constraint_acknowledgment,
)

# Constraints received by strategy phase
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
        field="primary_customer",
        value="Tech-Savvy Manager (Early Adopter)",
        source_section="detailed_personas",
        source_claim_id="CP-1",
        constraint_type="must_align",
        evidence_tier="E4",
        confidence=0.6,
    ),
]

# Agent acknowledges receipt
ack = create_constraint_acknowledgment(
    agent_name="business_strategy",
    phase="strategy",
    constraints=constraints,
    prompt_injected=True,
)

print(f"Agent: {ack.agent_name}")
print(f"Received: {ack.constraints_received_count} constraints")
print(f"Fields: {ack.constraint_fields}")
print(f"Prompt injection: {ack.prompt_injection_confirmed}")
```

### Example 3: Logging Constraint Propagation

```python
from agents.constraint_broadcaster import (
    log_constraint_propagation,
    create_constraint_acknowledgment,
)

# Generate constraints for strategy phase
generated = [...]  # List of ExecutionConstraint

# Deliver constraints to agents
delivered = generated  # All delivered successfully

# Agent acknowledges
ack = create_constraint_acknowledgment(
    agent_name="business_strategy",
    phase="strategy",
    constraints=delivered,
    prompt_injected=True,
)

# Log the propagation
log = log_constraint_propagation(
    session_id="session-123",
    source_phase="discovery",
    target_phase="strategy",
    generated_constraints=generated,
    delivered_constraints=delivered,
    acknowledgment=ack,
)

print(f"Status: {log.propagation_status}")  # 'success'
print(f"Generated: {log.constraints_generated}")
print(f"Delivered: {log.constraints_delivered}")
print(f"Acknowledged: {log.constraints_acknowledged}")
```

### Example 4: Batch Validation

```python
from agents.constraint_broadcaster import (
    ExecutionConstraint,
    validate_all_constraints,
)

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
        field="bad_field",
        value="test",
        source_section="test",
        source_claim_id="INVALID",  # ❌ Invalid format
        constraint_type="must_use",
    ),
]

valid_constraints, errors = validate_all_constraints(constraints)

print(f"Valid: {len(valid_constraints)}")  # 1
print(f"Invalid: {len(errors)}")  # 1
```

## Testing

Run constraint validation tests:

```bash
cd backend
pytest tests/unit/test_constraint_validation.py -v
```

### Test Coverage

The test suite covers:

1. **ConstraintPayload Validation** (12 tests)
   - Valid constraint creation
   - Default values
   - None value rejection
   - Claim ID format validation
   - Field name validation
   - Confidence-evidence tier matching
   - Confidence bounds

2. **LegalConstraint Validation** (4 tests)
   - Valid legal constraint creation
   - Regulation name case validation
   - Impact level validation
   - Field length validation

3. **Legal Constraint Extraction** (3 tests)
   - Valid extraction from preliminary_legal_scan
   - Malformed constraint handling
   - Empty regulations list

4. **ConstraintAcknowledgment** (4 tests)
   - Valid acknowledgment creation
   - Phase validation
   - Count-fields matching
   - Function integration

5. **ConstraintPropagationLog** (4 tests)
   - Valid log creation
   - Delivery count validation
   - Status-count matching
   - Function integration

6. **Integration Tests** (3 tests)
   - ExecutionConstraint validation
   - Invalid constraint rejection
   - Batch validation

**Total: 30 tests covering all validation scenarios**

## Integration with Existing Systems

### 1. Constraint Broadcaster

The constraint broadcaster (`agents/constraint_broadcaster.py`) now uses these validation functions before generating constraints for each phase.

### 2. Facilitator Agent

The facilitator (`agents/facilitator.py`) validates constraints before delivering them to agents and creates acknowledgments after successful delivery.

### 3. Output Validator

The output validator (`agents/output_validator.py`) uses constraint validation when checking agent outputs against constraints.

## Error Handling

All validation functions return tuples of `(valid_items, errors)`:

```python
valid_constraints, errors = validate_legal_constraints(scan)

if errors:
    logger.error(
        "legal_constraint_validation_failed",
        error_count=len(errors),
        errors=errors,
    )
    # Handle errors appropriately
else:
    # All constraints valid, proceed
    pass
```

## Monitoring and Logging

All validation functions log to structlog:

```python
logger.info(
    "constraint_propagation_logged",
    session_id="session-123",
    source="discovery",
    target="strategy",
    status="success",
    generated=3,
    delivered=3,
    acknowledged=3,
)
```

## Future Enhancements

1. **Constraint Persistence**: Store validated constraints in Supabase
2. **Constraint Replay**: Ability to replay constraint flow for debugging
3. **Constraint Metrics**: Track constraint violation rates per agent
4. **Constraint Suggestions**: AI-powered constraint generation from outputs
5. **Constraint Evolution**: Track how constraints change across iterations

## References

- Constraint Broadcaster: `backend/agents/constraint_broadcaster.py`
- Validation Schemas: `backend/models/constraint_schemas.py`
- Tests: `backend/tests/unit/test_constraint_validation.py`
- State Definition: `backend/agents/state.py`
- Output Validator: `backend/agents/output_validator.py`
