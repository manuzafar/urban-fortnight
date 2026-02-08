# Phase 9: Facilitator Pipeline Redesign

**Goal:** Wire everything together in the correct execution order with proper parallelism and dependency management.

**Dependencies:** Phases 1-8 (all agents must exist)

---

## 9.1 New Pipeline Architecture

**File:** `backend/agents/facilitator.py` (MODIFY — major rewrite of `run()` method)

```python
import asyncio
import structlog
from datetime import datetime
from utils.sse import StreamEventType

logger = structlog.get_logger("facilitator")


class FacilitatorAgent:

    async def run(self, state: dict) -> dict:
        """
        Complete 7-phase pipeline.

        Phase 1: Planning (sequential)
        Phase 2: Discovery Swarm (parallel)
        Phase 3: Strategy Swarm (parallel then sequential)
        Phase 4: Delivery Swarm (parallel then sequential)
        Phase 5: Design Phase (sequential)
        Phase 6: Quality Check (sequential with revision loop)
        Phase 7: Synthesis (parallel then sequential)
        """
        logger.info("pipeline_start", session_id=state.get("session_id"))
        start_time = datetime.utcnow()

        # ═══ PHASE 1: Planning ═══
        await self._emit(state, StreamEventType.PHASE_START, {"phase": "planning"})
        state = await self._run_planning_phase(state)

        # ═══ PHASE 2: Discovery Swarm (PARALLEL) ═══
        await self._emit(state, StreamEventType.PHASE_START, {"phase": "discovery"})
        state = await self._run_discovery_phase(state)

        # ═══ PHASE 3: Strategy Swarm (PARALLEL then SEQUENTIAL) ═══
        await self._emit(state, StreamEventType.PHASE_START, {"phase": "strategy"})
        state = await self._run_strategy_phase(state)

        # ═══ PHASE 4: Delivery Swarm (PARALLEL then SEQUENTIAL) ═══
        await self._emit(state, StreamEventType.PHASE_START, {"phase": "delivery"})
        state = await self._run_delivery_phase(state)

        # ═══ PHASE 5: Design Phase (SEQUENTIAL) ═══
        await self._emit(state, StreamEventType.DESIGN_PHASE, {"status": "starting"})
        state = await self._run_design_phase(state)

        # ═══ PHASE 6: Quality Check ═══
        await self._emit(state, StreamEventType.PHASE_START, {"phase": "quality_check"})
        state = await self._run_quality_check(state)

        # ═══ PHASE 7: Synthesis (PARALLEL then SEQUENTIAL) ═══
        await self._emit(state, StreamEventType.PHASE_START, {"phase": "synthesis"})
        state = await self._run_synthesis_phase(state)

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info("pipeline_complete", elapsed_seconds=elapsed)
        await self._emit(state, StreamEventType.COMPLETE, {"elapsed_seconds": elapsed})

        return state
```

---

## 9.2 Phase Implementations

### Planning Phase (existing, minimal changes)

```python
async def _run_planning_phase(self, state: dict) -> dict:
    """
    Quick preliminary scan to extract industry, competitors, regulatory hints.
    These feed into all downstream agents as context.
    Outputs: industry, target_market, competitors, preliminary_legal_scan
    """
    # Keep existing implementation — this is the facilitator's planning step
    # that runs before any agents start
    return state
```

### Discovery Phase (3 agents in parallel)

```python
async def _run_discovery_phase(self, state: dict) -> dict:
    """Market Intelligence + Competitive Landscape + Customer Personas (parallel)."""
    from agents.customer_research import run_market_intelligence_agent
    # Import other discovery agents from swarms or standalone files
    from agents.competitive_agent import run_competitive_landscape_agent
    from agents.personas_agent import run_personas_agent

    # Run all three in parallel
    mi_task = asyncio.create_task(run_market_intelligence_agent(state.copy()))
    cl_task = asyncio.create_task(run_competitive_landscape_agent(state.copy()))
    cp_task = asyncio.create_task(run_personas_agent(state.copy()))

    mi_state, cl_state, cp_state = await asyncio.gather(mi_task, cl_task, cp_task)

    # Merge results
    state["customer_research"] = mi_state.get("customer_research")
    state["competitive_analysis"] = cl_state.get("competitive_analysis")
    state["detailed_personas"] = cp_state.get("detailed_personas")

    # Merge cross-reference claims from all three
    self._merge_claims(state, [mi_state, cl_state, cp_state])

    return state
```

