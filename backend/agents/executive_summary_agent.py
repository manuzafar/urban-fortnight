"""
Executive Summary Agent — BUILD/INVESTIGATE/PIVOT/KILL recommendation.

This agent synthesizes all pack sections into a narrative executive summary
with a clear recommendation backed by evidence.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm
from agents.claim_extractor import extract_and_store_claims
from agents.context_builder import build_full_pack_summary, build_cross_reference_summary
from agents.state import DiscoveryState
from models.schemas import ExecutiveSummary, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Executive Summary"

EXECUTIVE_SUMMARY_PROMPT = """You are an Executive Brief Writer synthesizing an inception pack into a decision-ready summary.

## FULL INCEPTION PACK SUMMARY
{full_pack_summary}

## EVIDENCE SCORE & CROSS-REFERENCE INDEX
{cross_reference_summary}

## STAKEHOLDER SUMMARY
{stakeholder_summary}

## VALIDATION PRIORITIES
{validation_summary}

## EVIDENCE SCORE
Overall Evidence Score: {evidence_score}/1.0
(Higher = more grounded claims, Lower = more hypotheses)

## YOUR TASK

Create an executive summary that enables a GO/NO-GO decision.

### RECOMMENDATION FRAMEWORK

Based on evidence score and findings:

| Score | Recommendation |
|-------|---------------|
| 0.7+  | BUILD - Strong evidence, proceed with confidence |
| 0.5-0.7 | INVESTIGATE - Run validation experiments first |
| 0.3-0.5 | PIVOT - Significant concerns, need to adjust approach |
| <0.3  | KILL - Too many unvalidated assumptions |

### REQUIRED SECTIONS

1. **Product Identity**
   - Product name
   - Tagline (one line)

2. **Problem & Solution**
   - Problem statement (what pain)
   - Solution overview (how we solve it)
   - Value proposition (why us)

3. **Market Opportunity**
   - Target users (specific segments)
   - Market size (TAM/SAM/SOM with methodology)

4. **Competitive Position**
   - Key differentiators
   - Competitive landscape summary

5. **Financial Summary**
   - Funding required
   - Revenue model
   - Financial projections (Year 1 and Year 3)
   - Break-even timeline
   - Expected ROI

6. **Risk & Compliance**
   - Top 3-5 risks with mitigations
   - Regulatory summary

7. **Go-to-Market**
   - GTM strategy summary
   - Key milestones (12 months)

8. **Success Metrics**
   - 5-7 key KPIs

9. **Recommendation**
   - BUILD / INVESTIGATE / PIVOT / KILL
   - Clear rationale
   - Next steps

10. **Key Decisions**
    - 3-5 decisions requiring executive attention

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "product_name": "string",
  "tagline": "string - max 150 chars",

  "problem_statement": "string - the core problem",
  "solution_overview": "string - how we solve it",
  "value_proposition": "string - why customers choose us",

  "target_users": ["string - segment 1 with description", "string - segment 2"],
  "target_market_size": "string - TAM/SAM/SOM with methodology",

  "key_differentiators": ["string - differentiator 1", "string - differentiator 2"],
  "competitive_landscape": "string - 2-3 sentence summary",

  "funding_required": "string - initial investment",
  "revenue_model": "string - how we make money",
  "financial_projections": "string - Year 1 and Year 3 summary",
  "break_even_timeline": "string - when we break even",
  "expected_roi": "string - 3-year ROI projection",

  "top_risks": [
    "string - risk 1 with mitigation",
    "string - risk 2 with mitigation",
    "string - risk 3 with mitigation"
  ],
  "regulatory_summary": "string - key compliance requirements",

  "gtm_strategy": "string - go-to-market approach",
  "key_milestones": [
    "string - milestone 1 with timeline",
    "string - milestone 2 with timeline"
  ],

  "success_metrics": [
    "string - KPI 1 with target",
    "string - KPI 2 with target"
  ],

  "recommendation": "BUILD|INVESTIGATE|PIVOT|KILL",
  "recommendation_rationale": "string - 2-3 paragraphs explaining the recommendation",
  "evidence_confidence": "high|medium|low",
  "next_steps": [
    "string - immediate action 1",
    "string - immediate action 2",
    "string - immediate action 3"
  ],

  "key_decisions": [
    {{
      "decision": "string - what needs to be decided",
      "options": ["string - option A", "string - option B"],
      "recommendation": "string - which option and why",
      "deadline": "string - when decision is needed",
      "decision_owner": "string - who should decide"
    }}
  ],

  "validation_required_before_build": [
    "string - what must be validated"
  ],
  "assumptions_to_monitor": [
    "string - assumption that could change decision"
  ]
}}

