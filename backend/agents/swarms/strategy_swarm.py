"""
Strategy Swarm for Business Planning.

This swarm runs parallel agents for:
- Business Strategy (existing)
- GTM Strategy (new - go-to-market planning)
- Financial Modeling (new - detailed financial projections)
"""

from typing import Any, Coroutine

import structlog

from agents.business_strategy import run_business_strategy_agent
from agents.state import DiscoveryState
from agents.swarms.base import BaseSwarm

logger = structlog.get_logger(__name__)


class StrategySwarm(BaseSwarm):
    """
    Swarm for business strategy and planning.

    Runs business strategy, GTM planning, and financial modeling
    in parallel to build a comprehensive business case.
    """

    swarm_name = "StrategySwarm"
    agent_names = [
        "business_strategy",
        "gtm_strategy",
        "financial_modeling",
    ]

    def get_agent_tasks(
        self, state: DiscoveryState
    ) -> list[tuple[str, Coroutine[Any, Any, DiscoveryState]]]:
        """
        Get strategy agent coroutines.
        """
        tasks = [
            ("business_strategy", run_business_strategy_agent(state.copy())),
            ("gtm_strategy", run_gtm_strategy(state.copy())),
            ("financial_modeling", run_financial_modeling(state.copy())),
        ]
        return tasks


async def run_gtm_strategy(state: DiscoveryState) -> DiscoveryState:
    """
    Go-to-Market Strategy Agent.

    Focuses on:
    - Market entry strategy
    - Channel strategy
    - Launch planning
    - Growth tactics
    """
    from datetime import datetime
    import json
    from agents.base_agent import call_llm_with_grounding
    from models.schemas import SessionStatus

    AGENT_NAME = "GTM Strategy"

    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Get context from customer research if available
    customer_research = state.get("customer_research", {})

    prompt = f"""You are a Go-to-Market Strategist. Create a detailed GTM plan for this product.

## PRODUCT IDEA
{state['product_idea']}

## INDUSTRY
{state.get('industry', 'Not specified')}

## TARGET MARKET
{state.get('target_market', 'Not specified')}

## CUSTOMER RESEARCH CONTEXT
{json.dumps(customer_research, indent=2, default=str) if customer_research else 'Not yet available'}

## YOUR TASK

Create a comprehensive Go-to-Market strategy:

1. **Market Entry** - How to enter the market
2. **Channel Strategy** - How to reach customers
3. **Launch Plan** - Phases of launch
4. **Growth Tactics** - How to scale
5. **Partnerships** - Strategic partners to pursue

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "market_entry_strategy": {{
    "approach": "direct_sales|product_led|channel_partners|marketplace|hybrid",
    "initial_segment": "string - which segment to target first",
    "beachhead_market": "string - specific initial market to dominate",
    "expansion_path": ["string - sequence of market expansion"]
  }},
  "channel_strategy": {{
    "primary_channels": [
      {{
        "channel": "string - channel name",
        "role": "acquisition|activation|retention|revenue|referral",
        "expected_cac": "string - estimated CAC",
        "time_to_scale": "string"
      }}
    ],
    "channel_mix_rationale": "string - why this mix"
  }},
  "launch_plan": {{
    "phases": [
      {{
        "phase": "string - phase name",
        "duration": "string - timeline",
        "goals": ["string"],
        "key_activities": ["string"],
        "success_metrics": ["string"]
      }}
    ],
    "launch_type": "soft_launch|beta|public_launch|waitlist",
    "launch_date_dependency": "string - what launch depends on"
  }},
  "growth_tactics": [
    {{
      "tactic": "string - tactic name",
      "category": "acquisition|activation|retention|referral|revenue",
      "expected_impact": "high|medium|low",
      "effort_level": "high|medium|low",
      "priority": 1
    }}
  ],
  "partnership_opportunities": [
    {{
      "partner_type": "string - type of partner",
      "examples": ["string - specific company examples"],
      "value_exchange": "string - what we give and get",
      "priority": "high|medium|low"
    }}
  ],
  "key_metrics_to_track": [
    {{
      "metric": "string",
      "target_month_3": "string",
      "target_month_6": "string",
      "target_month_12": "string"
    }}
  ],
  "gtm_risks": [
    {{
      "risk": "string",
      "mitigation": "string"
    }}
  ]
}}

CRITICAL: Respond with ONLY the JSON object. Be specific with tactics and timelines.
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["gtm_plan"] = result["data"]
        logger.info(
            "agent_success",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            channels=len(result["data"].get("channel_strategy", {}).get("primary_channels", [])),
        )
    else:
        logger.error(
            "agent_failed",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            error=result.get("error"),
        )
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"{AGENT_NAME}: {result.get('error')}")

    state["updated_at"] = datetime.utcnow().isoformat()
    return state


async def run_financial_modeling(state: DiscoveryState) -> DiscoveryState:
    """
    Detailed Financial Modeling Agent.

    Creates comprehensive financial projections:
    - Revenue model breakdown
    - Cost structure details
    - Unit economics
    - Funding requirements
    - Scenario analysis
    """
    from datetime import datetime
    import json
    from agents.base_agent import call_llm_with_grounding
    from models.schemas import SessionStatus

    AGENT_NAME = "Financial Modeling"

    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Get context from business case if available
    business_case = state.get("business_case", {})

    prompt = f"""You are a Financial Analyst. Create detailed financial projections for this product.

