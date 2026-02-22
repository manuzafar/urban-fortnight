"""
Mini-Critique Module for Stage Reflection Loops.

Provides lightweight critique functionality for each stage to enable
the Generate -> Critique -> Refine pattern.
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm

logger = structlog.get_logger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE CRITIQUE PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

STAGE_CRITIQUE_PROMPTS = {
    "problem_love": """You are a product discovery coach critiquing a Problem Love analysis.

## Problem Love Output:
{stage_output}

## Critique Dimensions (score each 1-10):

1. **Problem Specificity**: Is the problem statement specific enough to validate?
   - Bad: "Users want better collaboration"
   - Good: "Remote PMs struggle to get stakeholder feedback within 48 hours"
   - Score 1-3: Vague, applies to everyone = no one
   - Score 4-6: Somewhat specific, could be more focused
   - Score 7-10: Crystal clear who has this problem and when

2. **Real People Evidence**: Are there real people experiencing this problem?
   - 0 people = score 2
   - 1-2 people = score 5
   - 3+ people = score 8+

3. **Frequency Validation**: Is the frequency claim supported by evidence?
   - No evidence = score 3
   - Some anecdotes = score 6
   - Interview data = score 9

4. **Tarpit Awareness**: Has the analysis considered why previous solutions failed?
   - No tarpit check = score 3
   - Basic tarpit check = score 6
   - Thorough with differentiation = score 9

5. **Overall Quality**: Ready to proceed to Customer Truth stage?

## OUTPUT FORMAT (JSON only, no markdown):
{{
    "dimension_scores": {{
        "specificity": 7,
        "real_people": 5,
        "frequency": 6,
        "tarpit_awareness": 8
    }},
    "overall_score": 6.5,
    "passes_threshold": false,
    "feedback": [
        "Problem statement is too vague - specify WHO and WHEN",
        "Add at least 1 more real person you know with this problem",
        "Clarify how you know the problem happens 'weekly'"
    ],
    "suggested_improvements": {{
        "problem_statement_refined": "Remote PMs at Series A startups struggle to...",
        "real_people_additions": "Add: Sarah, PM at Acme Corp - she mentioned this in..."
    }}
}}

Be rigorous but constructive. Score honestly - most first-pass outputs score 5-6.
""",
    "customer_truth": """You are critiquing a Customer Truth analysis.

## Customer Truth Output:
{stage_output}

## Critique Dimensions (score each 1-10):

1. **Interview Quality**: Are interviews properly structured with struggling moments?
   - Score based on: key quotes, emotions captured, workarounds documented

2. **Pattern Recognition**: Do patterns emerge from multiple data points?
   - 1 interview mentioning a pain = hypothesis (score 4)
   - 2+ interviews = emerging pattern (score 7)
   - 3+ interviews with quotes = validated pattern (score 9)

3. **Evidence Grounding**: Are claims tied to specific interview quotes?
   - Assertions without evidence = score 3
   - Some evidence = score 6
   - Every pattern has quote evidence = score 9

4. **Gap Identification**: Are interview gaps clearly identified?
   - No gaps mentioned = score 4
   - Generic gaps = score 6
   - Specific actionable gaps = score 9

## OUTPUT FORMAT (JSON only):
{{
    "dimension_scores": {{
        "interview_quality": 6,
        "pattern_recognition": 5,
        "evidence_grounding": 7,
        "gap_identification": 6
    }},
    "overall_score": 6.0,
    "passes_threshold": false,
    "feedback": [
        "Pain patterns need more interview backing",
        "Add direct quotes to support claims"
    ],
    "suggested_improvements": {{
        "patterns_to_strengthen": ["Pain pattern X needs more evidence"]
    }},
    "evidence_tier": "E3"
}}
""",
    "opportunity_mapping": """You are critiquing an Opportunity Mapping analysis.

## Opportunity Mapping Output:
{stage_output}

## Critique Dimensions:

1. **Four Forces Balance**: Is the force calculation accurate?
   - Are push/pull/anxiety/habit forces properly weighted?
   - Does force_balance math check out?

2. **Opportunity Tree Quality**: Are opportunities specific and actionable?
   - Vague opportunities = score 4
   - Specific but generic = score 6
   - Interview-backed, specific opportunities = score 9

3. **Evidence Linkage**: Are opportunities linked to customer patterns?
   - No evidence = score 3
   - Some interview references = score 6
   - Clear traceability to interviews = score 9

4. **Primary Opportunity Selection**: Is the choice justified?
   - No justification = score 3
   - Basic justification = score 6
   - Data-driven selection = score 9

## OUTPUT FORMAT (JSON only):
{{
    "dimension_scores": {{
        "four_forces_balance": 7,
        "opportunity_tree_quality": 6,
        "evidence_linkage": 5,
        "primary_opportunity_selection": 6
    }},
    "overall_score": 6.0,
    "passes_threshold": false,
    "feedback": [
        "Opportunities need stronger interview backing",
        "Primary opportunity selection needs clearer justification"
    ],
    "suggested_improvements": {{}}
}}
""",
    "solution_design": """You are critiquing a Solution Design.

