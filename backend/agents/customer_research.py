"""
Market Hypothesis Generator for the Product Discovery Multi-Agent System.

This agent generates hypotheses about target users, pain points,
market segments, and competitive landscape. These are AI-generated
assumptions that require validation through customer interviews.

Also generates visual data for competitive positioning charts.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm_with_grounding, extract_feedback_for_agent
from agents.claim_extractor import extract_and_store_claims
from agents.prompts import CUSTOMER_RESEARCH_PROMPT, format_prompt
from agents.state import DiscoveryState
from models.schemas import CustomerResearch, SessionStatus
from models.visual_schemas import CompetitivePositioning

logger = structlog.get_logger(__name__)

AGENT_NAME = "Market Hypothesis Generator"


async def run_customer_research_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Customer Research Agent.

    This agent:
    1. Analyzes the product idea for user personas
    2. Identifies pain points and market segments
    3. Estimates market size (TAM/SAM/SOM)
    4. Analyzes competitive landscape
    5. Identifies market trends and validation assumptions

    Args:
        state: Current discovery state with product idea and context.

    Returns:
        DiscoveryState: Updated state with customer research output.
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

    # Extract revision feedback if this is a revision iteration
    # Check both critique_feedback (standard path) and _injected_revision_context (enhanced path)
    revision_feedback = extract_feedback_for_agent(
        state.get("critique_feedback"),
        "customer_research_feedback",
    )

    # Also check for injected revision context from facilitator's _rerun_weak_sections
    injected_context = state.get("_injected_revision_context")
    if injected_context and not revision_feedback:
        # Use the injected context if no standard feedback
        revision_feedback = injected_context
    elif injected_context and revision_feedback:
        # Combine both contexts
        revision_feedback = f"{revision_feedback}\n\n{injected_context}"

    # Format the prompt with all context
    prompt = format_prompt(
        template=CUSTOMER_RESEARCH_PROMPT,
        product_idea=state["product_idea"],
        industry=state.get("industry"),
        target_market=state.get("target_market"),
        constraints=state.get("constraints"),
        additional_context=state.get("additional_context"),
        revision_context=revision_feedback,
        iteration=state.get("iteration", 1),
    )

    # Call the LLM with Google Search grounding for real-world market data
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
            validated_data = CustomerResearch.model_validate(result["data"])
            customer_research_dict = validated_data.model_dump()

            # Extract and validate competitive positioning visual data
            if "competitive_positioning" in result["data"]:
                try:
                    positioning = CompetitivePositioning.model_validate(
                        result["data"]["competitive_positioning"]
                    )
                    customer_research_dict["competitive_positioning"] = positioning.model_dump()
                    logger.info(
                        "visual_data_extracted",
                        agent=AGENT_NAME,
                        session_id=state["session_id"],
                        visual_type="competitive_positioning",
                        competitor_count=len(positioning.competitors),
                    )
                except ValidationError as ve:
                    logger.warning(
                        "visual_data_validation_warning",
                        agent=AGENT_NAME,
                        session_id=state["session_id"],
                        visual_type="competitive_positioning",
                        error=str(ve),
                    )
                    # Store raw data even if validation fails
                    customer_research_dict["competitive_positioning"] = result["data"].get(
                        "competitive_positioning"
                    )

            state["customer_research"] = customer_research_dict

            # Extract claims for cross-reference tracking (v3.0)
            state = await extract_and_store_claims(
                state, "Market Intelligence", "MI", customer_research_dict
            )

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                pain_signals_count=len(validated_data.pain_signals),
                uncomfortable_insights_count=len(validated_data.uncomfortable_insights),
                has_visual_data="competitive_positioning" in customer_research_dict,
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
            state["customer_research"] = result["data"]

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


def get_customer_research_summary(state: DiscoveryState) -> str:
    """
    Get a JSON string summary of customer research for use by other agents.

    Args:
        state: Current discovery state.

    Returns:
        str: JSON string of customer research or empty message.
    """
    research = state.get("customer_research")
    if not research:
        return "Customer research not yet available."

    return json.dumps(research, indent=2, default=str)
