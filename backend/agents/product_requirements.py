"""
Product Requirements Agent for the Product Discovery Multi-Agent System.

This is the CRITICAL agent that generates the complete Product Requirements
Document (PRD) with user stories, epics, functional requirements, and more.
The PRD is the primary deliverable of the discovery process.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm, extract_feedback_for_agent
from agents.business_strategy import get_business_case_summary
from agents.customer_research import get_customer_research_summary
from agents.prompts import PRODUCT_REQUIREMENTS_PROMPT, format_prompt
from agents.state import DiscoveryState
from models.schemas import ProductRequirementsDocument, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Product Requirements Agent"


async def run_product_requirements_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Product Requirements Agent.

    This agent generates the complete PRD including:
    1. Product overview and objectives
    2. Scope definition (in/out of scope)
    3. 3-5 Epics with 15-25 User Stories total
    4. 8-12 Functional Requirements
    5. 5-10 Non-Functional Requirements
    6. Data model with entities and relationships
    7. Integration requirements
    8. Release plan with phases
    9. Risks and mitigations

    This is the most important agent - the PRD is the core deliverable.

    Args:
        state: Current discovery state with customer research and business case.

    Returns:
        DiscoveryState: Updated state with PRD output.
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
    customer_research_json = get_customer_research_summary(state)
    business_case_json = get_business_case_summary(state)

    # Extract revision feedback if this is a revision iteration
    # Check both critique_feedback (standard path) and _injected_revision_context (enhanced path)
    revision_feedback = extract_feedback_for_agent(
        state.get("critique_feedback"),
        "product_requirements_feedback",
    )

    # Also check for injected revision context from facilitator's _rerun_weak_sections
    injected_context = state.get("_injected_revision_context")
    if injected_context and not revision_feedback:
        revision_feedback = injected_context
    elif injected_context and revision_feedback:
        revision_feedback = f"{revision_feedback}\n\n{injected_context}"

    # Format the prompt with all context
    prompt = format_prompt(
        template=PRODUCT_REQUIREMENTS_PROMPT,
        product_idea=state["product_idea"],
        industry=state.get("industry"),
        target_market=state.get("target_market"),
        constraints=state.get("constraints"),
        additional_context=state.get("additional_context"),
        customer_research=customer_research_json,
        business_case=business_case_json,
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
            validated_data = ProductRequirementsDocument.model_validate(result["data"])
            state["product_requirements"] = validated_data.model_dump()

            # Count stories across all epics
            total_stories = sum(len(epic.stories) for epic in validated_data.epics)

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                epics_count=len(validated_data.epics),
                stories_count=total_stories,
                functional_requirements_count=len(validated_data.functional_requirements),
                nfr_count=len(validated_data.non_functional_requirements),
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
            # This allows the critique agent to still evaluate it
            state["product_requirements"] = result["data"]

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


def get_product_requirements_summary(state: DiscoveryState) -> str:
    """
    Get a JSON string summary of PRD for use by other agents.

    Args:
        state: Current discovery state.

    Returns:
        str: JSON string of PRD or empty message.
    """
    prd = state.get("product_requirements")
    if not prd:
        return "Product requirements not yet available."

    return json.dumps(prd, indent=2, default=str)


def count_user_stories(state: DiscoveryState) -> int:
    """
    Count total user stories across all epics.

    Args:
        state: Current discovery state.

    Returns:
        int: Total number of user stories.
    """
    prd = state.get("product_requirements")
    if not prd:
        return 0

    epics = prd.get("epics", [])
    return sum(len(epic.get("stories", [])) for epic in epics)


def get_story_priority_distribution(state: DiscoveryState) -> dict[str, int]:
    """
    Get distribution of story priorities.

    Args:
        state: Current discovery state.

    Returns:
        dict: Count of stories by priority level.
    """
    prd = state.get("product_requirements")
    if not prd:
        return {}

    distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for epic in prd.get("epics", []):
        for story in epic.get("stories", []):
            priority = story.get("priority", "medium").lower()
            if priority in distribution:
                distribution[priority] += 1

    return distribution
