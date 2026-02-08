"""
Technical Architect Agent for the Product Discovery Multi-Agent System.

This agent designs the technical architecture including technology stack,
system components, integrations, and deployment strategy based on the PRD.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm, extract_feedback_for_agent
from agents.business_strategy import get_business_case_summary
from agents.claim_extractor import extract_and_store_claims
from agents.product_requirements import get_product_requirements_summary
from agents.prompts import TECHNICAL_ARCHITECT_PROMPT, format_prompt
from agents.state import DiscoveryState
from models.schemas import SessionStatus, TechnicalArchitecture

logger = structlog.get_logger(__name__)

AGENT_NAME = "Technical Architect Agent"


async def run_technical_architect_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Technical Architect Agent.

    This agent:
    1. Selects architecture style (microservices, monolith, etc.)
    2. Defines technology stack with rationale
    3. Designs system components and their interactions
    4. Plans integration points
    5. Addresses security, scalability, and deployment
    6. Identifies technical risks

    Args:
        state: Current discovery state with PRD and business case.

    Returns:
        DiscoveryState: Updated state with technical architecture output.
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

    # Get previous agent outputs for context
    business_case_json = get_business_case_summary(state)
    product_requirements_json = get_product_requirements_summary(state)

    # Extract revision feedback if this is a revision iteration
    revision_feedback = extract_feedback_for_agent(
        state.get("critique_feedback"),
        "technical_architecture_feedback",
    )

    # Format the prompt with all context
    prompt = format_prompt(
        template=TECHNICAL_ARCHITECT_PROMPT,
        product_idea=state["product_idea"],
        industry=state.get("industry"),
        target_market=state.get("target_market"),
        constraints=state.get("constraints"),
        additional_context=state.get("additional_context"),
        business_case=business_case_json,
        product_requirements=product_requirements_json,
        revision_context=revision_feedback,
        iteration=state.get("iteration", 1),
    )

    # Call the LLM
    result = await call_llm(prompt, AGENT_NAME)

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
            validated_data = TechnicalArchitecture.model_validate(result["data"])
            tech_arch_dict = validated_data.model_dump()
            state["technical_architecture"] = tech_arch_dict

            # Extract claims for cross-reference tracking (v3.0)
            state = await extract_and_store_claims(
                state, "Technical Architecture", "TA", tech_arch_dict
            )

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                architecture_style=validated_data.architecture_style[:50],
                tech_stack_count=len(validated_data.technology_stack),
                components_count=len(validated_data.system_components),
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
            state["technical_architecture"] = result["data"]

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


def get_technical_architecture_summary(state: DiscoveryState) -> str:
    """
    Get a JSON string summary of technical architecture for use by other agents.

    Args:
        state: Current discovery state.

    Returns:
        str: JSON string of technical architecture or empty message.
    """
    architecture = state.get("technical_architecture")
    if not architecture:
        return "Technical architecture not yet available."

    return json.dumps(architecture, indent=2, default=str)