## OUTPUT CHECKLIST (MANDATORY)

Before finalizing your response, verify ALL of the following:

[ ] PRODUCT NAME: Named product (not placeholder)
[ ] TAGLINE: Clear value proposition tagline (max 150 chars)
[ ] PROBLEM: Problem statement with specifics
[ ] SOLUTION: Solution description
[ ] TARGET MARKET: Defined market segments
[ ] DIFFERENTIATORS: 3+ items, each 20+ char, mentioning competitors
[ ] MARKET SIZE: TAM/SAM/SOM figures (not just "large market")
[ ] BUSINESS MODEL: Revenue/pricing approach defined
[ ] FUNDING: funding_required with specific $ amount
[ ] FINANCIAL PROJECTIONS: Year 1 and Year 3 with $ amounts
[ ] KEY DECISIONS: 3-5 decisions with:
    - id, title, context
    - options (2+ per decision)
    - recommendation
[ ] REGULATORY SUMMARY: 2+ regulations mentioned, timeline, cost estimate
[ ] RISKS: 3+ key risks with mitigation
[ ] RECOMMENDATION: Clear BUILD/INVESTIGATE/PIVOT/KILL with rationale
[ ] MILESTONES: Key milestones listed with timeline

CRITICAL:
- Be honest about evidence gaps
- Recommendation MUST match evidence score guidelines
- Include specific numbers where available
- Key decisions should be actionable
"""


async def run_executive_summary_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Executive Summary Agent.

    Synthesizes all sections into a decision-ready summary.
    Runs LAST - after all other agents complete.

    Args:
        state: Current discovery state.

    Returns:
        DiscoveryState: Updated state with executive_summary.
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
    full_pack_summary = build_full_pack_summary(state, 12000)
    cross_reference_summary = build_cross_reference_summary(state, 4000)

    # Get evidence score
    index = state.get("cross_reference_index", {})
    evidence_score = index.get("evidence_score", 0.5)

    # Get stakeholder and validation summaries
    stakeholder_views = state.get("stakeholder_views", {})
    stakeholder_summary = json.dumps(stakeholder_views, indent=2, default=str)[:3000] if stakeholder_views else "Not available"

    validation_playbook = state.get("validation_playbook", {})
    validation_summary = json.dumps(validation_playbook, indent=2, default=str)[:2000] if validation_playbook else "Not available"

    prompt = EXECUTIVE_SUMMARY_PROMPT.format(
        full_pack_summary=full_pack_summary,
        cross_reference_summary=cross_reference_summary,
        evidence_score=round(evidence_score, 2),
        stakeholder_summary=stakeholder_summary,
        validation_summary=validation_summary,
    )

    result = await call_llm(prompt, AGENT_NAME)

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            validated_data = ExecutiveSummary.model_validate(result["data"])
            exec_summary_dict = validated_data.model_dump()
            state["executive_summary"] = exec_summary_dict

            # Extract claims for cross-reference tracking
            state = await extract_and_store_claims(
                state, "Executive Summary", "ES", exec_summary_dict
            )

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                recommendation=exec_summary_dict.get("recommendation", "UNKNOWN"),
            )
        except ValidationError as e:
            logger.warning(
                "validation_warning",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                error=str(e),
            )
            state["executive_summary"] = result["data"]

            # Still extract claims
            state = await extract_and_store_claims(
                state, "Executive Summary", "ES", result["data"]
            )
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
