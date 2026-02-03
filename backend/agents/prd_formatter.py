"""
PRD Formatter Agent for the Product Discovery Multi-Agent System.

This agent validates and formats the final PRD, ensuring all IDs are
consistent and the structure is correct before passing to the
Technical Architect.

Part of the PRD sub-workflow: Generator -> Critic -> (loop) -> Formatter
"""

import json
from datetime import datetime
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.prompts import PRD_FORMATTER_PROMPT
from agents.state import DiscoveryState

logger = structlog.get_logger(__name__)


async def run_prd_formatter(state: DiscoveryState) -> dict[str, Any]:
    """
    Format and validate the final PRD.

    This agent:
    1. Validates PRD structure
    2. Ensures all IDs are sequential and properly formatted
    3. Adds missing optional fields with defaults
    4. Generates statistics about the PRD
    5. Sets the final product_requirements in state

    Args:
        state: Current discovery state with approved PRD draft.

    Returns:
        dict with state updates:
            - product_requirements: The final formatted PRD
            - current_agent: Agent name for status tracking
    """
    iteration = state.get("prd_iteration", 1)

    logger.info(
        "prd_formatter_start",
        session_id=state.get("session_id"),
        prd_iterations_completed=iteration,
    )

    prd_draft = state.get("prd_draft", {})

    # Format the prompt
    prompt = PRD_FORMATTER_PROMPT.format(
        prd_draft=json.dumps(prd_draft, indent=2),
    )

    # Call the LLM
    result = await call_llm(prompt, "PRD Formatter")

    if result["success"]:
        formatted_prd = result["data"]

        # Ensure we have required metadata
        if "version" not in formatted_prd:
            formatted_prd["version"] = "1.0"
        if "formatted_at" not in formatted_prd:
            formatted_prd["formatted_at"] = datetime.utcnow().isoformat()

        # Calculate statistics if not present
        if "statistics" not in formatted_prd:
            formatted_prd["statistics"] = _calculate_statistics(formatted_prd)

        # Store the quality score from the critic for reference
        formatted_prd["quality_score"] = state.get("prd_critic_score", 0.0)
        formatted_prd["iterations_required"] = iteration

        logger.info(
            "prd_formatter_success",
            session_id=state.get("session_id"),
            total_epics=formatted_prd.get("statistics", {}).get("total_epics", 0),
            total_stories=formatted_prd.get("statistics", {}).get("total_stories", 0),
            total_story_points=formatted_prd.get("statistics", {}).get("total_story_points", 0),
        )

        return {
            "product_requirements": formatted_prd,
            "current_agent": "PRD Formatter",
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "prd_formatter": {
                    "success": True,
                    "data": formatted_prd,
                    "raw_response": result["raw_response"],
                    "tokens_used": result["tokens_used"],
                    "duration_seconds": result["duration_seconds"],
                },
            },
        }
    else:
        logger.error(
            "prd_formatter_failed",
            session_id=state.get("session_id"),
            error=result["error"],
        )

        # On failure, use the draft as-is with basic formatting
        fallback_prd = _create_fallback_prd(prd_draft, state)

        return {
            "product_requirements": fallback_prd,
            "current_agent": "PRD Formatter",
            "errors": [
                *state.get("errors", []),
                f"PRD Formatter failed: {result['error']} - using fallback formatting",
            ],
        }


def _calculate_statistics(prd: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate statistics for a PRD.

    Args:
        prd: The PRD dictionary.

    Returns:
        dict with PRD statistics.
    """
    epics = prd.get("epics", [])
    total_stories = 0
    total_story_points = 0
    priority_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for epic in epics:
        stories = epic.get("stories", [])
        total_stories += len(stories)

        for story in stories:
            points = story.get("story_points", 0)
            if isinstance(points, int):
                total_story_points += points

            priority = story.get("priority", "medium").lower()
            if priority in priority_distribution:
                priority_distribution[priority] += 1

    # Count priorities in FRs and NFRs too
    for fr in prd.get("functional_requirements", []):
        priority = fr.get("priority", "medium").lower()
        if priority in priority_distribution:
            priority_distribution[priority] += 1

    for nfr in prd.get("non_functional_requirements", []):
        priority = nfr.get("priority", "medium").lower()
        if priority in priority_distribution:
            priority_distribution[priority] += 1

    return {
        "total_epics": len(epics),
        "total_stories": total_stories,
        "total_story_points": total_story_points,
        "total_functional_requirements": len(prd.get("functional_requirements", [])),
        "total_non_functional_requirements": len(prd.get("non_functional_requirements", [])),
        "priority_distribution": priority_distribution,
    }


def _create_fallback_prd(draft: dict[str, Any], state: DiscoveryState) -> dict[str, Any]:
    """
    Create a fallback PRD when formatter fails.

    Args:
        draft: The PRD draft to use as base.
        state: Current discovery state.

    Returns:
        dict with minimally formatted PRD.
    """
    fallback = {
        **draft,
        "version": "1.0",
        "formatted_at": datetime.utcnow().isoformat(),
        "quality_score": state.get("prd_critic_score", 0.0),
        "iterations_required": state.get("prd_iteration", 1),
        "statistics": _calculate_statistics(draft),
        "_fallback_formatted": True,
    }

    return fallback