### Strategy Phase (parallel then sequential)

```python
async def _run_strategy_phase(self, state: dict) -> dict:
    """
    Stage 1 (parallel): Business Case + Go-to-Market
    Stage 2 (sequential): Financial Model (needs both above)
    """
    from agents.business_case_agent import run_business_case_agent
    from agents.gtm_agent import run_gtm_agent
    from agents.financial_model_agent import run_financial_model_agent

    # Stage 1: Parallel
    bc_task = asyncio.create_task(run_business_case_agent(state.copy()))
    gtm_task = asyncio.create_task(run_gtm_agent(state.copy()))
    bc_state, gtm_state = await asyncio.gather(bc_task, gtm_task)

    # Merge results
    state["business_case"] = bc_state.get("business_case")
    state["gtm_plan"] = gtm_state.get("gtm_plan")
    self._merge_claims(state, [bc_state, gtm_state])

    # Stage 2: Sequential (Financial Model needs Business Case + GTM)
    state = await run_financial_model_agent(state)

    return state
```

### Delivery Phase (parallel then sequential)

```python
async def _run_delivery_phase(self, state: dict) -> dict:
    """
    Stage 1 (parallel): PRD + Technical Architecture + Regulatory & Compliance
    Stage 2 (sequential): Risk Assessment (needs all above)
    """
    from agents.prd_generator import run_prd_agent
    from agents.technical_architect import run_tech_arch_agent
    from agents.legal_regulatory import run_regulatory_agent
    from agents.risk_agent import run_risk_assessment_agent

    # Stage 1: Parallel
    prd_task = asyncio.create_task(run_prd_agent(state.copy()))
    ta_task = asyncio.create_task(run_tech_arch_agent(state.copy()))
    rc_task = asyncio.create_task(run_regulatory_agent(state.copy()))
    prd_state, ta_state, rc_state = await asyncio.gather(prd_task, ta_task, rc_task)

    # Merge results
    state["product_requirements"] = prd_state.get("product_requirements")
    state["technical_architecture"] = ta_state.get("technical_architecture")
    state["legal_regulatory_review"] = rc_state.get("legal_regulatory_review")
    self._merge_claims(state, [prd_state, ta_state, rc_state])

    # Stage 2: Sequential (Risk Assessment needs everything above)
    state = await run_risk_assessment_agent(state)

    return state
```

### Design Phase (sequential)

```python
async def _run_design_phase(self, state: dict) -> dict:
    """Wireframes → Prototype (sequential, both need PRD + Tech Arch)."""
    from agents.wireframe_agent import run_wireframe_agent
    from agents.prototype_agent import run_prototype_agent

    # Gate: only run if PRD and Tech Arch succeeded
    if not state.get("product_requirements") or not state.get("technical_architecture"):
        logger.warning("design_phase_skipped", reason="Missing PRD or Tech Architecture")
        return state

    # Step 1: Wireframes
    state = await run_wireframe_agent(state)
    await self._emit(state, StreamEventType.WIREFRAME_READY, {
        "screen_count": len(
            (state.get("wireframes") or {}).get("screens",
            (state.get("wireframes") or {}).get("wireframes", []))
        )
    })

    # Step 2: Prototype (needs wireframes)
    if state.get("wireframes"):
        state = await run_prototype_agent(state)
        await self._emit(state, StreamEventType.PROTOTYPE_READY, {})

    return state
```

### Quality Check (with revision loop)

