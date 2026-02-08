# Phase 5: New Strategy Agents — GTM + Financial Model

**Goal:** Build two agents that don't have existing counterparts in the codebase.

**Dependencies:** Phases 1-4

---

## 5.1 Go-to-Market Agent

**File:** `backend/agents/gtm_agent.py` (NEW)

→ **Prompt:** `seedcraft-v3-prompts/05-go-to-market.md`

```python
"""
Go-to-Market Strategy Agent.
Produces executable launch playbook, not strategy slides.

Inputs: Personas, Business Case, Competitive Landscape
Output: state["gtm_plan"]
Model: Pro
"""

import json
import structlog
from datetime import datetime
from agents.base_agent import call_llm, extract_and_store_claims
from agents.context_builder import build_context_summary

logger = structlog.get_logger("gtm_agent")

# ═══════════════════════════════════════════════════════════
# IMPORTANT: Copy the complete prompt from
# seedcraft-v3-prompts/05-go-to-market.md
# ═══════════════════════════════════════════════════════════
GTM_STRATEGY_PROMPT = """..."""  # ← REPLACE WITH FULL PROMPT


async def run_gtm_agent(state: dict) -> dict:
    """Generate go-to-market strategy."""
    logger.info("gtm_agent_start", session_id=state.get("session_id"))

    prompt = GTM_STRATEGY_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        personas_summary=build_context_summary(state, "detailed_personas"),
        business_case_summary=build_context_summary(state, "business_case"),
        competitive_landscape_summary=build_context_summary(state, "competitive_analysis"),
    )

    result = await call_llm(prompt, "Go-to-Market")

    if result["success"]:
        state["gtm_plan"] = result["data"]
        state = await extract_and_store_claims(
            state, "Go-to-Market", "GM", result["data"]
        )
        logger.info("gtm_agent_complete")
    else:
        logger.error("gtm_agent_failed", error=result.get("error"))

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

---

## 5.2 Financial Model Agent

**File:** `backend/agents/financial_model_agent.py` (NEW)

→ **Prompt:** `seedcraft-v3-prompts/06-financial-model.md`

**Critical:** Financial Model depends on Business Case AND GTM outputs. It runs AFTER both complete (sequential within Strategy Swarm).

```python
"""
Financial Model Agent.
Produces bottoms-up monthly projections with scenario analysis.

Inputs: Business Case (unit economics, pricing), GTM (channel costs, timelines)
Output: state["financial_model"]
Model: Pro
"""

import json
import structlog
from datetime import datetime
from agents.base_agent import call_llm, extract_and_store_claims
from agents.context_builder import build_context_summary

logger = structlog.get_logger("financial_model_agent")

# ═══════════════════════════════════════════════════════════
# IMPORTANT: Copy the complete prompt from
# seedcraft-v3-prompts/06-financial-model.md
# ═══════════════════════════════════════════════════════════
FINANCIAL_MODEL_PROMPT = """..."""  # ← REPLACE WITH FULL PROMPT


async def run_financial_model_agent(state: dict) -> dict:
    """Generate financial projections."""
    logger.info("financial_model_agent_start", session_id=state.get("session_id"))

    prompt = FINANCIAL_MODEL_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        business_case_summary=build_context_summary(state, "business_case"),
        gtm_summary=build_context_summary(state, "gtm_plan"),
        market_intelligence_summary=build_context_summary(state, "customer_research", 2000),
    )

    result = await call_llm(prompt, "Financial Model")

    if result["success"]:
        state["financial_model"] = result["data"]
        state = await extract_and_store_claims(
            state, "Financial Model", "FM", result["data"]
        )
        logger.info("financial_model_agent_complete")
    else:
        logger.error("financial_model_agent_failed", error=result.get("error"))

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

---

## 5.3 Integration Into Strategy Swarm

**File:** `backend/agents/swarms/strategy_swarm.py` (MODIFY)

The Strategy Swarm now runs in two stages:

```python
# Stage 1 (PARALLEL): Business Case + Go-to-Market
# Stage 2 (SEQUENTIAL): Financial Model (needs both above)
```

The actual wiring happens in the Facilitator (Phase 9). For now, just ensure:
1. `gtm_agent.py` and `financial_model_agent.py` exist and can be imported
2. Both agents follow the standard pattern (state mutation + claim extraction)

---

## Test Phase 5

1. Verify GTM plan includes:
   - Specific tactics per phase with budgets and timelines
   - Messaging per persona (not generic value prop)
   - Channel strategy with CAC estimates
   - Phase-gated success criteria
2. Verify Financial Model includes:
   - 12 monthly projections for Year 1 (not quarterly)
   - Revenue built up from users × conversion × ARPU
   - Cost structure with fixed and variable components
   - Scenario analysis (base, optimistic, pessimistic)
   - Cash balance tracking
3. Verify Financial Model numbers are consistent with Business Case unit economics
4. Verify both agents produce claims in the cross-reference index (GM-*, FM-* prefixes)
