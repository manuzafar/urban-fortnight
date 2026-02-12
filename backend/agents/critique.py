"""
Critique Agent for the Product Discovery Multi-Agent System.

This agent evaluates the complete inception pack, identifies gaps and
inconsistencies, and determines whether another revision iteration is needed.
It serves as the quality gate for the discovery process.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm
from agents.business_strategy import get_business_case_summary
from agents.context_builder import build_cross_reference_summary, build_full_pack_summary
from agents.customer_research import get_customer_research_summary
from agents.product_requirements import get_product_requirements_summary
from agents.prompts import CRITIQUE_PROMPT, EVIDENCE_CRITIQUE_PROMPT, format_prompt
from agents.technical_architect import get_technical_architecture_summary
from agents.state import CritiqueFeedback, DiscoveryState
from config import settings
from models.schemas import QualityAssessment, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Critique Agent"


async def run_critique_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Critique Agent.

    This agent:
    1. Evaluates each section of the inception pack
    2. Scores sections on a 0.0-1.0 scale
    3. Identifies strengths and weaknesses
    4. Provides specific feedback for improvement
    5. Determines if quality threshold is met
    6. Decides if another iteration is needed

    Args:
        state: Current discovery state with all agent outputs.

    Returns:
        DiscoveryState: Updated state with quality assessment and revision flags.
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

    # Get all previous agent outputs for evaluation
    customer_research_json = get_customer_research_summary(state)
    business_case_json = get_business_case_summary(state)
    product_requirements_json = get_product_requirements_summary(state)
    technical_architecture_json = get_technical_architecture_summary(state)

    # Log what data is available for debugging
    has_customer_research = state.get("customer_research") is not None
    has_business_case = state.get("business_case") is not None
    has_product_requirements = state.get("product_requirements") is not None
    has_technical_architecture = state.get("technical_architecture") is not None

    logger.info(
        "critique_inputs",
        session_id=state["session_id"],
        has_customer_research=has_customer_research,
        has_business_case=has_business_case,
        has_product_requirements=has_product_requirements,
        has_technical_architecture=has_technical_architecture,
        tech_arch_json_length=len(technical_architecture_json) if technical_architecture_json else 0,
    )

    # Get previous assessment if this is a later iteration
    previous_assessment = None
    if state.get("quality_assessment"):
        previous_assessment = json.dumps(state["quality_assessment"], indent=2)

    current_iteration = state.get("iteration", 1)
    max_iterations = settings.max_revision_iterations

    # Build a content availability note to help the LLM
    content_note = f"""
## CONTENT AVAILABILITY NOTE
The following sections have been generated and are provided below for your evaluation:
- Customer Research: {"PRESENT" if has_customer_research else "NOT AVAILABLE"}
- Business Case: {"PRESENT" if has_business_case else "NOT AVAILABLE"}
- Product Requirements: {"PRESENT" if has_product_requirements else "NOT AVAILABLE"}
- Technical Architecture: {"PRESENT" if has_technical_architecture else "NOT AVAILABLE"}

