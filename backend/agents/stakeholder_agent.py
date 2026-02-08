"""
Stakeholder View Agent — 3-4 role-specific views with objections.

This agent creates tailored summaries for specific stakeholder roles
(CFO, CISO, ARB, VP Product) with anticipated objections and evidence confidence.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm
from agents.claim_extractor import extract_and_store_claims
from agents.context_builder import build_full_pack_summary, build_cross_reference_summary
from agents.state import DiscoveryState
from models.schemas import StakeholderViews, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Stakeholder Views"

STAKEHOLDER_VIEW_PROMPT = """You are a Strategic Advisor preparing stakeholder briefings.

## FULL INCEPTION PACK SUMMARY
{full_pack_summary}

## CROSS-REFERENCE & EVIDENCE INDEX
{cross_reference_summary}

## YOUR TASK

Create tailored views for 4 key stakeholders:
1. **CFO** - Financial viability, ROI, risk/reward
2. **CISO** - Security, compliance, data protection
3. **ARB (Architecture Review Board)** - Technical feasibility, scalability, integration
4. **VP Product** - Market fit, competitive differentiation, user value

For each stakeholder, provide:

### Tailored Summary
A 2-3 paragraph summary written FOR that stakeholder, addressing their specific concerns.
Use their language and priorities.

### Key Questions Answered
3-5 specific questions this pack answers for them.

### Anticipated Objections
3-4 likely objections with:
- The objection itself
- Your response
- Which claim IDs from the cross-reference support your response

### Evidence Confidence
Rate overall confidence for this stakeholder: high/medium/low
Explain what would raise confidence.

### Decision Recommendation
Clear recommendation from their perspective.

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "views": [
    {{
      "stakeholder_role": "CFO",
      "tailored_summary": "string - 2-3 paragraphs written for CFO",
      "key_questions_answered": [
        "string - question 1",
        "string - question 2",
        "string - question 3"
      ],
      "anticipated_objections": [
        {{
          "objection": "string - the concern",
          "response": "string - your response",
          "supporting_claim_ids": ["BC-1", "FM-3"]
        }}
      ],
      "evidence_confidence": "high|medium|low",
      "confidence_improvement": "string - what would raise confidence",
      "decision_recommendation": "string - specific recommendation",
      "key_metrics_for_role": ["string - metric 1", "string - metric 2"]
    }},
    {{
      "stakeholder_role": "CISO",
      "tailored_summary": "string",
      "key_questions_answered": ["string"],
      "anticipated_objections": [{{}}],
      "evidence_confidence": "high|medium|low",
      "confidence_improvement": "string",
      "decision_recommendation": "string",
      "key_metrics_for_role": ["string"]
    }},
    {{
      "stakeholder_role": "ARB",
      "tailored_summary": "string",
      "key_questions_answered": ["string"],
      "anticipated_objections": [{{}}],
      "evidence_confidence": "high|medium|low",
      "confidence_improvement": "string",
      "decision_recommendation": "string",
      "key_metrics_for_role": ["string"]
    }},
    {{
      "stakeholder_role": "VP Product",
      "tailored_summary": "string",
      "key_questions_answered": ["string"],
      "anticipated_objections": [{{}}],
      "evidence_confidence": "high|medium|low",
      "confidence_improvement": "string",
      "decision_recommendation": "string",
      "key_metrics_for_role": ["string"]
    }}
  ],
  "common_concerns": [
    "string - concern shared across stakeholders"
  ],
  "alignment_opportunities": [
    "string - areas where stakeholders can agree"
  ],
  "decision_blockers": [
    "string - issues that could block approval"
  ],
  "recommended_presentation_order": [
    "string - stakeholder 1",
    "string - stakeholder 2"
  ]
}}

CRITICAL:
- Write FROM each stakeholder's perspective
- Use their domain language
- Reference specific claim IDs from the evidence index
- Be honest about evidence gaps
- Anticipate REAL objections they would raise
"""


async def run_stakeholder_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Stakeholder View Agent.

    Creates tailored views for CFO, CISO, ARB, and VP Product.

    Args:
        state: Current discovery state.

    Returns:
        DiscoveryState: Updated state with stakeholder_views.
    """
    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Build comprehensive context
    full_pack_summary = build_full_pack_summary(state, 10000)
    cross_reference_summary = build_cross_reference_summary(state, 4000)

    prompt = STAKEHOLDER_VIEW_PROMPT.format(
        full_pack_summary=full_pack_summary,
        cross_reference_summary=cross_reference_summary,
    )

    result = await call_llm(prompt, AGENT_NAME)

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            validated_data = StakeholderViews.model_validate(result["data"])
            stakeholder_dict = validated_data.model_dump()
            state["stakeholder_views"] = stakeholder_dict

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                views_count=len(validated_data.views),
            )
        except ValidationError as e:
            logger.warning(
                "validation_warning",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                error=str(e),
            )
            state["stakeholder_views"] = result["data"]
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
