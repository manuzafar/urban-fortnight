# Seedcraft Architecture Documentation

> A comprehensive guide to the multi-agent AI system that transforms product ideas into complete inception packs.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Agent Architecture](#3-agent-architecture)
4. [Workflow Orchestration](#4-workflow-orchestration)
5. [State Management](#5-state-management)
6. [Data Models](#6-data-models)
7. [API Reference](#7-api-reference)
8. [Real-time Streaming (SSE)](#8-real-time-streaming-sse)
9. [Database Schema](#9-database-schema)
10. [Authentication](#10-authentication)
11. [Configuration](#11-configuration)
12. [Complete Data Flow](#12-complete-data-flow)

---

## 1. System Overview

Seedcraft is a **multi-agent AI system** that transforms product ideas into comprehensive "inception packs" containing:

- Executive Summary
- Customer Research & Market Analysis
- Business Case & Financial Projections
- Product Requirements Document (PRD)
- Technical Architecture
- Legal & Regulatory Review
- Quality Assessment

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Dashboard  │  │  Execution  │  │ PackViewer  │  │    Auth     │        │
│  │             │  │    View     │  │             │  │  (Supabase) │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          │    REST API    │      SSE       │    REST API    │   OAuth
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         API Layer (main.py)                          │   │
│  │  POST /api/discovery/start    GET /api/discovery/session/{id}       │   │
│  │  GET  /api/discovery/session/{id}/stream (SSE)                      │   │
│  └──────────────────────────────────┬──────────────────────────────────┘   │
│                                     │                                       │
│  ┌──────────────────────────────────▼──────────────────────────────────┐   │
│  │                    LangGraph Orchestrator                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │Customer │→ │Business │→ │  PRD    │→ │Technical│→ │  Legal  │   │   │
│  │  │Research │  │Strategy │  │Subgraph │  │Architect│  │ Review  │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  │                                                            │        │   │
│  │                              ┌─────────┐ ←──────────────────┘        │   │
│  │                              │Critique │ (Quality Gate)             │   │
│  │                              └────┬────┘                            │   │
│  │                                   │                                  │   │
│  │                    ┌──────────────┴──────────────┐                  │   │
│  │                    ▼                              ▼                  │   │
│  │              [Score < 0.7]                  [Score >= 0.7]          │   │
│  │              Loop Back                      Executive Summary       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│  ┌──────────────────────────────────▼──────────────────────────────────┐   │
│  │                         Google Gemini API                            │   │
│  │                    (with optional Search Grounding)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUPABASE (PostgreSQL + Auth)                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │  discovery_sessions │  │   inception_packs   │  │    auth.users       │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | Async REST API with automatic OpenAPI docs |
| AI Orchestration | LangGraph | Stateful multi-agent workflow management |
| LLM | Google Gemini 2.0 Flash | Primary AI model with search grounding |
| Database | Supabase PostgreSQL | Persistent session and pack storage |
| Auth | Supabase Auth + JWT | User authentication and authorization |
| Validation | Pydantic v2 | Type-safe schema validation |
| Streaming | SSE (sse-starlette) | Real-time event streaming |
| Logging | Structlog | Structured JSON logging |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18 | UI components |
| Build Tool | Vite | Fast development and builds |
| Language | TypeScript | Type-safe development |
| Auth | Supabase JS Client | OAuth and session management |
| Styling | CSS Modules | Component-scoped styles |
| Charts | Mermaid.js | Architecture diagram rendering |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend Hosting | Railway | Auto-scaling container deployment |
| Frontend Hosting | Railway | Static site hosting |
| Database | Supabase | Managed PostgreSQL |
| PDF Generation | WeasyPrint | HTML to PDF conversion |

---

## 3. Agent Architecture

The system uses **6 primary agents** plus a **3-agent PRD sub-workflow**, each specialized for a specific domain.

### Agent Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AGENT PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐     Uses Google Search Grounding                  │
│  │  1. CUSTOMER        │     ────────────────────────────                  │
│  │     RESEARCH        │     Outputs: Personas, Pain Points, TAM/SAM/SOM   │
│  │                     │     Evidence Tiers: E1-E4                         │
│  └──────────┬──────────┘                                                   │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐     Uses Google Search Grounding                  │
│  │  2. BUSINESS        │     ────────────────────────────                  │
│  │     STRATEGY        │     Outputs: Lean Canvas, Revenue Model,          │
│  │                     │              Financial Projections, GTM           │
│  └──────────┬──────────┘                                                   │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  3. PRD SUB-WORKFLOW                                                 │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│  │  │    PRD      │ →  │    PRD      │ →  │    PRD      │              │   │
│  │  │  Generator  │    │   Critic    │    │  Formatter  │              │   │
│  │  └─────────────┘    └──────┬──────┘    └─────────────┘              │   │
│  │                            │                                         │   │
│  │                     [Score < 0.75]                                   │   │
│  │                     Loop back to Generator (max 3x)                  │   │
│  │                                                                      │   │
│  │  Outputs: Epics, User Stories, Functional/Non-Functional Reqs,      │   │
│  │           Data Model, Release Plan                                   │   │
│  └──────────┬──────────────────────────────────────────────────────────┘   │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐     No Grounding (deterministic design)           │
│  │  4. TECHNICAL       │     ────────────────────────────────              │
│  │     ARCHITECT       │     Outputs: Architecture, Tech Stack,            │
│  │                     │              Mermaid Diagrams, Security           │
│  └──────────┬──────────┘                                                   │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐     Uses Google Search Grounding                  │
│  │  5. LEGAL &         │     ────────────────────────────                  │
│  │     REGULATORY      │     Outputs: Regulations, Licensing,              │
│  │                     │              Compliance, Legal Risks              │
│  └──────────┬──────────┘                                                   │
│             │                                                               │
│             ▼                                                               │
│  ┌─────────────────────┐     Quality Gate                                  │
│  │  6. CRITIQUE        │     ────────────────────────────                  │
│  │                     │     Outputs: Quality Score, Section Scores,       │
│  │                     │              Revision Feedback                    │
│  └──────────┬──────────┘                                                   │
│             │                                                               │
│      ┌──────┴──────┐                                                       │
│      │             │                                                        │
│      ▼             ▼                                                        │
│  [< 0.7]       [>= 0.7]                                                    │
│  REVISE        FINALIZE                                                    │
│                    │                                                        │
│                    ▼                                                        │
│  ┌─────────────────────┐                                                   │
│  │  EXECUTIVE          │     Synthesizes all outputs into                  │
│  │  SUMMARY            │     board-ready summary                           │
│  └─────────────────────┘                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agent Details

#### Agent 1: Customer Research

**File**: `backend/agents/customer_research.py`

**Purpose**: Generate market hypotheses through evidence-based analysis. Designed to surface uncomfortable truths, not advocate for the product.

**Inputs**:
- Product idea, industry, target market, constraints
- Revision feedback (if iterating)

**Outputs** (`CustomerResearch` model):
```python
{
    "research_scope": {
        "segments_examined": [...],
        "observation_context": "...",
        "known_gaps": [...]
    },
    "job_to_be_done": {
        "trigger_situation": "...",
        "underlying_goal": "...",
        "success_definition": "..."
    },
    "pain_signals": [
        {
            "signal": "...",
            "evidence_tier": "E1",  # E1=direct, E2=observed, E3=market, E4=hypothesis
            "source": "...",
            "severity": "high"
        }
    ],
    "uncomfortable_insights": [...],
    "competitive_landscape": {...},
    "market_context": {
        "tam": "$X billion",
        "sam": "$Y million",
        "som": "$Z million",
        "growth_rate": "X%",
        "uncertainty_factors": [...]
    }
}
```

**Key Features**:
- Uses Google Search grounding for real-world validation
- Evidence tier system (E1-E4) for research rigor
- Mandatory "uncomfortable insights" requirement
- Explicitly surfaces research gaps

---

#### Agent 2: Business Strategy

**File**: `backend/agents/business_strategy.py`

**Purpose**: Create comprehensive business case from customer research findings.

**Inputs**:
- Product idea + context
- Customer research summary

**Outputs** (`BusinessCase` model):
```python
{
    "lean_canvas": {
        "problem": [...],
        "solution": [...],
        "unique_value_proposition": "...",
        "unfair_advantage": "...",
        "customer_segments": [...],
        "key_metrics": [...],
        "channels": [...],
        "cost_structure": {...},
        "revenue_streams": [...]
    },
    "revenue_streams": [
        {
            "name": "SaaS Subscription",
            "model": "recurring",
            "pricing": "$99/month",
            "rationale": "..."
        }
    ],
    "year_1_projection": {
        "users": 1000,
        "revenue": 500000,
        "costs": 400000,
        "profit_loss": 100000
    },
    "year_3_projection": {...},
    "break_even_analysis": "Month 18",
    "funding_requirement": "$500K seed",
    "roi_analysis": "3.2x over 3 years",
    "go_to_market_strategy": {...},
    "risks_and_mitigations": [...]
}
```

---

#### Agent 3: PRD Sub-Workflow

**Files**:
- `backend/agents/prd_subgraph.py` (orchestrator)
- `backend/agents/prd_generator.py`
- `backend/agents/prd_critic.py`
- `backend/agents/prd_formatter.py`

**Architecture**: Nested LangGraph sub-workflow with internal quality loop.

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRD SUB-WORKFLOW                            │
│                                                                 │
│   ┌─────────────┐         ┌─────────────┐                      │
│   │    PRD      │────────▶│    PRD      │                      │
│   │  Generator  │         │   Critic    │                      │
│   └─────────────┘         └──────┬──────┘                      │
│         ▲                        │                              │
│         │                        │                              │
│         │    [Score < 0.75       │                              │
│         │     AND iter < 3]      │                              │
│         │                        │                              │
│         └────────────────────────┤                              │
│                                  │                              │
│                           [Score >= 0.75                        │
│                            OR iter >= 3]                        │
│                                  │                              │
│                                  ▼                              │
│                         ┌─────────────┐                        │
│                         │    PRD      │                        │
│                         │  Formatter  │                        │
│                         └─────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**PRD Critic Scoring** (6 dimensions):
| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Epic Quality | 20% | Proper structure, business value alignment |
| User Story Quality | 25% | Format compliance, testability, pain point coverage |
| Functional Requirements | 20% | Completeness, specificity, actionability |
| Non-Functional Requirements | 15% | Coverage, measurability |
| Completeness | 10% | Data model, integrations, release plan |
| Consistency | 10% | Alignment across sections |

**Pass Threshold**: 0.75

**Outputs** (`ProductRequirementsDocument` model):
```python
{
    "version": "1.0",
    "overview": {...},
    "objectives": [...],  # 5-7 SMART objectives
    "scope_in": [...],
    "scope_out": [...],
    "user_personas": [...],
    "epics": [
        {
            "id": "EPIC-001",
            "title": "...",
            "description": "...",
            "business_value": "...",
            "stories": [
                {
                    "id": "US-001",
                    "title": "...",
                    "as_a": "user",
                    "i_want": "...",
                    "so_that": "...",
                    "acceptance_criteria": [
                        "Given ... When ... Then ..."
                    ],
                    "priority": "high",
                    "size": "M"
                }
            ]
        }
    ],
    "functional_requirements": [
        {
            "id": "FR-001",
            "title": "...",
            "description": "...",
            "priority": "critical"
        }
    ],
    "non_functional_requirements": [
        {
            "id": "NFR-001",
            "category": "performance",
            "title": "...",
            "metric": "response_time",
            "target": "< 200ms"
        }
    ],
    "data_model": {...},
    "release_plan": [...]
}
```

---

#### Agent 4: Technical Architect

**File**: `backend/agents/technical_architect.py`

**Purpose**: Design complete technical architecture addressing PRD requirements.

**Outputs** (`TechnicalArchitecture` model):
```python
{
    "architecture_style": {
        "pattern": "microservices",
        "justification": "..."
    },
    "architecture_diagram_mermaid": "graph TB\n  ...",
    "sequence_diagram_mermaid": "sequenceDiagram\n  ...",
    "technology_stack": [
        {
            "category": "Backend Framework",
            "technology": "FastAPI",
            "rationale": "...",
            "alternatives_considered": ["Django", "Flask"]
        }
    ],
    "system_components": [
        {
            "name": "API Gateway",
            "description": "...",
            "responsibilities": [...],
            "technologies": [...],
            "interfaces": [...]
        }
    ],
    "data_storage": {
        "primary_store": "PostgreSQL",
        "caching": "Redis",
        "search": "Elasticsearch"
    },
    "security_architecture": {...},
    "scalability_approach": {...},
    "deployment_strategy": {...},
    "technical_risks": [...]
}
```

---

#### Agent 5: Legal & Regulatory Review

**File**: `backend/agents/legal_regulatory.py`

**Purpose**: Stress-test product against legal/regulatory frameworks.

**Outputs** (`LegalRegulatoryReview` model):
```python
{
    "executive_summary": "...",
    "applicable_regulations": [
        {
            "name": "GDPR",
            "description": "...",
            "applicability": "...",
            "compliance_requirements": [...],
            "impact_level": "high",
            "timeline": "3 months",
            "estimated_cost": "$50,000"
        }
    ],
    "licensing_requirements": [...],
    "data_protection_requirements": [...],
    "legal_risks": [
        {
            "category": "privacy",
            "description": "...",
            "severity": "high",
            "likelihood": "medium",
            "mitigation_strategies": [...]
        }
    ],
    "intellectual_property": {...},
    "recommended_legal_structure": "Delaware C-Corp",
    "overall_risk_assessment": {
        "level": "medium",
        "key_concerns": [...],
        "blocking_issues": []
    },
    "next_steps": [...]
}
```

---

#### Agent 6: Critique (Quality Gate)

**File**: `backend/agents/critique.py`

**Purpose**: Evaluate entire inception pack quality and provide targeted feedback.

**Scoring Weights**:
| Section | Weight |
|---------|--------|
| Customer Research | 20% |
| Business Case | 20% |
| Product Requirements | 25% |
| Technical Architecture | 20% |
| Cross-Section Consistency | 15% |

**Quality Thresholds**:
- **< 0.7**: Fail - requires revision
- **0.7 - 0.79**: Pass - acceptable quality
- **0.8 - 0.89**: Strong - minor improvements possible
- **0.9 - 1.0**: Exceptional - ready for development

**Outputs** (`QualityAssessment` model):
```python
{
    "overall_score": 0.82,
    "passed": True,
    "section_scores": [
        {
            "section": "Customer Research",
            "score": 0.85,
            "feedback": "...",
            "suggestions": [...]
        }
    ],
    "strengths": [...],
    "weaknesses": [...],
    "critical_gaps": [],
    "recommendations": [...],
    "ready_for_delivery": True,
    "revision_feedback": {
        "customer_research_feedback": [...],
        "business_strategy_feedback": [...],
        "product_requirements_feedback": [...],
        "technical_architecture_feedback": [...],
        "priority_improvements": [...]
    }
}
```

---

## 4. Workflow Orchestration

**File**: `backend/agents/orchestrator.py`

The system uses **LangGraph** for stateful workflow orchestration with automatic checkpointing.

### Complete Workflow Graph

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(DiscoveryState)

# Add nodes
graph.add_node("customer_research", customer_research_node)
graph.add_node("business_strategy", business_strategy_node)
graph.add_node("product_requirements", product_requirements_node)  # PRD sub-workflow
graph.add_node("technical_architect", technical_architect_node)
graph.add_node("legal_regulatory", legal_regulatory_node)
graph.add_node("critique", critique_node)
graph.add_node("prepare_revision", prepare_revision_node)
graph.add_node("executive_summary", executive_summary_node)
graph.add_node("finalize", finalize_node)

# Sequential edges
graph.add_edge("customer_research", "business_strategy")
graph.add_edge("business_strategy", "product_requirements")
graph.add_edge("product_requirements", "technical_architect")
graph.add_edge("technical_architect", "legal_regulatory")
graph.add_edge("legal_regulatory", "critique")

# Conditional edge (quality gate)
graph.add_conditional_edges(
    "critique",
    should_revise_condition,
    {
        "revise": "prepare_revision",
        "finalize": "executive_summary"
    }
)

# Revision loop
graph.add_edge("prepare_revision", "customer_research")

# Finalization
graph.add_edge("executive_summary", "finalize")
graph.add_edge("finalize", END)

# Entry point
graph.set_entry_point("customer_research")
```

### Revision Loop Logic

```python
def should_revise_condition(state: DiscoveryState) -> str:
    quality_score = state.get("quality_assessment", {}).get("overall_score", 0)
    iteration = state.get("iteration", 1)
    max_iterations = settings.max_revision_iterations  # Default: 3
    min_score = settings.min_quality_score  # Default: 0.7

    if quality_score < min_score and iteration < max_iterations:
        return "revise"
    return "finalize"
```

### Node Execution Pattern

Each agent node follows this pattern:

```python
async def agent_node(state: DiscoveryState) -> DiscoveryState:
    # 1. Emit SSE: agent starting
    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("agent_name", "Processing...")

    # 2. Run the agent
    result = await run_agent(
        state["product_idea"],
        state.get("customer_research"),  # Previous outputs
        state.get("critique_feedback", {}).get("agent_feedback", [])
    )

    # 3. Emit SSE: insights discovered
    if emitter and result:
        await emitter.emit_insight("agent_name", "key", "value")

    # 4. Update state
    state["agent_output"] = result
    state["total_tokens_used"] += result.get("tokens_used", 0)

    # 5. Emit SSE: agent complete
    if emitter:
        await emitter.emit_agent_complete("agent_name", "Summary")

    return state
```

---

## 5. State Management

**File**: `backend/agents/state.py`

### DiscoveryState Structure

```python
class DiscoveryState(TypedDict, total=False):
    # ═══════════════════════════════════════════════════════════
    # INPUT FIELDS (set at workflow start)
    # ═══════════════════════════════════════════════════════════
    session_id: str
    product_idea: str
    industry: Optional[str]
    target_market: Optional[str]
    constraints: Optional[list[str]]
    additional_context: Optional[str]

    # ═══════════════════════════════════════════════════════════
    # PROCESSING FIELDS (updated during workflow)
    # ═══════════════════════════════════════════════════════════
    status: SessionStatus           # PENDING, IN_PROGRESS, COMPLETED, FAILED
    current_agent: str              # Currently executing agent name
    iteration: int                  # Current revision iteration (1-3)
    started_at: str                 # ISO datetime
    updated_at: str                 # ISO datetime

    # ═══════════════════════════════════════════════════════════
    # AGENT OUTPUTS (populated by respective agents)
    # ═══════════════════════════════════════════════════════════
    customer_research: Optional[dict]
    business_case: Optional[dict]
    product_requirements: Optional[dict]
    technical_architecture: Optional[dict]
    legal_regulatory_review: Optional[dict]
    quality_assessment: Optional[dict]
    executive_summary: Optional[dict]

    # ═══════════════════════════════════════════════════════════
    # PRD SUB-WORKFLOW FIELDS
    # ═══════════════════════════════════════════════════════════
    prd_iteration: int              # Internal PRD loop iteration
    prd_draft: Optional[dict]       # Current PRD draft
    prd_critic_feedback: Optional[list[str]]
    prd_critic_score: Optional[float]
    prd_quality_passed: bool

    # ═══════════════════════════════════════════════════════════
    # REVISION FEEDBACK FIELDS
    # ═══════════════════════════════════════════════════════════
    critique_feedback: Optional[CritiqueFeedback]
    quality_passed: bool
    requires_revision: bool

    # ═══════════════════════════════════════════════════════════
    # TRACKING FIELDS
    # ═══════════════════════════════════════════════════════════
    errors: list[str]               # All errors encountered
    total_tokens_used: int          # Cumulative token count
    total_duration_seconds: float   # Total processing time
```

### State Initialization

```python
def create_initial_state(
    session_id: str,
    product_idea: str,
    industry: Optional[str] = None,
    target_market: Optional[str] = None,
    constraints: Optional[list[str]] = None,
    additional_context: Optional[str] = None,
) -> DiscoveryState:
    return {
        "session_id": session_id,
        "product_idea": product_idea,
        "industry": industry,
        "target_market": target_market,
        "constraints": constraints or [],
        "additional_context": additional_context,
        "status": SessionStatus.PENDING,
        "iteration": 1,
        "prd_iteration": 0,
        "prd_quality_passed": False,
        "quality_passed": False,
        "requires_revision": False,
        "errors": [],
        "total_tokens_used": 0,
        "total_duration_seconds": 0.0,
        "started_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
```

### Progress Calculation

```python
AGENT_WEIGHTS = {
    "customer_research": 15,
    "business_strategy": 15,
    "product_requirements": 20,
    "technical_architect": 15,
    "legal_regulatory": 20,
    "quality_assessment": 15,
}

def get_progress_percentage(state: DiscoveryState) -> int:
    completed = 0
    for agent, weight in AGENT_WEIGHTS.items():
        if state.get(agent.replace("_", "_")):  # Check if output exists
            completed += weight
    return min(completed, 100)
```

---

## 6. Data Models

**File**: `backend/models/schemas.py`

### Enums

```python
class SessionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class StorySize(str, Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"

class EvidenceTier(str, Enum):
    E1 = "E1"  # Direct customer evidence
    E2 = "E2"  # Observed behavior
    E3 = "E3"  # Market/industry data
    E4 = "E4"  # Hypothesis/assumption
```

### API Request/Response Models

```python
class DiscoveryRequest(BaseModel):
    product_idea: str = Field(..., min_length=10, max_length=2000)
    industry: Optional[str] = Field(None, max_length=100)
    target_market: Optional[str] = Field(None, max_length=200)
    constraints: Optional[list[str]] = Field(None, max_items=10)
    additional_context: Optional[str] = Field(None, max_length=1000)

class DiscoveryResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str
    created_at: datetime

class SessionStatusResponse(BaseModel):
    session_id: str
    status: SessionStatus
    current_agent: Optional[str]
    iteration: int
    progress_percentage: int
    inception_pack: Optional[dict]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Inception Pack Model

```python
class InceptionPack(BaseModel):
    executive_summary: ExecutiveSummary
    customer_research: CustomerResearch
    business_case: BusinessCase
    product_requirements: ProductRequirementsDocument
    technical_architecture: TechnicalArchitecture
    legal_regulatory_review: LegalRegulatoryReview
    quality_assessment: QualityAssessment
    metadata: PackMetadata

class PackMetadata(BaseModel):
    session_id: str
    created_at: datetime
    completed_at: datetime
    iterations: int
    total_tokens: int
    total_duration_seconds: float
```

---

## 7. API Reference

**File**: `backend/main.py`

### Endpoints

#### Health Check

```
GET /api/health

Response 200:
{
    "status": "healthy",
    "timestamp": "2024-02-06T10:30:00Z",
    "version": "1.0.0",
    "environment": "production",
    "active_sessions": 3
}
```

#### Start Discovery

```
POST /api/discovery/start
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
    "product_idea": "An AI-powered meeting room booking system...",
    "industry": "Enterprise SaaS",
    "target_market": "Companies with 500+ employees",
    "constraints": ["Must support on-premise deployment"],
    "additional_context": "Integration with Outlook required"
}

Response 202 Accepted:
{
    "session_id": "disc_20240206_abc123",
    "status": "pending",
    "message": "Discovery session started. Use the session ID to check status.",
    "created_at": "2024-02-06T10:30:00Z"
}
```

#### Get Session Status

```
GET /api/discovery/session/{session_id}
Authorization: Bearer <jwt_token>

Response 200:
{
    "session_id": "disc_20240206_abc123",
    "status": "in_progress",
    "current_agent": "Technical Architect Agent",
    "iteration": 1,
    "progress_percentage": 65,
    "created_at": "2024-02-06T10:30:00Z",
    "updated_at": "2024-02-06T10:35:00Z"
}

Response 200 (completed):
{
    "session_id": "disc_20240206_abc123",
    "status": "completed",
    "current_agent": "Complete",
    "iteration": 2,
    "progress_percentage": 100,
    "inception_pack": { ... },
    "created_at": "2024-02-06T10:30:00Z",
    "updated_at": "2024-02-06T10:45:00Z"
}
```

#### Get Inception Pack Only

```
GET /api/discovery/session/{session_id}/pack
Authorization: Bearer <jwt_token>

Response 200:
{
    "executive_summary": { ... },
    "customer_research": { ... },
    "business_case": { ... },
    "product_requirements": { ... },
    "technical_architecture": { ... },
    "legal_regulatory_review": { ... },
    "quality_assessment": { ... },
    "metadata": { ... }
}
```

#### Stream Session Events (SSE)

```
GET /api/discovery/session/{session_id}/stream?token={jwt_token}
Accept: text/event-stream

Response: Server-Sent Events stream

event: agent_start
data: {"type":"agent_start","agent":"customer_research","data":{"message":"Analyzing market..."}}

event: insight
data: {"type":"insight","agent":"customer_research","data":{"key":"pain_signals","value":"Found 5 pain points"}}

event: progress
data: {"type":"progress","agent":"customer_research","data":{"percentage":15}}

event: agent_complete
data: {"type":"agent_complete","agent":"customer_research","data":{"summary":"Identified 3 personas"}}

event: done
data: {"type":"done","data":{"session_id":"...","status":"completed"}}
```

#### List User Sessions

```
GET /api/discovery/sessions
Authorization: Bearer <jwt_token>

Response 200:
{
    "count": 5,
    "sessions": [
        {
            "id": "disc_20240206_abc123",
            "status": "completed",
            "product_idea": "AI meeting room booking...",
            "progress_percentage": 100,
            "created_at": "2024-02-06T10:30:00Z",
            "updated_at": "2024-02-06T10:45:00Z"
        }
    ]
}
```

#### Delete Session

```
DELETE /api/discovery/session/{session_id}
Authorization: Bearer <jwt_token>

Response 204 No Content
```

#### Export PDF

```
GET /api/discovery/session/{session_id}/export/pdf
Authorization: Bearer <jwt_token>

Response 200: application/pdf binary
```

#### Export DOCX

```
GET /api/discovery/session/{session_id}/export/docx
Authorization: Bearer <jwt_token>

Response 200: application/vnd.openxmlformats-officedocument.wordprocessingml.document binary
```

---

## 8. Real-time Streaming (SSE)

**File**: `backend/utils/sse.py`

### Event Types

```python
class StreamEventType(str, Enum):
    AGENT_START = "agent_start"       # Agent begins processing
    INSIGHT = "insight"               # Key finding discovered
    AGENT_COMPLETE = "agent_complete" # Agent finished
    PROGRESS = "progress"             # Progress percentage update
    ERROR = "error"                   # Error occurred
    DONE = "done"                     # Session complete
    HEARTBEAT = "heartbeat"           # Keep-alive (every 30s)
```

### Event Structure

```python
class StreamEvent(BaseModel):
    type: StreamEventType
    agent: Optional[str]              # Which agent emitted this
    data: dict[str, Any]              # Event-specific payload
    timestamp: datetime

    def to_sse_format(self) -> str:
        """Format as SSE message."""
        event_data = {
            "type": self.type.value,
            "agent": self.agent,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }
        return f"event: {self.type.value}\ndata: {json.dumps(event_data)}\n\n"
```

### Session Event Emitter

```python
class SessionEventEmitter:
    """Per-session event queue for SSE streaming."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        self._closed = False

    async def emit_agent_start(self, agent: str, message: str) -> None:
        """Emit when agent starts processing."""

    async def emit_insight(self, agent: str, key: str, value: str) -> None:
        """Emit when agent discovers a key insight."""

    async def emit_agent_complete(self, agent: str, summary: str) -> None:
        """Emit when agent finishes."""

    async def emit_progress(self, percentage: int) -> None:
        """Emit progress update."""

    async def emit_error(self, message: str) -> None:
        """Emit error event."""

    async def emit_done(self, status: str) -> None:
        """Emit completion event and close stream."""

    async def events(self) -> AsyncGenerator[StreamEvent, None]:
        """Async generator for consuming events."""
        while not self._closed:
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=30.0)
                yield event
            except asyncio.TimeoutError:
                yield StreamEvent(type=StreamEventType.HEARTBEAT, data={})
```

### Frontend SSE Hook

**File**: `frontend/src/hooks/useSSE.ts`

```typescript
export function useSSE(
    sessionId: string | null,
    authToken: string | null,
    enabled: boolean = true
): UseSSEResult {
    const [isConnected, setIsConnected] = useState(false);
    const [currentAgent, setCurrentAgent] = useState<string | null>(null);
    const [agentStates, setAgentStates] = useState<Record<string, AgentState>>({});
    const [insights, setInsights] = useState<Record<string, Insight[]>>({});
    const [progress, setProgress] = useState(0);
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        const url = `${API_BASE}/api/discovery/session/${sessionId}/stream?token=${authToken}`;
        const eventSource = new EventSource(url);

        eventSource.addEventListener('agent_start', (e) => { ... });
        eventSource.addEventListener('insight', (e) => { ... });
        eventSource.addEventListener('agent_complete', (e) => { ... });
        eventSource.addEventListener('progress', (e) => { ... });
        eventSource.addEventListener('done', (e) => { ... });

        return () => eventSource.close();
    }, [sessionId, authToken, enabled]);

    return { isConnected, currentAgent, agentStates, insights, progress, isComplete };
}
```

---

## 9. Database Schema

**File**: `backend/utils/db.py`

### Tables

#### discovery_sessions

```sql
CREATE TABLE discovery_sessions (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    status TEXT NOT NULL DEFAULT 'pending',
    product_idea TEXT NOT NULL,
    industry TEXT,
    target_market TEXT,
    constraints JSONB,
    additional_context TEXT,
    current_agent TEXT,
    iteration INTEGER DEFAULT 1,
    progress_percentage INTEGER DEFAULT 0,
    error_message TEXT,
    errors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON discovery_sessions(user_id);
CREATE INDEX idx_sessions_status ON discovery_sessions(status);
```

#### inception_packs

```sql
CREATE TABLE inception_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL REFERENCES discovery_sessions(id),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    pack_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_packs_session_id ON inception_packs(session_id);
CREATE INDEX idx_packs_user_id ON inception_packs(user_id);
```

### Row Level Security

```sql
-- Users can only see their own sessions
ALTER TABLE discovery_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own sessions"
    ON discovery_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions"
    ON discovery_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Similar policies for inception_packs
```

---

## 10. Authentication

**File**: `backend/utils/auth.py`

### JWT Verification

The system supports both HS256 (symmetric) and ES256 (asymmetric) JWT algorithms.

```python
def decode_supabase_jwt(token: str) -> dict:
    """Decode and verify Supabase JWT."""
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "HS256")

    if alg == "ES256":
        # Fetch public key from Supabase JWKS
        public_key = get_public_key_from_jwks(token)
        payload = jwt.decode(token, public_key, algorithms=["ES256"], audience="authenticated")
    else:
        # Use JWT secret for HS256
        payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")

    return payload
```

### FastAPI Dependencies

```python
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> str:
    """Extract and verify user_id from JWT."""
    payload = decode_supabase_jwt(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

# Usage in endpoints
@app.post("/api/discovery/start")
async def start_discovery(
    request: DiscoveryRequest,
    user_id: str = Depends(get_current_user_id)
):
    ...
```

---

## 11. Configuration

**File**: `backend/config.py`

### Environment Variables

```bash
# ═══════════════════════════════════════════════════════════
# REQUIRED
# ═══════════════════════════════════════════════════════════
GOOGLE_API_KEY=...           # Gemini API key
SUPABASE_URL=...             # Supabase project URL
SUPABASE_SERVICE_KEY=...     # Supabase service role key
SUPABASE_JWT_SECRET=...      # JWT verification secret

# ═══════════════════════════════════════════════════════════
# LLM CONFIGURATION
# ═══════════════════════════════════════════════════════════
LLM_MODEL=gemini-2.0-flash   # Model to use
LLM_TEMPERATURE=0.7          # Generation temperature (0.0-1.0)
LLM_MAX_TOKENS=8192          # Max tokens per response
LLM_TIMEOUT=120              # Request timeout (seconds)
LLM_ENABLE_GROUNDING=true    # Enable Google Search grounding

# ═══════════════════════════════════════════════════════════
# AGENT ORCHESTRATION
# ═══════════════════════════════════════════════════════════
MAX_REVISION_ITERATIONS=3    # Max full workflow iterations
MIN_QUALITY_SCORE=0.7        # Quality threshold to pass
PRD_QUALITY_THRESHOLD=0.75   # PRD sub-workflow threshold
PRD_MAX_ITERATIONS=3         # Max PRD iterations

# ═══════════════════════════════════════════════════════════
# APPLICATION
# ═══════════════════════════════════════════════════════════
APP_ENV=development          # development|staging|production
DEBUG=true                   # Enable debug mode
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,https://app.seedcraft.ai
MAX_CONCURRENT_SESSIONS=100  # 0 = unlimited
LOG_LEVEL=INFO
```

### Settings Class

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    # Gemini
    google_api_key: str
    llm_model: str = "gemini-2.0-flash"
    llm_temperature: float = 0.7
    llm_enable_grounding: bool = True

    # Supabase
    supabase_url: str
    supabase_service_key: str
    supabase_jwt_secret: str

    # Orchestration
    max_revision_iterations: int = 3
    min_quality_score: float = 0.7
    prd_quality_threshold: float = 0.75

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    cors_origins: str = "http://localhost:5173"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
```

---

## 12. Complete Data Flow

### End-to-End Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. USER SUBMITS PRODUCT IDEA                                                │
│    Frontend: Dashboard.tsx → handleSubmit()                                 │
│    API Call: POST /api/discovery/start                                      │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. API LAYER PROCESSING                                                     │
│    main.py: start_discovery()                                               │
│    ├─ Authenticate user (JWT verification)                                  │
│    ├─ Validate request (Pydantic)                                           │
│    ├─ Sanitize inputs                                                       │
│    ├─ Create session in Supabase                                            │
│    ├─ Launch background task                                                │
│    └─ Return session_id (202 Accepted)                                      │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. FRONTEND CONNECTS TO SSE                                                 │
│    ExecutionView.tsx → useSSE(sessionId, authToken)                         │
│    EventSource: GET /api/discovery/session/{id}/stream?token=...            │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. BACKGROUND TASK EXECUTION                                                │
│    main.py: run_discovery_task()                                            │
│    ├─ Create SSE emitter for session                                        │
│    ├─ Update session status to IN_PROGRESS                                  │
│    └─ Call run_discovery_workflow()                                         │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. LANGGRAPH WORKFLOW EXECUTION                                             │
│    orchestrator.py: run_discovery_workflow()                                │
│                                                                             │
│    ITERATION 1:                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ Customer Research Agent                                         │     │
│    │ ├─ Emit SSE: agent_start                                        │     │
│    │ ├─ Format prompt with product_idea + context                    │     │
│    │ ├─ Call Gemini API (with Google Search grounding)               │     │
│    │ ├─ Parse and validate response                                  │     │
│    │ ├─ Update state.customer_research                               │     │
│    │ ├─ Emit SSE: insight (pain_signals, market_size, etc.)          │     │
│    │ └─ Emit SSE: agent_complete, progress=15%                       │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                          │                                                  │
│                          ▼                                                  │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ Business Strategy Agent                                         │     │
│    │ ├─ Input: product_idea + customer_research                      │     │
│    │ ├─ Call Gemini API (with grounding for benchmarks)              │     │
│    │ ├─ Update state.business_case                                   │     │
│    │ └─ Emit SSE events, progress=30%                                │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                          │                                                  │
│                          ▼                                                  │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ PRD Sub-Workflow (internal loop)                                │     │
│    │ ├─ PRD Generator → PRD Critic → [Loop if score < 0.75]         │     │
│    │ ├─ PRD Formatter (cleanup and validation)                       │     │
│    │ ├─ Update state.product_requirements                            │     │
│    │ └─ Emit SSE events, progress=50%                                │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                          │                                                  │
│                          ▼                                                  │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ Technical Architect Agent                                       │     │
│    │ ├─ Input: PRD + business_case                                   │     │
│    │ ├─ Generate architecture + Mermaid diagrams                     │     │
│    │ ├─ Update state.technical_architecture                          │     │
│    │ └─ Emit SSE events, progress=65%                                │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                          │                                                  │
│                          ▼                                                  │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ Legal & Regulatory Agent                                        │     │
│    │ ├─ Input: All previous outputs                                  │     │
│    │ ├─ Call Gemini API (with grounding for regulations)             │     │
│    │ ├─ Update state.legal_regulatory_review                         │     │
│    │ └─ Emit SSE events, progress=85%                                │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                          │                                                  │
│                          ▼                                                  │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ Critique Agent (Quality Gate)                                   │     │
│    │ ├─ Evaluate all sections                                        │     │
│    │ ├─ Calculate overall_score (weighted)                           │     │
│    │ ├─ Generate revision_feedback (if needed)                       │     │
│    │ └─ Emit SSE events                                              │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                          │                                                  │
│                   ┌──────┴──────┐                                          │
│                   │             │                                           │
│                   ▼             ▼                                           │
│            [Score < 0.7]  [Score >= 0.7]                                   │
│            AND iter < 3                                                     │
│                   │             │                                           │
│                   ▼             ▼                                           │
│    ┌─────────────────┐  ┌─────────────────┐                                │
│    │ Prepare Revision│  │Executive Summary│                                │
│    │ ├─ iteration++  │  │ ├─ Synthesize   │                                │
│    │ ├─ Clear outputs│  │ │   all outputs │                                │
│    │ └─ Keep feedback│  │ └─ Board-ready  │                                │
│    └────────┬────────┘  └────────┬────────┘                                │
│             │                    │                                          │
│             ▼                    ▼                                          │
│    [Loop back to         ┌─────────────────┐                               │
│     Customer Research]   │    Finalize     │                               │
│                          │ ├─ status=DONE  │                               │
│                          │ └─ Emit: done   │                               │
│                          └─────────────────┘                               │
│                                                                             │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. RESULTS STORAGE                                                          │
│    main.py: run_discovery_task() (continued)                                │
│    ├─ Build inception_pack from final state                                 │
│    ├─ Save to Supabase: inception_packs table                               │
│    ├─ Update session: status=completed, progress=100%                       │
│    └─ Emit SSE: done event                                                  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. FRONTEND COMPLETION                                                      │
│    ExecutionView.tsx:                                                       │
│    ├─ Receive SSE: done event                                               │
│    ├─ Fetch inception pack: GET /api/discovery/session/{id}/pack            │
│    └─ Navigate to PackViewer with results                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

Seedcraft is a **production-grade multi-agent AI system** that combines:

- **6 specialized AI agents** with domain expertise
- **LangGraph orchestration** for complex stateful workflows
- **Quality gates** with iterative refinement (up to 3 iterations)
- **Real-time SSE streaming** for live progress updates
- **Type-safe Pydantic models** for all data structures
- **Supabase PostgreSQL** for persistent storage
- **JWT authentication** with row-level security
- **Google Gemini 2.0** with search grounding for real-world validation

The architecture is designed for:
- **Extensibility**: Easy to add new agents or modify existing ones
- **Reliability**: Graceful error handling and state persistence
- **Observability**: Structured logging and real-time event streaming
- **Security**: Authentication, authorization, and input validation
- **Scalability**: Async execution, background tasks, and concurrency limits
