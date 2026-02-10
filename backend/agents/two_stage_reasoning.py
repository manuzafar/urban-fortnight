"""
Two-Stage Grounded Reasoning — Separates research from structured output.

This module solves the problem of grounded LLM calls mixing research and reasoning,
which leads to fragile JSON parsing. Instead, we separate the process into two stages:

Stage 1: Grounded research (free-form text with citations and real-world data)
Stage 2: Structure into JSON (with schema enforcement)

Benefits:
- Better JSON parsing reliability (no grounding constraints on Stage 2)
- Cleaner separation of concerns
- Preserved research context for debugging
- More accurate evidence tier assignment
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm, call_llm_with_grounding

logger = structlog.get_logger(__name__)


RESEARCH_ENHANCEMENT_PROMPT = """
Provide your findings as detailed text. For each finding:
- Include specific data points with sources
- Include URLs for verifiable claims where available
- Note your confidence level (high/medium/low) for each finding
- Distinguish between facts (verified), industry data (published), and hypotheses (inferred)

Be thorough and cite sources where possible.
"""


STRUCTURING_PROMPT_TEMPLATE = """
Transform the research findings below into the required JSON format.

For each claim or data point in your output, assign an evidence tier:
- E1: Primary research (user-provided data, surveys)
- E2: Verified source (has URL/citation from the research)
- E3: Industry data (references published reports/analyst data)
- E4: Hypothesis (inferred from data, reasoned conclusion)
- E5: Assumption (structural premise, unvalidated)

## RESEARCH FINDINGS TO STRUCTURE:

{research_text}

## STRUCTURING INSTRUCTIONS:

{structure_instructions}

Output valid JSON only.
"""


async def call_llm_two_stage(
    research_prompt: str,
    structure_prompt: str,
    agent_name: str,
    use_grounding: bool = True,
) -> dict[str, Any]:
    """
    Two-stage LLM call for grounded reasoning.

    Stage 1: Grounded research (free-form text with citations)
    Stage 2: Structure into JSON (with schema enforcement)

    This approach improves JSON parsing reliability by separating the
    grounded research step (which cannot use response_mime_type="application/json")
    from the structuring step (which can).

    Args:
        research_prompt: Prompt for Stage 1 research with grounding
        structure_prompt: Instructions for how to structure the output (schema info)
        agent_name: Name of the calling agent for logging
        use_grounding: Whether to use Google Search grounding in Stage 1

    Returns:
        dict containing:
            - success: bool indicating if both stages succeeded
            - data: parsed JSON from Stage 2 (if successful)
            - raw_response: raw text from Stage 2
            - research_text: raw text from Stage 1 (for debugging)
            - error: error message (if failed)
            - tokens_used: total tokens across both stages
            - duration_seconds: total time for both stages
            - grounded: whether grounding was used in Stage 1
            - stage_failed: which stage failed (1 or 2, if applicable)
    """
    logger.info(
        "two_stage_reasoning_start",
        agent=agent_name,
        use_grounding=use_grounding,
    )

    total_tokens = 0
    total_duration = 0.0

    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 1: Research with grounding (free-form text output)
    # ═══════════════════════════════════════════════════════════════════════════

    enhanced_research_prompt = f"""
{research_prompt}

