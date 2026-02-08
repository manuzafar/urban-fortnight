"""
Validation Playbook Agent — 5-8 experiments for E4/E5 claims.

This agent designs specific experiments to validate hypotheses,
prioritized by impact on dependent claims.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm
from agents.context_builder import build_cross_reference_summary, build_context_summary
from agents.state import DiscoveryState
from models.schemas import ValidationPlaybook, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Validation Playbook"

VALIDATION_PLAYBOOK_PROMPT = """You are a Lean Startup Validation Expert designing experiments to test assumptions.

## CROSS-REFERENCE INDEX WITH EVIDENCE TIERS
{cross_reference_summary}

## RISK ASSESSMENT SUMMARY
{risk_summary}

## PRODUCT IDEA
{product_idea}

## YOUR TASK

Design 5-8 specific experiments to validate the highest-impact E4 (Hypothesis) and E5 (Assumption) claims.

### EXPERIMENT PRIORITIZATION
Prioritize experiments that:
1. Test claims with MANY dependent claims (high upgrade potential)
2. Test claims with LOW confidence scores
3. Test claims related to CRITICAL risks
4. Can be completed QUICKLY with LOW cost

### FOR EACH EXPERIMENT

Provide:
1. **Experiment ID**: EXP-1, EXP-2, etc.
2. **Hypothesis Claim ID**: Which claim is being tested
3. **Experiment Name**: Clear, descriptive name
4. **Experiment Type**: interview|survey|landing_page|prototype|concierge|smoke_test
5. **Target Profile**: Exactly who to test with
6. **Specific Instructions**: Step-by-step how to run it
7. **Sample Size**: How many participants/data points
8. **Success Criteria**: Quantitative threshold for success
9. **Failure Criteria**: When to consider hypothesis false
10. **Expected Duration**: How long to run
11. **Cost Estimate**: Budget required
12. **Upgrade Path**: Which claim IDs upgrade if validated
13. **Risk if Skipped**: What happens if we don't validate

### EXPERIMENT TYPES

1. **Customer Interviews** (5-10 interviews)
   - Best for: Understanding motivations, pain points, behaviors
   - Time: 1-2 weeks

2. **Surveys** (50-200 responses)
   - Best for: Quantifying preferences, validating patterns at scale
   - Time: 1-2 weeks

3. **Landing Page Tests**
   - Best for: Validating demand, messaging, pricing
   - Time: 2-4 weeks

4. **Prototype Tests** (5-15 users)
   - Best for: Usability, feature value, workflow validation
   - Time: 2-3 weeks

5. **Concierge Tests** (3-5 customers)
   - Best for: Validating value delivery manually before automation
   - Time: 2-4 weeks

6. **Smoke Tests** (any traffic)
   - Best for: Quickly testing demand without building
   - Time: 1-2 weeks

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "experiments": [
    {{
      "experiment_id": "EXP-1",
      "hypothesis_claim_id": "MI-4",
      "experiment_name": "string - descriptive name",
      "experiment_type": "interview|survey|landing_page|prototype|concierge|smoke_test",
      "target_profile": "string - exactly who to recruit",
      "recruitment_strategy": "string - how to find participants",
      "specific_instructions": "string - step-by-step instructions",
      "key_questions_to_answer": ["string - question 1", "string - question 2"],
      "sample_size": "string - e.g., 8-10 interviews",
      "success_criteria": "string - quantitative threshold (e.g., 7/10 confirm pain point)",
      "failure_criteria": "string - when to consider false (e.g., <3/10 confirm)",
      "expected_duration": "string - e.g., 2 weeks",
      "cost_estimate": "string - e.g., $500-1000",
      "upgrade_path": ["MI-4", "BC-2", "BC-5"],
      "risk_if_skipped": "string - consequences of not validating"
    }}
  ],
  "validation_priorities": [
    {{
      "claim_id": "string",
      "claim_summary": "string - brief statement",
      "priority_rank": 1,
      "reason": "string - why this is high priority",
      "dependent_claims_count": 5
    }}
  ],
  "total_validation_budget": "string - estimated total",
  "total_validation_timeline": "string - e.g., 6-8 weeks",
  "critical_path_experiments": ["EXP-1", "EXP-3"],
  "parallel_experiments": [["EXP-2", "EXP-4"]],
  "validation_dashboard": {{
    "total_experiments": 0,
    "interview_count": 0,
    "survey_responses_needed": 0,
    "landing_page_tests": 0,
    "estimated_total_participants": 0
  }},
  "go_no_go_decision_framework": {{
    "green_light_conditions": ["string - condition for full go"],
    "yellow_light_conditions": ["string - condition for conditional go"],
    "red_light_conditions": ["string - condition for stop"]
  }}
}}

CRITICAL:
- Design experiments that are ACTIONABLE (a team could run them next week)
- Include SPECIFIC success/failure criteria (not vague)
- Reference actual claim IDs from the cross-reference index
- Order experiments by priority
"""


async def run_validation_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Validation Playbook Agent.

    Designs experiments to validate E4/E5 claims.

    Args:
        state: Current discovery state.

    Returns:
        DiscoveryState: Updated state with validation_playbook.
    """
    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Build context
    cross_reference_summary = build_cross_reference_summary(state, 5000)
    risk_summary = build_context_summary(state, "risk_assessment", 2000)

    prompt = VALIDATION_PLAYBOOK_PROMPT.format(
        cross_reference_summary=cross_reference_summary,
        risk_summary=risk_summary,
        product_idea=state["product_idea"],
    )

    result = await call_llm(prompt, AGENT_NAME)

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            validated_data = ValidationPlaybook.model_validate(result["data"])
            playbook_dict = validated_data.model_dump()
            state["validation_playbook"] = playbook_dict

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                experiments_count=len(validated_data.experiments),
            )
        except ValidationError as e:
            logger.warning(
                "validation_warning",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                error=str(e),
            )
            state["validation_playbook"] = result["data"]
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
