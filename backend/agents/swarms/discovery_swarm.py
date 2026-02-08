"""
Discovery Swarm for Market and Customer Research.

This swarm runs parallel agents for:
- Customer Research (existing)
- Competitive Intelligence (new - deep competitor analysis)
- Persona Development (new - detailed user personas)
"""

from typing import Any, Coroutine

import structlog

from agents.claim_extractor import extract_and_store_claims
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
    - Detailed competitor profiles with pricing evidence
    - Competitive positioning map
    - Market share analysis
    - Competitive moats and threats
    - Differentiation thesis
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

    prompt = f"""You are a competitive intelligence analyst at Bain & Company. You produce competitive analysis that enables strategic differentiation decisions. Your analysis goes beyond listing competitors — you understand their strategies, predict their moves, and identify gaps no one is filling.

## PRODUCT IDEA
{state['product_idea']}

## INDUSTRY
{state.get('industry', 'Not specified')}

## TARGET MARKET
{state.get('target_market', 'Not specified')}

## EVIDENCE TIER RULES (MANDATORY)
- **E2**: Verified via Google Search with URL — USE THIS FOR COMPETITOR DATA
- **E3**: Published industry reports (name the report)
- **E4**: Your hypothesis (mark as "HYPOTHESIS — requires validation")

For competitor data: pricing, funding, and features MUST be E2 (from their website/Crunchbase) or clearly marked E4 if estimating.

## YOUR TASK

Profile 4-6 direct competitors, 2-3 indirect, 2-3 potential entrants.

## OUTPUT FORMAT

Respond with ONLY valid JSON:

{{
  "direct_competitors": [
    {{
      "name": "string - exact company name",
      "website": "string - URL",
      "one_liner": "string - what they do in one sentence",
      "founded": "string - year if known",
      "funding": "string - amount and round if known",
      "funding_evidence_tier": "E2|E4",
      "target_customer": "string - who they sell to specifically",
      "pricing": {{
        "tiers": "string - specific pricing tiers with prices",
        "evidence_tier": "E2|E4",
        "source": "string - URL or null"
      }},
      "key_features": ["string - feature with specificity"],
      "strengths": ["string - specific strength with evidence"],
      "weaknesses": ["string - specific weakness"],
      "threat_level": "existential|significant|moderate|low",
      "threat_rationale": "string - why this threat level"
    }}
  ],
  "indirect_competitors": [
    {{
      "name": "string",
      "solution_type": "string - how they solve the problem differently",
      "threat_level": "high|medium|low"
    }}
  ],
  "potential_entrants": [
    {{
      "name": "string - company that could enter",
      "current_business": "string - what they do today",
      "entry_likelihood": "high|moderate|low",
      "entry_rationale": "string - why they might enter",
      "entry_timeline": "string - when they could enter",
      "competitive_advantage_if_enters": "string - what makes them dangerous"
    }}
  ],
  "positioning_map": {{
    "x_axis": "string - meaningful axis specific to this market",
    "y_axis": "string - meaningful axis (not generic price/features)",
    "positions": [
      {{
        "name": "string - competitor or Our Product",
        "x_score": 7.5,
        "y_score": 6.0,
        "is_target_product": false,
        "rationale": "string - why this position"
      }}
    ],
    "white_space": "string - where no one is positioned"
  }},
  "competitive_gaps": [
    {{
      "gap": "string - what's underserved",
      "why_unserved": "string - why no competitor addressed this",
      "our_advantage": "string - why we can fill this gap"
    }}
  ],
  "differentiation_thesis": "string - 2-3 sentences on why we win. Must be 10x better, not 10%.",
  "moat_analysis": {{
    "defensible": ["string - advantages hard to replicate and why"],
    "not_defensible": ["string - advantages that could be copied"],
    "moat_building_strategy": "string - how the moat deepens over time"
  }},
  "competitive_risks": [
    {{
      "risk": "string - specific competitive risk",
      "probability": "high|moderate|low",
      "impact": "string - what happens if this materializes",
      "mitigation": "string - specific action to reduce risk"
    }}
  ]
}}

CRITICAL: Use Google Search to find REAL competitor data. The positioning map axes must be specific to THIS market.
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["competitive_analysis"] = result["data"]

        # Extract claims for cross-reference tracking (v3.0)
        state = await extract_and_store_claims(
            state, "Competitive Landscape", "CL", result["data"]
        )

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

    prompt = f"""You are a senior user researcher at IDEO. You build personas that product teams use to make real design decisions — not demographic sketches that get printed and ignored. Your personas are decision-making models: how does this person discover, evaluate, buy, adopt, and champion (or abandon) tools?

