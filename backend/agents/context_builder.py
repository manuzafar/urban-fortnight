"""
Context Builder — creates concise summaries for prompt injection.

This utility extracts key fields from agent outputs and formats them
as readable summaries for use by downstream agents. Handles truncation
to stay within token limits.
"""

import json
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


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