```python
async def _run_quality_check(self, state: dict) -> dict:
    """Run evidence-aware critique with optional revision loop."""
    from agents.critique import run_critique_agent

    critique_result = await run_critique_agent(state)
    state["critique"] = critique_result

    overall_score = critique_result.get("overall_score", 10)

    if overall_score < 6.0:
        sections_to_revise = critique_result.get("sections_needing_revision", [])

        for section in sections_to_revise[:3]:  # Cap at 3 revisions
            agent_func = self.SECTION_TO_AGENT_MAP.get(section)
            if agent_func:
                logger.info("revising_section", section=section)
                state = await agent_func(state)

        # Re-critique
        state["critique"] = await run_critique_agent(state)

    return state
```

### Synthesis Phase (parallel then sequential)

```python
async def _run_synthesis_phase(self, state: dict) -> dict:
    """
    Stage 1 (parallel): Stakeholder Views + Validation Playbook
    Stage 2 (sequential): Executive Summary (needs both above)
    """
    from agents.stakeholder_agent import run_stakeholder_agent
    from agents.validation_agent import run_validation_agent
    from agents.executive_summary_agent import run_executive_summary_agent

    # Stage 1: Parallel
    sv_task = asyncio.create_task(run_stakeholder_agent(state.copy()))
    vp_task = asyncio.create_task(run_validation_agent(state.copy()))
    sv_state, vp_state = await asyncio.gather(sv_task, vp_task)

    # Merge results
    state["stakeholder_views"] = sv_state.get("stakeholder_views")
    state["validation_playbook"] = vp_state.get("validation_playbook")
    self._merge_claims(state, [sv_state, vp_state])

    # Stage 2: Sequential (Exec Summary needs stakeholder views + validation playbook)
    state = await run_executive_summary_agent(state)

    return state
```

---

## 9.3 Helper Methods

```python
def _merge_claims(self, state: dict, source_states: list[dict]) -> None:
    """Merge cross-reference claims from parallel agent results."""
    if state.get("cross_reference_index") is None:
        state["cross_reference_index"] = {"claims": []}

    for s in source_states:
        extra = (s.get("cross_reference_index") or {}).get("claims", [])
        state["cross_reference_index"]["claims"].extend(extra)


SECTION_TO_AGENT_MAP = {
    "customer_research": None,          # Will be set to actual agent functions
    "competitive_analysis": None,
    "detailed_personas": None,
    "business_case": None,
    "gtm_plan": None,
    "financial_model": None,
    "product_requirements": None,
    "technical_architecture": None,
    "legal_regulatory_review": None,
    "risk_assessment": None,
}
# Populate after imports — or use lazy imports in _run_quality_check
```

---

## 9.4 Execution Flow Diagram

```
Planning
    │
    ▼
┌─────────────────────────────┐
│   DISCOVERY (parallel)       │
│  MI ──┐                      │
│  CL ──┼──→ merge             │
│  CP ──┘                      │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   STRATEGY                   │
│  BC ──┐                      │
│  GTM ─┼──→ merge ──→ FM     │
│       └───────────────┘      │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   DELIVERY                   │
│  PRD ─┐                      │
│  TA ──┼──→ merge ──→ Risk   │
│  RC ──┘                      │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   DESIGN (sequential)        │
│  Wireframes ──→ Prototype    │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   QUALITY CHECK              │
│  Critique ──→ Revise? ──→   │
│             Re-critique      │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   SYNTHESIS                  │
│  Stakeholder ─┐              │
│  Validation ──┼→ merge →     │
│               └→ Exec Summary│
└─────────────────────────────┘
```

---

## Test Phase 9

1. Run a complete pack end-to-end with "AI cash flow forecasting for SME banking"
2. Verify all state fields are populated (check for None values):
   - `customer_research`, `competitive_analysis`, `detailed_personas`
   - `business_case`, `gtm_plan`, `financial_model`
   - `product_requirements`, `technical_architecture`, `legal_regulatory_review`, `risk_assessment`
   - `wireframes`, `prototype`
   - `stakeholder_views`, `validation_playbook`, `executive_summary`
   - `cross_reference_index` (with claims from all sections)
3. Verify pipeline order is correct (check logs for phase timestamps)
4. Verify Financial Model runs AFTER Business Case + GTM
5. Verify Executive Summary runs AFTER Stakeholder Views + Validation Playbook
6. Verify SSE events fire for each phase
7. Time the full pipeline — target under 10 minutes
