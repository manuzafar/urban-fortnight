# Seedcraft - AI-Powered Multi-Agent Product Discovery System

## Project Overview

Seedcraft transforms product ideas into comprehensive inception packs using a multi-agent AI system. It generates market research, business strategy, PRD, technical architecture, and more in under 15 minutes.

**Live URLs:**
- Frontend: https://mindful-luck-production.up.railway.app
- Backend API: https://urban-fortnight-production.up.railway.app

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+ / FastAPI / LangGraph |
| Frontend | React 19 / TypeScript / Vite |
| LLM | Google Gemini (Flash + Pro) |
| Database | Supabase PostgreSQL + pgvector |
| Deployment | Docker / Railway |
| Auth | Supabase JWT |

## Directory Structure

```
Product LifeCycle/
├── frontend/                     # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx              # Main app with routing
│   │   ├── components/          # React components
│   │   │   ├── v4/              # V4 UI (current)
│   │   │   │   ├── LandingPageV4.tsx
│   │   │   │   ├── InputFormV4.tsx
│   │   │   │   ├── ExecutionView.tsx
│   │   │   │   ├── PackViewerV4.tsx
│   │   │   │   └── discovery/   # V4 discovery stages
│   │   │   │       ├── DiscoveryViewV4.tsx
│   │   │   │       └── renderers/  # Stage output renderers
│   │   │   ├── PackViewer/      # Inception pack viewer
│   │   │   └── charts/          # Recharts components
│   │   ├── api/client.ts        # API client
│   │   ├── hooks/
│   │   │   ├── useAuth.ts       # Supabase auth hook
│   │   │   ├── useSSE.ts        # SSE streaming hook
│   │   │   └── useSSEV4.ts      # V4 SSE streaming
│   │   └── types/api.ts         # TypeScript types
│   └── package.json
│
├── backend/                      # Python FastAPI
│   ├── main.py                  # FastAPI app entry
│   ├── config.py                # Settings & env vars
│   ├── agents/                  # AI agents (LangGraph)
│   │   ├── orchestrator.py      # Main workflow graph
│   │   ├── state.py             # LangGraph state definition
│   │   ├── facilitator.py       # Master orchestrator
│   │   ├── base_agent.py        # Base agent class
│   │   ├── prompts.py           # All agent prompts
│   │   │
│   │   │   # Core Agents
│   │   ├── planner.py           # Domain analysis
│   │   ├── customer_research.py # Market research
│   │   ├── business_strategy.py # Lean Canvas, revenue model
│   │   ├── gtm_agent.py         # Go-to-market strategy
│   │   ├── financial_model_agent.py  # Financial projections
│   │   ├── technical_architect.py    # System design
│   │   ├── legal_regulatory.py  # Compliance analysis
│   │   ├── wireframe_agent.py   # UI mockups
│   │   ├── prototype_agent.py   # Interactive prototype
│   │   ├── critique.py          # Quality scoring
│   │   │
│   │   │   # PRD Agents
│   │   ├── product_requirements.py  # Requirements generation
│   │   ├── prd_generator.py     # PRD generation
│   │   ├── prd_critic.py        # PRD quality check
│   │   ├── prd_formatter.py     # PRD JSON structuring
│   │   ├── prd_subgraph.py      # PRD quality loop
│   │   │
│   │   │   # Synthesis Agents
│   │   ├── executive_summary_agent.py  # Decision brief
│   │   ├── stakeholder_agent.py # Stakeholder views
│   │   ├── validation_agent.py  # Validation playbook
│   │   ├── claim_extractor.py   # Evidence extraction
│   │   │
│   │   │   # Support Modules
│   │   ├── constraint_broadcaster.py  # Pre-execution constraints
│   │   ├── output_validator.py  # 700+ validation rules
│   │   ├── confidence_calibrator.py   # Evidence-weighted scoring
│   │   ├── context_builder.py   # Evidence-aware context
│   │   ├── two_stage_reasoning.py     # Research then structure
│   │   ├── eval_feedback_bridge.py    # Eval integration
│   │   │
│   │   │   # Swarms (Parallel Execution)
│   │   ├── swarms/
│   │   │   ├── base.py          # Base swarm class
│   │   │   ├── discovery_swarm.py   # Customer + competitive research
│   │   │   ├── strategy_swarm.py    # Business + GTM + financial
│   │   │   └── delivery_swarm.py    # PRD + tech + legal
│   │   │
│   │   └── discovery_v4/        # V4 hybrid discovery
│   │       ├── engine.py
│   │       └── stages/          # 5 discovery stages
│   │           ├── problem_love.py
│   │           ├── customer_truth.py
│   │           ├── opportunity_mapping.py
│   │           ├── solution_design.py
│   │           ├── validation_plan.py
│   │           └── mini_critique.py  # Stage-specific critique
│   │
│   ├── services/                # Cross-run learning + enterprise context
│   │   ├── embeddings.py        # Vector embeddings
│   │   ├── memory_pipeline.py   # Memory augmentation
│   │   └── enterprise_context_service.py  # Context parsing, validation, merging
│   │
│   ├── api/
│   │   ├── discovery_v4_routes.py  # V4 API (30+ endpoints)
│   │   └── enterprise_context_routes.py  # Context CRUD + session attachment
│   ├── models/
│   │   ├── schemas.py           # 60+ Pydantic models
│   │   ├── discovery_v4_schemas.py
│   │   └── enterprise_context_schemas.py  # Context models
│   ├── utils/
│   │   ├── db.py                # Supabase session store
│   │   ├── sse.py               # Server-Sent Events
│   │   ├── export_pdf.py
│   │   └── export_docx.py
│   ├── evals/                   # 22 evaluation types
│   │   ├── cli.py
│   │   ├── unit/
│   │   ├── llm_judge/
│   │   ├── consistency/
│   │   └── agents/              # Agent-specific evals
│   ├── tests/
│   │   ├── unit/                # Unit tests
│   │   └── integration/         # Integration tests
│   └── migrations/
│       ├── 002_add_run_memories.sql
│       └── 003_add_discovery_v4_tables.sql
│
├── docs/                        # Design documentation
└── .github/workflows/           # CI/CD
    ├── test.yml
    └── evals.yml
```

