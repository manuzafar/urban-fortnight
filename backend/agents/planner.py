"""
Planning Agent for the Product Discovery Multi-Agent System.

The Planning Agent runs first in the workflow to analyze the product idea
and create a research plan that guides all subsequent agents. This enables:

1. Domain-specific research focus (B2B SaaS vs Consumer vs Healthcare, etc.)
2. Targeted competitor identification
3. Specific regulatory domains to investigate
4. Financial benchmarks to use for projections

This upfront analysis reduces wasted cycles and improves output quality.
"""

import json
from datetime import datetime
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.prompts import PLANNER_PROMPT, format_prompt
from agents.state import DiscoveryState
from models.schemas import SessionStatus

logger = structlog.get_logger(__name__)


async def run_planner_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Planning Agent to create a research plan.

    The planner analyzes the product idea and creates a structured plan
    that guides all downstream agents. This includes:
    - Domain classification (B2B SaaS, Consumer, Marketplace, etc.)
    - Key research questions to answer
    - Named competitors to analyze
    - Specific regulations to review
    - Financial benchmarks to use

    Args:
        state: Current workflow state with product idea and context.

    Returns:
        DiscoveryState: Updated state with research_plan populated.
    """
    logger.info(
        "planner_agent_start",
        session_id=state["session_id"],
        product_idea=state["product_idea"][:100],
    )

    state["current_agent"] = "Planning Agent"
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Format the planning prompt
    prompt = format_prompt(
        template=PLANNER_PROMPT,
        product_idea=state["product_idea"],
        industry=state.get("industry"),
        target_market=state.get("target_market"),
        constraints=state.get("constraints"),
        additional_context=state.get("additional_context"),
    )

    # Call LLM (uses gemini-2.0-flash for speed)
    result = await call_llm(prompt, "Planning Agent")

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get(
        "tokens_used", 0
    )
    state["total_duration_seconds"] = state.get(
        "total_duration_seconds", 0.0
    ) + result.get("duration_seconds", 0.0)

    if result["success"]:
        research_plan = result["data"]

        # Validate the research plan has required fields
        required_fields = [
            "domain_type",
            "key_research_questions",
            "competitors_to_analyze",
            "regulatory_domains",
        ]
        missing_fields = [f for f in required_fields if f not in research_plan]

        if missing_fields:
            logger.warning(
                "planner_missing_fields",
                session_id=state["session_id"],
                missing=missing_fields,
            )
            # Add defaults for missing fields
            research_plan.setdefault("domain_type", "general")
            research_plan.setdefault("key_research_questions", [])
            research_plan.setdefault("competitors_to_analyze", [])
            research_plan.setdefault("regulatory_domains", [])
            research_plan.setdefault("financial_benchmarks", {})

        state["research_plan"] = research_plan

        logger.info(
            "planner_agent_success",
            session_id=state["session_id"],
            domain_type=research_plan.get("domain_type"),
            num_questions=len(research_plan.get("key_research_questions", [])),
            num_competitors=len(research_plan.get("competitors_to_analyze", [])),
            num_regulations=len(research_plan.get("regulatory_domains", [])),
        )
    else:
        # Create a minimal fallback plan
        logger.error(
            "planner_agent_failed",
            session_id=state["session_id"],
            error=result.get("error"),
        )
        state["research_plan"] = _create_fallback_plan(state)
        state["errors"] = state.get("errors", []) + [
            f"Planning Agent: {result.get('error', 'Unknown error')}"
        ]

    return state


def _create_fallback_plan(state: DiscoveryState) -> dict[str, Any]:
    """
    Create a fallback research plan when the LLM call fails.

    Extracts basic guidance from the product idea and context.

    Args:
        state: Current workflow state.

    Returns:
        dict: Minimal research plan.
    """
    product_idea = state.get("product_idea", "").lower()
    industry = (state.get("industry") or "").lower()
    combined = product_idea + " " + industry

    # Infer domain type from keywords
    # Order matters - check more specific domains first
    domain_type = "general"
    if any(kw in combined for kw in ["health", "medical", "patient", "clinical", "hospital"]):
        domain_type = "Healthcare"
    elif any(kw in combined for kw in ["fintech", "finance", "banking", "payment", "financial"]):
        domain_type = "Fintech"
    elif any(kw in combined for kw in ["marketplace", "two-sided", "buyer", "seller"]):
        domain_type = "Marketplace"
    elif any(kw in combined for kw in ["enterprise", "b2b", "saas", "business software"]):
        domain_type = "B2B_SaaS"
    elif any(kw in combined for kw in ["consumer", "lifestyle", "personal"]):
        domain_type = "Consumer"

    return {
        "domain_type": domain_type,
        "key_research_questions": [
            "What is the total addressable market size?",
            "Who are the main competitors and how are they positioned?",
            "What are the primary customer pain points?",
            "What is the typical pricing model in this space?",
            "What regulations apply to this product?",
        ],
        "competitors_to_analyze": [],  # Will be identified during research
        "regulatory_domains": [],  # Will be identified based on domain
        "financial_benchmarks": {
            "note": "Benchmarks will be researched during business strategy phase"
        },
        "fallback": True,
    }


def get_plan_context_for_agent(
    research_plan: dict[str, Any] | None,
    agent_name: str,
) -> str:
    """
    Extract relevant context from the research plan for a specific agent.

    This allows each agent to receive targeted guidance from the planner.

    Args:
        research_plan: The research plan from the planner agent.
        agent_name: The name of the agent requesting context.

    Returns:
        str: Formatted context string to inject into the agent's prompt.
    """
    if not research_plan:
        return ""

    context_parts = []

    # Domain type is relevant for all agents
    domain_type = research_plan.get("domain_type", "general")
    context_parts.append(f"Domain Classification: {domain_type}")

    # Agent-specific context
    if agent_name in ["customer_research", "Customer Research Agent"]:
        questions = research_plan.get("key_research_questions", [])
        if questions:
            context_parts.append("\nKey Research Questions to Address:")
            for i, q in enumerate(questions[:7], 1):
                context_parts.append(f"  {i}. {q}")

        competitors = research_plan.get("competitors_to_analyze", [])
        if competitors:
            # Handle both string and dict formats for competitors
            names = []
            for c in competitors[:5]:
                if isinstance(c, str):
                    names.append(c)
                elif isinstance(c, dict):
                    names.append(c.get("name", "Unknown"))
            context_parts.append(f"\nCompetitors to Analyze: {', '.join(names)}")

    elif agent_name in ["business_strategy", "Business Strategy Agent"]:
        benchmarks = research_plan.get("financial_benchmarks", {})
        if benchmarks:
            context_parts.append("\nFinancial Benchmarks to Reference:")
            context_parts.append(f"  {json.dumps(benchmarks, indent=2)}")

        competitors = research_plan.get("competitors_to_analyze", [])
        if competitors:
            # Handle both string and dict formats for competitors
            names = []
            for c in competitors[:3]:
                if isinstance(c, str):
                    names.append(c)
                elif isinstance(c, dict):
                    names.append(c.get("name", "Unknown"))
            context_parts.append(
                f"\nCompetitors for Pricing Research: {', '.join(names)}"
            )

    elif agent_name in ["legal_regulatory", "Legal & Regulatory Review Agent"]:
        regulations = research_plan.get("regulatory_domains", [])
        if regulations:
            context_parts.append("\nRegulatory Domains to Review:")
            for reg in regulations:
                context_parts.append(f"  - {reg}")

    elif agent_name in ["technical_architect", "Technical Architect Agent"]:
        tech_considerations = research_plan.get("technical_considerations", [])
        if tech_considerations:
            context_parts.append("\nTechnical Considerations from Planning:")
            for tc in tech_considerations:
                context_parts.append(f"  - {tc}")

    if not context_parts:
        return ""

    return "\n## RESEARCH PLAN CONTEXT\n" + "\n".join(context_parts) + "\n"
