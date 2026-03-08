"""
Context Builder — creates concise summaries for prompt injection.

This utility extracts key fields from agent outputs and formats them
as readable summaries for use by downstream agents. Handles truncation
to stay within token limits.

Enhanced with evidence-aware summaries that preserve evidence tier markers (E1-E5)
for downstream agents to treat claims appropriately based on their evidence quality.
"""

import json
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE-AWARE CONTEXT BUILDING (Quality Improvement System)
# ═══════════════════════════════════════════════════════════════════════════════

# Map state field names to section prefixes for claim lookup
FIELD_TO_SECTION_PREFIX: dict[str, str] = {
    "customer_research": "MI",
    "competitive_analysis": "CL",
    "detailed_personas": "CP",
    "business_case": "BC",
    "gtm_plan": "GM",
    "financial_model": "FM",
    "product_requirements": "PR",
    "technical_architecture": "TA",
    "legal_regulatory_review": "RC",
    "risk_assessment": "RM",
    "executive_summary": "ES",
    "stakeholder_views": "SV",
    "validation_playbook": "VP",
}


def build_evidence_aware_summary(
    state: dict[str, Any],
    source_sections: list[str],
    max_chars: int = 6000,
) -> str:
    """
    Build summary that preserves evidence tier markers.

    This function extracts claims from the cross_reference_index and formats them
    into categorized sections based on evidence quality. This ensures downstream
    agents treat claims appropriately - verified facts should be used as constraints,
    while hypotheses should be flagged for validation.

    Output format:
    ## VERIFIED FACTS (E1-E2)
    - [E2] Market size is $3.2B (MI-3) [source: usda.gov]
    - [E1] 67% of vendors want mobile payments (MI-7) [primary research]

    ## INDUSTRY DATA (E3)
    - [E3] Industry growing 5% annually (MI-12)

    ## HYPOTHESES (E4-E5)
    - [E4] Price sensitivity is high (MI-15) - NEEDS VALIDATION

    Args:
        state: Current workflow state containing cross_reference_index
        source_sections: List of state field names to include (e.g., ["customer_research", "business_case"])
        max_chars: Maximum characters for the summary

    Returns:
        Formatted summary string with evidence tiers preserved
    """
    cross_ref = state.get("cross_reference_index", {})
    claims = cross_ref.get("claims", [])

    if not claims:
        return "No claims available yet in cross-reference index."

    # Convert source_sections (field names) to prefixes for matching
    source_prefixes = set()
    for section in source_sections:
        if section in FIELD_TO_SECTION_PREFIX:
            source_prefixes.add(FIELD_TO_SECTION_PREFIX[section])
        else:
            # Try to match by section name directly (for flexibility)
            source_prefixes.add(section.upper()[:2])

    verified: list[str] = []
    industry: list[str] = []
    hypotheses: list[str] = []

    for claim in claims:
        claim_id = claim.get("claim_id", "")
        # Extract prefix from claim_id (e.g., "MI-3" -> "MI")
        prefix = claim_id.split("-")[0] if "-" in claim_id else ""

        # Filter to only include claims from requested sections
        if source_prefixes and prefix not in source_prefixes:
            continue

        tier = claim.get("evidence_tier", "E5")
        statement = claim.get("statement", "")
        source = claim.get("source")
        confidence = claim.get("confidence", 0.5)

        # Format the claim with evidence tier marker
        formatted = f"[{tier}] {statement} ({claim_id})"
        if source:
            # Truncate long sources
            source_display = source[:50] + "..." if len(source) > 50 else source
            formatted += f" [source: {source_display}]"

        # Add confidence indicator for lower confidence claims
        if confidence < 0.5:
            formatted += f" (confidence: {confidence:.0%})"

        # Categorize by evidence tier
        if tier in ["E1", "E2"]:
            verified.append(formatted)
        elif tier == "E3":
            industry.append(formatted)
        else:  # E4, E5
            hypotheses.append(formatted + " - NEEDS VALIDATION")

    # Build output sections
    sections = []

    if verified:
        verified_section = "## VERIFIED FACTS (E1-E2)\n"
        verified_section += "These are established facts that should be treated as constraints:\n"
        verified_section += "\n".join(f"- {v}" for v in verified[:15])
        sections.append(verified_section)

    if industry:
        industry_section = "## INDUSTRY DATA (E3)\n"
        industry_section += "Industry-level data from published sources:\n"
        industry_section += "\n".join(f"- {i}" for i in industry[:10])
        sections.append(industry_section)

    if hypotheses:
        hypotheses_section = "## HYPOTHESES (E4-E5)\n"
        hypotheses_section += "These are reasoned conclusions or assumptions that need validation:\n"
        hypotheses_section += "\n".join(f"- {h}" for h in hypotheses[:10])
        sections.append(hypotheses_section)

    if not sections:
        return f"No claims found for sections: {', '.join(source_sections)}"

    result = "\n\n".join(sections)
    return result[:max_chars]