## Multi-Agent Architecture

### Workflow Phases (LangGraph)

```
START
  │
PLANNING PHASE
  └── Planner Agent → Domain classification, competitors, regulatory scope
  │
DISCOVERY SWARM (parallel)
  ├── Customer Research → Market size, pain points, positioning
  ├── Competitive Intelligence → Competitor profiles, moats
  └── Persona Development → User personas with JTBD
  │
STRATEGY SWARM (parallel)
  ├── Business Strategy → Lean Canvas, revenue model
  ├── GTM Strategy → Launch phases, pricing
  └── Financial Modeling → Projections, unit economics
  │
DELIVERY SWARM (parallel)
  ├── PRD Generator → Epic/story generation
  ├── PRD Critic → Quality scoring
  ├── PRD Formatter → JSON structuring
  ├── Technical Architect → System design, diagrams
  ├── Legal & Regulatory → Compliance analysis
  └── Risk Assessment → Risk matrix
  │
QUALITY PHASE
  └── Critique Agent → Cross-validation, calibrated scoring
  │
SYNTHESIS PHASE
  └── Executive Summary → Decision brief
  │
END
```

### Agent List (20+ Specialized Agents)

#### Core Agents
| Agent | File | Purpose |
|-------|------|---------|
| Planner | `planner.py` | Domain classification, competitor ID, regulatory scope |
| Customer Research | `customer_research.py` | Market size, pain points, positioning |
| Business Strategy | `business_strategy.py` | Lean Canvas, revenue model, value proposition |
| GTM Strategy | `gtm_agent.py` | Go-to-market, launch phases, pricing |
| Financial Model | `financial_model_agent.py` | Revenue projections, unit economics |
| Technical Architect | `technical_architect.py` | System design, Mermaid diagrams |
| Legal/Regulatory | `legal_regulatory.py` | Compliance analysis, regulatory risks |
| Wireframe Designer | `wireframe_agent.py` | UI/UX mockups, screen flows |
| Prototype Generator | `prototype_agent.py` | Interactive HTML/CSS prototype |

#### PRD Agents (Sub-workflow)
| Agent | File | Purpose |
|-------|------|---------|
| PRD Generator | `prd_generator.py` | Epic and story generation |
| PRD Critic | `prd_critic.py` | Quality scoring, gap identification |
| PRD Formatter | `prd_formatter.py` | JSON structuring, schema compliance |
| Product Requirements | `product_requirements.py` | Requirements orchestration |

#### Synthesis Agents
| Agent | File | Purpose |
|-------|------|---------|
| Executive Summary | `executive_summary_agent.py` | Decision brief, go/no-go recommendation |
| Stakeholder Views | `stakeholder_agent.py` | Role-specific briefings (CEO, CTO, etc.) |
| Validation Playbook | `validation_agent.py` | Experiment design, hypothesis testing |
| Claim Extractor | `claim_extractor.py` | Evidence extraction with E1-E5 tiers |
| Critique | `critique.py` | Cross-validation, calibrated scoring |
| Facilitator | `facilitator.py` | Master orchestration, constraint routing |

#### Support Modules
| Module | File | Purpose |
|--------|------|---------|
| Constraint Broadcaster | `constraint_broadcaster.py` | Pre-execution constraints between phases + enterprise constraints |
| Output Validator | `output_validator.py` | 700+ validation rules, placeholder detection |
| Confidence Calibrator | `confidence_calibrator.py` | Evidence-weighted confidence scoring |
| Context Builder | `context_builder.py` | Evidence-aware context + agent-specific enterprise context filtering |
| Two-Stage Reasoning | `two_stage_reasoning.py` | Research then structure pattern |
| Enterprise Context Service | `services/enterprise_context_service.py` | Context parsing, validation, merging, constraint extraction |

