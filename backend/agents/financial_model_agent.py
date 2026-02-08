"""
Financial Model Agent — 12-month projections with scenarios.

This agent creates detailed financial projections including revenue model,
cost structure, unit economics, monthly projections, and scenario analysis.
"""

import json
from datetime import datetime

import structlog
from pydantic import ValidationError

from agents.base_agent import call_llm_with_grounding
from agents.claim_extractor import extract_and_store_claims
from agents.context_builder import build_context_summary
from agents.state import DiscoveryState
from models.schemas import FinancialModel, SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Financial Model"

FINANCIAL_MODEL_PROMPT = """You are a Financial Analyst. Create detailed, realistic financial projections for this product.

## PRODUCT IDEA
{product_idea}

## BUSINESS CASE SUMMARY
{business_case_summary}

## GTM SUMMARY
{gtm_summary}

## YOUR TASK

Create a comprehensive financial model with month-by-month Year 1 projections and quarterly Year 2-3 projections.

### MANDATORY: Input Assumptions
List ALL key assumptions with evidence tiers:
- E1: Primary research (user data, validated)
- E2: Verified source (competitor pricing, public data)
- E3: Industry benchmark (analyst reports, benchmarks)
- E4: Hypothesis (your estimate, unvalidated)
- E5: Structural assumption (market convention)

### 1. Revenue Model
Break down the revenue model:
- Primary revenue stream (subscription/transaction/licensing/etc.)
- Pricing tiers with specific prices
- Secondary revenue streams if applicable
- ARPU estimate with derivation

### 2. Cost Structure
Detail all costs:
- Fixed monthly costs (salaries, tools, overhead)
- Variable costs per user
- CAC breakdown by channel

### 3. Unit Economics
Calculate:
- LTV with methodology
- CAC (blended)
- LTV:CAC ratio
- Gross margin percentage
- Payback period in months
- Assessment: healthy/warning/unhealthy

### 4. Monthly Projections (Year 1)
For each of 12 months:
- Revenue
- Costs
- Profit/Loss
- Customer count
- MRR

### 5. Quarterly Projections (Years 2-3)
For 8 quarters (Y2Q1 through Y3Q4):
- Revenue, Costs, Profit
- Customer count
- ARR run rate

### 6. Scenario Analysis
Three scenarios with different assumptions:
- Base case (50% probability)
- Optimistic case (25% probability)
- Pessimistic case (25% probability)

### 7. Funding Requirements
By stage:
- Pre-seed: amount, runway, milestones
- Seed: amount, runway, milestones
- Series A: amount, runway, milestones

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "input_assumptions": [
    {{
      "name": "string - assumption name",
      "value": "string - the value",
      "evidence_tier": "E1|E2|E3|E4|E5",
      "source": "string - source if E1-E3, null if E4-E5",
      "sensitivity": "high|medium|low"
    }}
  ],
  "revenue_model": {{
    "primary_stream": {{
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
      "expected_tier_distribution": {{"tier_name": 0.5}}
    }},
    "secondary_streams": [
      {{"stream": "string", "contribution_percent": 0}}
    ],
    "arpu_estimate": 0,
    "arpu_derivation": "string - how ARPU was calculated"
  }},
  "cost_structure": {{
    "fixed_costs_monthly": {{
      "salaries": 0,
      "infrastructure": 0,
      "tools_and_software": 0,
      "office_and_overhead": 0,
      "marketing_fixed": 0,
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
    "ltv_derivation": "string - how LTV was calculated",
    "cac": 0,
    "ltv_cac_ratio": 0.0,
    "gross_margin_percent": 0,
    "payback_period_months": 0,
    "assessment": "healthy|warning|unhealthy",
    "assessment_rationale": "string"
  }},
  "monthly_projections_year_1": [
    {{
      "month": 1,
      "revenue": 0,
      "costs": 0,
      "profit": 0,
      "customers": 0,
      "mrr": 0,
      "new_customers": 0,
      "churned_customers": 0
    }}
  ],
  "quarterly_projections_year_2_3": [
    {{
      "quarter": "Y2Q1",
      "revenue": 0,
      "costs": 0,
      "profit": 0,
      "customers": 0,
      "arr": 0
    }}
  ],
  "scenario_analysis": {{
    "base_case": {{
      "description": "string",
      "assumptions": ["string - key difference from model"],
      "year_1_revenue": 0,
      "year_3_revenue": 0,
      "year_3_profit": 0,
      "probability": "50%"
    }},
    "optimistic": {{
      "description": "string",
      "assumptions": ["string"],
      "year_1_revenue": 0,
      "year_3_revenue": 0,
      "year_3_profit": 0,
      "probability": "25%"
    }},
    "pessimistic": {{
      "description": "string",
      "assumptions": ["string"],
      "year_1_revenue": 0,
      "year_3_revenue": 0,
      "year_3_profit": 0,
      "probability": "25%"
    }}
  }},
  "funding_requirements": {{
    "pre_seed": {{
      "amount": 0,
      "runway_months": 0,
      "key_milestones": ["string"],
      "use_of_funds": {{"category": 0}}
    }},
    "seed": {{
      "amount": 0,
      "runway_months": 0,
      "key_milestones": ["string"],
      "use_of_funds": {{"category": 0}}
    }},
    "series_a": {{
      "amount": 0,
      "runway_months": 0,
      "key_milestones": ["string"],
      "use_of_funds": {{"category": 0}}
    }},
    "total_required": "string - total funding to profitability"
  }},
  "key_financial_risks": [
    {{
      "risk": "string",
      "impact": "string - quantified if possible",
      "mitigation": "string"
    }}
  ],
  "sensitivity_analysis": {{
    "most_sensitive_assumptions": ["string - assumption 1", "string - assumption 2"],
    "break_even_sensitivity": "string - what changes break-even point"
  }}
}}

CRITICAL:
- All 12 months of Year 1 must be included
- All 8 quarters of Years 2-3 must be included
- Numbers must be internally consistent
- Use realistic industry benchmarks
"""


async def run_financial_model_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Financial Model Agent.

    This agent creates detailed financial projections based on:
    - Business case (unit economics, pricing)
    - GTM plan (channels, customer acquisition)

    Runs AFTER business case and GTM are complete.

    Args:
        state: Current discovery state.

    Returns:
        DiscoveryState: Updated state with financial_model.
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
    business_case_summary = build_context_summary(state, "business_case", 4000)
    gtm_summary = build_context_summary(state, "gtm_plan", 3000)

    prompt = FINANCIAL_MODEL_PROMPT.format(
        product_idea=state["product_idea"],
        business_case_summary=business_case_summary,
        gtm_summary=gtm_summary,
    )

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            validated_data = FinancialModel.model_validate(result["data"])
            financial_dict = validated_data.model_dump()
            state["financial_model"] = financial_dict

            # Extract claims for cross-reference tracking
            state = await extract_and_store_claims(
                state, "Financial Model", "FM", financial_dict
            )

            logger.info(
                "agent_success",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                assumptions=len(validated_data.input_assumptions),
                year1_months=len(validated_data.monthly_projections_year_1),
            )
        except ValidationError as e:
            logger.warning(
                "validation_warning",
                agent=AGENT_NAME,
                session_id=state["session_id"],
                error=str(e),
            )
            # Store raw data even if validation fails
            state["financial_model"] = result["data"]

            # Still extract claims
            state = await extract_and_store_claims(
                state, "Financial Model", "FM", result["data"]
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
