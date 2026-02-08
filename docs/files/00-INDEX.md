# Seedcraft v3.0 — Complete Implementation Plan

## For Claude Code Execution

**Date:** February 7, 2026
**Goal:** Transform Seedcraft output from "AI-generated documents" to "interconnected, evidence-graded, stakeholder-packaged strategic argument with working prototype"
**Total Estimated Effort:** 10 phases, each executable as one focused session
**Prompt Library:** All production-ready prompts in `seedcraft-v3-prompts/` (files 01–17)

---

## HOW TO USE THIS PLAN

Each phase is a separate file (01–10). Each lists every file to create or modify, complete code or a pointer to the prompt library file, test criteria, and dependencies.

**Rules for Claude Code:**
1. Complete and test each phase before starting the next.
2. When a phase says `→ Prompt: seedcraft-v3-prompts/XX-name.md`, read that file and copy the prompt constant into the target code file.
3. Preserve existing codebase patterns (state dict mutation, BaseSwarm ABC, `call_llm` helpers, SSE events).
4. Test with real product ideas ("AI cash flow forecasting for SME banking"), never toy examples.

---

## CURRENT CODEBASE — READ THESE FIRST

```
backend/agents/state.py           # DiscoveryState TypedDict with reducers
backend/agents/facilitator.py     # FacilitatorAgent — swarm coordinator
backend/agents/orchestrator.py    # LangGraph workflow
backend/agents/prompts.py         # All agent prompts (to be replaced)
backend/agents/base_agent.py      # call_llm, call_llm_with_grounding, call_llm_with_memory
backend/models/schemas.py         # All Pydantic models (60+)
backend/models/visual_schemas.py  # Chart data schemas
backend/config.py                 # AGENT_MODEL_CONFIG, settings
backend/utils/sse.py              # StreamEventType enum
```

**Key patterns:**
- Agent signature: `async def run_X_agent(state: DiscoveryState) -> DiscoveryState`
- Agents mutate state dict fields, not return new objects
- Parallel agents get `state.copy()` to prevent race conditions
- Swarms use `BaseSwarm` ABC with `get_agent_tasks()` and `get_output_fields()`
- LLM calls: `call_llm()` | `call_llm_with_grounding()` (Google Search) | `call_llm_with_memory()` (RAG)
- Model routing: `AGENT_MODEL_CONFIG` in `config.py` maps agent names → "flash" | "pro"
- SSE events via helpers in `utils/sse.py`
- All schemas use Pydantic v2

---

## ARCHITECTURE OVERVIEW — EXECUTION ORDER

```
Phase 1:  Cross-Reference Infrastructure     (foundation — claim tracking)
Phase 2:  Context Builder Utility             (plumbing — upstream→downstream injection)
Phase 3:  Revamp All Agent Schemas            (data layer — new Pydantic models)
Phase 4:  Revamp All Agent Prompts            (brain — production prompts from library)
Phase 5:  New Agents — GTM, Financial Model   (new strategy agents)
Phase 6:  Design Agents — Wireframes + Proto  (visual output)
Phase 7:  Synthesis Agents — Stakeholder, Validation, Exec Summary  (packaging)
Phase 8:  Critique Agent Revamp               (quality enforcement)
Phase 9:  Facilitator Pipeline Redesign       (orchestration — wire everything together)
Phase 10: Frontend Revamp + E2E Test          (render + validate)
```

**Dependency graph:**
```
Phase 1 ──┐
Phase 2 ──┤
Phase 3 ──┼──→ Phase 4 ──→ Phase 5 ──→ Phase 9 ──→ Phase 10
          │                Phase 6 ──→ Phase 9
          │                Phase 7 ──→ Phase 9
          └──────────────→ Phase 8 ──→ Phase 9
```

---

## FILES IN THIS PLAN

| File | Phase | Summary |
|------|-------|---------|
| `01-CROSS-REFERENCE-INFRASTRUCTURE.md` | 1 | Claim schema, extractor, state fields, integration |
| `02-CONTEXT-BUILDER.md` | 2 | Upstream→downstream summary injection utility |
| `03-AGENT-SCHEMAS.md` | 3 | All new/revised Pydantic models |
| `04-AGENT-PROMPTS.md` | 4 | Prompt replacement map and agent function updates |
| `05-NEW-STRATEGY-AGENTS.md` | 5 | GTM + Financial Model agents |
| `06-DESIGN-AGENTS.md` | 6 | Wireframe + Prototype agents |
| `07-SYNTHESIS-AGENTS.md` | 7 | Stakeholder Views, Validation, Exec Summary |
| `08-CRITIQUE-REVAMP.md` | 8 | Evidence-aware quality enforcement |
| `09-FACILITATOR-PIPELINE.md` | 9 | Complete pipeline orchestration redesign |
| `10-FRONTEND-AND-E2E.md` | 10 | Frontend components, showcase packs, quality checklist |
| `11-FILE-CHANGE-SUMMARY.md` | — | Complete list of new and modified files |

---

## EXECUTION NOTES FOR CLAUDE CODE

1. **Work phase by phase.** Complete and test each phase before moving on.
2. **Prompts are the product.** Copy them exactly from the prompt library files.
3. **Cross-references are the moat.** The interconnected knowledge graph of cross-referenced, evidence-graded claims CANNOT be replicated by a chat interface.
4. **The prototype must be impressive.** Colour, typography, realistic data, smooth interactions.
5. **Test with the banking scenario.** "AI-powered cash flow forecasting for SME banking customers" is the canonical test case.
6. **Evidence tiers are non-negotiable.** If any section produces output without evidence tiers, the prompt is wrong.