---

## Agentic Design Patterns (Andrew Ng Framework)

This system implements all four of Andrew Ng's agentic design patterns with production-grade sophistication.

### 1. Reflection Pattern (Grade: B+)

True Generate→Critique→Refine loops, not just post-hoc review.

#### Implementation Locations

| Component | File:Lines | Description |
|-----------|-----------|-------------|
| Core Reflection | `base_agent.py:733-936` | `call_llm_with_reflection()` - configurable iterations |
| V4 Stage Loops | `discovery_v4/stages/*.py` | All 5 stages with quality-gated iteration |
| Mini-Critique | `mini_critique.py:255-333` | Stage-specific dimensions + evidence boosting |
| Two-Stage Reasoning | `two_stage_reasoning.py:60-255` | Research (grounded) → Structure (JSON) |
| PRD Loop | `prd_subgraph.py:117-163` | Generator→Critic→Formatter with conditional loop |
| Pack Critique | `critique.py:31-275` | Full pack quality gate with revision decision |

#### Core Reflection Implementation (`base_agent.py:733-936`)

```python
async def call_llm_with_reflection(
    prompt: str,
    agent_name: str,
    max_reflection_rounds: int = 1,
) -> dict[str, Any]:
    """
    Generate → Self-Critique → Refine loop.

    Reflection checks 5 categories:
    1. Logical errors or contradictions
    2. Missing important information
    3. Unsupported claims (assertions without evidence)
    4. Vague or generic statements
    5. Constraint alignment violations
    """
```

**Return metadata includes:**
- `reflection_rounds`: Number of iterations completed
- `issues_found`: All issues discovered during reflection
- `was_revised`: Whether output was modified

#### V4 Stage Reflection Configuration

All 5 V4 Discovery stages implement identical reflection pattern:

| Setting | Value |
|---------|-------|
| Max Iterations | 2 |
| Quality Threshold | 7.0 (out of 10) |
| Early Exit | Yes (if score >= 7.0) |
| Evidence Boost | E1-E2 scores get +10% |

**Stage Critique Dimensions:**

| Stage | Dimensions Evaluated |
|-------|---------------------|
| Problem Love | Specificity, Real People, Frequency, Tarpit Awareness |
| Customer Truth | Interview Quality, Pattern Recognition, Evidence Grounding, Gap ID |
| Opportunity Mapping | Four Forces Balance, Tree Quality, Evidence Linkage, Primary Selection |
| Solution Design | DHM Scoring, Pre-Mortem Quality, Solution-Fit, Differentiation |
| Validation Plan | Experiment Design, Rung Progression, Success Criteria, Feasibility |

---

### 2. Tool Use Pattern (Grade: C+)

#### Implementation

| Tool | File | Description |
|------|------|-------------|
| Google Search Grounding | `base_agent.py:208-354` | `call_llm_with_grounding()` via Gemini native tool |
| Agent Model Routing | `config.py:345-447` | 30+ agent→model mappings (Flash vs Pro) |
| Memory Augmentation | `base_agent.py:599-695` | pgvector similarity search for past runs |
| Two-Stage Grounded | `two_stage_reasoning.py` | Separates grounded research from JSON structuring |

#### Agent Model Configuration

```python
# config.py:352-433 - AGENT_MODEL_CONFIG
{
    # Flash (2.0) - Speed/cost optimized
    "customer_research": "gemini-2.0-flash",
    "prd_generator": "gemini-2.0-flash",
    "wireframe_designer": "gemini-2.0-flash",

    # Pro (2.5) - Reasoning depth
    "business_strategy": "gemini-2.5-pro",
    "prd_critic": "gemini-2.5-pro",
    "legal_regulatory": "gemini-2.5-pro",
    "critique": "gemini-2.5-pro",
    "prototype_generator": "gemini-2.5-pro",
}
```

#### Token Budgets per Agent

| Agent | Max Tokens | Reason |
|-------|-----------|--------|
| Prototype Generator | 16,384 | React code generation |
| Wireframe Designer | 12,288 | UI code |
| Standard agents | 8,192 | Default |

**Limitation:** No external function calling beyond Google Search grounding.

---

### 3. Planning Pattern (Grade: B)

#### Dynamic Planning Components

| Component | When | Adaptive? | File |
|-----------|------|-----------|------|
| Planner Agent | Start | No (static plan) | `planner.py:29-145` |
| Constraint Broadcasting | Pre-phase | Yes (based on prior work) | `constraint_broadcaster.py:114-163` |
| Targeted Revision | Post-critique | Yes (routes to failing agent) | `orchestrator.py:962-1022` |
| Contradiction Detection | Post-phase | Yes (triggers re-runs) | `facilitator.py:1006-1161` |
| Evidence-Aware Context | Per-agent | Yes (tiered by E1-E5) | `context_builder.py:42-265` |

#### Constraint Types (`constraint_broadcaster.py`)

