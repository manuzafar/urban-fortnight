"""
Helper utilities for the Product Discovery Multi-Agent System.

This module provides:
- Session ID generation
- Logging configuration
- Input sanitization
- Inception pack building
"""

import logging
import re
import sys
import uuid
from datetime import datetime
from typing import Any

import structlog

from config import settings


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION ID GENERATION
# ═══════════════════════════════════════════════════════════════════════════════


def generate_session_id() -> str:
    """
    Generate a unique session ID.

    Format: disc_{timestamp}_{uuid}
    Example: disc_20240115_a1b2c3d4

    Returns:
        str: Unique session identifier.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:8]
    return f"disc_{timestamp}_{unique_id}"


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Sets up structlog with appropriate processors for either
    JSON output (production) or console output (development).
    """
    # Determine log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Common processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    if settings.log_json_format:
        # JSON format for production
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Pretty console output for development
        structlog.configure(
            processors=shared_processors
            + [
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Also configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SANITIZATION
# ═══════════════════════════════════════════════════════════════════════════════


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input text.

    - Strips leading/trailing whitespace
    - Removes control characters
    - Truncates to max length
    - Normalizes whitespace

    Args:
        text: Input text to sanitize.
        max_length: Maximum allowed length.

    Returns:
        str: Sanitized text.
    """
    if not text:
        return ""

    # Strip whitespace
    text = text.strip()

    # Remove control characters (except newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # Normalize whitespace (multiple spaces to single)
    text = re.sub(r" +", " ", text)

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    return text


def sanitize_constraints(constraints: list[str] | None) -> list[str] | None:
    """
    Sanitize a list of constraint strings.

    Args:
        constraints: List of constraints to sanitize.

    Returns:
        list[str] | None: Sanitized constraints or None.
    """
    if not constraints:
        return None

    sanitized = [sanitize_input(c, max_length=500) for c in constraints]
    return [c for c in sanitized if c]  # Remove empty strings


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATTING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        str: Formatted duration (e.g., "2m 30s", "45s").
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION TRANSFORMATIONS (Backend → Frontend)
# ═══════════════════════════════════════════════════════════════════════════════


def _transform_gtm_plan(gtm_plan: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Transform backend GTM plan to frontend GTM strategy format.

    Backend produces: market_entry_strategy, channel_strategy, launch_plan, growth_tactics
    Frontend expects: positioning_statement, launch_phases, channel_strategy[], messaging_framework
    """
    if not gtm_plan:
        return None

    transformed = {}

    # Map market_entry_strategy to positioning_statement
    market_entry = gtm_plan.get("market_entry_strategy", {}) or {}
    beachhead = market_entry.get("beachhead_market", "")
    approach = market_entry.get("approach", "")
    initial_segment = market_entry.get("initial_segment", "")
    if beachhead or approach or initial_segment:
        parts = []
        if initial_segment:
            parts.append(f"Targeting {initial_segment}")
        if approach:
            parts.append(f"through {approach} approach")
        if beachhead:
            parts.append(f"starting with {beachhead}")
        transformed["positioning_statement"] = " ".join(parts) if parts else ""

    # Map launch_plan.phases to launch_phases (rename fields)
    launch_plan = gtm_plan.get("launch_plan", {}) or {}
    phases = launch_plan.get("phases", []) or []
    transformed["launch_phases"] = [
        {
            "phase_name": phase.get("phase", ""),
            "duration": phase.get("duration", ""),
            "objectives": phase.get("goals", []) or [],
            "key_activities": phase.get("key_activities", []) or [],
            "success_metrics": phase.get("success_metrics", []) or [],
        }
        for phase in phases
    ]

    # Map channel_strategy.primary_channels to channel_strategy array
    channel_strategy = gtm_plan.get("channel_strategy", {}) or {}
    primary_channels = channel_strategy.get("primary_channels", []) or []
    transformed["channel_strategy"] = [
        {
            "channel": ch.get("channel", ""),
            "purpose": ch.get("role", ""),
            "tactics": [],
            "budget_allocation": "",
            "expected_roi": ch.get("expected_cac", ""),
        }
        for ch in primary_channels
    ]

    # Map target segments from expansion path or initial segment
    expansion_path = market_entry.get("expansion_path", []) or []
    transformed["target_segments"] = (
        expansion_path if expansion_path else ([initial_segment] if initial_segment else [])
    )

    # Create messaging_framework placeholder
    transformed["messaging_framework"] = {
        "headline": "",
        "subheadline": "",
        "key_benefits": [],
        "proof_points": [],
    }

    # Pass through growth_tactics and partnership_opportunities
    if gtm_plan.get("growth_tactics"):
        transformed["growth_tactics"] = gtm_plan["growth_tactics"]
    if gtm_plan.get("partnership_opportunities"):
        transformed["partnership_opportunities"] = gtm_plan["partnership_opportunities"]

    return transformed


def _transform_financial_model(
    financial_model: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Transform backend financial model to frontend format.

    Backend produces complex nested objects, frontend expects simpler structures.
    Key transformations:
    - funding_requirements: object → string
    - unit_economics: object → array of metrics
    - sensitivity_analysis: nested objects → simple strings
    - projections: monthly/quarterly → simplified array
    """
    if not financial_model:
        return None

    transformed = {}

    # Pass through summary as-is (ensure it's always a string)
    transformed["summary"] = financial_model.get("summary", "") or ""

    # Transform unit_economics from object to array
    unit_econ = financial_model.get("unit_economics", {}) or {}
    if unit_econ:
        transformed["unit_economics"] = [
            {
                "metric": "LTV",
                "value": f"${unit_econ.get('ltv', 0):,}",
                "benchmark": "Industry avg",
                "assessment": unit_econ.get("assessment", ""),
            },
            {
                "metric": "CAC",
                "value": f"${unit_econ.get('cac', 0):,}",
                "benchmark": "Industry avg",
                "assessment": unit_econ.get("assessment", ""),
            },
            {
                "metric": "LTV:CAC Ratio",
                "value": f"{unit_econ.get('ltv_cac_ratio', 0):.1f}x",
                "benchmark": ">3x healthy",
                "assessment": unit_econ.get("assessment", ""),
            },
            {
                "metric": "Gross Margin",
                "value": f"{unit_econ.get('gross_margin_percent', 0)}%",
                "benchmark": ">60% for SaaS",
                "assessment": unit_econ.get("assessment", ""),
            },
            {
                "metric": "Payback Period",
                "value": f"{unit_econ.get('payback_period_months', 0)} months",
                "benchmark": "<12 months ideal",
                "assessment": unit_econ.get("assessment", ""),
            },
        ]

    # Transform projections from monthly/quarterly to simplified array
    monthly = financial_model.get("monthly_projections_year_1", []) or []
    quarterly = financial_model.get("quarterly_projections_year_2_3", []) or []
    projections = []

    # First check if projections already exist
    existing_projections = financial_model.get("projections")
    if existing_projections:
        # If it's already a list, use it directly
        if isinstance(existing_projections, list):
            projections = existing_projections
        # If it's a dict (year_1, year_2 format), convert to array
        elif isinstance(existing_projections, dict):
            for year_key in sorted(existing_projections.keys()):
                year_data = existing_projections.get(year_key, {}) or {}
                if year_data:
                    # Format year_key: "year_1" -> "Year 1"
                    period = year_key.replace("_", " ").title()
                    projections.append({
                        "period": period,
                        "revenue": year_data.get("revenue", 0),
                        "costs": year_data.get("costs", 0),
                        "profit": year_data.get("profit", 0),
                        "cumulative_profit": year_data.get("cumulative_profit", 0),
                    })

    # If no existing projections, build from monthly/quarterly data
    if not projections:
        # Add key monthly milestones (months 1, 6, 12)
        cumulative = 0
        for month_data in monthly:
            month = month_data.get("month", 0)
            profit = month_data.get("profit", 0)
            cumulative += profit
            if month in [1, 6, 12]:
                projections.append({
                    "period": f"Month {month}",
                    "revenue": month_data.get("revenue", 0),
                    "costs": month_data.get("costs", 0),
                    "profit": profit,
                    "cumulative_profit": cumulative,
                })

        # Add quarterly data
        for q_data in quarterly:
            q_profit = q_data.get("profit", 0)
            cumulative += q_profit
            projections.append({
                "period": q_data.get("quarter", ""),
                "revenue": q_data.get("revenue", 0),
                "costs": q_data.get("costs", 0),
                "profit": q_profit,
                "cumulative_profit": cumulative,
            })

        # If still no projections, build minimal placeholder from five_year_projection
        if not projections:
            five_year = financial_model.get("five_year_projection", {}) or {}
            if five_year:
                for year_key in ["year_1", "year_2", "year_3", "year_4", "year_5"]:
                    year_data = five_year.get(year_key, {}) or {}
                    if year_data:
                        year_num = year_key.replace("year_", "Year ")
                        projections.append({
                            "period": year_num,
                            "revenue": year_data.get("revenue", 0),
                            "costs": year_data.get("costs", 0),
                            "profit": year_data.get("profit", 0),
                            "cumulative_profit": 0,
                        })

    # Always include projections (even if empty) so frontend doesn't fail
    transformed["projections"] = projections if projections else []

    # Transform assumptions - may be a list or part of scenarios
    assumptions = financial_model.get("assumptions", [])
    if not assumptions:
        # Try to extract from scenario analysis
        scenario = financial_model.get("scenario_analysis", {}) or {}
        base_case = scenario.get("base_case", {}) or {}
        assumptions = base_case.get("assumptions", [])
    transformed["assumptions"] = assumptions if assumptions else []

    # Transform sensitivity_analysis from nested objects to simple strings
    scenario = financial_model.get("scenario_analysis", {}) or {}
    sensitivity = financial_model.get("sensitivity_analysis", {}) or {}

    optimistic = scenario.get("optimistic", {}) or {}
    base_case = scenario.get("base_case", {}) or {}
    pessimistic = scenario.get("pessimistic", {}) or {}

    opt_desc = optimistic.get("description", "")
    opt_rev = optimistic.get("year_3_revenue", 0)
    base_desc = base_case.get("description", "")
    base_rev = base_case.get("year_3_revenue", 0)
    pess_desc = pessimistic.get("description", "")
    pess_rev = pessimistic.get("year_3_revenue", 0)

    transformed["sensitivity_analysis"] = {
        "optimistic": f"{opt_desc} - Y3 Revenue: ${opt_rev:,}" if opt_desc else "",
        "base_case": f"{base_desc} - Y3 Revenue: ${base_rev:,}" if base_desc else "",
        "pessimistic": f"{pess_desc} - Y3 Revenue: ${pess_rev:,}" if pess_desc else "",
    }

    # Transform funding_requirements from object to string
    funding = financial_model.get("funding_requirements", {}) or {}
    if funding:
        parts = []
        pre_seed = funding.get("pre_seed", {}) or {}
        seed = funding.get("seed", {}) or {}
        series_a = funding.get("series_a", {}) or {}
        total = funding.get("total_required", "")

        if pre_seed.get("amount"):
            parts.append(f"Pre-Seed: ${pre_seed['amount']:,}")
        if seed.get("amount"):
            parts.append(f"Seed: ${seed['amount']:,}")
        if series_a.get("amount"):
            parts.append(f"Series A: ${series_a['amount']:,}")
        if total:
            parts.append(f"Total: {total}")

        transformed["funding_requirements"] = " | ".join(parts) if parts else ""
    else:
        transformed["funding_requirements"] = ""

    # Transform break_even to string
    sensitivity_raw = financial_model.get("sensitivity_analysis", {}) or {}
    break_even_sensitivity = sensitivity_raw.get("break_even_sensitivity", "")
    # Also check for direct break_even field
    break_even = financial_model.get("break_even_analysis", "")
    if not break_even and break_even_sensitivity:
        break_even = break_even_sensitivity
    transformed["break_even_analysis"] = break_even

    return transformed


def _transform_detailed_personas(
    detailed_personas: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Transform backend personas to frontend format with personas array.

    Backend produces: primary_persona, secondary_personas[], anti_persona, persona_prioritisation
    Frontend expects: personas[], key_insights[], prioritization
    """
    if not detailed_personas:
        return None

    personas_list = []

    # Add primary persona to list
    primary = detailed_personas.get("primary_persona", {}) or {}
    if primary:
        personas_list.append(
            {
                "persona_id": "P1",
                "name": primary.get("name", ""),
                "role": primary.get("role", ""),
                "quote": primary.get("quote", ""),
                "demographics": {
                    "age_range": primary.get("tenure", ""),
                    "location": "",
                    "income_level": "",
                    "education": "",
                },
                "jobs_to_be_done": [
                    {"job": jtbd, "importance": "high", "current_solution": ""}
                    for jtbd in (primary.get("jobs_to_be_done", []) or [])
                ],
                "pain_points": primary.get("frustrations", []) or [],
                "goals": primary.get("goals", []) or [],
                "behaviors": [],
                "channels": primary.get("discovery_channels", []) or [],
                "decision_factors": primary.get("evaluation_criteria", []) or [],
                "day_in_life": "",
            }
        )

    # Add secondary personas to list
    secondary_personas = detailed_personas.get("secondary_personas", []) or []
    for idx, secondary in enumerate(secondary_personas, start=2):
        personas_list.append(
            {
                "persona_id": f"P{idx}",
                "name": secondary.get("name", ""),
                "role": secondary.get("role", ""),
                "quote": "",
                "demographics": {
                    "age_range": "",
                    "location": "",
                    "income_level": "",
                    "education": "",
                },
                "jobs_to_be_done": [
                    {"job": jtbd, "importance": "medium", "current_solution": ""}
                    for jtbd in (secondary.get("jobs_to_be_done", []) or [])
                ],
                "pain_points": [],
                "goals": secondary.get("goals", []) or [],
                "behaviors": [],
                "channels": [],
                "decision_factors": secondary.get("evaluation_criteria", []) or [],
                "day_in_life": "",
            }
        )

    # Build key insights from anti_persona
    anti = detailed_personas.get("anti_persona", {}) or {}
    key_insights = []
    if anti:
        desc = anti.get("description", "")
        if desc:
            key_insights.append(f"Not for: {desc}")
        for reason in (anti.get("reasons", []) or [])[:2]:
            key_insights.append(reason)

    # Get prioritization
    prio = detailed_personas.get("persona_prioritisation", {}) or {}
    prioritization = prio.get("primary_buyer", "")

    return {
        "personas": personas_list,
        "key_insights": key_insights,
        "prioritization": prioritization,
    }


def _transform_wireframes(wireframes: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Transform backend wireframes to frontend format.

    Key fix: user_flows use screens_referenced → screens
    """
    if not wireframes:
        return None

    transformed = {
        "screens": wireframes.get("screens", []) or [],
        "user_flow_description": wireframes.get("user_flow_description", ""),
        "user_flow_mermaid": wireframes.get("user_flow_mermaid", ""),
        "design_system_notes": wireframes.get("design_system_notes", []) or [],
        "responsive_notes": wireframes.get("responsive_notes", ""),
    }

    # Transform user_flows - map screens_referenced to screens
    user_flows = wireframes.get("user_flows", []) or []
    transformed["user_flows"] = [
        {
            "flow_name": flow.get("flow_name", ""),
            "description": flow.get("notes", flow.get("description", "")),
            "screens": flow.get("screens", flow.get("screens_referenced", [])) or [],
            "persona": flow.get("persona", ""),
            "mermaid_code": flow.get("mermaid_code", ""),
        }
        for flow in user_flows
    ]

    return transformed


# ═══════════════════════════════════════════════════════════════════════════════
# V4 DISCOVERY SECTION BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def _build_v4_discovery_section(state: dict[str, Any]) -> dict[str, Any] | None:
    """
    Build the V4 Discovery Journey section from state.

    Extracts V4-specific fields that were set during V4 discovery.
    Returns None if no V4 data is present.
    """
    # Check if this is a V4 session by looking for V4-specific fields
    has_v4_data = any(
        state.get(key)
        for key in [
            "_v4_problem_statement",
            "_v4_pain_patterns",
            "_v4_four_forces",
            "_v4_solution_concept",
            "_v4_validation_experiments",
        ]
    )

    if not has_v4_data:
        return None

    return {
        # Problem Love Stage
        "problem_love": {
            "problem_statement": state.get("_v4_problem_statement", ""),
            "problem_score": state.get("_v4_problem_score"),
            "evidence_quality": state.get("_discovery_evidence_tier", "E4"),
        },
        # Customer Truth Stage
        "customer_truth": {
            "interview_count": state.get("_v4_interview_count", 0),
            "key_quotes": state.get("_v4_key_quotes", []),
            "pain_patterns": state.get("_v4_pain_patterns", []),
            "trigger_patterns": state.get("_v4_trigger_patterns", []),
            "outcome_patterns": state.get("_v4_outcome_patterns", []),
        },
        # Opportunity Mapping Stage
        "opportunity_mapping": {
            "four_forces": state.get("_v4_four_forces", {}),
            "opportunity_tree": state.get("_v4_opportunity_tree", {}),
            "primary_opportunity": state.get("_v4_primary_opportunity", ""),
        },
        # Solution Design Stage
        "solution_design": {
            "solution_concept": state.get("_v4_solution_concept", ""),
            "dhm_score": state.get("_v4_dhm_score", {}),
            "pre_mortem": state.get("_v4_pre_mortem", {}),
        },
        # Validation Plan Stage
        "validation_plan": {
            "experiments": state.get("_v4_validation_experiments", []),
        },
        # Overall metadata
        "mode": state.get("_v4_mode", "unknown"),
        "high_confidence": state.get("_high_confidence_discovery", False),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INCEPTION PACK BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def build_inception_pack(state: dict[str, Any]) -> dict[str, Any]:
    """
    Build the final InceptionPack from workflow state.

    Assembles all agent outputs into the final deliverable format.
    Supports both V1.0 (7 sections) and V3.0 (16 sections) formats.
    Transforms backend structures to frontend-expected format.

    Args:
        state: Completed workflow state.

    Returns:
        dict: Complete InceptionPack structure.
    """
    logger = structlog.get_logger(__name__)
    session_id = state.get("session_id", "unknown")

    # Transform sections that have structural mismatches between backend and frontend
    gtm_strategy = _transform_gtm_plan(state.get("gtm_plan"))
    detailed_personas = _transform_detailed_personas(state.get("detailed_personas"))
    financial_model = _transform_financial_model(state.get("financial_model"))
    wireframes = _transform_wireframes(state.get("wireframes"))

    # Get customer_research - ensure it's not empty {}
    customer_research = state.get("customer_research")
    if customer_research == {}:
        customer_research = None

    # Build V4 Discovery Journey data if available in state
    v4_discovery = _build_v4_discovery_section(state)

    pack = {
        # V4 Discovery Journey (new top-level section)
        "discovery_journey": v4_discovery,
        # Core sections (V1.0)
        "executive_summary": state.get("executive_summary", {}),
        "customer_research": customer_research or {},
        "business_case": state.get("business_case", {}),
        "product_requirements_document": state.get("product_requirements", {}),
        "technical_architecture": state.get("technical_architecture", {}),
        "legal_regulatory_review": state.get("legal_regulatory_review", {}),
        "quality_assessment": state.get("quality_assessment") or {},
        # V3.0 Discovery sections
        "competitive_analysis": state.get("competitive_analysis"),
        "detailed_personas": detailed_personas,  # TRANSFORMED
        # V3.0 Strategy sections
        "gtm_strategy": gtm_strategy,  # TRANSFORMED
        "financial_model": financial_model,  # TRANSFORMED
        # V3.0 Delivery sections
        "risk_assessment": state.get("risk_assessment"),
        # V3.0 Design sections
        "wireframes": wireframes,  # TRANSFORMED
        "prototype": state.get("prototype"),
        # V3.0 Synthesis sections
        "stakeholder_views": state.get("stakeholder_views"),
        "validation_playbook": state.get("validation_playbook"),
        # V3.0 Cross-reference index (from claim extractor)
        "cross_reference_index": state.get("cross_reference_index"),
        # Metadata
        "metadata": {
            "session_id": session_id,
            "generated_at": datetime.utcnow().isoformat(),
            "version": "3.0",
            "generator": "Product Discovery Multi-Agent System",
            "iterations": str(state.get("iteration", 1)),
            "total_tokens_used": str(state.get("total_tokens_used", 0)),
            "total_duration_seconds": str(round(state.get("total_duration_seconds", 0) or 0, 2)),
            "quality_score": str((state.get("quality_assessment") or {}).get("overall_score", 0.0)),
            "quality_passed": str(state.get("quality_passed", False)),
        },
    }

    # Log warnings if discovery sections are empty/missing
    if not pack.get("customer_research") or pack.get("customer_research") == {}:
        logger.warning(
            "pack_missing_customer_research",
            session_id=session_id,
        )
    if not pack.get("competitive_analysis"):
        logger.warning(
            "pack_missing_competitive_analysis",
            session_id=session_id,
        )
    if not pack.get("detailed_personas"):
        logger.warning(
            "pack_missing_detailed_personas",
            session_id=session_id,
        )
    if not (financial_model or {}).get("projections"):
        logger.warning(
            "pack_missing_financial_projections",
            session_id=session_id,
        )

    # Remove None values to keep response clean
    return {k: v for k, v in pack.items() if v is not None}
