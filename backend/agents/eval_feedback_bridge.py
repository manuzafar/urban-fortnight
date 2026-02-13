"""
Eval Feedback Bridge — Converts eval failures to actionable revision feedback.

This module integrates with the eval system to convert eval failures
into specific, actionable feedback that can be injected into the
facilitator.py revision loop.

Key Features:
- Parses eval results and extracts failures by agent
- Converts failures to specific revision instructions
- Integrates with the facilitator's revision loop
- Tracks revision attempts and their outcomes
"""

from dataclasses import dataclass
from typing import Any, Optional
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class EvalFailure:
    """Represents a single eval failure."""
    agent: str
    eval_type: str
    rule_name: str
    expected: Any
    actual: Any
    severity: str  # "critical", "high", "medium", "low"
    fix_suggestion: str


@dataclass
class RevisionFeedback:
    """Revision feedback for an agent."""
    agent_name: str
    failures: list[EvalFailure]
    priority_score: float  # 0-1, higher = more urgent
    revision_instructions: str


# ═══════════════════════════════════════════════════════════════════════════════
# EVAL FAILURE PARSERS
# ═══════════════════════════════════════════════════════════════════════════════

def parse_eval_results(eval_output: dict[str, Any]) -> list[EvalFailure]:
    """
    Parse eval system output and extract failures.

    Args:
        eval_output: Output from the eval system (e.g., from evals.cli)

    Returns:
        List of EvalFailure objects
    """
    failures = []

    # Handle different eval output formats
    if "results" in eval_output:
        # Format from evals.cli run
        for result in eval_output.get("results", []):
            if not result.get("passed", True):
                failures.append(_parse_single_result(result))

    elif "agent_evals" in eval_output:
        # Format from agent-specific evals
        for agent_name, agent_results in eval_output.get("agent_evals", {}).items():
            for result in agent_results:
                if not result.get("passed", True):
                    failure = _parse_single_result(result)
                    failure.agent = agent_name
                    failures.append(failure)

    elif "summary" in eval_output:
        # Format with summary section
        for failure_info in eval_output.get("summary", {}).get("failures", []):
            failures.append(_parse_failure_info(failure_info))

    return failures


def _parse_single_result(result: dict[str, Any]) -> EvalFailure:
    """Parse a single eval result into an EvalFailure."""
    return EvalFailure(
        agent=result.get("agent", result.get("section", "unknown")),
        eval_type=result.get("eval_type", result.get("type", "unknown")),
        rule_name=result.get("rule", result.get("name", "unknown")),
        expected=result.get("expected"),
        actual=result.get("actual"),
        severity=_determine_severity(result),
        fix_suggestion=_generate_fix_suggestion(result),
    )


def _parse_failure_info(failure_info: dict[str, Any]) -> EvalFailure:
    """Parse failure info dict into an EvalFailure."""
    return EvalFailure(
        agent=failure_info.get("agent", "unknown"),
        eval_type=failure_info.get("type", "unknown"),
        rule_name=failure_info.get("rule", "unknown"),
        expected=failure_info.get("expected"),
        actual=failure_info.get("actual"),
        severity=failure_info.get("severity", "medium"),
        fix_suggestion=failure_info.get("suggestion", ""),
    )


def _determine_severity(result: dict[str, Any]) -> str:
    """Determine severity based on eval type and result."""
    eval_type = result.get("eval_type", result.get("type", ""))

    # Schema compliance failures are critical
    if "schema" in eval_type.lower():
        return "critical"

    # Contradiction failures are high
    if "contradiction" in eval_type.lower() or "consistency" in eval_type.lower():
        return "high"

    # Completeness failures are medium
    if "completeness" in eval_type.lower() or "required" in eval_type.lower():
        return "medium"

    return "low"


# ═══════════════════════════════════════════════════════════════════════════════
# FIX SUGGESTION GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

# Mapping of eval types/rules to fix suggestions
FIX_SUGGESTIONS = {
    # Schema compliance
    "schema_compliance": "Ensure all required fields are present and properly typed",
    "missing_field": "Add the missing field with appropriate value",
    "invalid_type": "Fix the field type to match the expected schema",

    # Contradiction failures
    "market_size_mismatch": "Use consistent market size figures across all sections",
    "pricing_mismatch": "Align pricing figures with business case and financial model",
    "target_customer_mismatch": "Use consistent target customer definitions",
    "competitor_mismatch": "Reference the same competitors across all analyses",

    # Completeness failures
    "insufficient_pain_points": "Add more specific, evidence-backed pain points (minimum 3)",
    "incomplete_jtbd": "Complete all three JTBD fields: trigger, goal, success definition",
    "missing_competitors": "Add at least 2 specific competitors with pricing data",
    "missing_risks": "Add at least 3 risks with mitigation strategies",
    "missing_projections": "Include all 12 months of Year 1 projections",
    "missing_scenarios": "Add base, optimistic, and pessimistic scenarios",

    # Quality failures
    "placeholder_detected": "Replace placeholder text (TBD, TODO, Lorem ipsum) with real content",
    "generic_content": "Make content specific to this product, not generic advice",
    "unsupported_claims": "Add evidence tier tags to all significant claims",

    # Math failures
    "profit_calculation_error": "Fix profit calculations: profit must equal revenue - costs exactly",
    "inconsistent_numbers": "Ensure all numbers are internally consistent",

    # Technical failures
    "invalid_react_code": "Fix React code structure: must have function/const, JSX, useState",
    "invalid_mermaid": "Fix Mermaid diagram syntax",
}