| Type | Enforcement | Example |
|------|-------------|---------|
| `must_use` | Exact value required | Market size must be $3.2B |
| `must_align` | Directionally consistent | Pricing must be premium |
| `must_reference` | Must cite the value | Must mention competitor X |
| `must_not_exceed` | Numeric upper bound | CAC must not exceed $50 |

#### Constraint Flow

```
Discovery Phase Outputs
        ↓
Constraint Broadcaster extracts E1-E3 claims
        ↓
Constraints injected into Strategy phase prompts
        ↓
Strategy outputs validated against constraints
        ↓
Violations trigger targeted revision
```

#### Contradiction Detection (`facilitator.py:1006-1161`)

Checks for cross-agent consistency:
- **Market size**: Customer Research TAM vs Business Case TAM
- **Pricing**: Business Case revenue streams vs Financial Model pricing
- **Target customer**: CR segments vs GTM initial_segment

HIGH severity contradictions trigger automatic re-run of second agent.

---

### 4. Multi-Agent Collaboration (Grade: B+)

#### Swarm Parallel Execution

| Swarm | Agents | Pattern |
|-------|--------|---------|
| Discovery | 3 agents | Full parallel via `asyncio.gather()` |
| Strategy | 3 agents | Full parallel |
| Delivery | 4 agents | Parallel (Risk runs after others) |
| Synthesis | 3 agents | Stakeholder+Validation parallel, then ExecSummary |

#### State Coordination (`state.py`)

70+ fields with custom reducers for parallel-safe merging:

```python
# Immutable (latest wins)
session_id: Annotated[str, keep_last]

# One-time (first non-None wins)
customer_research: Annotated[Optional[dict], keep_first_non_none]

# Accumulating (append)
revision_history: Annotated[list[dict], add]

# Complex (custom merge)
cross_reference_index: Annotated[Optional[dict], merge_cross_references]
```

#### Cross-Reference Index Merging (`state.py:56-117`)

```python
def merge_cross_references(current, new):
    """
    Intelligent claim merging:
    1. Deduplicate by claim_id
    2. Recalculate tier_distribution (E1-E5 counts)
    3. Recalculate evidence_score (weighted average)
    4. Track unresolved dependencies
    """
```

**Evidence Score Weights:**
- E1: 1.0 (primary research)
- E2: 0.85 (verified source)
- E3: 0.6 (industry data)
- E4: 0.3 (hypothesis)
- E5: 0.1 (assumption)

---

## Enterprise Context Integration

Enterprise Context allows organizations to inject company policies, technology standards, and compliance requirements as soft constraints that guide AI agents.

### Context Hierarchy

```
Company Context (organization-wide)
    └── Division Context (business unit)
        └── Team Context (team-specific)
```

Contexts are merged with team overriding division, and division overriding company.

### Agent-Specific Filtering

Each agent receives only the context sections relevant to their domain:

| Agent | Sections |
|-------|----------|
| Technical Architect | `technology`, `regulatory`, `risk_management` |
| Business Strategy | `strategy`, `organization`, `risk_management` |
| Legal/Regulatory | `regulatory`, `risk_management`, `organization` |
| GTM Strategy | `strategy`, `organization` |
| Customer Research | `strategy`, `organization` |
| PRD Generator | `technology`, `strategy`, `regulatory` |
| Facilitator/Critique | ALL sections |

### Key Files

| File | Purpose |
|------|---------|
| `services/enterprise_context_service.py` | Context parsing, validation, merging |
| `agents/context_builder.py:702-985` | Agent-specific filtering, prompt generation |
| `agents/constraint_broadcaster.py` | Enterprise constraint extraction |
| `api/enterprise_context_routes.py` | REST API endpoints |
| `models/enterprise_context_schemas.py` | Pydantic models |

### Context Sections

| Section | Fields | Used By |
|---------|--------|---------|
| `regulatory` | frameworks, data_residency, jurisdictions | Tech, Legal, PRD |
| `strategy` | priorities, constraints, innovation_stance | Business, GTM, Customer |
| `technology` | cloud, languages, databases, deprecated | Tech, PRD |
| `risk_management` | risk_appetite, categories | Tech, Business, Legal |
| `organization` | delivery_model, budget_cycle, approvals | Business, GTM, Legal |

---

## Swarm Architecture

### Base Swarm Architecture (`swarms/base.py`)

**Key Methods:**

| Method | Lines | Purpose |
|--------|-------|---------|
| `run()` | 96-163 | Orchestrates parallel execution with constraint injection |
| `_prepare_agent_state()` | 44-79 | Injects constraints and revision context into state copies |
| `_merge_results()` | 165-230 | Intelligent merging with field mapping |
| `_merge_cross_references()` | 260-316 | Claim deduplication with evidence scoring |

### Swarm Execution Pattern