def build_evidence_context_for_phase(
    state: dict[str, Any],
    target_phase: str,
    max_chars: int = 6000,
) -> str:
    """
    Build evidence-aware context for a specific phase.

    This automatically determines which upstream sections to include based on
    the target phase, ensuring agents receive properly categorized evidence.

    Args:
        state: Current workflow state
        target_phase: One of "strategy", "delivery", "design", "synthesis"
        max_chars: Maximum characters for the summary

    Returns:
        Formatted evidence-aware summary for the phase
    """
    # Define which upstream sections each phase needs
    phase_dependencies: dict[str, list[str]] = {
        "strategy": [
            "customer_research",
            "competitive_analysis",
            "detailed_personas",
        ],
        "delivery": [
            "customer_research",
            "competitive_analysis",
            "detailed_personas",
            "business_case",
            "gtm_plan",
            "financial_model",
        ],
        "design": [
            "product_requirements",
            "business_case",
            "detailed_personas",
        ],
        "synthesis": [
            "customer_research",
            "competitive_analysis",
            "detailed_personas",
            "business_case",
            "gtm_plan",
            "financial_model",
            "product_requirements",
            "technical_architecture",
            "legal_regulatory_review",
            "risk_assessment",
        ],
    }

    source_sections = phase_dependencies.get(target_phase, [])
    if not source_sections:
        logger.warning("unknown_phase_for_evidence_context", phase=target_phase)
        return ""

    return build_evidence_aware_summary(state, source_sections, max_chars)