IMPORTANT: Only mark a section as "absent" or "missing" if it shows "NOT AVAILABLE" above.
If a section shows "PRESENT", it contains actual content that must be evaluated.
"""

    # Choose between v3.0 evidence-aware critique or legacy critique
    has_cross_reference = state.get("cross_reference_index") is not None

    if has_cross_reference:
        # V3.0: Use evidence-aware critique with 5 dimensions
        cross_reference_summary = build_cross_reference_summary(state, 4000)
        full_pack_summary = build_full_pack_summary(state, 8000)

        prompt = EVIDENCE_CRITIQUE_PROMPT.format(
            cross_reference_summary=cross_reference_summary,
            full_pack_summary=full_pack_summary,
        )

        logger.info(
            "using_evidence_critique",
            session_id=state["session_id"],
            claims_count=state["cross_reference_index"].get("total_claims", 0),
        )
    else:
        # Legacy critique without cross-reference
        prompt = format_prompt(
            template=CRITIQUE_PROMPT,
            product_idea=state["product_idea"],
            customer_research=customer_research_json,
            business_case=business_case_json,
            product_requirements=product_requirements_json,
            technical_architecture=technical_architecture_json,
            iteration=current_iteration,
            max_iterations=max_iterations,
            previous_assessment=previous_assessment,
        )

        # Prepend the content note to help the LLM understand what's available
        prompt = content_note + "\n" + prompt

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
            validated_data = QualityAssessment.model_validate(result["data"])
            state["quality_assessment"] = validated_data.model_dump()

            # Determine if quality passed
            quality_passed = validated_data.overall_score >= settings.min_quality_score
            state["quality_passed"] = quality_passed

            # Determine if revision is needed
            needs_revision = (
                not quality_passed and current_iteration < max_iterations
            )
            state["requires_revision"] = needs_revision

            # Extract revision feedback for other agents
            if needs_revision and "revision_feedback" in result["data"]:
                state["critique_feedback"] = CritiqueFeedback(
                    customer_research_feedback=result["data"]["revision_feedback"].get(
                        "customer_research_feedback", []
                    ),
                    business_strategy_feedback=result["data"]["revision_feedback"].get(
                        "business_strategy_feedback", []
                    ),
                    product_requirements_feedback=result["data"]["revision_feedback"].get(
                        "product_requirements_feedback", []
                    ),
                    technical_architecture_feedback=result["data"]["revision_feedback"].get(
                        "technical_architecture_feedback", []
                    ),
                    priority_improvements=result["data"]["revision_feedback"].get(
                        "priority_improvements", []
                    ),
                )

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                overall_score=validated_data.overall_score,
                quality_passed=quality_passed,
                requires_revision=needs_revision,
                iteration=current_iteration,
            )

        except ValidationError as e:
            # Retry-aware validation error handling
            attempt = state.get("critique_attempt", 1)
            max_retries = settings.max_critique_retries
            error_msg = str(e)

            logger.warning(
                "critique_validation_retry",
                session_id=state["session_id"],
                attempt=attempt,
                max_retries=max_retries,
                error=error_msg,
            )

            if attempt < max_retries:
                # Return state for retry - don't mark as passed
                state["critique_attempt"] = attempt + 1
                state["quality_passed"] = False
                state["requires_revision"] = False  # Don't revise, retry critique
                state["_retry_critique"] = True  # Signal to facilitator
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(f"Critique validation failed (attempt {attempt}): {error_msg}")
            else:
                # Max retries exceeded - accept with warning
                logger.error(
                    "critique_max_retries_exceeded",
                    session_id=state["session_id"],
                    error=error_msg,
                )
                state["quality_assessment"] = result.get("data", {})
                state["quality_passed"] = True
                state["quality_passed_reason"] = "max_critique_retries_exceeded"
                state["requires_revision"] = False
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(f"QUALITY GATE BYPASSED: Critique failed after {max_retries} attempts")

    else:
        # Retry-aware LLM failure handling
        attempt = state.get("critique_attempt", 1)
        max_retries = settings.max_critique_retries
        error_msg = result.get("error", "Unknown error")

        logger.warning(
            "critique_llm_retry",
            session_id=state["session_id"],
            attempt=attempt,
            max_retries=max_retries,
            error=error_msg,
        )

        if attempt < max_retries:
            # Return state for retry
            state["critique_attempt"] = attempt + 1
            state["quality_passed"] = False
            state["requires_revision"] = False
            state["_retry_critique"] = True
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Critique LLM call failed (attempt {attempt}): {error_msg}")
        else:
            # Max retries exceeded
            logger.error(
                "critique_max_retries_exceeded",
                session_id=state["session_id"],
                error=error_msg,
            )
            state["quality_passed"] = True
            state["quality_passed_reason"] = "max_critique_retries_exceeded"
            state["requires_revision"] = False
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"QUALITY GATE BYPASSED: Critique LLM failed after {max_retries} attempts")

    state["updated_at"] = datetime.utcnow().isoformat()
    return state


def should_revise(state: DiscoveryState) -> bool:
    """
    Determine if another revision iteration should be performed.

    Args:
        state: Current discovery state.

    Returns:
        bool: True if revision is needed and allowed.
    """
    current_iteration = state.get("iteration", 1)
    max_iterations = settings.max_revision_iterations

    # Check if we've reached max iterations
    if current_iteration >= max_iterations:
        logger.info(
            "max_iterations_reached",
            session_id=state["session_id"],
            iteration=current_iteration,
        )
        return False

    # Check if quality passed
    if state.get("quality_passed", False):
        return False

    # Check if revision is flagged
    return state.get("requires_revision", False)


def get_quality_summary(state: DiscoveryState) -> dict:
    """
    Get a summary of the quality assessment.

    Args:
        state: Current discovery state.

    Returns:
        dict: Quality summary with key metrics.
    """
    assessment = state.get("quality_assessment")
    if not assessment:
        return {
            "status": "pending",
            "overall_score": None,
            "passed": False,
        }

    return {
        "status": "complete",
        "overall_score": assessment.get("overall_score"),
        "passed": assessment.get("passed", False),
        "ready_for_delivery": assessment.get("ready_for_delivery", False),
        "iteration": assessment.get("iteration", 1),
        "strengths_count": len(assessment.get("strengths", [])),
        "weaknesses_count": len(assessment.get("weaknesses", [])),
        "critical_gaps_count": len(assessment.get("critical_gaps", [])),
    }
