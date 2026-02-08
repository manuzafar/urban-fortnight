# Phase 7: Synthesis Agents — Stakeholder Views, Validation, Exec Summary

**Goal:** Build three agents that consume the entire pack and produce the packaging layer — the features that make Seedcraft's output impossible to replicate with ChatGPT.

**Dependencies:** Phases 1-6 (needs full pack + cross-reference index)

---

## 7.1 Stakeholder View Agent

**File:** `backend/agents/stakeholder_agent.py` (NEW)

→ **Prompt:** `seedcraft-v3-prompts/11-stakeholder-views.md`

This agent takes the ENTIRE inception pack plus cross-reference index and generates 3-4 stakeholder-specific views with anticipated objections.

```python
"""
Stakeholder View Agent — generates role-specific views of the inception pack.
Same underlying data, different packaging per stakeholder.

Inputs: Full pack summary, cross-reference summary
Output: state["stakeholder_views"] — 3-4 views with anticipated objections
Model: Pro (needs reasoning to reframe content for different audiences)
"""

import json
import structlog
from datetime import datetime
from agents.base_agent import call_llm
from agents.context_builder import build_full_pack_summary, build_cross_reference_summary

logger = structlog.get_logger("stakeholder_agent")

# ═══════════════════════════════════════════════════════════
# Copy from seedcraft-v3-prompts/11-stakeholder-views.md
# ═══════════════════════════════════════════════════════════
STAKEHOLDER_VIEW_PROMPT = """..."""  # ← REPLACE WITH FULL PROMPT


async def run_stakeholder_agent(state: dict) -> dict:
    """Generate stakeholder-specific views."""
    logger.info("stakeholder_agent_start", session_id=state.get("session_id"))

    prompt = STAKEHOLDER_VIEW_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        full_pack_summary=build_full_pack_summary(state),
        cross_reference_summary=build_cross_reference_summary(state),
    )

    result = await call_llm(prompt, "Stakeholder Views")

    if result["success"]:
        state["stakeholder_views"] = result["data"]
        view_count = len(result["data"].get("views", []))
        logger.info("stakeholder_agent_complete", view_count=view_count)
    else:
        logger.error("stakeholder_agent_failed", error=result.get("error"))

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

---

## 7.2 Validation Playbook Agent

**File:** `backend/agents/validation_agent.py` (NEW)

→ **Prompt:** `seedcraft-v3-prompts/12-validation-playbook.md`

This agent receives the cross-reference index, identifies all E4/E5 claims, analyses their downstream impact, and designs specific experiments to validate the highest-impact hypotheses.

```python
"""
Validation Playbook Agent — generates actionable experiments to validate hypotheses.
Tells the PM exactly what to do next, not "do more research."

Inputs: Cross-reference index (all claims with tiers and dependencies)
Output: state["validation_playbook"] — 5-8 experiments with specific instructions
Model: Pro (needs reasoning for experimental design)
"""

import json
import structlog
from datetime import datetime
from agents.base_agent import call_llm

logger = structlog.get_logger("validation_agent")

# ═══════════════════════════════════════════════════════════
# Copy from seedcraft-v3-prompts/12-validation-playbook.md
# ═══════════════════════════════════════════════════════════
VALIDATION_PLAYBOOK_PROMPT = """..."""  # ← REPLACE WITH FULL PROMPT


async def run_validation_agent(state: dict) -> dict:
    """Generate validation playbook from cross-reference index."""
    logger.info("validation_agent_start", session_id=state.get("session_id"))

    # Extract cross-reference stats
    index = state.get("cross_reference_index", {"claims": []})
    claims = index.get("claims", [])

    tier_counts = {"E1": 0, "E2": 0, "E3": 0, "E4": 0, "E5": 0}
    for c in claims:
        tier = c.get("evidence_tier", "E4") if isinstance(c, dict) else "E4"
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    total = len(claims)
    weights = {"E1": 1.0, "E2": 0.85, "E3": 0.6, "E4": 0.3, "E5": 0.1}
    score = round(
        sum(weights.get(
            c.get("evidence_tier", "E4") if isinstance(c, dict) else "E4", 0.3
        ) for c in claims) / max(total, 1),
        2,
    )

    prompt = VALIDATION_PLAYBOOK_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        cross_reference_index=json.dumps(index, indent=2, default=str)[:12000],
        total_claims=total,
        e1_count=tier_counts.get("E1", 0),
        e2_count=tier_counts.get("E2", 0),
        e3_count=tier_counts.get("E3", 0),
        e4_count=tier_counts.get("E4", 0),
        e5_count=tier_counts.get("E5", 0),
        evidence_score=score,
    )

    result = await call_llm(prompt, "Validation Playbook")

    if result["success"]:
        state["validation_playbook"] = result["data"]
        exp_count = len(result["data"].get("experiments", []))
        logger.info("validation_agent_complete", experiment_count=exp_count)
    else:
        logger.error("validation_agent_failed", error=result.get("error"))

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

