"""
Constraint Broadcaster — Generates constraints before parallel agent execution.

This module solves the problem of contradictions being detected post-execution
(in facilitator.py), which wastes compute. Instead, constraints are generated
BEFORE each phase runs, so downstream agents receive mandatory alignment
requirements upfront.

Key concepts:
- ExecutionConstraint: A constraint that downstream agents must respect
- Constraints are derived from upstream agent outputs with high evidence tiers
- Agents receive constraints in their prompts and must align their output
"""

from dataclasses import dataclass, asdict
from typing import Any, Optional

import structlog
from pydantic import ValidationError

from models.constraint_schemas import (
    ConstraintPayload,
    ConstraintType,
    EvidenceTier,
    LegalConstraint,
    ConstraintAcknowledgment,
    ConstraintPropagationLog,
)

logger = structlog.get_logger(__name__)


@dataclass
class ExecutionConstraint:
    """
    A constraint that downstream agents must respect.

    Attributes:
        field: The field being constrained (e.g., "market_size", "primary_customer")
        value: The constrained value (e.g., "$3.2B", "SMB Retailers")
        source_section: Which section this constraint comes from
        source_claim_id: The claim ID this constraint is based on
        constraint_type: Type of constraint:
            - "must_use": Agent must use this exact value
            - "must_not_exceed": Agent values cannot exceed this
            - "must_align": Agent output must be consistent with this
            - "must_reference": Agent must cite/reference this claim
        evidence_tier: The evidence tier of the source claim (E1-E5)
        confidence: Confidence level of the constraint (0.0-1.0)
        urgency: Enforcement level:
            - "required": Non-negotiable, violations trigger revision
            - "preferred": Should follow unless compelling reason to deviate
            - "guidance": Informational, agent can use judgment
    """
    field: str
    value: Any
    source_section: str
    source_claim_id: str
    constraint_type: str
    evidence_tier: str = "E2"  # Upgraded from E4 for stronger constraint enforcement
    confidence: float = 0.7  # Upgraded from 0.5 for stronger constraint enforcement
    urgency: str = "preferred"  # "required" | "preferred" | "guidance"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def _find_claim_id(state: dict[str, Any], keyword: str, section_prefix: str) -> str:
    """
    Find a claim ID that matches a keyword in the cross-reference index.

    Args:
        state: Current workflow state
        keyword: Keyword to search for in claim statements
        section_prefix: Section prefix to filter by (e.g., "MI", "BC")

    Returns:
        Matching claim ID or a default ID
    """
    cross_ref = state.get("cross_reference_index", {})
    claims = cross_ref.get("claims", [])

    keyword_lower = keyword.lower()
    for claim in claims:
        claim_id = claim.get("claim_id", "")
        if claim_id.startswith(section_prefix):
            statement = claim.get("statement", "").lower()
            if keyword_lower in statement:
                return claim_id

    # Return a default if not found
    return f"{section_prefix}-1"