```python
async def run(self, state: dict) -> dict:
    # 1. Prepare isolated state copies with constraints
    agent_states = [
        self._prepare_agent_state(state, agent)
        for agent in self.agents
    ]

    # 2. Execute in parallel with fault tolerance
    results = await asyncio.gather(
        *[agent.run(s) for agent, s in zip(self.agents, agent_states)],
        return_exceptions=True
    )

    # 3. Merge results with custom reducers
    return self._merge_results(results)
```

### Discovery Swarm
- Customer Research Agent
- Competitive Intelligence
- Persona Development
- Executes in parallel, results merged via state reducers

### Strategy Swarm
- Business Strategy Agent (reads: customer_research)
- GTM Strategy Agent (reads: customer_research)
- Financial Model Agent (reads: business_case)
- Parallel execution, ~30-40% latency reduction

### Delivery Swarm
- PRD Generator/Critic/Formatter (sub-graph)
- Technical Architect
- Legal/Regulatory
- Risk Assessment (reads: CR, BC, TA - runs after others)
- Parallel with dependency ordering

---

## State Management

### LangGraph TypedDict with Reducers

**File:** `agents/state.py` (468 lines)

The shared state uses `Annotated` types with custom reducers for parallel-safe merging across 70+ fields in 13 categories:

#### State Field Categories

| Category | Fields | Reducer |
|----------|--------|---------|
| Input | session_id, product_idea, constraints | `keep_last` |
| Processing | current_phase, iteration | `keep_last` |
| Agent Outputs | customer_research, business_case, etc. | `keep_first_non_none` |
| Quality | quality_assessment, critique_feedback | `keep_first_non_none` |
| Tracking | errors, revision_history | `merge_errors`, `add` |
| Cross-Reference | cross_reference_index | `merge_cross_references` |

#### Reducer Functions (`state.py:31-117`)

```python
def keep_last(current, new):
    """Use latest non-None value (immutable fields)"""
    return new if new is not None else current

def keep_first_non_none(current, new):
    """First non-None wins (one-time assignments)"""
    return current if current is not None else new

def merge_errors(current, new):
    """Accumulate errors with deduplication"""
    return list(set(current or []) | set(new or []))

def merge_cross_references(current, new):
    """
    Complex merge: deduplicate claims, recalculate scores
    - Deduplicates by claim_id
    - Recalculates tier_distribution
    - Recalculates weighted evidence_score
    - Tracks unresolved dependencies
    """
```

### Cross-Reference Index Structure

```python
{
    "claims": [
        {
            "claim_id": "MI-3",
            "statement": "Market size is $3.2B",
            "evidence_tier": "E2",
            "confidence": 0.85,
            "source": "https://...",
            "depends_on": ["MI-1"],
            "validation_method": "Industry report",
        }
    ],
    "tier_distribution": {"E1": 5, "E2": 12, "E3": 8, "E4": 15, "E5": 3},
    "evidence_score": 0.67,
    "unresolved_dependencies": ["MI-99"],
}
```

---

## Quality System

### 8-Component Framework (Detailed)

#### 1. Evidence-Aware Context (`context_builder.py:42-265`)

Preserves E1-E5 tier markers when passing context between agents:

```
## VERIFIED FACTS (E1-E2)
- [E2] Market size is $3.2B (MI-3) [source: url]

## INDUSTRY DATA (E3)
- [E3] Industry growing 5% annually (MI-12)

## HYPOTHESES (E4-E5)
- [E4] Price sensitivity is high (MI-15) - NEEDS VALIDATION
```

#### 2. Constraint Broadcasting (`constraint_broadcaster.py`)

Pre-execution constraints prevent post-hoc corrections:

```python
def generate_phase_constraints(state, target_phase):
    """
    Extract E1-E3 claims from upstream outputs as constraints.
    Strategy phase receives Discovery constraints.
    Delivery phase receives Discovery + Strategy constraints.
    """
```

#### 3. Two-Stage Reasoning (`two_stage_reasoning.py:60-255`)

Separates research from structuring due to Gemini API limitation:

- **Stage 1 (Research):** Grounded Google Search, free-form text with citations
- **Stage 2 (Structure):** Non-grounded JSON-enforced call

**Why:** Grounding incompatible with `response_mime_type="application/json"`

#### 4. Self-Reflection (`base_agent.py:733-936`)

`call_llm_with_reflection()` with configurable iterations:

- **Reflection Prompt Checks:**
  1. Logical errors or contradictions
  2. Missing important information
  3. Unsupported claims
  4. Vague or generic statements
  5. Constraint violations

#### 5. Confidence Calibration (`confidence_calibrator.py`)

Formula: `calibrated = raw_confidence * tier_weight + source_bonus`

| Tier | Weight | With Source |
|------|--------|-------------|
| E1 | 1.0 | 1.0 (capped) |
| E2 | 0.85 | 0.95 |
| E3 | 0.6 | 0.7 |
| E4 | 0.3 | 0.4 |
| E5 | 0.1 | 0.2 |

#### 6. Output Validation (`output_validator.py` - 700+ Rules)

Rules by agent:

| Agent | Key Rules | Example Checks |
|-------|-----------|----------------|
| Customer Research | 8 rules | 3+ pain_signals, JTBD trigger/goal/success |
| Business Strategy | 10 rules | Lean Canvas fields, revenue streams, Y1&Y3 projections |
| Financial Model | 9 rules | 12-month projections, profit math, LTV:CAC ratio |
| PRD | 9 rules | 3+ epics, 5+ stories, 80%+ proper format |
| Technical Architect | 9 rules | 70%+ real technologies, security/scalability text |
| Legal | 8 rules | 50%+ real regulations (GDPR, HIPAA), mitigations |

#### 7. Structured Revisions (`orchestrator.py:962-1022`)

Targeted revision routing based on section scores:

```python
def route_revision(state):
    """
    Analyzes section_scores from quality_assessment.
    Routes to FIRST section below threshold.
    Falls back to customer_research if unclear.
    """
```

#### 8. Claim Extraction (`claim_extractor.py`)

Minimum claims enforced per section:

| Section | Minimum Claims |
|---------|---------------|
| Market Intelligence | 5 |
| Competitive Landscape | 4 |
| Customer Personas | 3 |
| Business Case | 5 |
| Product Requirements | 5 |
| Technical Architecture | 4 |
| Risk Assessment | 3 |

### Evidence Tiers

| Tier | Description | Confidence | Example |
|------|-------------|------------|---------|
| E1 | Direct customer quote | ~1.0 | User interview verbatim |
| E2 | Industry report/study | ~0.85 | Gartner, McKinsey report |
| E3 | Expert opinion | ~0.6 | Analyst estimate |
| E4 | Market inference | ~0.3 | Reasoned hypothesis |
| E5 | AI hypothesis | ~0.1 | Unvalidated assumption |

---

## V4 Discovery System

### Three Modes

| Mode | Description | Time | Evidence |
|------|-------------|------|----------|
| Quick | AI generates everything | 3-5 min | E3-E4 |
| Guided | AI + checkpoints | 5-8 min | E2-E4 |
| Deep | User interviews + AI synthesis | Days | E1-E2 |

### 5 Stages

1. **Problem Love** - Problem validation (Uri Levine framework)
2. **Customer Truth** - Interview synthesis (Teresa Torres)
3. **Opportunity Mapping** - Four Forces model
4. **Solution Design** - DHM scoring (Delight, Hard-to-copy, Margin)
5. **Validation Plan** - Experiment ladder

### Reflection Loops (All 5 Stages)

Each V4 stage implements Generate→Critique→Refine:

**Configuration:**
- Max Iterations: 2
- Quality Threshold: 7.0 (out of 10)
- Evidence Tier Boost: E1-E2 scores get +10%

**Flow:**
```python
async def _generate_with_reflection(self, context):
    iteration = 0
    while iteration < MAX_REFLECTION_ITERATIONS:
        output = await self._generate_full(context) if not critique_feedback \
                 else await self._generate_with_feedback(context, critique_feedback)

        critique = await critique_stage_output(stage_name, output, evidence_tier="E4")

        if critique["overall_score"] >= MIN_QUALITY_THRESHOLD:
            break  # Early exit on quality pass

        critique_feedback = {...}
        iteration += 1
```

### Interview Count → Evidence Tier

| Interviews | Evidence Tier |
|------------|---------------|
| 5+ | E1 (primary research) |
| 3-4 | E2 (verified source) |
| 1-2 | E3 (expert opinion) |
| 0 | E4 (hypothesis) |

### V4 API Flow

```bash
# 1. Create session
POST /api/discovery/v4/test/sessions
{"product_idea": "...", "mode": "guided"}

# 2. Run stages (each with reflection loop)
POST /api/discovery/v4/test/sessions/{id}/stages/problem_love/run
POST /api/discovery/v4/test/sessions/{id}/stages/customer_truth/run
POST /api/discovery/v4/test/sessions/{id}/stages/opportunity_mapping/run
POST /api/discovery/v4/test/sessions/{id}/stages/solution_design/run
POST /api/discovery/v4/test/sessions/{id}/stages/validation_plan/run

# 3. Continue to full lifecycle
POST /api/discovery/v4/test/sessions/{id}/continue-to-strategy

# 4. Get final state
GET /api/discovery/v4/test/sessions/{id}
```

---

## API Endpoints

### Discovery (V3 - Full Pipeline)

```
POST   /api/discovery/start                     # Start session
GET    /api/discovery/session/{id}              # Get status/pack
GET    /api/discovery/session/{id}/stream       # SSE stream
GET    /api/discovery/sessions                  # List sessions
DELETE /api/discovery/session/{id}              # Delete session
```

### Discovery V4 (Staged/Hybrid) - 30+ Endpoints