## PRODUCT IDEA
{state['product_idea']}

## INDUSTRY
{state.get('industry', 'Not specified')}

## BUSINESS CASE CONTEXT
{json.dumps(business_case, indent=2, default=str) if business_case else 'Not yet available'}

## YOUR TASK

Create comprehensive financial projections including:

1. **Revenue Model** - Detailed breakdown of revenue streams
2. **Cost Structure** - Fixed vs variable costs
3. **Unit Economics** - LTV, CAC, margins
4. **Funding Requirements** - Capital needs by stage
5. **Scenario Analysis** - Base, optimistic, pessimistic cases

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "revenue_model": {{
    "primary_revenue_stream": {{
      "model": "subscription|transaction|advertising|marketplace|licensing",
      "pricing_tiers": [
        {{
          "name": "string - tier name",
          "price_monthly": 0,
          "price_annual": 0,
          "target_segment": "string",
          "features": ["string"]
        }}
      ],
      "arpu_estimate": 0
    }},
    "secondary_revenue_streams": [
      {{
        "stream": "string",
        "contribution_percent": 0
      }}
    ]
  }},
  "cost_structure": {{
    "fixed_costs_monthly": {{
      "salaries": 0,
      "infrastructure": 0,
      "tools_and_software": 0,
      "office_and_overhead": 0,
      "total": 0
    }},
    "variable_costs_per_user": {{
      "hosting": 0,
      "support": 0,
      "payment_processing": 0,
      "total": 0
    }},
    "cac_breakdown": {{
      "paid_acquisition": 0,
      "content_marketing": 0,
      "sales_cost": 0,
      "blended_cac": 0
    }}
  }},
  "unit_economics": {{
    "ltv": 0,
    "cac": 0,
    "ltv_cac_ratio": 0.0,
    "gross_margin_percent": 0,
    "payback_period_months": 0,
    "healthy": true
  }},
  "projections": {{
    "year_1": {{
      "revenue": 0,
      "costs": 0,
      "profit": 0,
      "users": 0,
      "mrr_end_of_year": 0
    }},
    "year_2": {{
      "revenue": 0,
      "costs": 0,
      "profit": 0,
      "users": 0,
      "mrr_end_of_year": 0
    }},
    "year_3": {{
      "revenue": 0,
      "costs": 0,
      "profit": 0,
      "users": 0,
      "mrr_end_of_year": 0
    }}
  }},
  "funding_requirements": {{
    "pre_seed": {{
      "amount": 0,
      "runway_months": 0,
      "key_milestones": ["string"]
    }},
    "seed": {{
      "amount": 0,
      "runway_months": 0,
      "key_milestones": ["string"]
    }},
    "series_a": {{
      "amount": 0,
      "runway_months": 0,
      "key_milestones": ["string"]
    }}
  }},
  "scenario_analysis": {{
    "base_case": {{
      "assumptions": ["string"],
      "year_3_revenue": 0,
      "probability": "50%"
    }},
    "optimistic": {{
      "assumptions": ["string"],
      "year_3_revenue": 0,
      "probability": "25%"
    }},
    "pessimistic": {{
      "assumptions": ["string"],
      "year_3_revenue": 0,
      "probability": "25%"
    }}
  }},
  "key_financial_risks": [
    {{
      "risk": "string",
      "impact": "string",
      "mitigation": "string"
    }}
  ]
}}

CRITICAL: Respond with ONLY the JSON object. Use realistic numbers based on industry benchmarks.
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["financial_model"] = result["data"]
        logger.info(
            "agent_success",
            agent=AGENT_NAME,
            session_id=state["session_id"],
        )
    else:
        logger.error(
            "agent_failed",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            error=result.get("error"),
        )
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"{AGENT_NAME}: {result.get('error')}")

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
