# Seedcraft Architecture Documentation

## Complete Technical Reference for the Multi-Agent Product Discovery System

**Version**: 2.1 (Parallel Execution Fixes + SSE Improvements)
**Last Updated**: February 6, 2026

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Agentic Architecture](#3-agentic-architecture)
4. [Swarm Architecture](#4-swarm-architecture)
5. [Facilitator Agent](#5-facilitator-agent)
6. [Cross-Run Learning](#6-cross-run-learning)
7. [State Management](#7-state-management)
8. [Backend Structure](#8-backend-structure)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Real-Time Streaming (SSE)](#10-real-time-streaming-sse)
11. [Data Flow](#11-data-flow)
12. [Database Schema](#12-database-schema)
13. [API Reference](#13-api-reference)
14. [Configuration](#14-configuration)

---

## 1. System Overview

Seedcraft is an AI-powered product discovery system that transforms product ideas into comprehensive "inception packs" - decision-ready documents containing market research, business strategy, technical architecture, and more.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Swarm-Based Multi-Agent Architecture** | 12+ specialized AI agents organized into 3 parallel swarms |
| **Facilitator Agent** | Central coordinator that detects contradictions and resolves conflicts |
| **Cross-Run Learning** | High-quality outputs stored with embeddings for future retrieval |
| **Parallel Execution** | Agents within swarms run concurrently via `asyncio.gather` |
| **Real-Time Streaming** | 15 SSE event types for granular progress tracking |
| **Multi-Model Routing** | Gemini Flash for speed, Gemini Pro for deep reasoning |
| **Search Grounding** | Google Search integration for real-world data validation |
| **Contradiction Detection** | Automatic detection and resolution of inconsistencies |

### What You Get

A complete inception pack containing 10+ sections:

| Swarm | Agents | Output Sections |
|-------|--------|-----------------|
| **Discovery** | Customer Research, Competitive Intelligence, Persona Development | Market Hypotheses, Competitive Analysis, Detailed Personas |
| **Strategy** | Business Strategy, GTM Strategy, Financial Modeling | Lean Canvas, Go-to-Market Plan, Financial Projections |
| **Delivery** | PRD Generator, Technical Architect, Legal & Regulatory, Risk Assessment | PRD, Architecture, Legal Review, Risk Matrix |

**Additional Components:**
- Research Plan (Planning Agent)
- Executive Summary (Synthesizer)
- Quality Assessment (Critique Agent)

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + TypeScript)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ LandingPage │  │DiscoveryForm│  │     PackViewer          │ │
│  │             │  │             │  │  ┌─────────────────────┐│ │
│  │             │  │ProgressTrack│  │  │ Charts (recharts)   ││ │
│  │             │  │             │  │  │ - Competitive Pos   ││ │
│  │             │  │   useSSE()  │  │  │ - Financial Proj    ││ │
│  │             │  │             │  │  │ - Risk Matrix       ││ │
│  │             │  │             │  │  │ - Lean Canvas       ││ │
│  └─────────────┘  └─────────────┘  │  └─────────────────────┘│ │
│                                     └─────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    REST API + SSE (15 event types)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     BACKEND (FastAPI + LangGraph)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FACILITATOR AGENT                      │  │
│  │          (Coordinates swarms, detects contradictions)     │  │
│  └─────────────────────────┬────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────────────────────▼────────────────────────────────┐  │
│  │                   PLANNING PHASE                          │  │
│  │  ┌─────────────┐    ┌─────────────────────┐              │  │
│  │  │   Planner   │    │  Legal Preliminary  │  (parallel)  │  │
│  │  │   Agent     │    │       Scan          │              │  │
│  │  └─────────────┘    └─────────────────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────────────────────▼────────────────────────────────┐  │
│  │                  DISCOVERY SWARM (Parallel)               │  │
│  │  ┌────────────────┐ ┌───────────────┐ ┌────────────────┐ │  │
│  │  │   Customer     │ │  Competitive  │ │    Persona     │ │  │
│  │  │   Research     │ │ Intelligence  │ │  Development   │ │  │
│  │  │   [Flash]      │ │   [Flash]     │ │    [Flash]     │ │  │
│  │  └────────────────┘ └───────────────┘ └────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                  Contradiction Check ──────────────────────┐   │
│                            │                               │   │
│  ┌─────────────────────────▼────────────────────────────┐ │   │
│  │                  STRATEGY SWARM (Parallel)            │ │   │
│  │  ┌────────────────┐ ┌───────────────┐ ┌────────────┐ │ │   │
│  │  │   Business     │ │     GTM       │ │  Financial │ │ │   │
│  │  │   Strategy     │ │   Strategy    │ │  Modeling  │ │ │   │
│  │  │    [Pro]       │ │    [Pro]      │ │   [Pro]    │ │ │   │
│  │  └────────────────┘ └───────────────┘ └────────────┘ │ │   │
│  └──────────────────────────────────────────────────────┘ │   │
│                            │                               │   │
│                  Contradiction Check ◄─────────────────────┘   │
│                            │                                    │
│  ┌─────────────────────────▼────────────────────────────────┐  │
│  │                  DELIVERY SWARM (Parallel)                │  │
│  │  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐  │  │
│  │  │   PRD    │ │  Tech    │ │  Legal  │ │    Risk      │  │  │
│  │  │  Loop    │ │ Architect│ │ Review  │ │  Assessment  │  │  │
│  │  │ [Mixed]  │ │ [Flash]  │ │  [Pro]  │ │   [Flash]    │  │  │
│  │  └──────────┘ └──────────┘ └─────────┘ └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────────────────────▼────────────────────────────────┐  │
│  │                  QUALITY & SYNTHESIS                      │  │
│  │  ┌─────────────┐         ┌───────────────────────┐       │  │
│  │  │  Critique   │────────▶│  Executive Summary    │       │  │
│  │  │   [Pro]     │         │       [Flash]         │       │  │
│  │  └─────────────┘         └───────────────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────────────────────▼────────────────────────────────┐  │
│  │                  MEMORY PIPELINE                          │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │  │
│  │  │ Generate    │───▶│   Store     │───▶│  Retrieve   │   │  │
│  │  │ Embedding   │    │ in pgvector │    │  Similar    │   │  │
│  │  │ (Gemini)    │    │             │    │  Memories   │   │  │
│  │  └─────────────┘    └─────────────┘    └─────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼─────────┐       ┌───────────▼───────────┐
    │   Google Gemini   │       │      Supabase         │
    │  Flash + Pro +    │       │  PostgreSQL + pgvector│
    │  Embeddings +     │       │    + Auth + RLS       │
    │  Search Grounding │       │                       │
    └───────────────────┘       └───────────────────────┘
```

---

## 3. Agentic Architecture

### Agent Overview

Seedcraft uses **12+ specialized agents** organized by function:

#### Planning Phase

| Agent | Model | File | Purpose |
|-------|-------|------|---------|
| **Planner** | Flash | `planner.py` | Domain classification, competitor identification, regulatory focus |
| **Legal Preliminary** | Flash | `legal_regulatory.py` | Quick regulatory landscape scan (runs in parallel with planner) |

#### Discovery Swarm

| Agent | Model | File | Purpose |
|-------|-------|------|---------|
| **Customer Research** | Flash + Grounding | `customer_research.py` | Market analysis, pain signals, competitive positioning |
| **Competitive Intelligence** | Flash + Grounding | `swarms/discovery_swarm.py` | Deep competitor profiles, market share, moats |
| **Persona Development** | Flash | `swarms/discovery_swarm.py` | Detailed user personas with psychographics |

#### Strategy Swarm

| Agent | Model | File | Purpose |
|-------|-------|------|---------|
| **Business Strategy** | Pro + Grounding | `business_strategy.py` | Lean Canvas, revenue model, strategic recommendations |
| **GTM Strategy** | Pro | `swarms/strategy_swarm.py` | Go-to-market plan, launch strategy, channels |
| **Financial Modeling** | Pro | `swarms/strategy_swarm.py` | Detailed projections, unit economics, break-even |

#### Delivery Swarm

| Agent | Model | File | Purpose |
|-------|-------|------|---------|
| **PRD Generator** | Flash | `prd_generator.py` | Epics, user stories, acceptance criteria |
| **PRD Critic** | Pro | `prd_critic.py` | Quality evaluation, feedback |
| **PRD Formatter** | Flash | `prd_formatter.py` | Final PRD formatting |
| **Technical Architect** | Flash | `technical_architect.py` | System design, Mermaid diagrams |
| **Legal & Regulatory** | Pro + Grounding | `legal_regulatory.py` | Full compliance review |
| **Risk Assessment** | Flash | `swarms/delivery_swarm.py` | Risk matrix with likelihood/impact |

#### Quality & Synthesis

| Agent | Model | File | Purpose |
|-------|-------|------|---------|
| **Critique** | Pro | `critique.py` | Cross-validation, calibrated scoring |
| **Executive Summary** | Flash | `orchestrator.py` | Decision brief, key decisions |

### Agent Implementation Pattern

Each agent follows this consistent pattern:

```python
# backend/agents/customer_research.py

async def run_customer_research_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Customer Research Agent implementation.

    Flow:
    1. Extract context from state
    2. Format the prompt with context
    3. Call LLM (optionally with memory augmentation)
    4. Parse and validate response
    5. Update state with results
    6. Return updated state
    """
    AGENT_NAME = "Customer Research"

    # Update state to show agent is running
    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Get research plan context from planning phase
    research_plan = state.get("research_plan", {})

    # Format prompt with all available context
    prompt = format_prompt(
        CUSTOMER_RESEARCH_PROMPT,
        product_idea=state["product_idea"],
        industry=state.get("industry"),
        target_market=state.get("target_market"),
        competitors=research_plan.get("competitors", []),
        regulatory_hints=state.get("preliminary_legal_scan", {}).get("key_areas", []),
    )

    # Call LLM with grounding enabled for real-world data
    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    # Update metrics
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get("duration_seconds", 0.0)

    # Parse response and update state
    if result["success"]:
        # Validate visual data if present
        if "competitive_positioning" in result["data"]:
            try:
                positioning = CompetitivePositioning.model_validate(
                    result["data"]["competitive_positioning"]
                )
                result["data"]["competitive_positioning"] = positioning.model_dump()
            except ValidationError:
                pass  # Use raw data if validation fails

        state["customer_research"] = result["data"]
    else:
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"{AGENT_NAME}: {result['error']}")

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

### Base Agent Utilities

```python
# backend/agents/base_agent.py

async def call_llm(prompt: str, agent_name: str) -> dict:
    """Basic LLM call without grounding."""
    model = get_model_for_agent(agent_name)  # Returns 'flash' or 'pro'
    full_model_name = settings.llm_model if model == "flash" else settings.llm_pro_model

    client = genai.Client(api_key=settings.google_api_key)

    response = await client.aio.models.generate_content(
        model=full_model_name,
        contents=prompt,
        config=GenerateContentConfig(
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_tokens,
        )
    )

    return parse_json_response(response)


async def call_llm_with_grounding(prompt: str, agent_name: str) -> dict:
    """LLM call with Google Search grounding enabled."""
    # Same as above but with search tool:
    config = GenerateContentConfig(
        tools=[Tool(google_search=GoogleSearch())],
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_tokens,
    )
    # ...


async def call_llm_with_memory(
    prompt: str,
    agent_name: str,
    state: DiscoveryState
) -> dict:
    """LLM call with memory augmentation from past high-quality runs."""
    from services.embeddings import generate_embedding, find_similar_memories, format_memories_for_prompt

    # 1. Generate embedding for current context
    domain_type = state.get("research_plan", {}).get("domain_type", "general")
    query_text = f"{state['product_idea']} {state.get('industry', '')} {domain_type}"

    try:
        query_embedding = await generate_embedding(query_text)

        # 2. Find similar high-quality memories
        memories = await find_similar_memories(
            query_embedding=query_embedding,
            domain_type=domain_type,
            agent_name=agent_name,
            limit=3,
        )

        # 3. Inject memories into prompt if found
        if memories:
            memory_context = format_memories_for_prompt(memories)
            prompt = f"{prompt}\n\n## HIGH-QUALITY EXAMPLES FROM SIMILAR PRODUCTS\n{memory_context}"

    except Exception as e:
        logger.warning("memory_retrieval_failed", error=str(e))
        # Continue without memories - non-blocking

    # 4. Call LLM with augmented prompt
    return await call_llm(prompt, agent_name)
```

---

## 4. Swarm Architecture

### Overview

Swarms enable **parallel execution** of independent agents, significantly reducing total execution time.

```
Without Swarms (Sequential):
┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
│Agent 1 │──▶│Agent 2 │──▶│Agent 3 │──▶│Agent 4 │──▶│Agent 5 │
└────────┘   └────────┘   └────────┘   └────────┘   └────────┘
Total time = 10 + 10 + 10 + 10 + 10 = 50 minutes

With Swarms (Parallel):
┌─────────────────────────────────┐
│ Swarm 1 (parallel)              │   ┌────────┐   ┌────────┐
│ ┌────────┐ ┌────────┐ ┌────────┐│──▶│ Merge  │──▶│ Next   │
│ │Agent 1 │ │Agent 2 │ │Agent 3 ││   └────────┘   │ Swarm  │
│ └────────┘ └────────┘ └────────┘│                └────────┘
└─────────────────────────────────┘
Total time = max(10, 10, 10) + merge = 12 minutes
```

### BaseSwarm Implementation

```python
# backend/agents/swarms/base.py

class BaseSwarm(ABC):
    """Abstract base class for agent swarms."""

    swarm_name: str = "BaseSwarm"
    agent_names: list[str] = []

    def __init__(self):
        self.logger = structlog.get_logger(f"swarm.{self.swarm_name}")

    @abstractmethod
    def get_agent_tasks(
        self, state: DiscoveryState
    ) -> list[tuple[str, Coroutine[Any, Any, DiscoveryState]]]:
        """
        Return list of (agent_name, coroutine) tuples to run in parallel.

        Each coroutine receives a COPY of the state to prevent race conditions.
        """
        pass

    async def run(self, state: DiscoveryState) -> DiscoveryState:
        """Execute all agents in the swarm in parallel."""
        start_time = datetime.utcnow()

        self.logger.info(
            "swarm_start",
            swarm=self.swarm_name,
            session_id=state["session_id"],
            agent_count=len(self.agent_names),
        )

        # Get agent tasks
        agent_tasks = self.get_agent_tasks(state)

        if not agent_tasks:
            return state

        # Extract names and coroutines
        agent_names = [name for name, _ in agent_tasks]
        coroutines = [coro for _, coro in agent_tasks]

        # Run ALL agents in parallel
        results = await asyncio.gather(
            *coroutines,
            return_exceptions=True,  # Don't fail entire swarm on single agent error
        )

        # Merge results back into state
        merged_state = self._merge_results(state, agent_names, results)

        # Log completion
        duration = (datetime.utcnow() - start_time).total_seconds()
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        self.logger.info(
            "swarm_complete",
            swarm=self.swarm_name,
            session_id=state["session_id"],
            duration_seconds=round(duration, 2),
            success_count=success_count,
            failure_count=len(results) - success_count,
        )

        return merged_state

    def _merge_results(
        self,
        base_state: DiscoveryState,
        agent_names: list[str],
        results: list[DiscoveryState | Exception],
    ) -> DiscoveryState:
        """Merge results from parallel agent executions."""
        merged = dict(base_state)

        for agent_name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                # Log error but continue with other agents' results
                self.logger.error(
                    "swarm_agent_failed",
                    swarm=self.swarm_name,
                    agent=agent_name,
                    error=str(result),
                )
                if "errors" not in merged:
                    merged["errors"] = []
                merged["errors"].append(f"{agent_name}: {str(result)}")
                continue

            # Copy specific output fields from the result
            output_fields = self.get_output_fields(agent_name)
            for field in output_fields:
                if field in result and result[field] is not None:
                    merged[field] = result[field]

            # Aggregate token usage and duration
            merged["total_tokens_used"] = merged.get("total_tokens_used", 0) + result.get("total_tokens_used", 0)
            merged["total_duration_seconds"] = merged.get("total_duration_seconds", 0.0) + result.get("total_duration_seconds", 0.0)

        merged["updated_at"] = datetime.utcnow().isoformat()
        return merged

    def get_output_fields(self, agent_name: str) -> list[str]:
        """Get the state fields that an agent outputs."""
        field_mappings = {
            "customer_research": ["customer_research"],
            "competitive_intelligence": ["competitive_analysis"],
            "persona_development": ["detailed_personas"],
            "business_strategy": ["business_case"],
            "gtm_strategy": ["gtm_plan"],
            "financial_modeling": ["financial_model"],
            "product_requirements": ["product_requirements"],
            "technical_architect": ["technical_architecture"],
            "legal_regulatory": ["legal_regulatory_review"],
            "risk_assessment": ["risk_assessment"],
        }
        return field_mappings.get(agent_name, [agent_name])
```

### Discovery Swarm

```python
# backend/agents/swarms/discovery_swarm.py

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
        """Get discovery agent coroutines."""
        return [
            ("customer_research", run_customer_research_agent(state.copy())),
            ("competitive_intelligence", run_competitive_intelligence(state.copy())),
            ("persona_development", run_persona_development(state.copy())),
        ]


async def run_competitive_intelligence(state: DiscoveryState) -> DiscoveryState:
    """
    Deep competitive analysis agent.

    Focuses on:
    - Detailed competitor profiles
    - Competitive positioning
    - Market share analysis
    - Competitive moats and threats
    """
    AGENT_NAME = "Competitive Intelligence"

    prompt = f"""You are a Competitive Intelligence Analyst...

## PRODUCT IDEA
{state['product_idea']}

## YOUR TASK
Perform deep competitive analysis:
1. Direct Competitors - Products solving the same problem
2. Indirect Competitors - Alternative solutions or workarounds
3. Potential Future Competitors - Companies that could enter
4. Competitive Moats - What makes each competitor defensible
5. Market Positioning - How each competitor positions themselves
6. Competitive Threats - Risks from competition

## OUTPUT FORMAT
{{
  "direct_competitors": [...],
  "indirect_competitors": [...],
  "potential_future_competitors": [...],
  "competitive_moats": {{...}},
  "market_dynamics": {{...}},
  "strategic_recommendations": [...]
}}
"""

    result = await call_llm_with_grounding(prompt, AGENT_NAME)

    if result["success"]:
        state["competitive_analysis"] = result["data"]

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
    # Similar implementation...
```

### Strategy Swarm

```python
# backend/agents/swarms/strategy_swarm.py

class StrategySwarm(BaseSwarm):
    """
    Swarm for business strategy development.

    Runs business strategy, GTM strategy, and financial modeling
    in parallel to create comprehensive business planning.
    """

    swarm_name = "StrategySwarm"
    agent_names = [
        "business_strategy",
        "gtm_strategy",
        "financial_modeling",
    ]

    def get_agent_tasks(self, state: DiscoveryState):
        return [
            ("business_strategy", run_business_strategy_agent(state.copy())),
            ("gtm_strategy", run_gtm_strategy(state.copy())),
            ("financial_modeling", run_financial_modeling(state.copy())),
        ]
```

### Delivery Swarm

```python
# backend/agents/swarms/delivery_swarm.py

class DeliverySwarm(BaseSwarm):
    """
    Swarm for product delivery specifications.

    Runs PRD generation, technical architecture, legal review,
    and risk assessment in parallel.
    """

    swarm_name = "DeliverySwarm"
    agent_names = [
        "product_requirements",
        "technical_architect",
        "legal_regulatory",
        "risk_assessment",
    ]
```

---

## 5. Facilitator Agent

The Facilitator is the **central coordinator** that orchestrates all swarms and ensures consistency.

### Responsibilities

1. **Dispatches swarms** in dependency order (Discovery → Strategy → Delivery)
2. **Detects contradictions** between agent outputs
3. **Resolves conflicts** by re-running specific agents with context
4. **Synthesizes outputs** into final inception pack

### Implementation

```python
# backend/agents/facilitator.py

class FacilitatorAgent:
    """Central intelligence coordinating all swarms."""

    def __init__(self):
        self.logger = structlog.get_logger("facilitator")
        self.discovery_swarm = DiscoverySwarm()
        self.strategy_swarm = StrategySwarm()
        self.delivery_swarm = DeliverySwarm()

    async def run(self, state: DiscoveryState) -> DiscoveryState:
        """Execute the complete swarm-based workflow."""
        self.logger.info("facilitator_start", session_id=state["session_id"])

        try:
            # Phase 1: Planning
            state = await self._run_planning_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # Phase 2: Discovery Swarm
            state = await self._run_discovery_phase(state)

            # Check for contradictions in discovery outputs
            contradictions = self.detect_contradictions(state, phase="discovery")
            if contradictions:
                state = await self._resolve_contradictions(state, contradictions)

            # Phase 3: Strategy Swarm (depends on Discovery)
            state = await self._run_strategy_phase(state)

            # Check for contradictions between discovery and strategy
            contradictions = self.detect_contradictions(state, phase="strategy")
            if contradictions:
                state = await self._resolve_contradictions(state, contradictions)

            # Phase 4: Delivery Swarm (depends on Discovery + Strategy)
            state = await self._run_delivery_phase(state)

            # Phase 5: Quality Check
            state = await self._run_quality_check(state)

            # Phase 6: Executive Summary and Finalization
            state = await self._synthesize_outputs(state)

            return state

        except Exception as e:
            self.logger.error("facilitator_error", error=str(e))
            state["status"] = SessionStatus.FAILED
            state["errors"].append(f"Facilitator error: {str(e)}")
            return state

    def detect_contradictions(
        self, state: DiscoveryState, phase: str = "all"
    ) -> list[dict]:
        """
        Detect contradictions between agent outputs.

        Checks for inconsistencies in:
        - Market size estimates (TAM/SAM/SOM)
        - Pricing assumptions
        - Target customer definitions
        - Technical feasibility vs business requirements
        """
        contradictions = []

        customer_research = state.get("customer_research", {})
        business_case = state.get("business_case", {})
        financial_model = state.get("financial_model", {})
        gtm_plan = state.get("gtm_plan", {})

        # Check 1: Market size consistency
        if customer_research and business_case:
            cr_tam = customer_research.get("market_context", {}).get("total_addressable_market", "")
            bc_tam = business_case.get("market_size", {}).get("tam", "")

            if cr_tam and bc_tam and self._values_differ_significantly(cr_tam, bc_tam):
                contradictions.append({
                    "type": "market_size",
                    "agents": ["customer_research", "business_strategy"],
                    "field": "TAM",
                    "values": {"customer_research": cr_tam, "business_case": bc_tam},
                    "severity": "medium",
                })

        # Check 2: Pricing consistency
        if business_case and financial_model:
            bc_pricing = business_case.get("revenue_streams", [])
            fm_pricing = financial_model.get("revenue_model", {}).get("pricing_tiers", [])

            bc_price = self._extract_price(bc_pricing)
            fm_price = fm_pricing[0].get("price_monthly", 0) if fm_pricing else 0

            if bc_price and fm_price and abs(bc_price - fm_price) / max(bc_price, fm_price) > 0.5:
                contradictions.append({
                    "type": "pricing",
                    "agents": ["business_strategy", "financial_modeling"],
                    "field": "pricing",
                    "values": {"business_case": bc_price, "financial_model": fm_price},
                    "severity": "high",
                })

        # Check 3: Target customer consistency
        if customer_research and gtm_plan:
            cr_segments = customer_research.get("market_context", {}).get("customer_segments", [])
            gtm_segment = gtm_plan.get("market_entry_strategy", {}).get("initial_segment", "")

            if cr_segments and gtm_segment:
                if not any(gtm_segment.lower() in str(seg).lower() for seg in cr_segments):
                    contradictions.append({
                        "type": "target_customer",
                        "agents": ["customer_research", "gtm_strategy"],
                        "severity": "medium",
                    })

        if contradictions:
            self.logger.warning(
                "contradictions_detected",
                phase=phase,
                count=len(contradictions),
                types=[c["type"] for c in contradictions],
            )

        return contradictions

    async def _resolve_contradictions(
        self,
        state: DiscoveryState,
        contradictions: list[dict],
    ) -> DiscoveryState:
        """Resolve contradictions by re-running specific agents with context."""
        self.logger.info(
            "resolving_contradictions",
            session_id=state["session_id"],
            count=len(contradictions),
        )

        # Only resolve high-severity contradictions
        high_severity = [c for c in contradictions if c.get("severity") == "high"]

        if not high_severity:
            return state  # Just log medium severity and continue

        # Add contradiction context to state for agents to consider
        state["contradiction_context"] = {
            "contradictions": contradictions,
            "resolution_instruction": (
                "Previous outputs contained inconsistencies. "
                "Please review and ensure your output is consistent with other agents' findings."
            ),
        }

        # Re-run the second agent in each contradiction
        agents_to_rerun = set()
        for c in high_severity:
            agents_to_rerun.add(c["agents"][1])

        for agent in agents_to_rerun:
            self.logger.info("rerunning_agent_for_resolution", agent=agent)

            if agent == "business_strategy":
                from agents.business_strategy import run_business_strategy_agent
                state = await run_business_strategy_agent(state)
            elif agent == "financial_modeling":
                from agents.swarms.strategy_swarm import run_financial_modeling
                state = await run_financial_modeling(state)
            elif agent == "gtm_strategy":
                from agents.swarms.strategy_swarm import run_gtm_strategy
                state = await run_gtm_strategy(state)

        # Clear contradiction context after resolution
        del state["contradiction_context"]

        return state
```

---

## 6. Cross-Run Learning

### Overview

The memory system stores high-quality outputs with vector embeddings, enabling retrieval of similar past examples to improve future outputs.

```
┌──────────────────────────────────────────────────────────────┐
│                    MEMORY PIPELINE                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  STORAGE (after successful run with score >= 0.8)            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │   Output    │───▶│  Compress   │───▶│  Generate   │       │
│  │   (JSON)    │    │  to Summary │    │  Embedding  │       │
│  │             │    │  (2000 chr) │    │  (768-dim)  │       │
│  └─────────────┘    └─────────────┘    └──────┬──────┘       │
│                                               │              │
│                                        ┌──────▼──────┐       │
│                                        │   Store in  │       │
│                                        │   pgvector  │       │
│                                        └─────────────┘       │
│                                                               │
│  RETRIEVAL (during new run)                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │   Query     │───▶│  Generate   │───▶│   Vector    │       │
│  │   Context   │    │  Embedding  │    │ Similarity  │       │
│  │             │    │             │    │   Search    │       │
│  └─────────────┘    └─────────────┘    └──────┬──────┘       │
│                                               │              │
│                                        ┌──────▼──────┐       │
│                                        │ Top 3 Most  │       │
│                                        │   Similar   │───────┤
│                                        │  (>70% sim) │       │
│                                        └─────────────┘       │
│                                               │              │
│                                        ┌──────▼──────┐       │
│                                        │   Inject    │       │
│                                        │ into Prompt │       │
│                                        └─────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### Embedding Service

```python
# backend/services/embeddings.py

EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 768

async def generate_embedding(text: str) -> list[float]:
    """
    Generate 768-dimensional embedding using Gemini.

    Uses text-embedding-004 which produces high-quality
    semantic embeddings suitable for similarity search.
    """
    client = genai.Client(api_key=settings.google_api_key)

    # Truncate if too long (embedding models have limits)
    max_chars = 25000
    if len(text) > max_chars:
        text = text[:max_chars]
        logger.warning("text_truncated_for_embedding", original_length=len(text))

    result = await client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    embedding = result.embeddings[0].values

    logger.debug(
        "embedding_generated",
        text_length=len(text),
        embedding_dimension=len(embedding),
    )

    return embedding


async def find_similar_memories(
    query_embedding: list[float],
    domain_type: str | None = None,
    agent_name: str | None = None,
    user_id: str | None = None,
    match_threshold: float = 0.7,
    limit: int = 3,
) -> list[dict]:
    """
    Find similar high-quality memories using vector similarity.

    Uses pgvector's cosine similarity search with optional filters.
    """
    supabase = await get_supabase_client()

    # Call the match_memories function via RPC
    result = await supabase.rpc(
        "match_memories",
        {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": limit,
            "filter_domain": domain_type,
            "filter_agent": agent_name,
            "filter_user_id": user_id,
        }
    ).execute()

    memories = result.data or []

    logger.info(
        "similar_memories_found",
        count=len(memories),
        domain_type=domain_type,
        agent_name=agent_name,
    )

    return memories


def format_memories_for_prompt(memories: list[dict]) -> str:
    """Format retrieved memories into a prompt-friendly string."""
    if not memories:
        return ""

    formatted = []

    for i, memory in enumerate(memories, 1):
        similarity = memory.get("similarity", 0)
        quality = memory.get("quality_score", 0)
        content = memory.get("content_summary", "")

        formatted.append(
            f"### Example {i} (Similarity: {similarity:.0%}, Quality: {quality:.0%})\n"
            f"{content}\n"
        )

    return "\n".join(formatted)
```

### Memory Storage Pipeline

```python
# backend/services/memory_pipeline.py

async def store_successful_run(
    session_id: str,
    user_id: str,
    state: DiscoveryState,
) -> None:
    """
    Extract and store memories from a successful run.

    Only stores outputs from runs with quality score >= 0.8
    """
    quality_score = state.get("quality_assessment", {}).get("overall_score", 0)

    # Only store high-quality runs
    if quality_score < 0.8:
        logger.info(
            "memory_skipped_low_quality",
            session_id=session_id,
            quality_score=quality_score,
        )
        return

    domain_type = state.get("research_plan", {}).get("domain_type", "general")
    industry = state.get("industry")

    # Store memories for each major agent output
    agent_outputs = [
        ("customer_research", state.get("customer_research")),
        ("competitive_intelligence", state.get("competitive_analysis")),
        ("business_strategy", state.get("business_case")),
        ("gtm_strategy", state.get("gtm_plan")),
        ("financial_modeling", state.get("financial_model")),
        ("product_requirements", state.get("prd")),
        ("technical_architect", state.get("technical_architecture")),
        ("legal_regulatory", state.get("legal_review")),
    ]

    for agent_name, output in agent_outputs:
        if not output:
            continue

        try:
            # Compress output to summary (key fields, max 2000 chars)
            summary = compress_to_summary(output)

            # Generate embedding
            embedding = await generate_embedding(summary)

            # Store in database
            success = await store_memory(
                user_id=user_id,
                session_id=session_id,
                domain_type=domain_type,
                industry=industry,
                agent_name=agent_name,
                quality_score=quality_score,
                content_summary=summary,
                embedding=embedding,
            )

            if success:
                logger.info(
                    "memory_stored",
                    agent_name=agent_name,
                    quality_score=quality_score,
                )

        except Exception as e:
            logger.error(
                "memory_storage_failed",
                agent_name=agent_name,
                error=str(e),
            )
            # Continue with other agents - non-blocking


def compress_to_summary(output: dict, max_chars: int = 2000) -> str:
    """
    Compress agent output to a summary suitable for embedding.

    Extracts key sections and truncates to fit within embedding limits.
    """
    # Key fields to prioritize for different agent types
    priority_fields = [
        "executive_summary",
        "recommendation",
        "key_findings",
        "summary",
        "pain_signals",
        "lean_canvas",
        "user_personas",
        "epics",
        "system_components",
        "overall_risk_assessment",
    ]

    summary_parts = []

    for field in priority_fields:
        if field in output and output[field]:
            value = output[field]
            if isinstance(value, str):
                summary_parts.append(f"{field}: {value}")
            elif isinstance(value, list) and len(value) > 0:
                items = value[:3]  # Take first few items
                summary_parts.append(f"{field}: {json.dumps(items, default=str)}")
            elif isinstance(value, dict):
                summary_parts.append(f"{field}: {json.dumps(value, default=str)[:500]}")

    summary = "\n".join(summary_parts)

    if len(summary) > max_chars:
        summary = summary[:max_chars - 3] + "..."

    return summary
```

### Database Schema for Memories

```sql
-- backend/migrations/002_add_run_memories.sql

-- Enable pgvector extension (Supabase has this)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE run_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_id TEXT,
    domain_type TEXT NOT NULL,
    industry TEXT,
    agent_name TEXT NOT NULL,
    quality_score FLOAT NOT NULL,
    content_summary TEXT NOT NULL,
    embedding VECTOR(768),  -- Gemini text-embedding-004 dimension
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Only store high-quality outputs
    CONSTRAINT quality_threshold CHECK (quality_score >= 0.8)
);

-- Indexes for efficient querying
CREATE INDEX idx_memories_domain ON run_memories(domain_type);
CREATE INDEX idx_memories_agent ON run_memories(agent_name);
CREATE INDEX idx_memories_user ON run_memories(user_id);

-- IVFFlat index for fast approximate nearest neighbor search
CREATE INDEX idx_memories_embedding ON run_memories
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Function for similarity search with filters
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 3,
    filter_domain TEXT DEFAULT NULL,
    filter_agent TEXT DEFAULT NULL,
    filter_user_id UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content_summary TEXT,
    quality_score FLOAT,
    similarity FLOAT,
    domain_type TEXT,
    agent_name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        rm.id,
        rm.content_summary,
        rm.quality_score,
        1 - (rm.embedding <=> query_embedding) AS similarity,
        rm.domain_type,
        rm.agent_name
    FROM run_memories rm
    WHERE
        1 - (rm.embedding <=> query_embedding) > match_threshold
        AND (filter_domain IS NULL OR rm.domain_type = filter_domain)
        AND (filter_agent IS NULL OR rm.agent_name = filter_agent)
        AND (filter_user_id IS NULL OR rm.user_id = filter_user_id)
    ORDER BY rm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

---

## 7. State Management

### Parallel State Merging with Reducers

LangGraph's parallel execution requires special handling when multiple branches update state simultaneously. We use `Annotated` types with custom reducers to control how state is merged when parallel branches converge.

```python
# backend/agents/state.py

from typing import Annotated, Any, Optional

# ═══════════════════════════════════════════════════════════════
# REDUCERS FOR PARALLEL STATE MERGING
# ═══════════════════════════════════════════════════════════════

def keep_last(current: Any, new: Any) -> Any:
    """Keep the last non-None value (for immutable fields like session_id)."""
    return new if new is not None else current

def keep_first_non_none(current: Any, new: Any) -> Any:
    """Keep the first non-None value (for agent outputs set once)."""
    return current if current is not None else new

def merge_errors(current: list[str], new: list[str]) -> list[str]:
    """Merge error lists from parallel branches (deduplicates)."""
    if current is None:
        current = []
    if new is None:
        new = []
    return list(set(current + new))
```

### DiscoveryState Structure

```python
class DiscoveryState(TypedDict, total=False):
    # ═══════════════════════════════════════════════════════════
    # INPUT FIELDS (immutable - use keep_last for parallel safety)
    # ═══════════════════════════════════════════════════════════
    session_id: Annotated[str, keep_last]
    product_idea: Annotated[str, keep_last]
    industry: Annotated[Optional[str], keep_last]
    target_market: Annotated[Optional[str], keep_last]
    constraints: Annotated[Optional[list[str]], keep_last]
    additional_context: Annotated[Optional[str], keep_last]

    # ═══════════════════════════════════════════════════════════
    # WORKFLOW CONTROL (use keep_last for parallel merging)
    # ═══════════════════════════════════════════════════════════
    status: Annotated[SessionStatus, keep_last]
    current_agent: Annotated[str, keep_last]
    iteration: Annotated[int, keep_last]
    started_at: Annotated[str, keep_last]
    updated_at: Annotated[str, keep_last]

    # ═══════════════════════════════════════════════════════════
    # PLANNING PHASE OUTPUTS
    # ═══════════════════════════════════════════════════════════
    research_plan: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    preliminary_legal_scan: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════
    # AGENT OUTPUTS (use keep_first_non_none - set once per agent)
    # ═══════════════════════════════════════════════════════════
    customer_research: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    competitive_analysis: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    detailed_personas: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    business_case: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    gtm_plan: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    financial_model: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    product_requirements: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    technical_architecture: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    legal_regulatory_review: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    risk_assessment: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    quality_assessment: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    executive_summary: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════
    # PRD SUB-WORKFLOW
    # ═══════════════════════════════════════════════════════════
    prd_iteration: Annotated[int, keep_last]
    prd_draft: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    prd_critic_feedback: Annotated[Optional[list[str]], keep_first_non_none]
    prd_critic_score: Annotated[Optional[float], keep_first_non_none]
    prd_quality_passed: Annotated[bool, keep_last]

    # ═══════════════════════════════════════════════════════════
    # FACILITATOR FIELDS
    # ═══════════════════════════════════════════════════════════
    contradiction_context: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════
    # METRICS (errors merge, others keep_last)
    # ═══════════════════════════════════════════════════════════
    errors: Annotated[list[str], merge_errors]
    total_tokens_used: Annotated[int, keep_last]
    total_duration_seconds: Annotated[float, keep_last]
```

### Why Reducers Are Needed

When parallel branches (e.g., `customer_research` and `legal_preliminary`) converge, LangGraph must merge their states. Without reducers, LangGraph throws:

```
InvalidUpdateError: At key 'session_id': Can receive only one value per step.
```

The reducers tell LangGraph how to handle this:

| Reducer | Use Case | Behavior |
|---------|----------|----------|
| `keep_last` | Immutable fields (session_id) | Keep latest value |
| `keep_first_non_none` | Agent outputs | Keep first set value |
| `merge_errors` | Error tracking | Combine from all branches |

---

## 8. Backend Structure

```
backend/
├── main.py                    # FastAPI entry point
├── config.py                  # Settings & model routing
├── requirements.txt           # Dependencies
│
├── agents/                    # Agent implementations
│   ├── __init__.py           # Exports
│   ├── orchestrator.py       # LangGraph workflow + parallel execution
│   ├── facilitator.py        # Swarm coordinator
│   ├── state.py              # DiscoveryState TypedDict
│   ├── prompts.py            # All agent prompts
│   ├── base_agent.py         # LLM utilities + memory augmentation
│   │
│   ├── planner.py            # Planning Agent
│   ├── customer_research.py  # Customer Research Agent
│   ├── business_strategy.py  # Business Strategy Agent
│   ├── legal_regulatory.py   # Legal & Preliminary Scan
│   ├── technical_architect.py# Technical Architect
│   ├── critique.py           # Critique Agent
│   ├── prd_generator.py      # PRD Generator
│   ├── prd_critic.py         # PRD Critic
│   ├── prd_formatter.py      # PRD Formatter
│   ├── prd_subgraph.py       # PRD sub-workflow
│   │
│   └── swarms/               # Swarm implementations
│       ├── __init__.py       # Swarm exports
│       ├── base.py           # BaseSwarm (parallel execution)
│       ├── discovery_swarm.py# Customer, Competitive, Persona
│       ├── strategy_swarm.py # Business, GTM, Financial
│       └── delivery_swarm.py # PRD, Tech, Legal, Risk
│
├── models/                    # Pydantic schemas
│   ├── __init__.py
│   ├── schemas.py            # 60+ data models
│   └── visual_schemas.py     # Chart data schemas
│
├── services/                  # Cross-run learning
│   ├── __init__.py
│   ├── embeddings.py         # Gemini embeddings + similarity
│   └── memory_pipeline.py    # Memory storage/retrieval
│
├── migrations/               # Database migrations
│   └── 002_add_run_memories.sql
│
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── helpers.py            # Session store
│   ├── sse.py                # SSE events (15 types)
│   └── db.py                 # Database client
│
└── tests/                    # Test suite
    ├── unit/
    │   ├── test_orchestrator_routing.py
    │   ├── test_planner.py
    │   ├── test_visual_schemas.py
    │   └── test_export_formatting.py
    └── integration/
        └── test_export_pipeline.py
```

---

## 9. Frontend Architecture

```
frontend/src/
├── main.tsx                    # Entry point
├── App.tsx                     # Main app + state machine
├── App.css                     # Global styles
│
├── components/
│   ├── LandingPage.tsx        # Landing page
│   ├── DiscoveryForm.tsx      # Product idea input
│   ├── ProgressTracker.tsx    # Real-time progress
│   ├── PackViewer.tsx         # Results viewer with charts
│   │
│   └── charts/                # Visualization components
│       ├── index.ts           # Exports
│       ├── charts.css         # Chart styles
│       ├── CompetitivePositionChart.tsx  # Scatter plot
│       ├── FinancialProjectionChart.tsx  # Area chart
│       ├── RiskMatrixChart.tsx           # 5x5 heatmap
│       └── LeanCanvasVisual.tsx          # Canvas grid
│
├── hooks/
│   └── useSSE.ts              # SSE hook (15 event types)
│
├── api/
│   └── client.ts              # API client
│
└── types/
    └── api.ts                 # TypeScript types
```

### Chart Components

```typescript
// frontend/src/components/charts/CompetitivePositionChart.tsx

import { ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export interface CompetitorPosition {
  name: string;
  x_score: number;  // 0-10
  y_score: number;  // 0-10
  description: string;
  is_target_product: boolean;
}

export function CompetitivePositionChart({
  data,
  xAxisLabel,
  yAxisLabel
}: {
  data: CompetitorPosition[];
  xAxisLabel: string;
  yAxisLabel: string;
}) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
        <XAxis
          type="number"
          dataKey="x_score"
          domain={[0, 10]}
          label={{ value: xAxisLabel, position: 'bottom' }}
        />
        <YAxis
          type="number"
          dataKey="y_score"
          domain={[0, 10]}
          label={{ value: yAxisLabel, angle: -90, position: 'left' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Scatter
          data={data}
          shape={({ cx, cy, payload }) => (
            <circle
              cx={cx}
              cy={cy}
              r={payload.is_target_product ? 12 : 8}
              fill={payload.is_target_product ? '#22c55e' : '#6366f1'}
              stroke={payload.is_target_product ? '#16a34a' : '#4f46e5'}
              strokeWidth={2}
            />
          )}
        />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
```

---

## 10. Real-Time Streaming (SSE)

### 15 Event Types

```python
# backend/utils/sse.py

class StreamEventType(str, Enum):
    # Core events
    AGENT_START = "agent_start"       # Agent begins work
    INSIGHT = "insight"               # Key finding discovered
    AGENT_COMPLETE = "agent_complete" # Agent finished
    PROGRESS = "progress"             # Progress percentage
    ERROR = "workflow_error"          # Error occurred (NOT 'error' - reserved by EventSource!)
    DONE = "done"                     # Session complete
    HEARTBEAT = "heartbeat"           # Keep-alive

    # Enhanced events for richer UI
    PLAN_READY = "plan_ready"         # Research plan created
    COMPETITOR_FOUND = "competitor"   # Named competitor identified
    MARKET_DATA = "market_data"       # Market size or trend
    RISK_IDENTIFIED = "risk"          # Risk flagged
    FINANCIAL_METRIC = "financial"    # Financial data point
    DIAGRAM_READY = "diagram"         # Architecture diagram
    CITATION = "citation"             # Source citation
    DECISION_POINT = "decision"       # Key decision identified
```

> **Important**: The error event is named `workflow_error` instead of `error` because `error` is a reserved EventSource event type used by browsers for connection errors. Using `error` for custom events causes conflicts.

### SSE Connection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Client connects to /api/discovery/session/{id}/stream?token= │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Backend sends IMMEDIATE HEARTBEAT                            │
│    (Establishes connection, prevents browser timeout)           │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Backend streams events as agents progress                    │
│    agent_start → insight → insight → agent_complete → ...       │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Workflow complete: Backend sends DONE event                  │
│    Client receives pack, closes connection                      │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend SSE Hook with Safe Event Handling

```typescript
// frontend/src/hooks/useSSE.ts

export function useSSE(
  sessionId: string | null,
  authToken: string | null,
  enabled: boolean = true
): UseSSEResult {
  const [isConnected, setIsConnected] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!sessionId || !authToken || !enabled) return;

    const url = `${API_BASE}/api/discovery/session/${sessionId}/stream?token=${authToken}`;
    const eventSource = new EventSource(url);

    // Safe event handler - validates data exists before JSON parsing
    // This prevents "undefined is not valid JSON" errors when browser
    // fires native EventSource events (which don't have .data)
    const safeEventHandler = (eventType: string) => (e: Event) => {
      const messageEvent = e as MessageEvent;
      if (messageEvent.data !== undefined && messageEvent.data !== null) {
        handleEvent(eventType, messageEvent.data);
      }
    };

    // Core event handlers
    eventSource.addEventListener('agent_start', safeEventHandler('agent_start'));
    eventSource.addEventListener('progress', safeEventHandler('progress'));
    eventSource.addEventListener('done', safeEventHandler('done'));
    eventSource.addEventListener('heartbeat', safeEventHandler('heartbeat'));

    // IMPORTANT: Use 'workflow_error' NOT 'error' (reserved by EventSource)
    eventSource.addEventListener('workflow_error', safeEventHandler('error'));

    // Enhanced event handlers
    eventSource.addEventListener('plan_ready', safeEventHandler('plan_ready'));
    eventSource.addEventListener('competitor', safeEventHandler('competitor'));
    eventSource.addEventListener('market_data', safeEventHandler('market_data'));
    eventSource.addEventListener('financial', safeEventHandler('financial'));
    eventSource.addEventListener('risk', safeEventHandler('risk'));
    eventSource.addEventListener('diagram', safeEventHandler('diagram'));
    eventSource.addEventListener('citation', safeEventHandler('citation'));
    eventSource.addEventListener('decision', safeEventHandler('decision'));

    // Handle browser connection errors (NOT our custom errors)
    eventSource.onerror = (e) => {
      console.error('SSE connection error:', e);
      setIsConnected(false);
      setError('Connection lost. Attempting to reconnect...');
    };

    return () => eventSource.close();
  }, [sessionId, authToken, enabled]);

  return { isConnected, currentAgent, progress, isComplete, /* ... */ };
}
```

### SSE Event Format

All events follow this structure:

```json
{
  "type": "agent_start",
  "agent": "customer_research",
  "data": {
    "message": "Analyzing market and customer needs",
    "display_name": "Customer Research",
    "icon": "search"
  },
  "timestamp": "2026-02-06T15:30:00.000000"
}
```

---

## 11. Data Flow

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. USER SUBMITS PRODUCT IDEA                                        │
│    Frontend: DiscoveryForm → handleSubmit()                         │
│    API: POST /api/discovery/start                                   │
└────────────────────────────────────┬────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. BACKEND PROCESSING                                               │
│    • Validate request (Pydantic)                                    │
│    • Create session_id                                              │
│    • Initialize DiscoveryState                                      │
│    • Launch background task                                         │
│    • Return session_id (202 Accepted)                               │
└────────────────────────────────────┬────────────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
                 ▼                                       ▼
      ┌─────────────────────┐               ┌─────────────────────┐
      │  SSE Connection     │               │  Background Worker  │
      │  (Real-time UI)     │               │  (Facilitator)      │
      └─────────────────────┘               └──────────┬──────────┘
                 │                                     │
                 │                                     ▼
                 │                          ┌─────────────────────┐
                 │                          │   PLANNING PHASE    │
                 │◄─────────────────────────│   Planner + Legal   │
                 │         events           │   (parallel)        │
                 │                          └──────────┬──────────┘
                 │                                     │
                 │                                     ▼
                 │                          ┌─────────────────────┐
                 │                          │  DISCOVERY SWARM    │
                 │◄─────────────────────────│  Customer + Compet  │
                 │                          │  + Persona (||)     │
                 │                          └──────────┬──────────┘
                 │                                     │
                 │                          Contradiction Check
                 │                                     │
                 │                                     ▼
                 │                          ┌─────────────────────┐
                 │                          │   STRATEGY SWARM    │
                 │◄─────────────────────────│  Business + GTM     │
                 │                          │  + Financial (||)   │
                 │                          └──────────┬──────────┘
                 │                                     │
                 │                          Contradiction Check
                 │                                     │
                 │                                     ▼
                 │                          ┌─────────────────────┐
                 │                          │   DELIVERY SWARM    │
                 │◄─────────────────────────│  PRD + Tech + Legal │
                 │                          │  + Risk (||)        │
                 │                          └──────────┬──────────┘
                 │                                     │
                 │                                     ▼
                 │                          ┌─────────────────────┐
                 │◄─────────────────────────│  QUALITY CHECK      │
                 │                          │  Critique + Summary │
                 │                          └──────────┬──────────┘
                 │                                     │
                 │                                     ▼
                 │                          ┌─────────────────────┐
                 │◄─────────────────────────│  STORE MEMORIES     │
                 │        "done"            │  (if score >= 0.8)  │
                 │                          └─────────────────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │  PackViewer shows   │
      │  results with       │
      │  interactive charts │
      └─────────────────────┘
```

---

## 12. Database Schema

### Tables

```sql
-- Discovery Sessions
CREATE TABLE discovery_sessions (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    status TEXT NOT NULL DEFAULT 'pending',
    product_idea TEXT NOT NULL,
    industry TEXT,
    target_market TEXT,
    constraints JSONB,
    current_agent TEXT,
    iteration INTEGER DEFAULT 1,
    progress_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inception Packs
CREATE TABLE inception_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE REFERENCES discovery_sessions(id),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    pack_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Run Memories (Cross-Run Learning)
CREATE TABLE run_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_id TEXT,
    domain_type TEXT NOT NULL,
    industry TEXT,
    agent_name TEXT NOT NULL,
    quality_score FLOAT NOT NULL CHECK (quality_score >= 0.8),
    content_summary TEXT NOT NULL,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 13. API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/discovery/start` | Start discovery session |
| `GET` | `/api/discovery/session/{id}` | Get session status |
| `GET` | `/api/discovery/session/{id}/stream` | SSE event stream |
| `GET` | `/api/discovery/session/{id}/pack` | Get inception pack |
| `DELETE` | `/api/discovery/session/{id}` | Delete session |
| `GET` | `/api/discovery/sessions` | List all sessions |
| `GET` | `/api/discovery/session/{id}/export/pdf` | Export as PDF |
| `GET` | `/api/discovery/session/{id}/export/docx` | Export as DOCX |
| `GET` | `/api/health` | Health check |

---

## 14. Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=...           # Gemini API key
SUPABASE_URL=...             # Supabase project URL
SUPABASE_KEY=...             # Supabase anon key

# LLM Configuration
LLM_MODEL=gemini-2.0-flash   # Default model
LLM_PRO_MODEL=gemini-2.5-pro # Pro model for reasoning
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8192
LLM_ENABLE_GROUNDING=true

# Orchestration
MAX_REVISION_ITERATIONS=3
MIN_QUALITY_SCORE=0.7
PRD_QUALITY_THRESHOLD=0.75

# Application
APP_ENV=development
CORS_ORIGINS=http://localhost:5173
```

### Model Routing

```python
# backend/config.py

AGENT_MODEL_CONFIG = {
    # Flash (speed + cost efficiency)
    "planner": "flash",
    "customer_research": "flash",
    "competitive_intelligence": "flash",
    "persona_development": "flash",
    "prd_generator": "flash",
    "prd_formatter": "flash",
    "technical_architect": "flash",
    "risk_assessment": "flash",
    "executive_summary": "flash",

    # Pro (deep reasoning)
    "business_strategy": "pro",
    "gtm_strategy": "pro",
    "financial_modeling": "pro",
    "prd_critic": "pro",
    "legal_regulatory": "pro",
    "critique": "pro",
}
```

---

## 15. Troubleshooting & Known Issues

### SSE Connection Errors

**Symptom**: `Error parsing SSE event: SyntaxError: "undefined" is not valid JSON`

**Cause**: The browser's EventSource fires native `error` events (for connection issues) which don't have a `.data` property. If you use `addEventListener('error', ...)` for custom events, the handler receives both native errors (no data) and custom events (with data).

**Solution**:
1. Use `workflow_error` instead of `error` for custom SSE events
2. Use `safeEventHandler` that checks if `data` exists before parsing

```typescript
const safeEventHandler = (eventType: string) => (e: Event) => {
  const messageEvent = e as MessageEvent;
  if (messageEvent.data !== undefined && messageEvent.data !== null) {
    handleEvent(eventType, messageEvent.data);
  }
};

// Listen to custom errors (NOT browser errors)
eventSource.addEventListener('workflow_error', safeEventHandler('error'));
```

### Parallel Execution State Merge Errors

**Symptom**: `InvalidUpdateError: At key 'session_id': Can receive only one value per step`

**Cause**: When LangGraph parallel branches converge, both branches have the same field values (e.g., `session_id`). Without reducers, LangGraph can't decide which value to keep.

**Solution**: Use `Annotated` types with reducers in `DiscoveryState`:

```python
from typing import Annotated

def keep_last(current: Any, new: Any) -> Any:
    return new if new is not None else current

session_id: Annotated[str, keep_last]
```

### Critique Agent Reports Section as "Absent" When Present

**Symptom**: Quality assessment says a section (e.g., Technical Architecture) is missing, but it appears in the final pack.

**Cause**: LLM hallucination - the model doesn't carefully read the input or misinterprets the content.

**Solution**: The critique agent now:
1. Logs what content is actually available (`critique_inputs` in logs)
2. Prepends a "Content Availability Note" to the prompt:

```
## CONTENT AVAILABILITY NOTE
- Customer Research: PRESENT
- Business Case: PRESENT
- Technical Architecture: PRESENT

IMPORTANT: Only mark a section as "absent" if it shows "NOT AVAILABLE" above.
```

### OAuth Redirects to Production Instead of Localhost

**Symptom**: After Google sign-in, browser redirects to production URL instead of localhost.

**Cause**: Supabase's OAuth redirect settings. The `redirectTo` parameter may be overridden by Supabase's Site URL setting.

**Solution**:
1. Add `http://localhost:5174` to Supabase Authentication → URL Configuration → Redirect URLs
2. The frontend now uses explicit localhost in development mode:

```typescript
const redirectUrl = import.meta.env.DEV
  ? 'http://localhost:5174'
  : window.location.origin;
```

### Railway Deployment Not Picking Up Changes

**Symptom**: Code changes pushed but production still shows old behavior.

**Causes**:
1. Frontend service hasn't redeployed (backend and frontend are separate services)
2. Browser caching old JavaScript bundles

**Solution**:
1. Check Railway dashboard - verify both services show recent deployments
2. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
3. Check JavaScript filename hash in Network tab - should change after deployment

### Debugging Tips

**Check SSE Events in Browser**:
```
DevTools → Network → Filter by "EventStream" → Click stream → Events tab
```

**Check Backend Logs on Railway**:
```bash
railway logs  # Get recent logs
railway logs | grep "agent_success"  # Filter for agent completions
```

**Check Content Availability Before Critique**:
```bash
railway logs | grep "critique_inputs"
# Shows: has_customer_research=True, has_technical_architecture=True, etc.
```

---

## Summary

Seedcraft v2.0 is a production-grade multi-agent AI system featuring:

- **12+ specialized agents** organized into 3 parallel swarms
- **Facilitator agent** for swarm coordination and contradiction detection
- **Cross-run learning** with vector embeddings and pgvector
- **Real-time SSE streaming** with 15 event types
- **Interactive visualizations** using recharts
- **Multi-model routing** (Gemini Flash + Pro)
- **Search grounding** for real-world data validation

The swarm architecture reduces execution time by running agents in parallel while maintaining consistency through automatic contradiction detection and resolution.