def get_high_priority_claims_for_validation(
    state: dict[str, Any],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Get the highest priority claims that need validation.

    Prioritizes claims that:
    1. Are E4/E5 (hypotheses/assumptions)
    2. Have many dependent claims
    3. Have low confidence

    Args:
        state: Current workflow state
        limit: Maximum number of claims to return

    Returns:
        List of claim dictionaries sorted by validation priority
    """
    cross_ref = state.get("cross_reference_index", {})
    claims = cross_ref.get("claims", [])

    # Filter to E4/E5 claims
    e4_e5_claims = [
        c for c in claims
        if c.get("evidence_tier") in ("E4", "E5")
    ]

    if not e4_e5_claims:
        return []

    # Count how many claims depend on each claim
    def count_dependents(claim: dict) -> int:
        claim_id = claim.get("claim_id")
        return sum(
            1 for c in claims
            if claim_id in c.get("depends_on", [])
        )

    # Sort by: number of dependents (desc), confidence (asc), validation effort (asc)
    effort_order = {"quick": 1, "moderate": 2, "significant": 3}

    def sort_key(c: dict) -> tuple:
        dependents = count_dependents(c)
        confidence = c.get("confidence", 1.0)
        effort = effort_order.get(c.get("validation_effort", "moderate"), 2)
        return (-dependents, confidence, effort)

    sorted_claims = sorted(e4_e5_claims, key=sort_key)

    return sorted_claims[:limit]


# Field mappings for each section - which keys to extract
SUMMARY_FIELDS: dict[str, list[str]] = {
    # Discovery Phase
    "customer_research": [
        "market_definition",
        "market_size",
        "tam_estimate",
        "sam_estimate",
        "som_estimate",
        "pain_signals",
        "why_now",
        "key_assumptions",
    ],
    "competitive_analysis": [
        "direct_competitors",
        "indirect_competitors",
        "competitive_moats",
        "market_dynamics",
        "strategic_recommendations",
    ],
    "detailed_personas": [
        "primary_persona",
        "secondary_personas",
        "anti_persona",
        "persona_insights",
    ],

    # Strategy Phase
    "business_case": [
        "value_proposition",
        "unique_value_proposition",
        "revenue_streams",
        "pricing_strategy",
        "cost_structure",
        "lean_canvas",
        "financial_projections",
    ],
    "gtm_plan": [
        "market_entry_strategy",
        "channel_strategy",
        "launch_plan",
        "growth_tactics",
        "key_metrics_to_track",
    ],
    "financial_model": [
        "revenue_model",
        "cost_structure",
        "unit_economics",
        "projections",
        "funding_requirements",
        "scenario_analysis",
    ],

    # Delivery Phase
    "product_requirements": [
        "product_name",
        "vision_statement",
        "problem_statement",
        "target_users",
        "epics",
        "functional_requirements",
        "non_functional_requirements",
        "success_metrics",
    ],
    "technical_architecture": [
        "architecture_style",
        "technology_stack",
        "system_components",
        "data_architecture",
        "security_architecture",
        "deployment_strategy",
    ],
    "legal_regulatory_review": [
        "applicable_regulations",
        "compliance_requirements",
        "licensing_requirements",
        "data_protection",
        "overall_risk_assessment",
    ],
    "risk_assessment": [
        "risk_matrix",
        "risk_summary",
        "top_3_risks",
        "risk_appetite_recommendation",
    ],

    # Synthesis Phase
    "stakeholder_views": [
        "cfo_view",
        "ciso_view",
        "arb_view",
        "vp_product_view",
    ],
    "validation_playbook": [
        "experiments",
        "validation_priorities",
        "success_criteria",
    ],

    # Preliminary outputs
    "preliminary_legal_scan": [
        "regulatory_domains",
        "jurisdiction_notes",
        "blocking_issues",
        "initial_risk_level",
    ],
    "research_plan": [
        "domain_classification",
        "key_research_questions",
        "competitor_focus_areas",
        "regulatory_domains",
        "financial_benchmarks",
    ],
}


def build_context_summary(
    state: dict[str, Any],
    field: str,
    max_chars: int = 4000,
) -> str:
    """
    Extract key fields and format as readable summary.

    Args:
        state: Current workflow state
        field: State field to summarize (e.g., "customer_research")
        max_chars: Maximum characters to return

    Returns:
        Formatted summary string or "Not yet available" if empty
    """
    data = state.get(field)
    if not data:
        return f"{_field_to_label(field)} not yet available."

    # Get the fields to extract
    fields_to_extract = SUMMARY_FIELDS.get(field, [])

    if not fields_to_extract:
        # If no specific fields defined, just dump the whole thing
        summary = json.dumps(data, indent=2, default=str)
        return _truncate(summary, max_chars)

    # Build summary from specific fields
    summary_parts = []
    for key in fields_to_extract:
        if key in data and data[key]:
            value = data[key]
            formatted = _format_value(key, value)
            if formatted:
                summary_parts.append(f"**{_key_to_label(key)}:**\n{formatted}")

    if not summary_parts:
        # Fallback to full dump if no specific fields found
        summary = json.dumps(data, indent=2, default=str)
        return _truncate(summary, max_chars)

    summary = "\n\n".join(summary_parts)
    return _truncate(summary, max_chars)


def build_full_pack_summary(
    state: dict[str, Any],
    max_chars: int = 12000,
) -> str:
    """
    Build summary across ALL sections for synthesis agents.

    Args:
        state: Current workflow state
        max_chars: Maximum total characters

    Returns:
        Comprehensive summary of all available sections
    """
    sections = [
        ("Market Intelligence", "customer_research"),
        ("Competitive Landscape", "competitive_analysis"),
        ("Customer Personas", "detailed_personas"),
        ("Business Case", "business_case"),
        ("Go-to-Market", "gtm_plan"),
        ("Financial Model", "financial_model"),
        ("Product Requirements", "product_requirements"),
        ("Technical Architecture", "technical_architecture"),
        ("Regulatory & Compliance", "legal_regulatory_review"),
        ("Risk Assessment", "risk_assessment"),
    ]

    # Calculate per-section budget
    available_sections = [s for s in sections if state.get(s[1])]
    if not available_sections:
        return "No sections available yet."

    per_section_chars = max_chars // len(available_sections)

    summary_parts = []
    for label, field in sections:
        if state.get(field):
            section_summary = build_context_summary(state, field, per_section_chars)
            summary_parts.append(f"## {label}\n{section_summary}")

    return "\n\n---\n\n".join(summary_parts)


def build_cross_reference_summary(
    state: dict[str, Any],
    max_chars: int = 4000,
) -> str:
    """
    Build evidence snapshot for Validation Playbook and Exec Summary.

    Args:
        state: Current workflow state
        max_chars: Maximum characters

    Returns:
        Summary of cross-reference index with evidence statistics
    """
    index = state.get("cross_reference_index")
    if not index:
        return "Cross-reference index not yet available."

    parts = []

    # Overall statistics
    total = index.get("total_claims", 0)
    score = index.get("evidence_score", 0.0)
    parts.append(f"**Total Claims:** {total}")
    parts.append(f"**Evidence Score:** {score:.2f} (higher is better)")

    # Tier distribution
    tier_dist = index.get("tier_distribution", {})
    if tier_dist:
        tier_lines = []
        tier_labels = {
            "E1": "Primary Research",
            "E2": "Verified Source",
            "E3": "Industry Data",
            "E4": "Hypothesis",
            "E5": "Assumption",
        }
        for tier, count in sorted(tier_dist.items()):
            label = tier_labels.get(tier, tier)
            tier_lines.append(f"  - {tier} ({label}): {count}")
        parts.append("**Evidence Tier Distribution:**\n" + "\n".join(tier_lines))

    # Unresolved dependencies
    unresolved = index.get("unresolved_dependencies", [])
    if unresolved:
        parts.append(f"**Unresolved Dependencies:** {len(unresolved)}")

    # Top validation priorities
    claims = index.get("claims", [])
    e4_e5_claims = [
        c for c in claims
        if c.get("evidence_tier") in ("E4", "E5")
    ]

    if e4_e5_claims:
        # Sort by number of claims that depend on them
        def count_dependents(claim: dict) -> int:
            return sum(
                1 for c in claims
                if claim.get("claim_id") in c.get("depends_on", [])
            )

        sorted_claims = sorted(
            e4_e5_claims,
            key=lambda c: (-count_dependents(c), c.get("confidence", 1.0)),
        )[:5]

        priority_lines = []
        for c in sorted_claims:
            cid = c.get("claim_id", "?")
            tier = c.get("evidence_tier", "?")
            statement = c.get("statement", "")[:80]
            method = c.get("validation_method", "TBD")
            priority_lines.append(f"  - [{cid}] ({tier}) {statement}... → {method}")

        parts.append("**Top Validation Priorities:**\n" + "\n".join(priority_lines))

    summary = "\n\n".join(parts)
    return _truncate(summary, max_chars)


def build_upstream_context(
    state: dict[str, Any],
    current_agent: str,
) -> dict[str, str]:
    """
    Build context from all relevant upstream agents.

    Args:
        state: Current workflow state
        current_agent: Name of the agent requesting context

    Returns:
        Dict of context variable names to summaries
    """
    # Define which upstream outputs each agent needs
    agent_dependencies: dict[str, list[tuple[str, str, int]]] = {
        "Business Case": [
            ("market_intelligence_summary", "customer_research", 3000),
            ("competitive_landscape_summary", "competitive_analysis", 2000),
            ("personas_summary", "detailed_personas", 2000),
        ],
        "Go-to-Market": [
            ("personas_summary", "detailed_personas", 2000),
            ("business_case_summary", "business_case", 3000),
            ("competitive_landscape_summary", "competitive_analysis", 2000),
        ],
        "Financial Model": [
            ("business_case_summary", "business_case", 3000),
            ("gtm_summary", "gtm_plan", 2000),
        ],
        "Product Requirements": [
            ("market_intelligence_summary", "customer_research", 2000),
            ("personas_summary", "detailed_personas", 2000),
            ("business_case_summary", "business_case", 2000),
        ],
        "Technical Architecture": [
            ("product_requirements_summary", "product_requirements", 3000),
            ("business_case_summary", "business_case", 2000),
        ],
        "Regulatory & Compliance": [
            ("product_requirements_summary", "product_requirements", 2000),
            ("technical_architecture_summary", "technical_architecture", 2000),
            ("preliminary_scan", "preliminary_legal_scan", 1000),
        ],
        "Risk Assessment": [
            ("full_pack_summary", None, 6000),  # Special case
        ],
        "Stakeholder Views": [
            ("full_pack_summary", None, 8000),
            ("cross_reference_summary", None, 3000),
        ],
        "Validation Playbook": [
            ("cross_reference_summary", None, 4000),
            ("risk_summary", "risk_assessment", 2000),
        ],
        "Executive Summary": [
            ("full_pack_summary", None, 10000),
            ("cross_reference_summary", None, 3000),
            ("stakeholder_summary", "stakeholder_views", 2000),
            ("validation_summary", "validation_playbook", 2000),
        ],
    }

    dependencies = agent_dependencies.get(current_agent, [])
    context = {}

    for var_name, field, max_chars in dependencies:
        if field is None:
            # Special builders
            if var_name == "full_pack_summary":
                context[var_name] = build_full_pack_summary(state, max_chars)
            elif var_name == "cross_reference_summary":
                context[var_name] = build_cross_reference_summary(state, max_chars)
        else:
            context[var_name] = build_context_summary(state, field, max_chars)

    return context


def _truncate(text: str, max_chars: int) -> str:
    """Truncate text to max_chars with ellipsis."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 30] + "\n\n... [truncated for brevity]"


def _field_to_label(field: str) -> str:
    """Convert field name to human-readable label."""
    labels = {
        "customer_research": "Market Intelligence",
        "competitive_analysis": "Competitive Landscape",
        "detailed_personas": "Customer Personas",
        "business_case": "Business Case",
        "gtm_plan": "Go-to-Market Strategy",
        "financial_model": "Financial Model",
        "product_requirements": "Product Requirements",
        "technical_architecture": "Technical Architecture",
        "legal_regulatory_review": "Regulatory & Compliance",
        "risk_assessment": "Risk Assessment",
        "preliminary_legal_scan": "Preliminary Legal Scan",
        "research_plan": "Research Plan",
    }
    return labels.get(field, field.replace("_", " ").title())


def _key_to_label(key: str) -> str:
    """Convert key name to human-readable label."""
    return key.replace("_", " ").title()


def _format_value(key: str, value: Any) -> str:
    """Format a value for summary display."""
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, list):
        if not value:
            return ""
        if len(value) <= 5:
            # Short list - format inline or as bullets
            if isinstance(value[0], str):
                return "\n".join(f"  - {item}" for item in value)
            else:
                return json.dumps(value, indent=2, default=str)
        else:
            # Long list - summarize
            summary = json.dumps(value[:3], indent=2, default=str)
            return f"{summary}\n  ... and {len(value) - 3} more items"

    if isinstance(value, dict):
        # For dicts, extract key info
        return json.dumps(value, indent=2, default=str)

    return str(value)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTERPRISE CONTEXT PROMPT BUILDING
