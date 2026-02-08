"""
Go-to-Market Strategy Agent — executable launch playbook.

This agent creates a detailed GTM strategy including market entry approach,
channel strategy, launch phases, messaging by persona, and growth tactics.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm_with_grounding
from agents.claim_extractor import extract_and_store_claims
from agents.context_builder import build_context_summary
from agents.state import DiscoveryState
from models.schemas import GoToMarket, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Go-to-Market"

GTM_STRATEGY_PROMPT = """You are a VP of Marketing at a high-growth B2B SaaS company that has scaled from $0 to $10M ARR. You don't produce marketing strategy slides — you produce launch playbooks that a marketing team can execute next Monday morning. Every tactic has a timeline, a cost, an expected result, and a way to measure it.

## PRODUCT IDEA
{product_idea}

## INDUSTRY
{industry}

## PERSONAS (your channels and messaging must match how these people discover and evaluate tools)
{personas_summary}

## BUSINESS CASE (your CAC assumptions must be consistent with this)
{business_case_summary}

## COMPETITIVE LANDSCAPE (your positioning must differentiate from these competitors)
{competitive_landscape_summary}

## EVIDENCE TIER RULES (MANDATORY)
- E2: Verified channel data (platform pricing, benchmark CTRs from published sources)
- E3: Industry benchmarks (typical B2B SaaS conversion rates, CAC by channel)
- E4: Your projections — almost everything here will be E4
- E5: Assumptions about buyer behaviour

## YOUR TASK

Create a comprehensive, EXECUTABLE Go-to-Market strategy that a startup team could implement immediately.

### 1. Positioning Statement
Write a clear positioning statement following the format:
"For [target customer] who [needs/wants], [Product] is a [category] that [key benefit]. Unlike [competitors], we [key differentiator]."

### 2. Messaging by Persona
For each key persona from the personas summary, create:
- Tailored headline
- Value proposition (from THEIR perspective)
- 3 key benefits they care about
- 2-3 common objections with responses

### 3. Market Entry Strategy
- Beachhead market: Which specific segment to dominate first
- Why this segment: Strategic rationale
- Expansion path: Sequence of market expansion

### 4. Channel Strategy
For each channel, specify:
- Role (acquisition/activation/retention/revenue/referral)
- Expected CAC
- Time to scale
- Priority rank (1-10)

Recommend 3-5 primary channels with specific tactics.

### 5. Launch Phases
Define 3 phases (e.g., Beta → Soft Launch → Public Launch):
- Duration
- Specific goals with numbers
- Key activities
- Success metrics

### 6. Growth Tactics
Rank 5-8 specific growth tactics by:
- Expected impact (high/medium/low)
- Effort level (high/medium/low)
- Priority order

### 7. Partnership Opportunities
Identify 2-4 strategic partnership types:
- Partner type
- Specific examples (name companies)
- Value exchange (what we give and get)