---

## 7.3 Narrative Executive Summary Agent

**File:** `backend/agents/executive_summary_agent.py` (NEW)

→ **Prompt:** `seedcraft-v3-prompts/13-narrative-executive-summary.md`

This agent runs LAST — after stakeholder views and validation playbook are complete. It synthesises everything into a strategic argument with a clear recommendation.

```python
"""
Narrative Executive Summary Agent — produces a strategic argument, not a section summary.

Runs LAST in the pipeline. Synthesises full pack into a recommendation.

Inputs: Full pack summary, evidence stats, validation priorities, stakeholder view names
Output: state["executive_summary"]
Model: Flash (synthesis from rich context, not deep reasoning)
"""

import json
import structlog
from datetime import datetime
from agents.base_agent import call_llm
from agents.context_builder import build_full_pack_summary, build_cross_reference_summary

logger = structlog.get_logger("executive_summary_agent")

# ═══════════════════════════════════════════════════════════
# Copy from seedcraft-v3-prompts/13-narrative-executive-summary.md
# ═══════════════════════════════════════════════════════════
NARRATIVE_EXECUTIVE_SUMMARY_PROMPT = """..."""  # ← REPLACE WITH FULL PROMPT


async def run_executive_summary_agent(state: dict) -> dict:
    """Generate narrative executive summary."""
    logger.info("executive_summary_agent_start", session_id=state.get("session_id"))

    # Evidence stats
    index = state.get("cross_reference_index", {"claims": []})
    claims = index.get("claims", [])
    tier_counts = {"E1": 0, "E2": 0, "E3": 0, "E4": 0, "E5": 0}
    for c in claims:
        tier = c.get("evidence_tier", "E4") if isinstance(c, dict) else "E4"
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    total = len(claims)
    weights = {"E1": 1.0, "E2": 0.85, "E3": 0.6, "E4": 0.3, "E5": 0.1}
    score = round(
        sum(weights.get(
            c.get("evidence_tier", "E4") if isinstance(c, dict) else "E4", 0.3
        ) for c in claims) / max(total, 1),
        2,
    )

    # Validation priorities (top 3 experiments)
    val_experiments = state.get("validation_playbook", {}).get("experiments", [])[:3]

    # Stakeholder view role names
    sv = state.get("stakeholder_views", {})
    stakeholder_roles = [v.get("stakeholder_role") for v in sv.get("views", [])]

    prompt = NARRATIVE_EXECUTIVE_SUMMARY_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        full_pack_summary=build_full_pack_summary(state),
        cross_reference_summary=build_cross_reference_summary(state),
        total_claims=total,
        evidence_score=score,
        e1_count=tier_counts.get("E1", 0),
        e2_count=tier_counts.get("E2", 0),
        e3_count=tier_counts.get("E3", 0),
        e4_count=tier_counts.get("E4", 0),
        e5_count=tier_counts.get("E5", 0),
        validation_priorities=json.dumps(val_experiments, indent=2, default=str)[:3000],
        stakeholder_view_names=json.dumps(stakeholder_roles, default=str),
    )

    result = await call_llm(prompt, "Executive Summary")

    if result["success"]:
        state["executive_summary"] = result["data"]
        logger.info("executive_summary_agent_complete")
    else:
        logger.error("executive_summary_agent_failed", error=result.get("error"))

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

---

## Test Phase 7

1. Verify `state["stakeholder_views"]` has 3-4 views for different roles (e.g. CFO, CISO, ARB, VP Product)
2. Verify each view has:
   - Tailored executive summary (different per role)
   - Key question answered (the first thing that stakeholder asks)
   - 2-4 anticipated objections with pre-responses
   - Objections reference actual claim_ids from the cross-reference index
   - Evidence confidence assessment per stakeholder
3. Verify `state["validation_playbook"]` has 5-8 experiments with:
   - Specific instructions (not "talk to customers" but "interview 5 CFOs at mid-tier banks...")
   - Success/failure criteria
   - Target profiles
   - upgrade_path showing which claims improve when validated
   - Decision framework (Build/Pivot/Kill signals)
4. Verify `state["executive_summary"]` includes:
   - BUILD/INVESTIGATE/PIVOT/KILL recommendation
   - Evidence score prominently displayed
   - Top 3 strongest claims and top 3 biggest unknowns
   - Specific immediate actions (executable this week)
   - Stakeholder quick-links
5. Verify the exec summary reads as a narrative argument, not a section-by-section summary