#### Test Mode (No Auth Required)
```
POST   /api/discovery/v4/test/sessions                              # Create test session
GET    /api/discovery/v4/test/sessions/{id}                         # Get session state
POST   /api/discovery/v4/test/sessions/{id}/stages/{stage}/run      # Run stage
POST   /api/discovery/v4/test/sessions/{id}/stages/{stage}/approve  # Approve stage
POST   /api/discovery/v4/test/sessions/{id}/stages/{stage}/skip     # Skip stage
PUT    /api/discovery/v4/test/sessions/{id}/stages/{stage}/output   # Update stage output
GET    /api/discovery/v4/test/sessions/{id}/stream                  # SSE stream
POST   /api/discovery/v4/test/sessions/{id}/interviews              # Add interview
POST   /api/discovery/v4/test/sessions/{id}/interviews/synthesize   # Synthesize interviews
POST   /api/discovery/v4/test/sessions/{id}/continue-to-strategy    # Continue to execution
GET    /api/discovery/v4/test/sessions/{id}/lifecycle-check         # Check lifecycle status
POST   /api/discovery/v4/test/sessions/{id}/run-lifecycle-sync      # Run full lifecycle
```

#### Authenticated Mode
```
POST   /api/discovery/v4/sessions                              # Create session
GET    /api/discovery/v4/sessions/{id}                         # Get session
GET    /api/discovery/v4/sessions/{id}/status                  # Get status
GET    /api/discovery/v4/sessions                              # List sessions
POST   /api/discovery/v4/sessions/{id}/stages/{stage}/run      # Run stage
POST   /api/discovery/v4/sessions/{id}/stages/{stage}/ai-assist # AI assistance
PUT    /api/discovery/v4/sessions/{id}/stages/{stage}/output   # Update output
POST   /api/discovery/v4/sessions/{id}/stages/{stage}/approve  # Approve stage
POST   /api/discovery/v4/sessions/{id}/stages/{stage}/skip     # Skip stage
POST   /api/discovery/v4/sessions/{id}/interviews              # Add interview
GET    /api/discovery/v4/sessions/{id}/interviews              # List interviews
PUT    /api/discovery/v4/sessions/{id}/interviews/{iid}        # Update interview
DELETE /api/discovery/v4/sessions/{id}/interviews/{iid}        # Delete interview
POST   /api/discovery/v4/sessions/{id}/interviews/synthesize   # Synthesize
GET    /api/discovery/v4/sessions/{id}/interview-guide         # Get guide
POST   /api/discovery/v4/sessions/{id}/tarpit-check            # Check tarpit
POST   /api/discovery/v4/sessions/{id}/four-forces             # Four forces analysis
POST   /api/discovery/v4/sessions/{id}/opportunity-tree        # Opportunity tree
```

### Export

```
GET    /api/discovery/session/{id}/export/pdf   # Export PDF
GET    /api/discovery/session/{id}/export/docx  # Export DOCX
GET    /api/discovery/session/{id}/pack         # Get JSON pack
```

---

## Database Schema

### Core Tables

```sql
-- Main session tracking
discovery_sessions (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    product_idea TEXT,
    status TEXT,  -- pending|in_progress|completed|failed
    progress_percentage INT,
    additional_context TEXT,  -- V4 state JSON
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)

-- Completed packs
inception_packs (
    id UUID PRIMARY KEY,
    session_id TEXT REFERENCES discovery_sessions(id),
    pack_data JSONB,
    created_at TIMESTAMPTZ
)

-- Cross-run learning (pgvector)
run_memories (
    id UUID PRIMARY KEY,
    domain TEXT,
    agent_name TEXT,
    memory_type TEXT,
    content TEXT,
    embedding vector(768),
    quality_score FLOAT,
    created_at TIMESTAMPTZ
)
```

### V4 Discovery Tables

```sql
-- Stage outputs
draft_states (
    id UUID PRIMARY KEY,
    session_id TEXT REFERENCES discovery_sessions(id),
    stage_name TEXT,
    stage_output JSONB,
    stage_status TEXT,
    user_edits JSONB,
    ai_coaching JSONB,
    score INT,
    UNIQUE(session_id, stage_name)
)

-- Customer interviews
interviews (
    id UUID PRIMARY KEY,
    session_id TEXT REFERENCES discovery_sessions(id),
    interviewee_name TEXT,
    interviewee_role TEXT,
    story_raw TEXT,
    key_quote TEXT,
    struggling_moment TEXT,
    emotions TEXT[],
    ai_extracted_insights JSONB
)

-- Pattern synthesis
pattern_synthesis (
    id UUID PRIMARY KEY,
    session_id TEXT REFERENCES discovery_sessions(id),
    pain_patterns JSONB,
    trigger_patterns JSONB,
    outcome_patterns JSONB,
    UNIQUE(session_id)
)
```

---

## Services Layer

### Memory Augmentation

**Files:**
- `services/embeddings.py` - Vector embeddings (Gemini text-embedding-004, 768 dimensions)
- `services/memory_pipeline.py` - Cross-run learning from past sessions

