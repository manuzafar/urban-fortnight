"""
Legal & Regulatory Review Agent for the Product Discovery Multi-Agent System.

This agent stress tests product ideas against legal and regulatory requirements
for specific industries, helping teams understand compliance obligations,
potential legal risks, and regulatory barriers before building.
"""

import json
from datetime import datetime
import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm_with_grounding, extract_feedback_for_agent
from agents.prompts import LEGAL_REGULATORY_PROMPT, format_prompt
from agents.state import DiscoveryState
from models.schemas import LegalRegulatoryReview, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Legal & Regulatory Review"


async def run_legal_regulatory_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute Legal & Regulatory Review Agent.

    This agent analyzes the product idea for legal and regulatory compliance,
    identifying industry-specific regulations, licensing requirements, data
    protection obligations, and potential legal risks.

    Args:
        state: Current discovery state.

    Returns:
        DiscoveryState: Updated state with legal & regulatory analysis.
    """
    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    # Update state
    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Get context from previous agents
    customer_research_json = get_customer_research_summary(state)
    business_case_json = get_business_case_summary(state)
    prd_json = get_prd_summary(state)
    tech_arch_json = get_tech_arch_summary(state)

    # Extract revision feedback if iterating
    revision_feedback = extract_feedback_for_agent(
        state.get("critique_feedback"),
        "legal_regulatory_feedback",
    )

    # Format prompt with context
    prompt = format_prompt(
        template=LEGAL_REGULATORY_PROMPT,
        product_idea=state["product_idea"],
        industry=state.get("industry"),
        target_market=state.get("target_market"),
        constraints=state.get("constraints"),
        additional_context=state.get("additional_context"),
        customer_research=customer_research_json,
        business_case=business_case_json,
        prd=prd_json,
        technical_architecture=tech_arch_json,
        revision_context=revision_feedback,
        iteration=state.get("iteration", 1),
    )

    # Call LLM with Google Search grounding for current regulations and compliance requirements
    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    # Store raw output
    if "agent_outputs" not in state:
        state["agent_outputs"] = {}
    state["agent_outputs"][AGENT_NAME] = result

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            # Validate against Pydantic model
            validated_data = LegalRegulatoryReview.model_validate(result["data"])
            state["legal_regulatory_review"] = validated_data.model_dump()

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                risk_level=validated_data.overall_risk_assessment.risk_level,
                regulation_count=len(validated_data.applicable_regulations),
            )
        except ValidationError as e:
            error_msg = f"Validation failed: {str(e)}"
            logger.error(
                "agent_validation_error",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                error=error_msg,
            )
            state["legal_regulatory_review"] = result["data"]
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


def get_legal_regulatory_summary(state: DiscoveryState) -> str:
    """
    Get JSON summary of legal & regulatory review for use by other agents.

    Args:
        state: Current discovery state.

    Returns:
        str: JSON string or empty message.
    """
    data = state.get("legal_regulatory_review")
    if not data:
        return "Legal & regulatory review not yet available."
    return json.dumps(data, indent=2, default=str)


def get_customer_research_summary(state: DiscoveryState) -> str:
    """Get customer research summary from state."""
    data = state.get("customer_research")
    if not data:
        return "Customer research not yet available."
    return json.dumps(data, indent=2, default=str)


def get_business_case_summary(state: DiscoveryState) -> str:
    """Get business case summary from state."""
    data = state.get("business_case")
    if not data:
        return "Business case not yet available."
    return json.dumps(data, indent=2, default=str)


def get_prd_summary(state: DiscoveryState) -> str:
    """Get PRD summary from state."""
    data = state.get("product_requirements")
    if not data:
        return "Product requirements not yet available."
    return json.dumps(data, indent=2, default=str)


def get_tech_arch_summary(state: DiscoveryState) -> str:
    """Get technical architecture summary from state."""
    data = state.get("technical_architecture")
    if not data:
        return "Technical architecture not yet available."
    return json.dumps(data, indent=2, default=str)
