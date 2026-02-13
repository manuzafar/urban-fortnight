"""
Output Validator — Pre-output validation with retry for all 16 agents.

This module validates agent outputs against mandatory checklist requirements
before they are stored in state. If validation fails, it provides specific
fix instructions for retry.

Key Features:
- Validation rules for all 16 agents
- Runs immediately after LLM response
- Checks mandatory fields
- Triggers retry with specific fix instructions if validation fails
"""

from dataclasses import dataclass
from typing import Any, Callable
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of output validation."""
    valid: bool
    errors: list[str]
    warnings: list[str]
    fix_instructions: str


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION RULES FOR ALL 16 AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

def _safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current


def _check_length(val: Any, min_len: int) -> bool:
    """Check if value has minimum length (works for strings and lists)."""
    if val is None:
        return False
    if isinstance(val, (str, list)):
        return len(val) >= min_len
    return False


def _check_not_placeholder(val: Any) -> bool:
    """Check if value is not a placeholder."""
    if val is None:
        return False
    val_str = str(val).lower()
    placeholders = ["tbd", "todo", "xxx", "placeholder", "lorem ipsum",
                    "item 1", "item 2", "$x", "n/a", "not available"]
    return not any(p in val_str for p in placeholders)


# ─────────────────────────────────────────────────────────────────────────────
# PLANNER AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

PLANNER_RULES = {
    "research_questions": lambda o: _check_length(_safe_get(o, "key_research_questions"), 3),
    "competitor_targets": lambda o: _check_length(_safe_get(o, "competitors_to_analyze"), 2),
    "domain_classification": lambda o: bool(_safe_get(o, "domain_type")),
    "regulatory_domains": lambda o: _check_length(_safe_get(o, "regulatory_domains"), 1),
}


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER RESEARCH AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

CUSTOMER_RESEARCH_RULES = {
    "pain_signals": lambda o: _check_length(_safe_get(o, "pain_signals"), 3),
    "segments_examined": lambda o: _check_length(
        _safe_get(o, "research_scope", "segments_examined"), 2
    ),
    "jtbd_trigger": lambda o: bool(_safe_get(o, "job_to_be_done", "trigger_situation")),
    "jtbd_goal": lambda o: bool(_safe_get(o, "job_to_be_done", "underlying_goal")),
    "jtbd_success": lambda o: bool(_safe_get(o, "job_to_be_done", "success_definition")),
    "uncomfortable_insights": lambda o: _check_length(
        _safe_get(o, "uncomfortable_insights"), 1
    ),
    "existing_solutions": lambda o: _check_length(
        _safe_get(o, "current_behaviour", "existing_solutions"), 1
    ),
    "friction_points": lambda o: _check_length(
        _safe_get(o, "current_behaviour", "friction_points"), 1
    ),
    "competitors": lambda o: _check_length(
        _safe_get(o, "competitive_landscape", "competitors"), 2
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# BUSINESS STRATEGY AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

BUSINESS_STRATEGY_RULES = {
    "lean_canvas_problem": lambda o: _check_length(
        _safe_get(o, "lean_canvas", "problem"), 1
    ),
    "lean_canvas_solution": lambda o: _check_length(
        _safe_get(o, "lean_canvas", "solution"), 1
    ),
    "lean_canvas_uvp": lambda o: bool(
        _safe_get(o, "lean_canvas", "unique_value_proposition")
    ),
    "revenue_streams": lambda o: _check_length(_safe_get(o, "revenue_streams"), 1),
    "risks_and_mitigations": lambda o: _check_length(
        _safe_get(o, "risks_and_mitigations"), 3
    ),
    "year_1_projection": lambda o: bool(_safe_get(o, "year_1_projection")),
    "year_3_projection": lambda o: bool(_safe_get(o, "year_3_projection")),
    "funding_requirement": lambda o: _check_not_placeholder(
        _safe_get(o, "funding_requirement")
    ),
    "unit_economics_cac": lambda o: bool(_safe_get(o, "unit_economics", "cac")),
    "unit_economics_ltv": lambda o: bool(_safe_get(o, "unit_economics", "ltv")),
}


# ─────────────────────────────────────────────────────────────────────────────
# GTM AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

GTM_RULES = {
    "positioning_statement": lambda o: _check_length(
        _safe_get(o, "positioning_statement"), 20
    ),
    "channel_strategy": lambda o: _check_length(_safe_get(o, "channel_strategy"), 2),
    "launch_phases": lambda o: _check_length(_safe_get(o, "launch_phases"), 2),
    "messaging_by_persona": lambda o: _check_length(
        _safe_get(o, "messaging_by_persona"), 1
    ),
    "metrics_dashboard": lambda o: _check_length(_safe_get(o, "metrics_dashboard"), 3),
    "partnership_opportunities": lambda o: _check_length(
        _safe_get(o, "partnership_opportunities"), 1
    ),
    "gtm_budget": lambda o: _check_not_placeholder(
        _safe_get(o, "total_gtm_budget_estimate")
    ),
    "gtm_risks": lambda o: _check_length(_safe_get(o, "gtm_risks"), 2),
}


# ─────────────────────────────────────────────────────────────────────────────
# FINANCIAL MODEL AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

def _check_monthly_projections(output: dict) -> bool:
    """Check that exactly 12 months are present."""
    projections = _safe_get(output, "monthly_projections_year_1", default=[])
    return len(projections) >= 12


def _check_profit_math(output: dict) -> bool:
    """Check that profit = revenue - costs for all months."""
    projections = _safe_get(output, "monthly_projections_year_1", default=[])
    if not projections:
        return False
    for m in projections:
        if not isinstance(m, dict):
            continue
        revenue = m.get("revenue", 0) or 0
        costs = m.get("costs", 0) or 0
        profit = m.get("profit", 0) or 0
        # Allow small rounding errors
        if abs(profit - (revenue - costs)) > 1:
            return False
    return True


def _check_scenario_analysis(output: dict) -> bool:
    """Check all three scenarios are present."""
    sa = _safe_get(output, "scenario_analysis", default={})
    return all([
        _safe_get(sa, "base_case"),
        _safe_get(sa, "optimistic"),
        _safe_get(sa, "pessimistic"),
    ])


FINANCIAL_MODEL_RULES = {
    "input_assumptions": lambda o: _check_length(_safe_get(o, "input_assumptions"), 5),
    "monthly_projections_count": _check_monthly_projections,
    "profit_math_valid": _check_profit_math,
    "unit_economics_cac": lambda o: _safe_get(o, "unit_economics", "cac") is not None,
    "unit_economics_ltv": lambda o: _safe_get(o, "unit_economics", "ltv") is not None,
    "ltv_cac_ratio": lambda o: _safe_get(o, "unit_economics", "ltv_cac_ratio") is not None,
    "scenario_analysis": _check_scenario_analysis,
    "funding_requirements": lambda o: bool(
        _safe_get(o, "funding_requirements", "total_required") or
        _safe_get(o, "funding_requirements", "seed")
    ),
    "key_financial_risks": lambda o: _check_length(
        _safe_get(o, "key_financial_risks"), 2
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# PRD AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

def _count_total_stories(output: dict) -> int:
    """Count total user stories across all epics."""
    epics = _safe_get(output, "epics", default=[])
    total = 0
    for epic in epics:
        if isinstance(epic, dict):
            stories = epic.get("stories", [])
            total += len(stories) if stories else 0
    return total


def _check_story_format(output: dict) -> bool:
    """Check 80%+ stories have proper format."""
    epics = _safe_get(output, "epics", default=[])
    total_stories = 0
    well_formatted = 0

    for epic in epics:
        if not isinstance(epic, dict):
            continue
        for story in epic.get("stories", []):
            if not isinstance(story, dict):
                continue
            total_stories += 1
            # Check for as_a/i_want/so_that OR title/description
            has_format = (
                (story.get("as_a") and story.get("i_want") and story.get("so_that")) or
                (story.get("title") and _check_length(story.get("description"), 10))
            )
            if has_format:
                well_formatted += 1

    if total_stories == 0:
        return False
    return (well_formatted / total_stories) >= 0.8


def _check_stories_have_priority(output: dict) -> bool:
    """Check 80%+ stories have priority field."""
    epics = _safe_get(output, "epics", default=[])
    total_stories = 0
    with_priority = 0

    for epic in epics:
        if not isinstance(epic, dict):
            continue
        for story in epic.get("stories", []):
            if not isinstance(story, dict):
                continue
            total_stories += 1
            if story.get("priority"):
                with_priority += 1

    if total_stories == 0:
        return False
    return (with_priority / total_stories) >= 0.8


PRD_RULES = {
    "epic_count": lambda o: _check_length(_safe_get(o, "epics"), 3),
    "story_count": lambda o: _count_total_stories(o) >= 5,
    "story_format": _check_story_format,
    "story_priority": _check_stories_have_priority,
    "functional_requirements": lambda o: _check_length(
        _safe_get(o, "functional_requirements"), 5
    ),
    "non_functional_requirements": lambda o: _check_length(
        _safe_get(o, "non_functional_requirements"), 3
    ),
    "release_plan": lambda o: _check_length(
        _safe_get(o, "release_plan") or _safe_get(o, "release_plan", "phases"), 2
    ),
    "data_model_entities": lambda o: _check_length(
        _safe_get(o, "data_model", "entities"), 2
    ),
    "risks": lambda o: _check_length(
        _safe_get(o, "risks") or _safe_get(o, "risks_and_mitigations"), 3
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# TECHNICAL ARCHITECTURE AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_TECHNOLOGIES = {
    "react", "vue", "angular", "svelte", "next.js", "nuxt", "gatsby",
    "node.js", "node", "express", "fastapi", "django", "flask", "rails", "spring",
    "go", "golang", "rust", "python", "java", "kotlin", "typescript", "javascript",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform",
    "graphql", "rest", "grpc", "kafka", "rabbitmq", "sqs", "sns",
    "datadog", "prometheus", "grafana", "new relic", "cloudwatch",
    "auth0", "okta", "firebase", "supabase", "vercel", "netlify",
    "stripe", "twilio", "sendgrid", "cloudflare",
}


def _check_real_technologies(output: dict) -> bool:
    """Check 70%+ technologies are real/recognizable."""
    tech_stack = _safe_get(output, "technology_stack", default=[])
    if not tech_stack:
        return False

    total = len(tech_stack)
    real_count = 0

    for tech in tech_stack:
        if not isinstance(tech, dict):
            continue
        tech_name = str(tech.get("technology", "")).lower()
        # Check if any known tech is in the name
        if any(known in tech_name for known in KNOWN_TECHNOLOGIES):
            real_count += 1

    return total > 0 and (real_count / total) >= 0.7


TECHNICAL_ARCHITECTURE_RULES = {
    "architecture_style": lambda o: _check_length(_safe_get(o, "architecture_style"), 10),
    "technology_stack": lambda o: _check_length(_safe_get(o, "technology_stack"), 3),
    "real_technologies": _check_real_technologies,
    "system_components": lambda o: _check_length(_safe_get(o, "system_components"), 2),
    "security_architecture": lambda o: _check_length(
        _safe_get(o, "security_architecture"), 20
    ),
    "scalability_approach": lambda o: _check_length(
        _safe_get(o, "scalability_approach"), 20
    ),
    "deployment_strategy": lambda o: _check_length(
        _safe_get(o, "deployment_strategy"), 20
    ),
    "infrastructure_requirements": lambda o: _check_length(
        _safe_get(o, "infrastructure_requirements"), 1
    ),
    "architecture_diagram": lambda o: bool(
        _safe_get(o, "architecture_diagram_mermaid") or
        _safe_get(o, "architecture_diagram_description")
    ),
    "technical_risks": lambda o: _check_length(_safe_get(o, "technical_risks"), 2),
}


# ─────────────────────────────────────────────────────────────────────────────
# LEGAL REGULATORY AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_REGULATIONS = {
    "gdpr", "ccpa", "hipaa", "pci-dss", "pci dss", "sox", "soc 2", "soc2",
    "iso 27001", "iso27001", "ferpa", "coppa", "glba", "fcra", "ftc",
    "lgpd", "pipeda", "data protection", "privacy", "dpa", "sec", "finra",
    "mifid", "psd2", "fda", "hitech", "aml", "kyc", "fatca",
}


def _check_real_regulations(output: dict) -> bool:
    """Check 50%+ regulations are real/recognizable."""
    regulations = _safe_get(output, "applicable_regulations", default=[])
    if not regulations:
        return False

    total = len(regulations)
    real_count = 0

    for reg in regulations:
        if not isinstance(reg, dict):
            continue
        reg_name = str(reg.get("name", "")).lower()
        if any(known in reg_name for known in KNOWN_REGULATIONS):
            real_count += 1

    return total > 0 and (real_count / total) >= 0.5


def _check_risks_have_mitigation(output: dict) -> bool:
    """Check 70%+ risks have mitigation strategies."""
    risks = _safe_get(output, "legal_risks", default=[])
    if not risks:
        return True  # No risks is acceptable

    total = len(risks)
    with_mitigation = 0

    for risk in risks:
        if not isinstance(risk, dict):
            continue
        if risk.get("mitigation_strategies") or risk.get("mitigation"):
            with_mitigation += 1

    return total > 0 and (with_mitigation / total) >= 0.7


LEGAL_REGULATORY_RULES = {
    "executive_summary": lambda o: _check_length(
        _safe_get(o, "executive_summary"), 50
    ),
    "applicable_regulations": lambda o: _check_length(
        _safe_get(o, "applicable_regulations"), 1
    ),
    "real_regulations": _check_real_regulations,
    "data_protection_requirements": lambda o: _check_length(
        _safe_get(o, "data_protection_requirements"), 1
    ),
    "legal_risks": lambda o: _check_length(_safe_get(o, "legal_risks"), 2),
    "risks_have_mitigation": _check_risks_have_mitigation,
    "risk_level": lambda o: bool(
        _safe_get(o, "overall_risk_assessment", "risk_level")
    ),
    "next_steps": lambda o: _check_length(_safe_get(o, "next_steps"), 2),
}


# ─────────────────────────────────────────────────────────────────────────────
# EXECUTIVE SUMMARY AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

EXECUTIVE_SUMMARY_RULES = {
    "product_name": lambda o: _check_not_placeholder(_safe_get(o, "product_name")),
    "tagline": lambda o: _check_length(_safe_get(o, "tagline"), 10),
    "problem_statement": lambda o: bool(_safe_get(o, "problem_statement")),
    "solution_overview": lambda o: bool(_safe_get(o, "solution_overview")),
    "target_users": lambda o: _check_length(_safe_get(o, "target_users"), 1),
    "key_differentiators": lambda o: _check_length(
        _safe_get(o, "key_differentiators"), 3
    ),
    "funding_required": lambda o: _check_not_placeholder(
        _safe_get(o, "funding_required")
    ),
    "financial_projections": lambda o: bool(_safe_get(o, "financial_projections")),
    "key_decisions": lambda o: _check_length(_safe_get(o, "key_decisions"), 3),
    "top_risks": lambda o: _check_length(_safe_get(o, "top_risks"), 3),
    "recommendation": lambda o: _safe_get(o, "recommendation") in [
        "BUILD", "INVESTIGATE", "PIVOT", "KILL",
        "PROCEED", "PROCEED WITH CONDITIONS", "DO NOT PROCEED"
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# STAKEHOLDER VIEWS AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

def _check_stakeholder_views_complete(output: dict) -> bool:
    """Check each view has required fields."""
    views = _safe_get(output, "views", default=[])
    if len(views) < 3:
        return False

    complete_count = 0
    for view in views:
        if not isinstance(view, dict):
            continue
        has_required = all([
            view.get("stakeholder_role"),
            _check_length(view.get("tailored_summary"), 50),
            _check_length(view.get("anticipated_objections"), 1),
            _check_length(view.get("decision_recommendation"), 20),
            _check_length(view.get("key_questions_answered"), 2),
        ])
        if has_required:
            complete_count += 1

    return complete_count >= 3


STAKEHOLDER_VIEWS_RULES = {
    "view_count": lambda o: _check_length(_safe_get(o, "views"), 3),
    "views_complete": _check_stakeholder_views_complete,
    "common_concerns": lambda o: _check_length(_safe_get(o, "common_concerns"), 1),
    "alignment_opportunities": lambda o: _check_length(
        _safe_get(o, "alignment_opportunities"), 1
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION PLAYBOOK AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

VALID_EXPERIMENT_TYPES = {
    "interview", "survey", "landing_page", "prototype", "concierge",
    "smoke_test", "a/b test", "a/b_test", "usability", "mvp",
    "customer_interview", "user_interview", "landing page", "smoke test",
}


def _check_experiment_types(output: dict) -> bool:
    """Check 80%+ experiments use recognized types."""
    experiments = _safe_get(output, "experiments", default=[])
    if not experiments:
        return False

    total = len(experiments)
    valid_count = 0

    for exp in experiments:
        if not isinstance(exp, dict):
            continue
        exp_type = str(exp.get("experiment_type", "")).lower().replace("-", "_")
        if any(valid in exp_type for valid in VALID_EXPERIMENT_TYPES):
            valid_count += 1

    return total > 0 and (valid_count / total) >= 0.8


def _check_experiments_complete(output: dict) -> bool:
    """Check experiments have required fields."""
    experiments = _safe_get(output, "experiments", default=[])
    if not experiments:
        return False

    total = len(experiments)
    with_success_criteria = 0
    with_failure_criteria = 0
    with_instructions = 0

    for exp in experiments:
        if not isinstance(exp, dict):
            continue
        if _check_length(exp.get("success_criteria"), 10):
            with_success_criteria += 1
        if _check_length(exp.get("failure_criteria"), 10):
            with_failure_criteria += 1
        if _check_length(exp.get("specific_instructions"), 30):
            with_instructions += 1

    # 100% need success criteria, 70% need failure and instructions
    return (
        with_success_criteria == total and
        (with_failure_criteria / total) >= 0.7 and
        (with_instructions / total) >= 0.7
    )


VALIDATION_PLAYBOOK_RULES = {
    "experiment_count": lambda o: _check_length(_safe_get(o, "experiments"), 3),
    "experiment_types_valid": _check_experiment_types,
    "experiments_complete": _check_experiments_complete,
    "critical_path": lambda o: _check_length(
        _safe_get(o, "critical_path_experiments"), 1
    ),
    "validation_timeline": lambda o: bool(
        _safe_get(o, "total_validation_timeline")
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# WIREFRAME AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

def _check_screens_have_react_code(output: dict) -> bool:
    """Check 70%+ screens have react_code with 80+ chars."""
    screens = _safe_get(output, "screens", default=[])
    if not screens:
        return False

    total = len(screens)
    with_code = 0

    for screen in screens:
        if not isinstance(screen, dict):
            continue
        react_code = screen.get("react_code", "")
        if _check_length(react_code, 80):
            with_code += 1

    return total > 0 and (with_code / total) >= 0.7


def _check_screens_have_navigation(output: dict) -> bool:
    """Check all screens have navigation_to array."""
    screens = _safe_get(output, "screens", default=[])
    if not screens:
        return False

    for screen in screens:
        if not isinstance(screen, dict):
            continue
        if not screen.get("navigation_to"):
            return False
    return True


WIREFRAME_RULES = {
    "screen_count": lambda o: _check_length(_safe_get(o, "screens"), 3),
    "screens_have_react_code": _check_screens_have_react_code,
    "screens_have_navigation": _check_screens_have_navigation,
    "user_flows": lambda o: _check_length(_safe_get(o, "user_flows"), 2),
    "design_system_notes": lambda o: _check_length(
        _safe_get(o, "design_system_notes"), 1
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# PROTOTYPE AGENT RULES
# ─────────────────────────────────────────────────────────────────────────────

def _check_react_code_valid(output: dict) -> bool:
    """Check react code has basic structure."""
    code = _safe_get(output, "react_component_code", default="")
    if not code:
        return False

    # Check for basic React patterns
    has_function = "function" in code or "const" in code
    has_jsx = "<" in code and ">" in code
    has_usestate = "useState" in code

    return has_function and has_jsx and has_usestate


def _check_no_placeholders_in_code(output: dict) -> bool:
    """Check react code has no placeholder text."""
    code = _safe_get(output, "react_component_code", default="")
    if not code:
        return True  # Will fail other checks

    code_lower = code.lower()
    placeholders = ["lorem ipsum", "todo", "tbd", "placeholder", "item 1", "item 2"]
    return not any(p in code_lower for p in placeholders)


PROTOTYPE_RULES = {
    "prototype_name": lambda o: _check_not_placeholder(_safe_get(o, "prototype_name")),
    "react_code_length": lambda o: _check_length(
        _safe_get(o, "react_component_code"), 100
    ),
    "react_code_valid": _check_react_code_valid,
    "no_placeholders": _check_no_placeholders_in_code,
    "primary_persona": lambda o: bool(_safe_get(o, "primary_persona")),
    "key_user_story": lambda o: _check_length(_safe_get(o, "key_user_story"), 20),
    "demo_scenario": lambda o: _check_length(_safe_get(o, "demo_scenario"), 30),
    "color_palette": lambda o: bool(_safe_get(o, "color_palette", "primary")),
    "screens_included": lambda o: _check_length(_safe_get(o, "screens_included"), 3),
}


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT VALIDATION RULES REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_VALIDATION_RULES: dict[str, dict[str, Callable[[dict], bool]]] = {
    "planner": PLANNER_RULES,
    "Planning Agent": PLANNER_RULES,
    "customer_research": CUSTOMER_RESEARCH_RULES,
    "Customer Research Agent": CUSTOMER_RESEARCH_RULES,
    "business_strategy": BUSINESS_STRATEGY_RULES,
    "Business Strategy Agent": BUSINESS_STRATEGY_RULES,
    "gtm_agent": GTM_RULES,
    "Go-to-Market": GTM_RULES,
    "financial_model_agent": FINANCIAL_MODEL_RULES,
    "Financial Model": FINANCIAL_MODEL_RULES,
    "product_requirements": PRD_RULES,
    "Product Requirements Agent": PRD_RULES,
    "technical_architect": TECHNICAL_ARCHITECTURE_RULES,
    "Technical Architect Agent": TECHNICAL_ARCHITECTURE_RULES,
    "legal_regulatory": LEGAL_REGULATORY_RULES,
    "Legal & Regulatory Review": LEGAL_REGULATORY_RULES,
    "executive_summary_agent": EXECUTIVE_SUMMARY_RULES,
    "Executive Summary": EXECUTIVE_SUMMARY_RULES,
    "stakeholder_agent": STAKEHOLDER_VIEWS_RULES,
    "Stakeholder Views": STAKEHOLDER_VIEWS_RULES,
    "validation_agent": VALIDATION_PLAYBOOK_RULES,
    "Validation Playbook": VALIDATION_PLAYBOOK_RULES,
    "wireframe_agent": WIREFRAME_RULES,
    "Wireframe Designer": WIREFRAME_RULES,
    "prototype_agent": PROTOTYPE_RULES,
    "Prototype Generator": PROTOTYPE_RULES,
}


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_agent_output(
    agent_name: str,
    output: dict[str, Any],
) -> ValidationResult:
    """
    Validate an agent's output against its mandatory checklist.

    Args:
        agent_name: The name of the agent
        output: The agent's output dictionary

    Returns:
        ValidationResult with validation status and any errors/warnings
    """
    rules = AGENT_VALIDATION_RULES.get(agent_name)

    if not rules:
        logger.debug("no_validation_rules", agent=agent_name)
        return ValidationResult(
            valid=True,
            errors=[],
            warnings=["No validation rules defined for this agent"],
            fix_instructions=""
        )

    errors = []
    warnings = []

    for rule_name, check_fn in rules.items():
        try:
            if not check_fn(output):
                errors.append(f"FAILED: {rule_name}")
        except Exception as e:
            warnings.append(f"Could not check {rule_name}: {str(e)}")

    # Generate fix instructions
    fix_instructions = ""
    if errors:
        fix_instructions = _generate_fix_instructions(agent_name, errors)

    valid = len(errors) == 0

    logger.info(
        "validation_result",
        agent=agent_name,
        valid=valid,
        error_count=len(errors),
        warning_count=len(warnings),
    )

    return ValidationResult(
        valid=valid,
        errors=errors,
        warnings=warnings,
        fix_instructions=fix_instructions,
    )


def _generate_fix_instructions(agent_name: str, errors: list[str]) -> str:
    """Generate specific fix instructions based on validation errors."""
    instructions = [
        f"## REVISION REQUIRED FOR {agent_name}",
        "",
        "Your previous output failed validation. Please fix these issues:",
        "",
    ]

    # Map error names to specific fix instructions
    FIX_GUIDANCE = {
        "research_questions": "Add 3+ specific research questions in key_research_questions",
        "competitor_targets": "Add 2+ competitors in competitors_to_analyze with name and type",
        "pain_signals": "Add 3+ pain signals with description and evidence_tier",
        "jtbd_trigger": "Add trigger_situation in job_to_be_done (when does need arise)",
        "jtbd_goal": "Add underlying_goal in job_to_be_done (what outcome they want)",
        "jtbd_success": "Add success_definition in job_to_be_done (how they measure success)",
        "uncomfortable_insights": "Add 1+ insight that challenges the product idea",
        "lean_canvas_problem": "Add problem array with 3 problems in lean_canvas",
        "lean_canvas_solution": "Add solution array with 3 solutions in lean_canvas",
        "revenue_streams": "Add 1+ revenue stream with pricing_model",
        "risks_and_mitigations": "Add 3+ risks with mitigation strategies",
        "monthly_projections_count": "Include exactly 12 months in monthly_projections_year_1",
        "profit_math_valid": "Fix profit calculations: profit must equal revenue - costs exactly",
        "scenario_analysis": "Add base_case, optimistic, and pessimistic scenarios",
        "epic_count": "Add 3-5 epics in the epics array",
        "story_count": "Add 5+ user stories across all epics",
        "story_format": "Ensure 80%+ stories have as_a/i_want/so_that OR title/description",
        "technology_stack": "Add 3+ technologies with name and rationale",
        "real_technologies": "Use real technology names (React, PostgreSQL, AWS, etc.)",
        "architecture_diagram": "Add architecture_diagram_mermaid with valid Mermaid code",
        "applicable_regulations": "Add 1+ applicable regulation (GDPR, HIPAA, etc.)",
        "real_regulations": "Use real regulation names (GDPR, HIPAA, SOC 2, etc.)",
        "experiment_count": "Add 3+ validation experiments",
        "experiments_complete": "Each experiment needs success_criteria, failure_criteria, instructions",
        "screen_count": "Add 3+ screens in the screens array",
        "screens_have_react_code": "Add react_code (80+ chars) to 70%+ of screens",
        "react_code_valid": "React code must have function/const, JSX, and useState",
        "no_placeholders": "Remove placeholder text (Lorem ipsum, TODO, TBD, Item 1)",
    }

    for error in errors:
        rule_name = error.replace("FAILED: ", "")
        guidance = FIX_GUIDANCE.get(rule_name, f"Fix the {rule_name} requirement")
        instructions.append(f"- {guidance}")

    instructions.append("")
    instructions.append("Address ALL issues above before finalizing your response.")

    return "\n".join(instructions)


def get_retry_prompt(
    agent_name: str,
    original_output: dict[str, Any],
    validation_result: ValidationResult,
) -> str:
    """
    Generate a retry prompt with fix instructions.

    Args:
        agent_name: The agent name
        original_output: The failed output
        validation_result: The validation result

    Returns:
        Prompt text to prepend to retry request
    """
    return f"""
{validation_result.fix_instructions}

## PREVIOUS OUTPUT (for reference)
Your previous output had {len(validation_result.errors)} validation failures.

Key fields that need fixing: {', '.join(e.replace('FAILED: ', '') for e in validation_result.errors)}

Please regenerate the complete output, ensuring all mandatory fields are present and properly formatted.
"""