**Flow:**
1. After successful completion (quality >= 0.8), extract agent outputs
2. Compress to summary via `compress_to_summary()`
3. Generate 768-dimensional embedding
4. Store in pgvector with metadata (domain_type, quality_score)
5. On new runs, retrieve similar past outputs via similarity search

**Configuration:**
- `ENABLE_MEMORY_AUGMENTATION=true`
- Similarity threshold: 0.7
- Non-blocking: graceful degradation on errors

---

## Environment Variables

### Required

```bash
# LLM
GOOGLE_API_KEY=                    # Gemini API key

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_JWT_SECRET=

# App
APP_ENV=production
```

### Optional

```bash
# LLM Config
LLM_MODEL=gemini-2.0-flash
LLM_PRO_MODEL=gemini-2.5-pro
LLM_TEMPERATURE=0.7
LLM_ENABLE_GROUNDING=true

# Quality System
ENABLE_MEMORY_AUGMENTATION=true
ENABLE_TWO_STAGE_REASONING=true
MAX_REVISION_ITERATIONS=3
MIN_QUALITY_SCORE=0.7

# Email (optional)
RESEND_API_KEY=
FOUNDER_EMAIL=

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Evaluation System (22 Evals)

### Categories

```bash
# Run all evals
python -m evals.cli run test_outputs/state.json

# Run specific category
python -m evals.cli run state.json -t unit
python -m evals.cli run state.json -t consistency
python -m evals.cli run state.json -t agent_specific
python -m evals.cli run state.json -t llm_judge
```

### Key Evals

| Eval | Category | Purpose |
|------|----------|---------|
| schema_compliance | unit | Validate Pydantic schemas |
| contradiction_detector | consistency | Cross-section conflicts |
| numerical_consistency | consistency | Financial alignment |
| multi_dimension_quality | llm_judge | 6-dimension scoring |
| customer_research_eval | agent | 3+ pain points check |
| prd_eval | agent | Epic/story requirements |

---

## Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit -v

# Run with coverage
pytest tests/ --cov=utils --cov-report=term
```

---

## Deployment

### Railway

```bash
# Link project
railway link --project sublime-empathy

# View backend logs
railway service link urban-fortnight
railway logs

# View frontend logs
railway service link mindful-luck
railway logs

# Trigger redeploy
git commit --allow-empty -m "chore: trigger redeploy"
git push origin main
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app, all endpoints |
| `backend/agents/orchestrator.py` | LangGraph workflow |
| `backend/agents/state.py` | State definition with reducers |
| `backend/agents/facilitator.py` | 7-phase orchestration |
| `backend/agents/base_agent.py` | LLM calls, reflection, grounding |
| `backend/agents/prompts.py` | All agent prompts |
| `backend/agents/constraint_broadcaster.py` | Pre-execution constraints |
| `backend/agents/output_validator.py` | 700+ validation rules |
| `backend/agents/two_stage_reasoning.py` | Grounded research pattern |
| `backend/agents/discovery_v4/stages/mini_critique.py` | V4 stage reflection |
| `backend/models/schemas.py` | Pydantic models |
| `backend/utils/db.py` | Supabase session store |
| `backend/utils/sse.py` | Real-time streaming |
| `backend/config.py` | Settings & env vars |
| `frontend/src/App.tsx` | Main React app |
| `frontend/src/api/client.ts` | API client |

---

## Common Commands

```bash
# Backend
cd backend
pytest tests/unit -v                    # Run tests
python -m evals.cli run state.json     # Run evals
uvicorn main:app --reload              # Dev server

# Frontend
cd frontend
npm run dev                            # Dev server
npm run build                          # Production build
npm run preview                        # Preview build

# Git
git status
git add -A && git commit -m "message"
git push origin main

# Railway
railway logs                           # View logs
railway variables                      # View env vars
```

---

## Troubleshooting

### Session Stuck
- Check backend logs: `railway logs`
- Session state persists in DB via `additional_context` column
- V4 sessions survive redeploys

### Evals Failing
- Workflow only runs when `backend/agents/**`, `backend/models/**`, or `backend/evals/**` change
- Manual trigger: `gh workflow run evals.yml`

### Frontend Not Loading
- Check CORS in `config.py`
- Verify `VITE_API_URL` points to backend

---

## Architecture Decisions

1. **LangGraph over LangChain** - Better state management for multi-agent workflows
2. **Swarm Pattern** - Parallel execution with custom state reducers for ~30-40% latency reduction
3. **SSE over WebSockets** - Simpler, works through proxies
4. **Supabase** - Auth + DB + pgvector in one
5. **Evidence Tiers** - Explicit E1-E5 confidence tracking throughout
6. **Output Checklists** - Mandatory requirements in prompts (700+ rules)
7. **Constraint Broadcasting** - Pre-execution alignment prevents post-hoc corrections
8. **Two-Stage Reasoning** - Separates grounded research from JSON structuring
9. **Reflection Loops** - Quality-gated iteration in V4 stages and PRD workflow
10. **Cross-Reference Index** - Claim tracking with dependency resolution
