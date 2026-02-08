# Phase 4: Revamp All Agent Prompts

**Goal:** Replace every agent prompt with production-ready versions from the prompt library, and update agent functions to use the context builder.

**Dependencies:** Phases 1-3

---

## 4.1 Prompt Replacement Map

For each agent:
1. Open the prompt library file listed below
2. Copy the `PROMPT_NAME = """..."""` constant
3. Replace the existing prompt in `backend/agents/prompts.py`
4. Update the agent's `run_X_agent()` to format the new prompt with context builder variables

| Current Prompt | Replace With | Prompt Library File | LLM Call Type |
|---------------|-------------|--------------------|----|
| `CUSTOMER_RESEARCH_PROMPT` | `MARKET_INTELLIGENCE_PROMPT` | `01-market-intelligence.md` | `call_llm_with_grounding` |
| Competitive section in discovery_swarm | `COMPETITIVE_LANDSCAPE_PROMPT` | `02-competitive-landscape.md` | `call_llm_with_grounding` |
| Persona section in discovery_swarm | `CUSTOMER_PERSONAS_PROMPT` | `03-customer-personas.md` | `call_llm` |
| `BUSINESS_STRATEGY_PROMPT` | `BUSINESS_CASE_PROMPT` | `04-business-case.md` | `call_llm_with_grounding` |
| `PRD_GENERATOR_PROMPT` | `PRODUCT_REQUIREMENTS_PROMPT` | `07-product-requirements.md` | `call_llm` |
| `TECHNICAL_ARCHITECT_PROMPT` | `TECHNICAL_ARCHITECTURE_PROMPT` | `08-technical-architecture.md` | `call_llm` |
| `LEGAL_REGULATORY_PROMPT` | `REGULATORY_COMPLIANCE_PROMPT` | `09-regulatory-compliance.md` | `call_llm_with_grounding` |
| `CRITIQUE_PROMPT` (risk portion) | `RISK_ASSESSMENT_PROMPT` | `10-risk-assessment.md` | `call_llm` |

---

## 4.2 Agent Function Update Pattern

Every agent function needs the same structural change:

```python
# ── BEFORE (typical existing pattern) ──
from agents.prompts import CUSTOMER_RESEARCH_PROMPT

async def run_customer_research_agent(state):
    prompt = CUSTOMER_RESEARCH_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state["industry"],
    )
    result = await call_llm(prompt, "Customer Research")
    if result["success"]:
        state["customer_research"] = result["data"]
    return state


# ── AFTER ──
from agents.prompts import MARKET_INTELLIGENCE_PROMPT
from agents.context_builder import build_context_summary
from agents.base_agent import call_llm_with_grounding, extract_and_store_claims

async def run_market_intelligence_agent(state):
    prompt = MARKET_INTELLIGENCE_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        target_market=state.get("target_market", ""),
        competitors=state.get("competitors", "Not yet identified"),
        regulatory_hints=build_context_summary(state, "preliminary_legal_scan", max_chars=2000),
        memory_context=state.get("memory_context", ""),
    )
    result = await call_llm_with_grounding(prompt, "Market Intelligence")
    if result["success"]:
        state["customer_research"] = result["data"]  # Keep same state field for now
        state = await extract_and_store_claims(state, "Market Intelligence", "MI", result["data"])
    return state
```

---

## 4.3 Per-Agent Prompt Variables

Each prompt has specific variables that must be populated. Here is what each agent needs:

### Market Intelligence (01)
```python
prompt = MARKET_INTELLIGENCE_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    target_market=state.get("target_market", ""),
    competitors=state.get("competitors", "Not yet identified"),
    regulatory_hints=build_context_summary(state, "preliminary_legal_scan", 2000),
    memory_context=state.get("memory_context", ""),
)
# LLM: call_llm_with_grounding
```

### Competitive Landscape (02)
```python
prompt = COMPETITIVE_LANDSCAPE_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    target_market=state.get("target_market", ""),
    market_intelligence_summary=build_context_summary(state, "customer_research"),
)
# LLM: call_llm_with_grounding
```

