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
    """
    field: str
    value: Any
    source_section: str
    source_claim_id: str
    constraint_type: str
    evidence_tier: str = "E4"
    confidence: float = 0.5

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


async def generate_phase_constraints(
    state: dict[str, Any],
    target_phase: str,
) -> list[ExecutionConstraint]:
    """
    Generate constraints for a phase based on completed upstream work.

    This function analyzes outputs from prior phases and extracts key facts
    that downstream agents must align with. Constraints are only generated
    from high-confidence, well-evidenced claims (E1-E3).

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
            evidence_tier="E3",
            confidence=0.7,
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
                    evidence_tier="E4",
                    confidence=0.6,
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
            evidence_tier="E3",
            confidence=0.7,
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

    Creates a clear, structured block that agents can understand and follow.
    Emphasizes that constraints are MANDATORY for consistency.

    Args:
        constraints: List of ExecutionConstraint objects

    Returns:
        Formatted string ready for prompt injection, or empty string if no constraints
    """
    if not constraints:
        return ""

    lines = [
        "## EXECUTION CONSTRAINTS (MANDATORY)",
        "",
        "You MUST align your output with these established constraints from upstream agents.",
        "These ensure consistency across the discovery pack. DO NOT contradict these values.",
        "",
    ]

    # Group constraints by type for clarity
    must_use = [c for c in constraints if c.constraint_type == "must_use"]
    must_align = [c for c in constraints if c.constraint_type == "must_align"]
    must_reference = [c for c in constraints if c.constraint_type == "must_reference"]
    must_not_exceed = [c for c in constraints if c.constraint_type == "must_not_exceed"]

    if must_use:
        lines.append("### MUST USE (exact values)")
        for c in must_use:
            lines.append(f"- **{c.field}**: {c.value}")
            lines.append(f"  Source: {c.source_section} ({c.source_claim_id}) [{c.evidence_tier}]")
        lines.append("")

    if must_align:
        lines.append("### MUST ALIGN WITH (directional consistency)")
        for c in must_align:
            lines.append(f"- **{c.field}**: {c.value}")
            lines.append(f"  Source: {c.source_section} ({c.source_claim_id}) [{c.evidence_tier}]")
        lines.append("")

    if must_reference:
        lines.append("### MUST REFERENCE (cite in output)")
        for c in must_reference:
            lines.append(f"- **{c.field}**: {c.value}")
            lines.append(f"  Source: {c.source_section} ({c.source_claim_id}) [{c.evidence_tier}]")
        lines.append("")

    if must_not_exceed:
        lines.append("### MUST NOT EXCEED (upper bounds)")
        for c in must_not_exceed:
            lines.append(f"- **{c.field}**: {c.value}")
            lines.append(f"  Source: {c.source_section} ({c.source_claim_id}) [{c.evidence_tier}]")
        lines.append("")

    lines.append("If you believe a constraint should be revised based on new information,")
    lines.append("explicitly note this in your output with justification.")

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
