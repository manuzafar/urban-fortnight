"""
Delivery Swarm for Product Specification.

This swarm runs parallel agents for:
- PRD Generator (existing via subgraph)
- Technical Architect (existing)
- Legal & Regulatory (existing)
- Risk Assessment (new - dedicated risk analysis)
"""

from typing import Any, Coroutine

import structlog

from agents.claim_extractor import extract_and_store_claims
from agents.prd_subgraph import run_prd_subworkflow
from agents.technical_architect import run_technical_architect_agent
from agents.legal_regulatory import run_legal_regulatory_agent
from agents.state import DiscoveryState
from agents.swarms.base import BaseSwarm

logger = structlog.get_logger(__name__)


class DeliverySwarm(BaseSwarm):
    """
    Swarm for product delivery specifications.

    Runs PRD, technical architecture, legal review, and risk
    assessment in parallel to create complete delivery specs.
    """

    swarm_name = "DeliverySwarm"
    agent_names = [
        "product_requirements",
        "technical_architect",
        "legal_regulatory",
        "risk_assessment",
    ]

    def get_agent_tasks(
        self, state: DiscoveryState
    ) -> list[tuple[str, Coroutine[Any, Any, DiscoveryState]]]:
        """
        Get delivery agent coroutines.
        """
        tasks = [
            ("product_requirements", run_prd_subworkflow(state.copy())),
            ("technical_architect", run_technical_architect_agent(state.copy())),
            ("legal_regulatory", run_legal_regulatory_agent(state.copy())),
            ("risk_assessment", run_risk_assessment(state.copy())),
        ]
        return tasks


async def run_risk_assessment(state: DiscoveryState) -> DiscoveryState:
    """
    Dedicated Risk Assessment Agent.

    Performs comprehensive risk analysis:
    - Market risks
    - Technical risks
    - Financial risks
    - Operational risks
    - Strategic risks

    Creates a risk matrix and mitigation plans.
    """
    from datetime import datetime
    import json
    from agents.base_agent import call_llm_with_grounding
    from models.schemas import SessionStatus

    AGENT_NAME = "Risk Assessment"

    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Gather context from all available data
    customer_research = state.get("customer_research", {})
    business_case = state.get("business_case", {})
    technical_architecture = state.get("technical_architecture", {})

    prompt = f"""You are a Risk Management Expert. Conduct a comprehensive risk assessment for this product.

## PRODUCT IDEA
{state['product_idea']}

## INDUSTRY
{state.get('industry', 'Not specified')}

## CUSTOMER RESEARCH
{json.dumps(customer_research, indent=2, default=str)[:2000] if customer_research else 'Not available'}

## BUSINESS CASE
{json.dumps(business_case, indent=2, default=str)[:2000] if business_case else 'Not available'}

## TECHNICAL ARCHITECTURE
{json.dumps(technical_architecture, indent=2, default=str)[:1500] if technical_architecture else 'Not available'}

## YOUR TASK

Conduct comprehensive risk assessment across all dimensions:

1. **Market Risks** - Competition, market timing, demand
2. **Technical Risks** - Technology, scalability, security
3. **Financial Risks** - Cash flow, pricing, funding
4. **Operational Risks** - Team, processes, suppliers
5. **Strategic Risks** - Pivots, partnerships, regulation

For each risk, assess likelihood (1-5) and impact (1-5).

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "risk_matrix": [
    {{
      "id": "RISK-001",
      "name": "string - risk name",
      "description": "string - detailed description",
      "category": "market|technical|financial|operational|strategic|legal",
      "likelihood": 3,
      "impact": 4,
      "risk_score": 12,
      "triggers": ["string - what would cause this risk"],
      "early_warning_signs": ["string - how to detect early"],
      "mitigation_strategy": "string - how to reduce likelihood/impact",
      "contingency_plan": "string - what to do if it happens",
      "owner": "string - who should own this risk",
      "review_frequency": "weekly|monthly|quarterly"
    }}
  ],
  "risk_summary": {{
    "total_risks": 0,
    "critical_risks": 0,
    "high_risks": 0,
    "medium_risks": 0,
    "low_risks": 0,
    "overall_risk_level": "low|medium|high|critical"
  }},
  "top_3_risks": [
    {{
      "risk_id": "string",
      "name": "string",
      "why_critical": "string",
      "immediate_action": "string"
    }}
  ],
  "risk_interdependencies": [
    {{
      "primary_risk": "string - risk id",
      "related_risks": ["string - risk ids"],
      "cascade_effect": "string - how risks compound"
    }}
  ],
  "risk_appetite_recommendation": {{
    "risk_tolerance_level": "aggressive|moderate|conservative",
    "rationale": "string",
    "go_no_go_recommendation": "go|conditional_go|no_go",
    "conditions_for_go": ["string - conditions that must be met"]
  }},
  "monitoring_plan": {{
    "key_risk_indicators": [
      {{
        "indicator": "string",
        "threshold": "string",
        "action_if_exceeded": "string"
      }}
    ],
    "review_cadence": "string",
    "escalation_process": "string"
  }}
}}

CRITICAL: Respond with ONLY the JSON object. Include 8-15 risks across all categories.
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["risk_assessment"] = result["data"]

        # Extract claims for cross-reference tracking (v3.0)
        state = await extract_and_store_claims(
            state, "Risk Assessment", "RM", result["data"]
        )

        risk_summary = result["data"].get("risk_summary", {})
        logger.info(
            "agent_success",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            total_risks=risk_summary.get("total_risks", 0),
            critical_risks=risk_summary.get("critical_risks", 0),
            overall_level=risk_summary.get("overall_risk_level", "unknown"),
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