def _generate_fix_suggestion(result: dict[str, Any]) -> str:
    """Generate a fix suggestion based on the failure type."""
    eval_type = result.get("eval_type", result.get("type", "")).lower()
    rule_name = result.get("rule", result.get("name", "")).lower()

    # Check for direct match
    key = f"{eval_type}_{rule_name}".replace(" ", "_")
    if key in FIX_SUGGESTIONS:
        return FIX_SUGGESTIONS[key]

    # Check for partial matches
    for pattern, suggestion in FIX_SUGGESTIONS.items():
        if pattern in key or pattern in eval_type or pattern in rule_name:
            return suggestion

    # Default suggestion based on expected/actual
    expected = result.get("expected")
    actual = result.get("actual")
    if expected is not None and actual is not None:
        return f"Expected {expected} but got {actual}. Fix this discrepancy."

    return "Review and fix the failing requirement"


# ═══════════════════════════════════════════════════════════════════════════════
# REVISION FEEDBACK GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_revision_feedback(
    failures: list[EvalFailure],
) -> dict[str, RevisionFeedback]:
    """
    Group failures by agent and generate revision feedback.

    Args:
        failures: List of EvalFailure objects

    Returns:
        Dict mapping agent names to RevisionFeedback
    """
    # Group failures by agent
    failures_by_agent: dict[str, list[EvalFailure]] = {}
    for failure in failures:
        agent = _normalize_agent_name(failure.agent)
        if agent not in failures_by_agent:
            failures_by_agent[agent] = []
        failures_by_agent[agent].append(failure)

    # Generate feedback for each agent
    feedback_map = {}
    for agent_name, agent_failures in failures_by_agent.items():
        priority_score = _calculate_priority_score(agent_failures)
        revision_instructions = _generate_revision_instructions(agent_name, agent_failures)

        feedback_map[agent_name] = RevisionFeedback(
            agent_name=agent_name,
            failures=agent_failures,
            priority_score=priority_score,
            revision_instructions=revision_instructions,
        )

    return feedback_map


def _normalize_agent_name(name: str) -> str:
    """Normalize agent name to standard format."""
    name_lower = name.lower().replace(" ", "_").replace("-", "_")

    # Map common variations
    AGENT_NAME_MAP = {
        "customer_research": "customer_research",
        "market_intelligence": "customer_research",
        "competitive_analysis": "customer_research",
        "business_strategy": "business_case",
        "business_case": "business_case",
        "gtm": "gtm_plan",
        "gtm_strategy": "gtm_plan",
        "go_to_market": "gtm_plan",
        "financial_model": "financial_model",
        "financial_modeling": "financial_model",
        "prd": "product_requirements",
        "product_requirements": "product_requirements",
        "technical_architecture": "technical_architecture",
        "technical_architect": "technical_architecture",
        "legal": "legal_regulatory_review",
        "legal_regulatory": "legal_regulatory_review",
        "executive_summary": "executive_summary",
        "stakeholder": "stakeholder_views",
        "stakeholder_views": "stakeholder_views",
        "validation": "validation_playbook",
        "validation_playbook": "validation_playbook",
        "wireframe": "wireframes",
        "wireframes": "wireframes",
        "prototype": "prototype",
    }

    return AGENT_NAME_MAP.get(name_lower, name_lower)


def _calculate_priority_score(failures: list[EvalFailure]) -> float:
    """Calculate priority score based on failure severity."""
    if not failures:
        return 0.0

    severity_weights = {
        "critical": 1.0,
        "high": 0.7,
        "medium": 0.4,
        "low": 0.2,
    }

    total_weight = sum(
        severity_weights.get(f.severity, 0.2) for f in failures
    )

    # Normalize to 0-1 range (cap at 1.0)
    return min(1.0, total_weight / 3)