### 8. Key Metrics Dashboard
Define 5-8 metrics with targets at Month 3, 6, and 12.

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "positioning_statement": "string - full positioning statement",
  "messaging_by_persona": [
    {{
      "persona_name": "string - persona name from input",
      "headline": "string - tailored headline",
      "value_proposition": "string - from their perspective",
      "key_benefits": ["string", "string", "string"],
      "objection_handling": [
        {{"objection": "string", "response": "string"}}
      ]
    }}
  ],
  "market_entry_strategy": {{
    "approach": "direct_sales|product_led|channel_partners|marketplace|hybrid",
    "beachhead_market": "string - specific initial segment",
    "why_this_segment": "string - strategic rationale",
    "expansion_path": ["string - segment 1", "string - segment 2", "string - segment 3"]
  }},
  "channel_strategy": [
    {{
      "channel": "string - channel name (e.g., Content Marketing, LinkedIn Ads)",
      "role": "acquisition|activation|retention|revenue|referral",
      "expected_cac": "string - e.g., $50-100",
      "time_to_scale": "string - e.g., 3-6 months",
      "priority": 1,
      "specific_tactics": ["string - tactic 1", "string - tactic 2"]
    }}
  ],
  "launch_phases": [
    {{
      "phase": "string - phase name (e.g., 'Phase 1: Seed (Weeks 1-4)')",
      "duration": "string - timeline",
      "objective": "string - what success looks like at end of phase",
      "goals": ["string - specific goal with number"],
      "tactics": [
        {{
          "tactic": "string - specific tactic (not generic 'content marketing')",
          "channel": "string - specific channel",
          "budget": "string - monthly cost",
          "expected_result": "string - specific: '500 visits, 25 signups, 3 demos'",
          "measurement": "string - how to measure",
          "timeline": "string - Week 1-2, etc.",
          "evidence_tier": "E3|E4"
        }}
      ],
      "key_activities": ["string - activity"],
      "success_metrics": ["string - metric and target"],
      "total_phase_budget": "string - total budget for phase",
      "phase_success_criteria": "string - measurable gate for next phase"
    }}
  ],
  "growth_tactics": [
    {{
      "tactic": "string - tactic name",
      "category": "acquisition|activation|retention|referral|revenue",
      "description": "string - how to implement",
      "expected_impact": "high|medium|low",
      "effort_level": "high|medium|low",
      "priority": 1
    }}
  ],
  "partnership_opportunities": [
    {{
      "partner_type": "string - type of partner",
      "examples": ["string - company 1", "string - company 2"],
      "value_exchange": "string - what we give and get",
      "priority": "high|medium|low"
    }}
  ],
  "metrics_dashboard": [
    {{
      "metric": "string - metric name",
      "description": "string - what this measures",
      "target_month_3": "string",
      "target_month_6": "string",
      "target_month_12": "string"
    }}
  ],
  "gtm_risks": [
    {{
      "risk": "string - risk description",
      "likelihood": "high|medium|low",
      "mitigation": "string - how to mitigate"
    }}
  ],
  "competitive_response_plan": {{
    "if_competitor_copies": "string - what we do if a competitor launches similar feature",
    "if_incumbent_enters": "string - what we do if major player adds this capability",
    "moat_deepening_tactics": ["string - actions that make us harder to displace"]
  }},
  "total_gtm_budget_estimate": "string - rough budget range for first 12 months"
}}

CRITICAL: Be specific with company names, dollar amounts, and timelines. No generic advice.
"""


async def run_gtm_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Go-to-Market Strategy Agent.

    This agent creates a comprehensive GTM strategy based on:
    - Customer personas
    - Business case
    - Competitive landscape

    Args:
        state: Current discovery state.

    Returns:
        DiscoveryState: Updated state with gtm_plan.
    """
    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Build context from upstream agents
    personas_summary = build_context_summary(state, "detailed_personas", 3000)
    business_case_summary = build_context_summary(state, "business_case", 3000)
    competitive_landscape_summary = build_context_summary(state, "competitive_analysis", 2000)

    prompt = GTM_STRATEGY_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", "Not specified"),
        personas_summary=personas_summary,
        business_case_summary=business_case_summary,
        competitive_landscape_summary=competitive_landscape_summary,
    )

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            validated_data = GoToMarket.model_validate(result["data"])
            gtm_dict = validated_data.model_dump()
            state["gtm_plan"] = gtm_dict

            # Extract claims for cross-reference tracking
            state = await extract_and_store_claims(
                state, "Go-to-Market", "GM", gtm_dict
            )

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                channels=len(validated_data.channel_strategy),
                phases=len(validated_data.launch_phases),
            )
        except ValidationError as e:
            logger.warning(
                "validation_warning",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                error=str(e),
            )
            # Store raw data even if validation fails
            state["gtm_plan"] = result["data"]

            # Still extract claims
            state = await extract_and_store_claims(
                state, "Go-to-Market", "GM", result["data"]
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