## Solution Design Output:
{stage_output}

## Critique Dimensions:

1. **DHM Scoring**: Are Delight/Hard-to-copy/Margin scores justified?
   - Scores without reasoning = score 4
   - Basic reasoning = score 6
   - Thorough, evidence-based reasoning = score 9

2. **Pre-Mortem Quality**: Are tigers/paper tigers/elephants realistic?
   - Generic risks = score 4
   - Some specific risks = score 6
   - Insightful, non-obvious risks = score 9

3. **Solution-Problem Fit**: Does solution address the primary opportunity?
   - Misaligned = score 3
   - Partially aligned = score 6
   - Directly solves the validated pain = score 9

4. **Differentiation Clarity**: Is moat type clearly articulated?
   - No moat = score 3
   - Weak moat = score 5
   - Clear, defensible moat = score 9

## OUTPUT FORMAT (JSON only):
{{
    "dimension_scores": {{
        "dhm_scoring": 6,
        "pre_mortem_quality": 7,
        "solution_problem_fit": 8,
        "differentiation_clarity": 5
    }},
    "overall_score": 6.5,
    "passes_threshold": false,
    "feedback": [
        "Moat type needs clearer articulation",
        "DHM scores need better justification"
    ],
    "suggested_improvements": {{}}
}}
""",
    "validation_plan": """You are critiquing a Validation Plan.

## Validation Plan Output:
{stage_output}

## Critique Dimensions:

1. **Experiment Design**: Are hypotheses falsifiable?
   - Vague hypotheses = score 3
   - Somewhat testable = score 6
   - Clear success/failure criteria = score 9

2. **Rung Progression**: Are experiments ordered by validation ladder?
   - Wrong order = score 3
   - Mostly correct = score 6
   - Perfect progression = score 9

3. **Success Criteria**: Are success/failure criteria measurable?
   - Qualitative only = score 4
   - Some metrics = score 6
   - Clear, measurable thresholds = score 9

4. **Feasibility**: Are timelines and participant counts realistic?
   - Unrealistic = score 3
   - Somewhat realistic = score 6
   - Practical and achievable = score 9

## OUTPUT FORMAT (JSON only):
{{
    "dimension_scores": {{
        "experiment_design": 7,
        "rung_progression": 8,
        "success_criteria": 6,
        "feasibility": 7
    }},
    "overall_score": 7.0,
    "passes_threshold": true,
    "feedback": [
        "Success criteria could be more specific",
        "Consider adding failure criteria"
    ],
    "suggested_improvements": {{}}
}}
""",
}


async def critique_stage_output(
    stage: str,
    output: dict[str, Any],
    evidence_tier: str = "E4",
) -> dict[str, Any]:
    """
    Run mini-critique on a stage output.

    Args:
        stage: The stage name (e.g., "problem_love")
        output: The stage output to critique
        evidence_tier: The current evidence tier (E1-E5)

    Returns:
        Critique result with dimension_scores, overall_score, feedback, etc.
    """
    if stage not in STAGE_CRITIQUE_PROMPTS:
        logger.warning(
            "critique_unknown_stage",
            stage=stage,
        )
        return {
            "dimension_scores": {},
            "overall_score": 5.0,
            "passes_threshold": False,
            "feedback": [f"No critique available for stage: {stage}"],
            "suggested_improvements": {},
        }

    prompt = STAGE_CRITIQUE_PROMPTS[stage].format(
        stage_output=json.dumps(output, indent=2, default=str)
    )

    logger.info(
        "critique_stage_output_start",
        stage=stage,
        evidence_tier=evidence_tier,
    )

    result = await call_llm(prompt, f"{stage}_critique")

    if result.get("success"):
        critique = result["data"]

        # Apply evidence tier weighting - boost score for interview-backed evidence
        if evidence_tier in ["E1", "E2"]:
            original_score = critique.get("overall_score", 0)
            boosted_score = min(10, original_score * 1.1)
            critique["overall_score"] = round(boosted_score, 1)
            logger.info(
                "critique_evidence_boost_applied",
                stage=stage,
                original_score=original_score,
                boosted_score=boosted_score,
                evidence_tier=evidence_tier,
            )

        logger.info(
            "critique_stage_output_complete",
            stage=stage,
            overall_score=critique.get("overall_score"),
            passes_threshold=critique.get("passes_threshold"),
        )

        return critique
    else:
        logger.error(
            "critique_stage_output_failed",
            stage=stage,
            error=result.get("error"),
        )
        # Return a default critique that allows progression
        return {
            "dimension_scores": {},
            "overall_score": 6.0,
            "passes_threshold": False,
            "feedback": ["Unable to critique - please review manually"],
            "suggested_improvements": {},
        }