def _extract_value_safely(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely extract a nested value from a dictionary.

    Args:
        data: Dictionary to extract from
        *keys: Sequence of keys to traverse
        default: Default value if not found

    Returns:
        Extracted value or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current


def generate_enterprise_constraints(state: dict[str, Any]) -> list[ExecutionConstraint]:
    """
    Generate constraints from enterprise context.

    Enterprise context provides organizational guidelines that all agents
    should respect. These constraints are prepended to phase constraints.

    Args:
        state: Current workflow state with enterprise_context field

    Returns:
        List of ExecutionConstraint objects from enterprise context
    """
    constraints: list[ExecutionConstraint] = []
    enterprise_context = state.get("enterprise_context", {})

    if not enterprise_context:
        return constraints

    claim_counter = 1

    # Regulatory constraints (E1, REQUIRED - non-negotiable)
    regulatory = enterprise_context.get("regulatory", {})
    if regulatory.get("frameworks"):
        for framework in regulatory["frameworks"]:
            constraints.append(ExecutionConstraint(
                field="compliance_framework",
                value=framework,
                source_section="enterprise_context",
                source_claim_id=f"EC-REG-{claim_counter}",
                constraint_type="must_use",
                evidence_tier="E1",
                confidence=1.0,
                urgency="required",  # Non-negotiable
            ))
            claim_counter += 1

    if regulatory.get("data_residency"):
        constraints.append(ExecutionConstraint(
            field="data_residency",
            value=regulatory["data_residency"],
            source_section="enterprise_context",
            source_claim_id=f"EC-REG-{claim_counter}",
            constraint_type="must_use",
            evidence_tier="E1",
            confidence=1.0,
            urgency="required",  # Non-negotiable
        ))
        claim_counter += 1

    # Strategy constraints (E1, REQUIRED)
    strategy = enterprise_context.get("strategy", {})
    if strategy.get("strategic_constraints"):
        for sc in strategy["strategic_constraints"]:
            constraints.append(ExecutionConstraint(
                field="strategic_alignment",
                value=sc,
                source_section="enterprise_context",
                source_claim_id=f"EC-STR-{claim_counter}",
                constraint_type="must_align",
                evidence_tier="E1",
                confidence=0.95,
                urgency="required",  # Strategic constraints are required
            ))
            claim_counter += 1

    if strategy.get("strategic_priorities"):
        constraints.append(ExecutionConstraint(
            field="strategic_priorities",
            value=", ".join(strategy["strategic_priorities"]),
            source_section="enterprise_context",
            source_claim_id=f"EC-STR-{claim_counter}",
            constraint_type="must_align",
            evidence_tier="E1",
            confidence=0.95,
            urgency="required",  # Strategic priorities are required
        ))
        claim_counter += 1

    # Technology constraints (E1-E2, PREFERRED - can deviate with justification)
    tech = enterprise_context.get("technology", {})
    if tech.get("cloud"):
        constraints.append(ExecutionConstraint(
            field="cloud_platform",
            value=tech["cloud"],
            source_section="enterprise_context",
            source_claim_id=f"EC-TECH-{claim_counter}",
            constraint_type="must_use",
            evidence_tier="E1",
            confidence=0.95,
            urgency="preferred",  # Tech can be deviated with justification
        ))
        claim_counter += 1

    if tech.get("primary_languages"):
        constraints.append(ExecutionConstraint(
            field="programming_languages",
            value=", ".join(tech["primary_languages"]),
            source_section="enterprise_context",
            source_claim_id=f"EC-TECH-{claim_counter}",
            constraint_type="must_use",
            evidence_tier="E1",
            confidence=0.9,
            urgency="preferred",
        ))
        claim_counter += 1

    if tech.get("databases"):
        constraints.append(ExecutionConstraint(
            field="database_technologies",
            value=", ".join(tech["databases"]),
            source_section="enterprise_context",
            source_claim_id=f"EC-TECH-{claim_counter}",
            constraint_type="must_use",
            evidence_tier="E1",
            confidence=0.9,
            urgency="preferred",
        ))
        claim_counter += 1

    if tech.get("deprecated_technologies"):
        constraints.append(ExecutionConstraint(
            field="deprecated_technologies",
            value=", ".join(tech["deprecated_technologies"]),
            source_section="enterprise_context",
            source_claim_id=f"EC-TECH-{claim_counter}",
            constraint_type="must_not_exceed",  # Using as "must_not_use"
            evidence_tier="E1",
            confidence=0.95,
            urgency="required",  # Deprecated tech is non-negotiable
        ))
        claim_counter += 1

    # Risk management constraints (E1, REQUIRED)
    risk = enterprise_context.get("risk_management", {})
    if risk.get("risk_appetite"):
        constraints.append(ExecutionConstraint(
            field="risk_appetite",
            value=risk["risk_appetite"],
            source_section="enterprise_context",
            source_claim_id=f"EC-RISK-{claim_counter}",
            constraint_type="must_align",
            evidence_tier="E1",
            confidence=0.95,
            urgency="required",  # Risk appetite is required
        ))
        claim_counter += 1

    logger.info(
        "enterprise_constraints_generated",
        session_id=state.get("session_id"),
        constraint_count=len(constraints),
    )

    return constraints


async def generate_phase_constraints(
    state: dict[str, Any],
    target_phase: str,
) -> list[ExecutionConstraint]:
    """
    Generate constraints for a phase based on completed upstream work.

    This function analyzes outputs from prior phases and extracts key facts
    that downstream agents must align with. Constraints are only generated
    from high-confidence, well-evidenced claims (E1-E3).

    Enterprise context constraints are prepended to ensure organizational
    guidelines are always considered first.

    Args:
        state: Current workflow state with completed agent outputs
        target_phase: The phase about to run ("strategy", "delivery", "design", "synthesis")

    Returns:
        List of ExecutionConstraint objects for the target phase
    """
    constraints: list[ExecutionConstraint] = []

    logger.info(
        "generating_phase_constraints",
        target_phase=target_phase,
        session_id=state.get("session_id"),
    )

    # Prepend enterprise context constraints (organizational guidelines)
    constraints.extend(generate_enterprise_constraints(state))

    if target_phase == "strategy":
        # Strategy phase receives constraints from Discovery outputs
        constraints.extend(_generate_strategy_constraints(state))

    elif target_phase == "delivery":
        # Delivery phase receives constraints from Discovery + Strategy outputs
        constraints.extend(_generate_delivery_constraints(state))

    elif target_phase == "design":
        # Design phase receives constraints from Delivery outputs
        constraints.extend(_generate_design_constraints(state))

    elif target_phase == "synthesis":
        # Synthesis phase receives constraints from all prior phases
        constraints.extend(_generate_synthesis_constraints(state))

    logger.info(
        "phase_constraints_generated",
        target_phase=target_phase,
        constraint_count=len(constraints),
        constraint_fields=[c.field for c in constraints],
    )

    return constraints


def _generate_strategy_constraints(state: dict[str, Any]) -> list[ExecutionConstraint]:
    """Generate constraints for Strategy phase from Discovery outputs."""
    constraints = []

    # Constraint from customer_research: Market size
    cr = state.get("customer_research", {})
    market_context = cr.get("market_context", {})
    tam = market_context.get("total_addressable_market")
    if tam:
        constraints.append(ExecutionConstraint(
            field="market_size",
            value=tam,
            source_section="customer_research",
            source_claim_id=_find_claim_id(state, "market", "MI"),
            constraint_type="must_use",
            evidence_tier="E2",  # Upgraded from E3 for stronger enforcement
            confidence=0.8,
        ))

    # Constraint from detailed_personas: Primary customer
    personas = state.get("detailed_personas", {})
    primary_persona = personas.get("primary_persona", {})
    if primary_persona:
        persona_name = primary_persona.get("name", "")
        archetype = primary_persona.get("archetype", "")
        if persona_name or archetype:
            constraints.append(ExecutionConstraint(
                field="primary_customer",
                value=f"{persona_name} ({archetype})" if archetype else persona_name,
                source_section="detailed_personas",
                source_claim_id=_find_claim_id(state, "persona", "CP"),
                constraint_type="must_align",
                evidence_tier="E4",
                confidence=0.6,
            ))

    # Constraint from competitive_analysis: Competitive positioning
    ca = state.get("competitive_analysis", {})
    direct_competitors = ca.get("direct_competitors", [])
    if direct_competitors:
        competitor_names = [c.get("name", "") for c in direct_competitors[:3] if isinstance(c, dict)]
        if competitor_names:
            constraints.append(ExecutionConstraint(
                field="competitive_landscape",
                value=", ".join(competitor_names),
                source_section="competitive_analysis",
                source_claim_id=_find_claim_id(state, "competitor", "CL"),
                constraint_type="must_reference",
                evidence_tier="E3",
                confidence=0.7,
            ))

    return constraints


def _generate_delivery_constraints(state: dict[str, Any]) -> list[ExecutionConstraint]:
    """Generate constraints for Delivery phase from Discovery + Strategy outputs."""
    constraints = []

    # Constraint from business_case: Pricing strategy
    bc = state.get("business_case", {})
    revenue_streams = bc.get("revenue_streams", [])
    if revenue_streams:
        pricing_info = revenue_streams[0] if revenue_streams else {}
        if isinstance(pricing_info, dict):
            price = pricing_info.get("price") or pricing_info.get("pricing")
            if price:
                constraints.append(ExecutionConstraint(
                    field="pricing_model",
                    value=str(price),
                    source_section="business_case",
                    source_claim_id=_find_claim_id(state, "pricing", "BC"),
                    constraint_type="must_use",
                    evidence_tier="E3",  # Upgraded from E4 for stronger enforcement
                    confidence=0.7,
                ))

    # Constraint from business_case: Value proposition
    value_prop = bc.get("unique_value_proposition") or bc.get("value_proposition")
    if value_prop:
        constraints.append(ExecutionConstraint(
            field="value_proposition",
            value=value_prop[:200] if len(str(value_prop)) > 200 else value_prop,
            source_section="business_case",
            source_claim_id=_find_claim_id(state, "value", "BC"),
            constraint_type="must_align",
            evidence_tier="E4",
            confidence=0.7,
        ))

    # Constraint from gtm_plan: Target segment
    gtm = state.get("gtm_plan", {})
    market_entry = gtm.get("market_entry_strategy", {})
    initial_segment = market_entry.get("initial_segment")
    if initial_segment:
        constraints.append(ExecutionConstraint(
            field="target_segment",
            value=initial_segment,
            source_section="gtm_plan",
            source_claim_id=_find_claim_id(state, "segment", "GM"),
            constraint_type="must_align",
            evidence_tier="E4",
            confidence=0.6,
        ))

    # Constraint from financial_model: Unit economics
    fm = state.get("financial_model", {})
    unit_economics = fm.get("unit_economics", {})
    ltv_cac = unit_economics.get("ltv_cac_ratio")
    if ltv_cac:
        constraints.append(ExecutionConstraint(
            field="unit_economics",
            value=f"LTV:CAC = {ltv_cac}",
            source_section="financial_model",
            source_claim_id=_find_claim_id(state, "ltv", "FM"),
            constraint_type="must_reference",
            evidence_tier="E4",
            confidence=0.5,
        ))

    # Include strategy constraints as well (additive)
    constraints.extend(_generate_strategy_constraints(state))

    return constraints


def _generate_design_constraints(state: dict[str, Any]) -> list[ExecutionConstraint]:
    """Generate constraints for Design phase from Delivery outputs."""
    constraints = []

    # Constraint from product_requirements: Core features
    prd = state.get("product_requirements", {})
    epics = prd.get("epics", [])
    if epics:
        epic_names = [e.get("name", "") for e in epics[:3] if isinstance(e, dict)]
        if epic_names:
            constraints.append(ExecutionConstraint(
                field="core_features",
                value=", ".join(epic_names),
                source_section="product_requirements",
                source_claim_id=_find_claim_id(state, "epic", "PR"),
                constraint_type="must_reference",
                evidence_tier="E4",
                confidence=0.7,
            ))

    # Constraint from product_requirements: Target users
    target_users = prd.get("target_users", [])
    if target_users:
        user_names = [u.get("name", "") if isinstance(u, dict) else str(u) for u in target_users[:2]]
        if user_names:
            constraints.append(ExecutionConstraint(
                field="target_users",
                value=", ".join(user_names),
                source_section="product_requirements",
                source_claim_id=_find_claim_id(state, "user", "PR"),
                constraint_type="must_align",
                evidence_tier="E4",
                confidence=0.6,
            ))

    # Constraint from technical_architecture: Tech stack
    ta = state.get("technical_architecture", {})
    stack = ta.get("recommended_stack", {})
    frontend = stack.get("frontend")
    if frontend:
        constraints.append(ExecutionConstraint(
            field="tech_stack_frontend",
            value=frontend,
            source_section="technical_architecture",
            source_claim_id=_find_claim_id(state, "stack", "TA"),
            constraint_type="must_use",
            evidence_tier="E4",
            confidence=0.8,
        ))

    return constraints


def _generate_synthesis_constraints(state: dict[str, Any]) -> list[ExecutionConstraint]:
    """Generate constraints for Synthesis phase from all prior phases."""
    constraints = []

    # Key metrics that must be consistent
    cr = state.get("customer_research", {})
    market_context = cr.get("market_context", {})
    tam = market_context.get("total_addressable_market")
    if tam:
        constraints.append(ExecutionConstraint(
            field="market_size",
            value=tam,
            source_section="customer_research",
            source_claim_id=_find_claim_id(state, "market", "MI"),
            constraint_type="must_use",
            evidence_tier="E2",  # Upgraded from E3 for stronger enforcement
            confidence=0.8,
        ))

    # Financial projections that must be consistent
    fm = state.get("financial_model", {})
    five_year = fm.get("five_year_projection", {})
    year_5 = five_year.get("year_5", {})
    if year_5.get("revenue"):
        constraints.append(ExecutionConstraint(
            field="projected_revenue_y5",
            value=year_5["revenue"],
            source_section="financial_model",
            source_claim_id=_find_claim_id(state, "revenue", "FM"),
            constraint_type="must_use",
            evidence_tier="E4",
            confidence=0.6,
        ))

    # Risk factors that must be acknowledged
    ra = state.get("risk_assessment", {})
    top_risks = ra.get("top_3_risks", [])
    if top_risks:
        risk_names = [r.get("name", "") if isinstance(r, dict) else str(r) for r in top_risks[:3]]
        if risk_names:
            constraints.append(ExecutionConstraint(
                field="key_risks",
                value=", ".join(risk_names),
                source_section="risk_assessment",
                source_claim_id=_find_claim_id(state, "risk", "RM"),
                constraint_type="must_reference",
                evidence_tier="E4",
                confidence=0.6,
            ))

    return constraints


def format_constraints_for_prompt(constraints: list[ExecutionConstraint]) -> str:
    """
    Format constraints for injection into agent prompts.

    Creates a visually prominent, structured block that agents MUST follow.
    Uses box drawing characters for maximum visibility.

    Args:
        constraints: List of ExecutionConstraint objects

    Returns:
        Formatted string ready for prompt injection, or empty string if no constraints
    """
    if not constraints:
        return ""

    # Separate by urgency
    required = [c for c in constraints if c.urgency == "required"]
    preferred = [c for c in constraints if c.urgency == "preferred"]
    guidance = [c for c in constraints if c.urgency == "guidance"]

    lines = [
        "╔══════════════════════════════════════════════════════════════════════════════╗",
        "║  MANDATORY ORGANIZATIONAL & EXECUTION CONSTRAINTS                             ║",
        "║  You MUST respect these. Violations will trigger revision.                    ║",
        "╚══════════════════════════════════════════════════════════════════════════════╝",
        "",
    ]

    # REQUIRED constraints (non-negotiable)
    if required:
        lines.append("### 🔴 REQUIRED (Non-negotiable - violations trigger revision)")
        lines.append("")
        for c in required:
            urgency_icon = "⛔" if c.constraint_type in ["must_use", "must_not_exceed"] else "⚠️"
            lines.append(f"{urgency_icon} **{c.field}**: {c.value}")
            lines.append(f"   └─ Type: {c.constraint_type} | Source: {c.source_section} ({c.source_claim_id}) [{c.evidence_tier}]")
        lines.append("")

    # PREFERRED constraints (should follow, can deviate with justification)
    if preferred:
        lines.append("### 🟡 PREFERRED (Follow unless compelling reason to deviate)")
        lines.append("")
        for c in preferred:
            lines.append(f"📌 **{c.field}**: {c.value}")
            lines.append(f"   └─ Type: {c.constraint_type} | Source: {c.source_section} ({c.source_claim_id}) [{c.evidence_tier}]")
        lines.append("")

    # GUIDANCE constraints (informational)
    if guidance:
        lines.append("### 🟢 GUIDANCE (Informational, use judgment)")
        lines.append("")
        for c in guidance:
            lines.append(f"💡 **{c.field}**: {c.value}")
            lines.append(f"   └─ Source: {c.source_section} ({c.source_claim_id})")
        lines.append("")

    lines.extend([
        "────────────────────────────────────────────────────────────────────────────────",
        "",
        "**COMPLIANCE REQUIREMENTS:**",
        "1. For REQUIRED constraints: You MUST comply. No exceptions.",
        "2. For PREFERRED constraints: Comply unless you have E1-E2 evidence to deviate.",
        "3. If deviating: Explicitly state the constraint, your deviation, and justification.",
        "",
        "**In your output, include a 'Constraint Compliance' section:**",
        "```",
        "## Constraint Compliance",
        "- ✓ [constraint_field]: Compliant - [how addressed]",
        "- ⚠ [constraint_field]: Deviation - [justification with evidence]",
        "```",
        "",
        "────────────────────────────────────────────────────────────────────────────────",
    ])

    return "\n".join(lines)


def validate_output_against_constraints(
    output: dict[str, Any],
    constraints: list[ExecutionConstraint],
) -> list[dict[str, str]]:
    """
    Validate an agent's output against constraints.

    This can be used post-generation to detect violations before they
    cause downstream issues.

    Args:
        output: The agent's output dictionary
        constraints: List of constraints to validate against

    Returns:
        List of violation dictionaries with field, expected, actual, and severity
    """
    violations = []

    for constraint in constraints:
        if constraint.constraint_type == "must_use":
            # Check if the field exists and matches
            actual = _extract_value_safely(output, constraint.field)
            if actual is None:
                violations.append({
                    "field": constraint.field,
                    "expected": constraint.value,
                    "actual": "NOT FOUND",
                    "severity": "high",
                    "constraint_type": constraint.constraint_type,
                })
            elif str(actual).lower() != str(constraint.value).lower():
                # Allow some flexibility for "must_use" - check if value is referenced
                if str(constraint.value).lower() not in str(actual).lower():
                    violations.append({
                        "field": constraint.field,
                        "expected": constraint.value,
                        "actual": actual,
                        "severity": "medium",
                        "constraint_type": constraint.constraint_type,
                    })

    return violations


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def validate_constraint_payload(constraint: ExecutionConstraint) -> tuple[bool, Optional[str]]:
    """
    Validate a constraint using Pydantic schema.

    Args:
        constraint: ExecutionConstraint to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Convert dataclass to dict
        constraint_dict = constraint.to_dict()

        # Map constraint_type to enum
        constraint_type_map = {
            "must_use": ConstraintType.MUST_USE,
            "must_align": ConstraintType.MUST_ALIGN,
            "must_reference": ConstraintType.MUST_REFERENCE,
            "must_not_exceed": ConstraintType.MUST_NOT_EXCEED,
        }

        # Map evidence_tier to enum
        evidence_tier_map = {
            "E1": EvidenceTier.E1,
            "E2": EvidenceTier.E2,
            "E3": EvidenceTier.E3,
            "E4": EvidenceTier.E4,
            "E5": EvidenceTier.E5,
        }

        # Create validated payload
        ConstraintPayload(
            field=constraint_dict["field"],
            value=constraint_dict["value"],
            source_section=constraint_dict["source_section"],
            source_claim_id=constraint_dict["source_claim_id"],
            constraint_type=constraint_type_map.get(
                constraint_dict["constraint_type"],
                ConstraintType.MUST_ALIGN,
            ),
            evidence_tier=evidence_tier_map.get(
                constraint_dict["evidence_tier"],
                EvidenceTier.E4,
            ),
            confidence=constraint_dict.get("confidence", 0.5),
        )

        return True, None

    except ValidationError as e:
        error_msg = f"Constraint validation failed: {str(e)}"
        logger.error(
            "constraint_validation_failed",
            field=constraint.field,
            error=str(e),
        )
        return False, error_msg


def validate_legal_constraints(
    preliminary_legal_scan: dict[str, Any]
) -> tuple[list[LegalConstraint], list[str]]:
    """
    Validate legal constraints from preliminary_legal_scan.

    Args:
        preliminary_legal_scan: Output from legal_preliminary agent

    Returns:
        Tuple of (valid_constraints, errors)
    """
    valid_constraints = []
    errors = []

    regulations = preliminary_legal_scan.get("applicable_regulations", [])

    for idx, reg in enumerate(regulations):
        try:
            # Extract regulation data
            legal_constraint = LegalConstraint(
                regulation_name=reg.get("name", f"Unknown Regulation {idx}"),
                requirement=reg.get("description", "No description provided"),
                applicability=reg.get("applicability", "Applicability not specified"),
                impact_level=reg.get("impact_level", "medium").lower(),
                compliance_timeline=reg.get(
                    "estimated_compliance_timeline",
                    "Timeline not specified"
                ),
                blocking=reg.get("impact_level", "").lower() == "high",
            )

            valid_constraints.append(legal_constraint)

        except ValidationError as e:
            error_msg = f"Legal constraint {idx} validation failed: {str(e)}"
            errors.append(error_msg)
            logger.error(
                "legal_constraint_validation_failed",
                index=idx,
                regulation=reg.get("name", "unknown"),
                error=str(e),
            )

    logger.info(
        "legal_constraints_validated",
        total=len(regulations),
        valid=len(valid_constraints),
        errors=len(errors),
    )

    return valid_constraints, errors


def create_constraint_acknowledgment(
    agent_name: str,
    phase: str,
    constraints: list[ExecutionConstraint],
    prompt_injected: bool = False,
) -> ConstraintAcknowledgment:
    """
    Create an acknowledgment that an agent received constraints.

    Args:
        agent_name: Name of the agent
        phase: Phase name
        constraints: List of constraints received
        prompt_injected: Whether constraints were injected into prompt

    Returns:
        ConstraintAcknowledgment object
    """
    try:
        acknowledgment = ConstraintAcknowledgment(
            agent_name=agent_name,
            phase=phase,
            constraints_received_count=len(constraints),
            constraint_fields=[c.field for c in constraints],
            prompt_injection_confirmed=prompt_injected,
        )

        logger.info(
            "constraint_acknowledgment_created",
            agent=agent_name,
            phase=phase,
            count=len(constraints),
            prompt_injected=prompt_injected,
        )

        return acknowledgment

    except ValidationError as e:
        logger.error(
            "constraint_acknowledgment_failed",
            agent=agent_name,
            phase=phase,
            error=str(e),
        )
        raise


def log_constraint_propagation(
    session_id: str,
    source_phase: str,
    target_phase: str,
    generated_constraints: list[ExecutionConstraint],
    delivered_constraints: list[ExecutionConstraint],
    acknowledgment: Optional[ConstraintAcknowledgment] = None,
    errors: Optional[list[str]] = None,
) -> ConstraintPropagationLog:
    """
    Log constraint propagation from one phase to another.

    Args:
        session_id: Session identifier
        source_phase: Phase generating constraints
        target_phase: Phase receiving constraints
        generated_constraints: Constraints generated
        delivered_constraints: Constraints successfully delivered
        acknowledgment: Optional acknowledgment from receiving agent
        errors: Optional list of errors

    Returns:
        ConstraintPropagationLog object
    """
    generated_count = len(generated_constraints)
    delivered_count = len(delivered_constraints)
    acknowledged_count = (
        acknowledgment.constraints_received_count if acknowledgment else 0
    )

    # Determine status
    if delivered_count == 0 and generated_count > 0:
        status = "failed"
    elif delivered_count < generated_count or acknowledged_count < delivered_count:
        status = "partial"
    else:
        status = "success"

    try:
        propagation_log = ConstraintPropagationLog(
            session_id=session_id,
            source_phase=source_phase,
            target_phase=target_phase,
            constraints_generated=generated_count,
            constraints_delivered=delivered_count,
            constraints_acknowledged=acknowledged_count,
            propagation_status=status,
            errors=errors or [],
        )

        logger.info(
            "constraint_propagation_logged",
            session_id=session_id,
            source=source_phase,
            target=target_phase,
            status=status,
            generated=generated_count,
            delivered=delivered_count,
            acknowledged=acknowledged_count,
        )

        return propagation_log

    except ValidationError as e:
        logger.error(
            "constraint_propagation_log_failed",
            session_id=session_id,
            error=str(e),
        )
        raise


def validate_all_constraints(
    constraints: list[ExecutionConstraint]
) -> tuple[list[ExecutionConstraint], list[str]]:
    """
    Validate all constraints in a list.

    Args:
        constraints: List of constraints to validate

    Returns:
        Tuple of (valid_constraints, error_messages)
    """
    valid_constraints = []
    errors = []

    for constraint in constraints:
        is_valid, error_msg = validate_constraint_payload(constraint)

        if is_valid:
            valid_constraints.append(constraint)
        else:
            errors.append(error_msg)

    logger.info(
        "constraints_batch_validated",
        total=len(constraints),
        valid=len(valid_constraints),
        invalid=len(errors),
    )

    return valid_constraints, errors
