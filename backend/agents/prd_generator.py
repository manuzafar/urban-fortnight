"""
PRD Generator Agent for the Product Discovery Multi-Agent System.

This agent is the Product Manager persona responsible for generating
and refining Product Requirements Documents (PRDs). It takes customer
research and business case as inputs and produces a structured PRD.

Part of the PRD sub-workflow: Generator -> Critic -> (loop) -> Formatter
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.prompts import PRD_GENERATOR_PROMPT
from agents.state import DiscoveryState

logger = structlog.get_logger(__name__)


async def run_prd_generator(state: DiscoveryState) -> dict[str, Any]:
    """
    Generate or refine a PRD based on customer research and business case.

    This agent:
    1. On first iteration: Creates an initial PRD draft
    2. On subsequent iterations: Refines the PRD based on critic feedback

    Args:
        state: Current discovery state with customer research, business case,
               and optionally previous PRD draft and critic feedback.

    Returns:
        dict with state updates:
            - prd_draft: The generated/refined PRD
            - prd_iteration: Updated iteration count
            - current_agent: Agent name for status tracking
    """
    iteration = state.get("prd_iteration", 0) + 1
    is_revision = iteration > 1

    logger.info(
        "prd_generator_start",
        session_id=state.get("session_id"),
        iteration=iteration,
        is_revision=is_revision,
    )

    # Prepare context based on whether this is initial or revision
    if is_revision:
        task_context = f"REVISION ITERATION {iteration}: Improve the PRD based on critic feedback."
        previous_draft = state.get("prd_draft", {})
        critic_feedback = state.get("prd_critic_feedback", [])

        revision_instructions = f"""
## REVISION REQUIRED

This is iteration {iteration}. The previous PRD draft received the following feedback:

### Critic Feedback:
{chr(10).join(f'- {fb}' for fb in critic_feedback) if critic_feedback else 'No specific feedback provided.'}

### Previous PRD Draft:
{json.dumps(previous_draft, indent=2)[:3000]}...

IMPORTANT: Address ALL feedback items while maintaining the strengths of the previous draft.
Focus on the specific improvements requested by the critic.
"""
    else:
        task_context = "INITIAL GENERATION: Create a comprehensive PRD from scratch."
        revision_instructions = ""

    # Format the prompt
    prompt = PRD_GENERATOR_PROMPT.format(
        task_context=task_context,
        product_idea=state.get("product_idea", ""),
        industry=state.get("industry") or "Not specified",
        target_market=state.get("target_market") or "Not specified",
        customer_research=json.dumps(state.get("customer_research", {}), indent=2),
        business_case=json.dumps(state.get("business_case", {}), indent=2),
        revision_instructions=revision_instructions,
    )

    # Call the LLM
    result = await call_llm(prompt, f"PRD Generator (iteration {iteration})")

    if result["success"]:
        prd_draft = result["data"]

        logger.info(
            "prd_generator_success",
            session_id=state.get("session_id"),
            iteration=iteration,
            epics_count=len(prd_draft.get("epics", [])),
            fr_count=len(prd_draft.get("functional_requirements", [])),
            nfr_count=len(prd_draft.get("non_functional_requirements", [])),
        )

        return {
            "prd_draft": prd_draft,
            "prd_iteration": iteration,
            "current_agent": "PRD Generator",
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                f"prd_generator_iteration_{iteration}": {
                    "success": True,
                    "data": prd_draft,
                    "raw_response": result["raw_response"],
                    "tokens_used": result["tokens_used"],
                    "duration_seconds": result["duration_seconds"],
                },
            },
        }
    else:
        logger.error(
            "prd_generator_failed",
            session_id=state.get("session_id"),
            iteration=iteration,
            error=result["error"],
        )

        return {
            "prd_iteration": iteration,
            "current_agent": "PRD Generator",
            "errors": [
                *state.get("errors", []),
                f"PRD Generator (iteration {iteration}) failed: {result['error']}",
            ],
        }