def _generate_revision_instructions(
    agent_name: str,
    failures: list[EvalFailure],
) -> str:
    """Generate specific revision instructions for an agent."""
    lines = [
        f"## REVISION REQUIRED: {agent_name}",
        "",
        f"Your output has {len(failures)} eval failures that must be fixed:",
        "",
    ]

    # Group by severity
    critical = [f for f in failures if f.severity == "critical"]
    high = [f for f in failures if f.severity == "high"]
    medium = [f for f in failures if f.severity == "medium"]
    low = [f for f in failures if f.severity == "low"]

    if critical:
        lines.append("### CRITICAL (must fix immediately)")
        for f in critical:
            lines.append(f"- **{f.rule_name}**: {f.fix_suggestion}")
        lines.append("")

    if high:
        lines.append("### HIGH PRIORITY")
        for f in high:
            lines.append(f"- **{f.rule_name}**: {f.fix_suggestion}")
        lines.append("")

    if medium:
        lines.append("### MEDIUM PRIORITY")
        for f in medium:
            lines.append(f"- **{f.rule_name}**: {f.fix_suggestion}")
        lines.append("")

    if low:
        lines.append("### LOW PRIORITY")
        for f in low:
            lines.append(f"- **{f.rule_name}**: {f.fix_suggestion}")
        lines.append("")

    lines.append("Address ALL issues above. The eval system will re-check your output.")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# FACILITATOR INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

def inject_feedback_into_state(
    state: dict[str, Any],
    feedback_map: dict[str, RevisionFeedback],
) -> dict[str, Any]:
    """
    Inject revision feedback into state for facilitator.

    This updates the state's critique_feedback to include eval-based
    revision instructions that agents will see on retry.

    Args:
        state: Current workflow state
        feedback_map: Dict mapping agent names to RevisionFeedback

    Returns:
        Updated state with feedback injected
    """
    # Ensure critique_feedback exists
    if "critique_feedback" not in state or state["critique_feedback"] is None:
        state["critique_feedback"] = {}

    # Map agent names to critique_feedback keys
    FEEDBACK_KEY_MAP = {
        "customer_research": "customer_research_feedback",
        "business_case": "business_strategy_feedback",
        "gtm_plan": "gtm_plan_feedback",
        "financial_model": "financial_model_feedback",
        "product_requirements": "product_requirements_feedback",
        "technical_architecture": "technical_architecture_feedback",
        "legal_regulatory_review": "legal_regulatory_feedback",
        "executive_summary": "executive_summary_feedback",
        "stakeholder_views": "stakeholder_views_feedback",
        "validation_playbook": "validation_playbook_feedback",
        "wireframes": "wireframe_feedback",
        "prototype": "prototype_feedback",
    }

    for agent_name, feedback in feedback_map.items():
        feedback_key = FEEDBACK_KEY_MAP.get(agent_name, f"{agent_name}_feedback")

        # Convert failures to feedback strings
        feedback_strings = []
        for failure in feedback.failures:
            feedback_strings.append(
                f"[EVAL FAILURE] {failure.rule_name}: {failure.fix_suggestion}"
            )

        # Add or extend existing feedback
        if feedback_key in state["critique_feedback"]:
            existing = state["critique_feedback"][feedback_key]
            if isinstance(existing, list):
                state["critique_feedback"][feedback_key] = existing + feedback_strings
            else:
                state["critique_feedback"][feedback_key] = feedback_strings
        else:
            state["critique_feedback"][feedback_key] = feedback_strings

    # Also store revision priorities for facilitator
    revision_priority = []
    for agent_name, feedback in sorted(
        feedback_map.items(),
        key=lambda x: x[1].priority_score,
        reverse=True
    ):
        revision_priority.append({
            "section": agent_name,
            "score": 1.0 - feedback.priority_score,  # Lower score = needs more work
            "feedback": [f.fix_suggestion for f in feedback.failures],
        })

    state["eval_revision_priority"] = revision_priority

    logger.info(
        "eval_feedback_injected",
        agents_needing_revision=list(feedback_map.keys()),
        total_failures=sum(len(f.failures) for f in feedback_map.values()),
    )

    return state


def get_agents_needing_revision(
    feedback_map: dict[str, RevisionFeedback],
    threshold: float = 0.3,
) -> list[str]:
    """
    Get list of agents that need revision based on priority score.

    Args:
        feedback_map: Dict mapping agent names to RevisionFeedback
        threshold: Minimum priority score to trigger revision

    Returns:
        List of agent names needing revision, sorted by priority
    """
    agents = [
        (name, feedback.priority_score)
        for name, feedback in feedback_map.items()
        if feedback.priority_score >= threshold
    ]

    # Sort by priority (highest first)
    agents.sort(key=lambda x: x[1], reverse=True)

    return [name for name, _ in agents]


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def process_eval_output_to_feedback(
    eval_output: dict[str, Any],
    state: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """
    Convenience function to process eval output and update state.

    Args:
        eval_output: Output from eval system
        state: Current workflow state

    Returns:
        Tuple of (updated_state, agents_needing_revision)
    """
    # Parse failures
    failures = parse_eval_results(eval_output)

    if not failures:
        logger.info("no_eval_failures_detected")
        return state, []

    # Generate feedback
    feedback_map = generate_revision_feedback(failures)

    # Inject into state
    updated_state = inject_feedback_into_state(state, feedback_map)

    # Get agents needing revision
    agents_to_revise = get_agents_needing_revision(feedback_map)

    logger.info(
        "eval_feedback_processed",
        total_failures=len(failures),
        agents_to_revise=agents_to_revise,
    )

    return updated_state, agents_to_revise