# ═══════════════════════════════════════════════════════════════════════════════


def build_enterprise_context_prompt(
    enterprise_context: dict[str, Any],
    max_chars: int = 4000,
) -> str:
    """
    Format enterprise context as soft guidance for agents.

    This creates a structured prompt section that agents can understand
    and follow, while making clear these are organizational guidelines
    that can be deviated from with justification.

    Args:
        enterprise_context: Merged enterprise context dict
        max_chars: Maximum characters for the prompt

    Returns:
        Formatted string ready for prompt injection
    """
    if not enterprise_context:
        return ""

    lines = [
        "╔══════════════════════════════════════════════════════════════════════════════╗",
        "║  ORGANIZATIONAL CONTEXT (Guidelines from Enterprise Context)                 ║",
        "║  Align with these unless there's a compelling reason to deviate.             ║",
        "╚══════════════════════════════════════════════════════════════════════════════╝",
        "",
    ]

    # Add company info
    company = enterprise_context.get("company")
    if company:
        lines.append(f"**Company:** {company}")
        industry = enterprise_context.get("industry")
        if industry:
            lines.append(f"**Industry:** {industry}")
        lines.append("")

    # Regulatory section (non-negotiable)
    regulatory = enterprise_context.get("regulatory", {})
    if regulatory:
        has_content = False
        reg_lines = ["### Compliance Requirements (Non-negotiable)"]

        if regulatory.get("frameworks"):
            reg_lines.append(f"- **Frameworks:** {', '.join(regulatory['frameworks'])}")
            has_content = True
        if regulatory.get("jurisdictions"):
            reg_lines.append(f"- **Jurisdictions:** {', '.join(regulatory['jurisdictions'])}")
            has_content = True
        if regulatory.get("data_residency"):
            reg_lines.append(f"- **Data Residency:** {regulatory['data_residency']}")
            has_content = True

        if has_content:
            lines.extend(reg_lines)
            lines.append("")

    # Strategy section
    strategy = enterprise_context.get("strategy", {})
    if strategy:
        has_content = False
        strat_lines = ["### Strategic Alignment"]

        if strategy.get("strategic_priorities"):
            strat_lines.append(f"- **Priorities:** {', '.join(strategy['strategic_priorities'])}")
            has_content = True
        if strategy.get("strategic_constraints"):
            for sc in strategy["strategic_constraints"]:
                strat_lines.append(f"- **Constraint:** {sc}")
            has_content = True
        if strategy.get("innovation_stance"):
            strat_lines.append(f"- **Innovation Stance:** {strategy['innovation_stance']}")
            has_content = True
        if strategy.get("investment_thesis"):
            strat_lines.append(f"- **Investment Thesis:** {strategy['investment_thesis']}")
            has_content = True

        if has_content:
            lines.extend(strat_lines)
            lines.append("")

    # Technology section
    tech = enterprise_context.get("technology", {})
    if tech:
        has_content = False
        tech_lines = ["### Technology Standards"]

        if tech.get("cloud"):
            tech_lines.append(f"- **Cloud Platform:** {tech['cloud']}")
            has_content = True
        if tech.get("primary_languages"):
            tech_lines.append(f"- **Languages:** {', '.join(tech['primary_languages'])}")
            has_content = True
        if tech.get("databases"):
            tech_lines.append(f"- **Databases:** {', '.join(tech['databases'])}")
            has_content = True
        if tech.get("infrastructure"):
            tech_lines.append(f"- **Infrastructure:** {', '.join(tech['infrastructure'])}")
            has_content = True
        if tech.get("deprecated_technologies"):
            tech_lines.append(f"- **Deprecated (avoid):** {', '.join(tech['deprecated_technologies'])}")
            has_content = True
        if tech.get("technical_constraints"):
            for tc in tech["technical_constraints"]:
                tech_lines.append(f"- **Tech Constraint:** {tc}")
            has_content = True

        if has_content:
            lines.extend(tech_lines)
            lines.append("")

    # Risk management section
    risk = enterprise_context.get("risk_management", {})
    if risk:
        has_content = False
        risk_lines = ["### Risk Management"]

        if risk.get("risk_appetite"):
            risk_lines.append(f"- **Risk Appetite:** {risk['risk_appetite']}")
            has_content = True
        if risk.get("risk_categories"):
            risk_lines.append(f"- **Key Risk Categories:** {', '.join(risk['risk_categories'])}")
            has_content = True

        if has_content:
            lines.extend(risk_lines)
            lines.append("")

    # Organization section
    org = enterprise_context.get("organization", {})
    if org:
        has_content = False
        org_lines = ["### Organizational Context"]

        if org.get("delivery_model"):
            org_lines.append(f"- **Delivery Model:** {org['delivery_model']}")
            has_content = True
        if org.get("budget_cycle"):
            org_lines.append(f"- **Budget Cycle:** {org['budget_cycle']}")
            has_content = True
        if org.get("approval_process"):
            org_lines.append(f"- **Approval Process:** {org['approval_process']}")
            has_content = True

        if has_content:
            lines.extend(org_lines)
            lines.append("")

    # Add compliance footer
    lines.extend([
        "────────────────────────────────────────────────────────────────────────────────",
        "",
        "**COMPLIANCE REQUIREMENTS:**",
        "1. 🔴 Regulatory requirements (frameworks, jurisdictions, data residency) are NON-NEGOTIABLE",
        "2. 🟡 Strategic constraints should be followed unless you have strong evidence to deviate",
        "3. 🟢 Technology standards are preferred but can be justified if needed",
        "",
        "**In your output, acknowledge compliance:**",
        "```",
        "## Organizational Alignment",
        "- ✓ [requirement]: Compliant - [how addressed]",
        "- ⚠ [requirement]: Deviation - [justification]",
        "```",
        "────────────────────────────────────────────────────────────────────────────────",
    ])

    result = "\n".join(lines)
    if len(result) > max_chars:
        return result[:max_chars - 30] + "\n\n... [truncated]"
    return result


def get_enterprise_context_for_agent(
    state: dict[str, Any],
    agent_name: str,
) -> str:
    """
    Get the enterprise context prompt for a specific agent.

    Uses pre-formatted prompt if available in state, otherwise builds one.

    Args:
        state: Current workflow state
        agent_name: Name of the agent requesting context

    Returns:
        Formatted enterprise context prompt
    """
    # Use pre-formatted prompt if available
    if state.get("enterprise_context_prompt"):
        return state["enterprise_context_prompt"]

    # Otherwise build from enterprise_context
    enterprise_context = state.get("enterprise_context", {})
    if not enterprise_context:
        return ""

    return build_enterprise_context_prompt(enterprise_context)