{RESEARCH_ENHANCEMENT_PROMPT}
"""

    try:
        if use_grounding:
            stage1_result = await call_llm_with_grounding(
                prompt=enhanced_research_prompt,
                agent_name=f"{agent_name}_research",
            )
        else:
            stage1_result = await call_llm(
                prompt=enhanced_research_prompt,
                agent_name=f"{agent_name}_research",
            )

        total_tokens += stage1_result.get("tokens_used", 0)
        total_duration += stage1_result.get("duration_seconds", 0.0)

        if not stage1_result.get("success"):
            logger.error(
                "two_stage_research_failed",
                agent=agent_name,
                error=stage1_result.get("error"),
            )
            return {
                "success": False,
                "data": None,
                "raw_response": "",
                "research_text": "",
                "error": f"Stage 1 (research) failed: {stage1_result.get('error')}",
                "tokens_used": total_tokens,
                "duration_seconds": total_duration,
                "grounded": use_grounding,
                "stage_failed": 1,
            }

        # Extract research text - handle both dict and string responses
        research_data = stage1_result.get("data")
        if isinstance(research_data, dict):
            # If Stage 1 returned JSON (unexpected but handle it)
            research_text = json.dumps(research_data, indent=2)
        else:
            research_text = stage1_result.get("raw_response", "")

        logger.info(
            "two_stage_research_complete",
            agent=agent_name,
            research_length=len(research_text),
            tokens=stage1_result.get("tokens_used", 0),
        )

    except Exception as e:
        logger.error(
            "two_stage_research_exception",
            agent=agent_name,
            error=str(e),
            exc_info=True,
        )
        return {
            "success": False,
            "data": None,
            "raw_response": "",
            "research_text": "",
            "error": f"Stage 1 (research) exception: {str(e)}",
            "tokens_used": total_tokens,
            "duration_seconds": total_duration,
            "grounded": use_grounding,
            "stage_failed": 1,
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # STAGE 2: Structure into JSON (with schema enforcement)
    # ═══════════════════════════════════════════════════════════════════════════

    # Build the structuring prompt with the research findings
    full_structure_prompt = STRUCTURING_PROMPT_TEMPLATE.format(
        research_text=research_text[:12000],  # Truncate if very long
        structure_instructions=structure_prompt,
    )

    try:
        # Stage 2 uses call_llm (not grounded) for reliable JSON output
        stage2_result = await call_llm(
            prompt=full_structure_prompt,
            agent_name=f"{agent_name}_structure",
        )

        total_tokens += stage2_result.get("tokens_used", 0)
        total_duration += stage2_result.get("duration_seconds", 0.0)

        if not stage2_result.get("success"):
            logger.error(
                "two_stage_structure_failed",
                agent=agent_name,
                error=stage2_result.get("error"),
            )
            return {
                "success": False,
                "data": None,
                "raw_response": stage2_result.get("raw_response", ""),
                "research_text": research_text,
                "error": f"Stage 2 (structuring) failed: {stage2_result.get('error')}",
                "tokens_used": total_tokens,
                "duration_seconds": total_duration,
                "grounded": use_grounding,
                "stage_failed": 2,
            }

        logger.info(
            "two_stage_reasoning_complete",
            agent=agent_name,
            total_tokens=total_tokens,
            total_duration=round(total_duration, 2),
        )

        return {
            "success": True,
            "data": stage2_result["data"],
            "raw_response": stage2_result.get("raw_response", ""),
            "research_text": research_text,
            "error": None,
            "tokens_used": total_tokens,
            "duration_seconds": total_duration,
            "grounded": use_grounding,
            "model_used": stage2_result.get("model_used"),
        }

    except Exception as e:
        logger.error(
            "two_stage_structure_exception",
            agent=agent_name,
            error=str(e),
            exc_info=True,
        )
        return {
            "success": False,
            "data": None,
            "raw_response": "",
            "research_text": research_text,
            "error": f"Stage 2 (structuring) exception: {str(e)}",
            "tokens_used": total_tokens,
            "duration_seconds": total_duration,
            "grounded": use_grounding,
            "stage_failed": 2,
        }


async def call_llm_two_stage_with_constraints(
    research_prompt: str,
    structure_prompt: str,
    agent_name: str,
    constraints_prompt: str | None = None,
    use_grounding: bool = True,
) -> dict[str, Any]:
    """
    Two-stage LLM call with constraint injection.

    This variant injects constraints into both stages:
    - Stage 1 receives constraints as context for research
    - Stage 2 receives constraints for structuring alignment

    Args:
        research_prompt: Prompt for Stage 1 research
        structure_prompt: Instructions for structuring
        agent_name: Name of the calling agent
        constraints_prompt: Formatted constraints from constraint_broadcaster
        use_grounding: Whether to use grounding in Stage 1

    Returns:
        dict with same structure as call_llm_two_stage
    """
    # Inject constraints into both prompts
    if constraints_prompt:
        enhanced_research = f"""
{constraints_prompt}

---

{research_prompt}
"""
        enhanced_structure = f"""
{constraints_prompt}

---

{structure_prompt}
"""
    else:
        enhanced_research = research_prompt
        enhanced_structure = structure_prompt

    return await call_llm_two_stage(
        research_prompt=enhanced_research,
        structure_prompt=enhanced_structure,
        agent_name=agent_name,
        use_grounding=use_grounding,
    )
