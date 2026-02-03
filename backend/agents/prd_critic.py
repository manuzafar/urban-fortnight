"""
PRD Critic Agent for the Product Discovery Multi-Agent System.

This agent reviews PRD drafts and provides quality scores and feedback.
It determines whether the PRD meets the quality threshold or needs revision.

Part of the PRD sub-workflow: Generator -> Critic -> (loop) -> Formatter
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.prompts import PRD_CRITIC_PROMPT
from agents.state import DiscoveryState
from config import settings

logger = structlog.get_logger(__name__)


async def run_prd_critic(state: DiscoveryState) -> dict[str, Any]:
    """
    Evaluate the PRD draft and determine if it meets quality standards.

    This agent:
    1. Evaluates the PRD against quality criteria
    2. Provides a score (0.0 - 1.0)
    3. Provides specific feedback for improvement
    4. Determines if the PRD passes the quality threshold

    Args:
        state: Current discovery state with PRD draft.

    Returns:
        dict with state updates:
            - prd_critic_score: Quality score (0.0 - 1.0)
            - prd_critic_feedback: List of improvement suggestions
            - prd_quality_passed: Whether PRD passed quality threshold
            - current_agent: Agent name for status tracking
    """
    iteration = state.get("prd_iteration", 1)
    max_iterations = settings.prd_max_iterations
    quality_threshold = settings.prd_quality_threshold

    logger.info(
        "prd_critic_start",
        session_id=state.get("session_id"),
        iteration=iteration,
        max_iterations=max_iterations,
        quality_threshold=quality_threshold,
    )

    prd_draft = state.get("prd_draft", {})

    # Format the prompt
    prompt = PRD_CRITIC_PROMPT.format(
        product_idea=state.get("product_idea", ""),
        iteration=iteration,
        max_iterations=max_iterations,
        prd_draft=json.dumps(prd_draft, indent=2),
        customer_research=json.dumps(state.get("customer_research", {}), indent=2),
        business_case=json.dumps(state.get("business_case", {}), indent=2),
    )

    # Call the LLM
    result = await call_llm(prompt, f"PRD Critic (iteration {iteration})")

    if result["success"]:
        evaluation = result["data"]

        score = evaluation.get("score", 0.0)
        passed = evaluation.get("passed", False)
        improvements = evaluation.get("improvements_needed", [])
        critical_issues = evaluation.get("critical_issues", [])

        # Combine improvements and critical issues as feedback
        all_feedback = critical_issues + improvements

        # Determine if we should pass based on score and threshold
        # Also consider if we've hit max iterations
        at_max_iterations = iteration >= max_iterations
        quality_passed = score >= quality_threshold or at_max_iterations

        if at_max_iterations and not passed:
            logger.warning(
                "prd_critic_max_iterations_reached",
                session_id=state.get("session_id"),
                iteration=iteration,
                score=score,
                threshold=quality_threshold,
            )

        logger.info(
            "prd_critic_success",
            session_id=state.get("session_id"),
            iteration=iteration,
            score=score,
            passed=passed,
            quality_passed=quality_passed,
            improvements_count=len(improvements),
            critical_issues_count=len(critical_issues),
        )

        return {
            "prd_critic_score": score,
            "prd_critic_feedback": all_feedback,
            "prd_quality_passed": quality_passed,
            "current_agent": "PRD Critic",
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                f"prd_critic_iteration_{iteration}": {
                    "success": True,
                    "data": evaluation,
                    "raw_response": result["raw_response"],
                    "tokens_used": result["tokens_used"],
                    "duration_seconds": result["duration_seconds"],
                },
            },
        }
    else:
        logger.error(
            "prd_critic_failed",
            session_id=state.get("session_id"),
            iteration=iteration,
            error=result["error"],
        )

        # On failure, allow proceeding with a warning
        return {
            "prd_critic_score": 0.0,
            "prd_critic_feedback": ["Critic evaluation failed - proceeding with caution"],
            "prd_quality_passed": iteration >= max_iterations,  # Pass if at max iterations
            "current_agent": "PRD Critic",
            "errors": [
                *state.get("errors", []),
                f"PRD Critic (iteration {iteration}) failed: {result['error']}",
            ],
        }