### Customer Personas (03)
```python
prompt = CUSTOMER_PERSONAS_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    target_market=state.get("target_market", ""),
    market_intelligence_summary=build_context_summary(state, "customer_research"),
)
# LLM: call_llm
```

### Business Case (04)
```python
prompt = BUSINESS_CASE_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    market_intelligence_summary=build_context_summary(state, "customer_research"),
    competitive_landscape_summary=build_context_summary(state, "competitive_analysis"),
    personas_summary=build_context_summary(state, "detailed_personas"),
)
# LLM: call_llm_with_grounding
```

### Product Requirements (07)
```python
prompt = PRODUCT_REQUIREMENTS_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    personas_summary=build_context_summary(state, "detailed_personas"),
    business_case_summary=build_context_summary(state, "business_case"),
    regulatory_hints=build_context_summary(state, "preliminary_legal_scan", 2000),
)
# LLM: call_llm
```

### Technical Architecture (08)
```python
prompt = TECHNICAL_ARCHITECTURE_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    prd_summary=build_context_summary(state, "product_requirements"),
    personas_summary=build_context_summary(state, "detailed_personas"),
    regulatory_hints=build_context_summary(state, "preliminary_legal_scan", 2000),
)
# LLM: call_llm
```

### Regulatory & Compliance (09)
```python
prompt = REGULATORY_COMPLIANCE_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    prd_summary=build_context_summary(state, "product_requirements"),
    tech_arch_summary=build_context_summary(state, "technical_architecture"),
)
# LLM: call_llm_with_grounding
```

### Risk Assessment (10)
```python
prompt = RISK_ASSESSMENT_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    market_intelligence_summary=build_context_summary(state, "customer_research"),
    competitive_landscape_summary=build_context_summary(state, "competitive_analysis"),
    business_case_summary=build_context_summary(state, "business_case"),
    prd_summary=build_context_summary(state, "product_requirements"),
    tech_arch_summary=build_context_summary(state, "technical_architecture"),
    regulatory_summary=build_context_summary(state, "legal_regulatory_review"),
)
# LLM: call_llm
```

---

## 4.4 Update Model Config

**File:** `backend/config.py` (MODIFY)

```python
AGENT_MODEL_CONFIG = {
    # Discovery Swarm
    "Market Intelligence": "flash",
    "Competitive Landscape": "flash",
    "Customer Personas": "flash",

    # Strategy Swarm
    "Business Case": "pro",
    "Go-to-Market": "pro",          # Phase 5
    "Financial Model": "pro",        # Phase 5

    # Delivery Swarm
    "Product Requirements": "flash",
    "Technical Architecture": "flash",
    "Regulatory & Compliance": "pro",
    "Risk Assessment": "flash",

    # Design Agents (Phase 6)
    "Wireframe Designer": "flash",
    "Prototype Generator": "pro",

    # Synthesis Agents (Phase 7)
    "Stakeholder Views": "pro",
    "Validation Playbook": "pro",
    "Executive Summary": "flash",

    # Utilities
    "claim_extractor": "flash",
    "Critique": "pro",
}
```

---

## 4.5 Grounding Decision

Agents using `call_llm_with_grounding()` — need real-world data:
- Market Intelligence (01) — market sizes, growth rates, competitor data
- Competitive Landscape (02) — pricing, funding, features
- Business Case (04) — industry benchmarks, comparable company data
- Regulatory & Compliance (09) — specific regulation texts and requirements

All other agents use `call_llm()` — they work from upstream context, not web search.

---

## Test Phase 4

1. Run a full pack with "AI-powered cash flow forecasting for SME banking"
2. Compare output quality against pre-revamp output — should be noticeably better
3. Verify evidence tiers appear throughout all sections
4. Verify market sizing includes methodology (not just "$X billion")
5. Verify competitive landscape has real competitor data with source URLs
6. Verify PRD user stories reference personas by name and include screen IDs (S1, S2)
7. Verify no agent produces generic output ("the market is growing rapidly")
