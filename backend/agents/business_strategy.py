"""
Business Strategy Agent for the Product Discovery Multi-Agent System.

This agent creates the business case including Lean Canvas, revenue models,
financial projections, and go-to-market strategy based on customer research.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm_with_grounding, extract_feedback_for_agent
from agents.customer_research import get_customer_research_summary
from agents.prompts import BUSINESS_STRATEGY_PROMPT, format_prompt
from agents.state import DiscoveryState
from models.schemas import BusinessCase, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Business Strategy Agent"


async def run_business_strategy_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Business Strategy Agent.

    This agent:
    1. Creates a Lean Canvas model
    2. Defines revenue streams and pricing models
    3. Analyzes cost structure
    4. Projects financials (Year 1 and Year 3)
    5. Develops go-to-market strategy
    6. Identifies risks and mitigations

    Args:
        state: Current discovery state with customer research.

    Returns:
        DiscoveryState: Updated state with business case output.
    """
    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    # Update state to show current agent
    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Get customer research for context
    customer_research_json = get_customer_research_summary(state)

    # Extract revision feedback if this is a revision iteration
    revision_feedback = extract_feedback_for_agent(
        state.get("critique_feedback"),
        "business_strategy_feedback",
    )

    # Format the prompt with all context
    prompt = format_prompt(
        template=BUSINESS_STRATEGY_PROMPT,
        product_idea=state["product_idea"],
        industry=state.get("industry"),
        target_market=state.get("target_market"),
        constraints=state.get("constraints"),
        additional_context=state.get("additional_context"),
        customer_research=customer_research_json,
        revision_context=revision_feedback,
        iteration=state.get("iteration", 1),
    )

    # Call the LLM with Google Search grounding for industry benchmarks and pricing data
    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    # Store raw agent output
    if "agent_outputs" not in state:
        state["agent_outputs"] = {}
    state["agent_outputs"][AGENT_NAME] = result

    # Update token and timing tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            # Validate the response against our Pydantic model
            validated_data = BusinessCase.model_validate(result["data"])
            state["business_case"] = validated_data.model_dump()

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                revenue_streams_count=len(validated_data.revenue_streams),
                risks_count=len(validated_data.risks_and_mitigations),
            )

        except ValidationError as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(
                "agent_validation_error",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                error=error_msg,
            )

            # Store the raw data even if validation fails
            state["business_case"] = result["data"]

            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"{AGENT_NAME}: {error_msg}")

    else:
        error_msg = result.get("error", "Unknown error")
        logger.error(
            "agent_failed",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            error=error_msg,
        )

        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"{AGENT_NAME}: {error_msg}")

    state["updated_at"] = datetime.utcnow().isoformat()
    return state


def get_business_case_summary(state: DiscoveryState) -> str:
    """
    Get a JSON string summary of business case for use by other agents.

    Args:
        state: Current discovery state.

    Returns:
        str: JSON string of business case or empty message.
    """
    business_case = state.get("business_case")
    if not business_case:
        return "Business case not yet available."

    return json.dumps(business_case, indent=2, default=str)
