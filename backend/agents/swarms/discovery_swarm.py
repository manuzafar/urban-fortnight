"""
Discovery Swarm for Market and Customer Research.

This swarm runs parallel agents for:
- Customer Research (existing)
- Competitive Intelligence (new - deep competitor analysis)
- Persona Development (new - detailed user personas)
"""

from typing import Any, Coroutine

import structlog

from agents.customer_research import run_customer_research_agent
from agents.state import DiscoveryState
from agents.swarms.base import BaseSwarm

logger = structlog.get_logger(__name__)


class DiscoverySwarm(BaseSwarm):
    """
    Swarm for market discovery and customer research.

    Runs customer research, competitive intelligence, and persona
    development in parallel to build a comprehensive market picture.
    """

    swarm_name = "DiscoverySwarm"
    agent_names = [
        "customer_research",
        "competitive_intelligence",
        "persona_development",
    ]

    def get_agent_tasks(
        self, state: DiscoveryState
    ) -> list[tuple[str, Coroutine[Any, Any, DiscoveryState]]]:
        """
        Get discovery agent coroutines.

        Currently runs customer_research with competitive_intelligence
        and persona_development as enhanced versions that share the
        same underlying research but focus on different aspects.
        """
        tasks = [
            ("customer_research", run_customer_research_agent(state.copy())),
            ("competitive_intelligence", run_competitive_intelligence(state.copy())),
            ("persona_development", run_persona_development(state.copy())),
        ]
        return tasks


async def run_competitive_intelligence(state: DiscoveryState) -> DiscoveryState:
    """
    Deep competitive analysis agent.

    Focuses on:
    - Detailed competitor profiles
    - Competitive positioning
    - Market share analysis
    - Competitive moats and threats
    """
    from datetime import datetime
    from agents.base_agent import call_llm_with_grounding
    from models.schemas import SessionStatus

    AGENT_NAME = "Competitive Intelligence"

    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    prompt = f"""You are a Competitive Intelligence Analyst. Analyze the competitive landscape for this product idea.

## PRODUCT IDEA
{state['product_idea']}

## INDUSTRY
{state.get('industry', 'Not specified')}

## TARGET MARKET
{state.get('target_market', 'Not specified')}

## YOUR TASK

Perform deep competitive analysis:

1. **Direct Competitors** - Products solving the same problem
2. **Indirect Competitors** - Alternative solutions or workarounds
3. **Potential Future Competitors** - Companies that could enter this space
4. **Competitive Moats** - What makes each competitor defensible
5. **Market Positioning** - How each competitor positions themselves
6. **Competitive Threats** - Risks from competition

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "direct_competitors": [
    {{
      "name": "string - company name",
      "product": "string - product name",
      "market_share": "string - estimated share",
      "strengths": ["string"],
      "weaknesses": ["string"],
      "positioning": "string - how they position",
      "pricing": "string - pricing model/range",
      "funding": "string - known funding if applicable"
    }}
  ],
  "indirect_competitors": [
    {{
      "name": "string",
      "solution_type": "string - how they solve the problem differently",
      "threat_level": "high|medium|low"
    }}
  ],
  "potential_future_competitors": [
    {{
      "company": "string",
      "likelihood": "high|medium|low",
      "timeline": "string - when they might enter",
      "rationale": "string"
    }}
  ],
  "competitive_moats": {{
    "strongest_moats_in_market": ["string - what protects incumbents"],
    "potential_moats_for_new_entrant": ["string - what we could build"]
  }},
  "market_dynamics": {{
    "consolidation_trend": "consolidating|fragmenting|stable",
    "winner_take_all": true,
    "key_battlegrounds": ["string - where competition is fiercest"]
  }},
  "strategic_recommendations": [
    "string - recommendation for competing effectively"
  ]
}}

CRITICAL: Respond with ONLY the JSON object. Use real company names where known.
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["competitive_analysis"] = result["data"]
        logger.info(
            "agent_success",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            competitors_found=len(result["data"].get("direct_competitors", [])),
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


async def run_persona_development(state: DiscoveryState) -> DiscoveryState:
    """
    Detailed persona development agent.

    Creates rich, detailed user personas beyond basic demographics:
    - Psychographics and motivations
    - Jobs to be done
    - Decision-making process
    - Technology adoption profile
    """
    from datetime import datetime
    from agents.base_agent import call_llm_with_grounding
    from models.schemas import SessionStatus

    AGENT_NAME = "Persona Development"

    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    prompt = f"""You are a User Research Specialist. Create detailed user personas for this product.

## PRODUCT IDEA
{state['product_idea']}

## INDUSTRY
{state.get('industry', 'Not specified')}

## TARGET MARKET
{state.get('target_market', 'Not specified')}

## YOUR TASK

Create 3-4 detailed personas that represent the target users:

1. **Primary Persona** - The main target user
2. **Secondary Personas** - Other important user types
3. **Anti-Persona** - Who this product is NOT for

For each persona, provide deep psychographic detail.

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "primary_persona": {{
    "name": "string - representative name",
    "role": "string - job title or role",
    "demographics": {{
      "age_range": "string",
      "location": "string",
      "income_level": "string",
      "education": "string"
    }},
    "psychographics": {{
      "values": ["string - what they value"],
      "fears": ["string - what they fear"],
      "aspirations": ["string - what they aspire to"]
    }},
    "jobs_to_be_done": [
      {{
        "job": "string - what they're trying to accomplish",
        "frequency": "daily|weekly|monthly|occasionally",
        "importance": "critical|high|medium|low"
      }}
    ],
    "current_solutions": ["string - how they solve the problem today"],
    "pain_points": ["string - frustrations with current solutions"],
    "decision_criteria": ["string - what matters when choosing a solution"],
    "technology_adoption": "innovator|early_adopter|early_majority|late_majority|laggard",
    "quote": "string - something this persona might say about the problem"
  }},
  "secondary_personas": [
    {{
      "name": "string",
      "role": "string",
      "key_difference": "string - how they differ from primary",
      "jobs_to_be_done": ["string"],
      "decision_criteria": ["string"]
    }}
  ],
  "anti_persona": {{
    "description": "string - who this product is NOT for",
    "reasons": ["string - why they wouldn't benefit"]
  }},
  "persona_insights": [
    "string - key insight about the target users"
  ]
}}

CRITICAL: Respond with ONLY the JSON object. Make personas realistic and specific.
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["detailed_personas"] = result["data"]
        logger.info(
            "agent_success",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            secondary_personas=len(result["data"].get("secondary_personas", [])),
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
