"""
Base prompt utilities and helper functions.

This module contains shared utilities for formatting prompts
and common helper functions used across all agent prompts.
"""


def format_prompt(
    template: str,
    product_idea: str,
    industry: str | None = None,
    target_market: str | None = None,
    constraints: list[str] | None = None,
    additional_context: str | None = None,
    customer_research: str | None = None,
    business_case: str | None = None,
    product_requirements: str | None = None,
    prd: str | None = None,
    technical_architecture: str | None = None,
    legal_regulatory_review: str | None = None,
    revision_context: str | None = None,
    iteration: int = 1,
    max_iterations: int = 3,
    previous_assessment: str | None = None,
    regulatory_hints: str | None = None,
    preliminary_legal_scan: str | None = None,
    upstream_constraints: str | None = None,
) -> str:
    """
    Format a prompt template with the provided context.

    Args:
        template: The prompt template string.
        product_idea: The product idea being analyzed.
        industry: Optional industry context.
        target_market: Optional target market specification.
        constraints: Optional list of constraints.
        additional_context: Any additional context.
        customer_research: JSON string of customer research output.
        business_case: JSON string of business case output.
        product_requirements: JSON string of PRD output.
        prd: Alias for product_requirements (used by legal agent).
        technical_architecture: JSON string of technical architecture output.
        legal_regulatory_review: JSON string of legal & regulatory review output.
        revision_context: Feedback from previous iteration for improvement.
        iteration: Current iteration number.
        max_iterations: Maximum allowed iterations.
        previous_assessment: Previous quality assessment for reference.

    Returns:
        str: Formatted prompt ready for LLM.
    """
    # Use prd as fallback for product_requirements
    prd_value = product_requirements or prd or "Not yet available"

    return template.format(
        product_idea=product_idea,
        industry=industry or "Not specified",
        target_market=target_market or "Not specified",
        constraints=", ".join(constraints) if constraints else "None specified",
        additional_context=additional_context or "None provided",
        customer_research=customer_research or "Not yet available",
        business_case=business_case or "Not yet available",
        product_requirements=prd_value,
        prd=prd_value,
        technical_architecture=technical_architecture or "Not yet available",
        legal_regulatory_review=legal_regulatory_review or "Not yet available",
        revision_context=_format_revision_context(revision_context),
        iteration=iteration,
        max_iterations=max_iterations,
        previous_assessment=_format_previous_assessment(previous_assessment),
        regulatory_hints=regulatory_hints or "None identified yet",
        preliminary_legal_scan=preliminary_legal_scan or "Not yet available",
        upstream_constraints=_format_upstream_constraints(upstream_constraints),
    )


def _format_revision_context(feedback: str | None) -> str:
    """Format revision feedback for inclusion in prompts."""
    if not feedback:
        return ""

    return f"""
## REVISION INSTRUCTIONS

This is a revision based on quality feedback. Please address the following improvements:

{feedback}

Focus on addressing the specific feedback while maintaining the quality of areas that were already strong.
"""


def _format_upstream_constraints(constraints: str | None) -> str:
    """
    Format upstream constraints for inclusion in prompts.

    These constraints come from the constraint_broadcaster and represent
    established facts from upstream phases that this agent must align with.
    """
    if not constraints:
        return ""

    return f"""
## UPSTREAM CONSTRAINTS (MANDATORY)

The following constraints have been established by upstream agents and MUST be respected in your output.
Do NOT contradict these values. If you believe a constraint is incorrect, note it explicitly but still align your output.

{constraints}

Failure to align with these constraints will result in consistency errors and required revisions.
"""


def _format_previous_assessment(assessment: str | None) -> str:
    """Format previous assessment for the critique agent."""
    if not assessment:
        return ""

    return f"""
## PREVIOUS ASSESSMENT

This is a re-evaluation after revisions. The previous assessment was:

{assessment}

Evaluate whether the identified issues have been adequately addressed.
"""