## PRODUCT IDEA
{state['product_idea']}

## INDUSTRY
{state.get('industry', 'Not specified')}

## TARGET MARKET
{state.get('target_market', 'Not specified')}

## EVIDENCE TIER RULES
- **E3**: Based on published persona research or industry reports
- **E4**: Your inference based on role/industry knowledge — mark as HYPOTHESIS
- **E5**: Assumption about behaviour

Most persona claims will be E3 or E4. Be honest about this.

## YOUR TASK

Create 2-3 detailed personas. Depth over breadth.
Personas must enable design decisions: "Sarah would prefer X over Y because [specific attribute]."

## OUTPUT FORMAT

Respond with ONLY valid JSON. Keep structure flat to ensure valid JSON:

{{
  "primary_persona": {{
    "name": "string - realistic full name",
    "role": "string - specific job title",
    "archetype": "string - one-line label like 'The Pragmatic Innovator'",
    "organisation_type": "string - what kind of company",
    "team_size": "string - how many people they manage",
    "reports_to": "string - who they report to",
    "tenure": "string - how long in this role",
    "goals": ["string - what their boss measures them on"],
    "frustrations": ["string - daily operational frustrations, be specific"],
    "jobs_to_be_done": ["string - 'When [situation], I want to [action] so that [outcome]'"],
    "discovery_channels": ["string - how they find new tools"],
    "evaluation_criteria": ["string - what matters when choosing, ranked"],
    "decision_authority": "sole_decision_maker|influencer|recommender|budget_approver",
    "procurement_timeline": "string - how long from want to paid",
    "procurement_blockers": ["string - what stops them buying"],
    "champions_what": "string - what they advocate for internally",
    "internal_blockers": ["string - who blocks their initiatives"],
    "current_tools": ["string - what they use today"],
    "satisfaction_level": "happy|tolerable|frustrated|desperate",
    "switching_triggers": ["string - what event would make them look for alternative"],
    "success_moment": "string - when they'd say 'this was worth it'",
    "evidence_tier": "E3|E4",
    "quote": "string - something this persona might say"
  }},
  "secondary_personas": [
    {{
      "name": "string",
      "role": "string",
      "archetype": "string",
      "key_difference": "string - how they differ from primary",
      "goals": ["string"],
      "jobs_to_be_done": ["string - 'When [situation], I want to [action] so that [outcome]'"],
      "decision_authority": "string",
      "evaluation_criteria": ["string"]
    }}
  ],
  "anti_persona": {{
    "description": "string - who this product is NOT for",
    "reasons": ["string - why they wouldn't benefit"]
  }},
  "persona_prioritisation": {{
    "primary_buyer": "string - which persona makes purchase decision",
    "primary_user": "string - which persona uses product daily",
    "primary_champion": "string - which persona advocates internally"
  }}
}}

CRITICAL:
- Keep JSON flat - no deeply nested objects
- Internal politics matter more than demographics
- Jobs-to-be-done in single string format: "When [situation], I want to [action] so that [outcome]"
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["detailed_personas"] = result["data"]

        # Extract claims for cross-reference tracking (v3.0)
        state = await extract_and_store_claims(
            state, "Customer Personas", "CP", result["data"]
        )

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
