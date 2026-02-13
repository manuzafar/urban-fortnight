# Seedcraft - Multi-Agent Product Discovery System

<p align="center">
  <img src="docs/logo.svg" alt="Seedcraft Logo" width="120" height="120">
</p>

<p align="center">
  <strong>Transform product ideas into decision-ready inception packs using 12+ specialized AI agents with swarm architecture and cross-run learning</strong>
</p>

<p align="center">
  <a href="#features">Features</a> |
  <a href="#architecture">Architecture</a> |
  <a href="#getting-started">Getting Started</a> |
  <a href="#usage">Usage</a> |
  <a href="#api-reference">API Reference</a> |
  <a href="#configuration">Configuration</a>
</p>

---

## Overview

Seedcraft is an AI-powered product discovery system that compresses weeks of discovery work into a single, structured inception pack. It uses a **swarm-based multi-agent architecture** built on **LangGraph** and powered by **Google Gemini**, orchestrating 12+ specialized agents organized into three parallel swarms with a Facilitator agent for coordination.

The system features:
- **Swarm Architecture**: Agents run in parallel within Discovery, Strategy, and Delivery swarms
- **Cross-Run Learning**: High-quality outputs are stored with embeddings for future retrieval
- **Contradiction Detection**: Facilitator agent detects and resolves inconsistencies between agent outputs
- **Hypothesis-First Approach**: All outputs are framed as testable hypotheses requiring customer validation
- **Quality Improvement System**: Evidence-aware context, constraint broadcasting, confidence calibration, and structured revisions

### What You Get

A complete inception pack containing 10+ sections produced by three parallel swarms:

| Swarm | Agents | Output Sections |
|-------|--------|-----------------|
| **Discovery** | Customer Research, Competitive Intelligence, Persona Development | Market Hypotheses, Competitive Analysis, Detailed Personas |
| **Strategy** | Business Strategy, GTM Strategy, Financial Modeling | Lean Canvas, Go-to-Market Plan, Financial Projections |
| **Delivery** | PRD Generator, Technical Architect, Legal & Regulatory, Risk Assessment | PRD, Architecture, Legal Review, Risk Matrix |

**Additional Components:**
| Component | Agent | Description |
|-----------|-------|-------------|
| Research Plan | Planning Agent | Domain classification, competitor list, regulatory focus |
| Executive Summary | Synthesizer | Decision brief with key decisions requiring executive action |
| Quality Assessment | Critique Agent | Calibrated scoring with mandatory deductions |
| Coordination | Facilitator Agent | Contradiction detection, conflict resolution, synthesis |

---

## Features

### Swarm-Based Multi-Agent Architecture
- **12+ Specialized AI Agents** organized into three parallel swarms
- **Facilitator Agent** coordinates swarms, detects contradictions, resolves conflicts
- **Parallel Execution**: Agents within each swarm run concurrently via `asyncio.gather`
- **Planning Agent** runs first to classify domain and create targeted research plan
- **Multi-Model Routing**: Gemini Flash for speed, Gemini Pro for deep reasoning
- **Targeted Revision**: On quality failure, only failing agents re-run (not full pipeline)
- **PRD Quality Loop** with automatic revision cycles (Generator -> Critic -> Formatter)
- **Calibrated Critique** with mandatory deductions preventing score inflation

### Cross-Run Learning
- **Memory Pipeline**: High-quality outputs (score >= 0.8) are stored with embeddings
- **Vector Similarity Search**: Uses pgvector to find similar past examples
- **Memory-Augmented Agents**: Relevant examples injected into prompts for improved output
- **Gemini Embeddings**: Uses `text-embedding-004` for 768-dimensional vectors

### Structured Search Grounding
Three agents use **Google Search grounding** with mandatory search protocols:

| Agent | Required Searches |
|-------|-------------------|
| Market Hypotheses | Market size, top 3-5 competitors by name, pain point surveys, recent funding |
| Business Strategy | Competitor pricing, revenue multiples, CAC/LTV benchmarks, unit economics |
| Legal & Regulatory | Specific regulations with sections, penalty ranges, certification requirements |

All claims require citations with confidence tags: `[CONFIRMED]`, `[ESTIMATED]`, `[HYPOTHESIS]`

### Hypothesis-First Approach
Inspired by product thought leaders (Marty Cagan, Teresa Torres):
- All market research outputs are framed as **hypotheses requiring validation**
- Evidence tiering system (E1-E5) indicates confidence levels
- Uncomfortable insights and "what customers don't care about" sections challenge assumptions
- Validation reminders embedded throughout outputs

### Agent Quality Improvement System (NEW)
A comprehensive system to improve output quality by 25-35% through better evidence tracking and consistency enforcement:

| Component | Description |
|-----------|-------------|
| **Evidence-Aware Context** | Summaries preserve E1-E5 tier markers, ensuring downstream agents respect evidence quality |
| **Constraint Broadcasting** | Pre-execution constraints generated from upstream phases prevent contradictions |
| **Two-Stage Reasoning** | Separates grounded research from JSON structuring for reliable parsing |
| **Self-Reflection Pattern** | Agents self-critique before submitting, catching errors early |
| **Confidence Calibration** | Raw confidence adjusted by evidence tier (E1=1.0, E5=0.1) and source quality |
| **Structured Revisions** | Revision history tracking prevents repeating mistakes across iterations |
| **Mandatory Claim Extraction** | Minimum claims enforced per section (e.g., 5 for Market Intelligence) |

### Rich Visual Output
New structured schemas for frontend visualization:
- **Competitive Positioning**: Quadrant chart data with X/Y scores for each competitor
- **Financial Projections**: Monthly time-series for revenue, costs, MRR, users
- **Lean Canvas Visual**: Structured canvas blocks ready for rendering
- **Key Decisions**: 3-5 executive decisions with options, pros/cons, recommendations
- **Risk Matrix**: Likelihood/impact grid for risk assessment

### Real-Time Streaming
Enhanced SSE events for granular progress tracking:
- `plan_ready` - Research plan created
- `competitor` - Named competitor identified
- `market_data` - Market size or trend found
- `risk` - Risk flagged
- `financial` - Financial metric calculated
- `diagram` - Architecture diagram ready
- `citation` - Source citation for claim

### Modern Tech Stack
- **Backend**: Python 3.11+ / FastAPI / LangGraph / Google Gemini API (Flash + Pro)
- **Frontend**: React 18 / TypeScript / Vite
- **Validation**: Pydantic v2 with 60+ strict schemas
- **Testing**: pytest with 180+ tests (including 73 quality module tests)
- **Deployment**: Docker / Railway

---

## Architecture

### Swarm Architecture Overview

```
+---------------------------------------------------------------+
|                     Frontend (React + TypeScript)               |
|  +-------------+  +--------------+  +---------------------+   |
|  | LandingPage |  |DiscoveryForm |  |InceptionPackViewer  |   |
|  +-------------+  +--------------+  +---------------------+   |
|                    |ProgressTracker|  (Charts, Canvas, etc)    |
|                    +--------------+                            |
+---------------------------------------------------------------+
                              |
                      REST API + SSE
                              |
+---------------------------------------------------------------+
|                     Backend (FastAPI)                           |
|  +----------------------------------------------------------+ |
|  |                   FACILITATOR AGENT                       | |
|  |         (Coordinates swarms, detects contradictions)      | |
|  +---------------------------+------------------------------+ |
|                              |                                 |
|  +---------------------------v------------------------------+ |
|  |                    PLANNING PHASE                         | |
|  |  +-------------+                                          | |
|  |  |   Planner   |  Domain, competitors, regulations        | |
|  |  +-------------+                                          | |
|  +----------------------------------------------------------+ |
|                              |                                 |
|  +---------------------------v------------------------------+ |
|  |                   DISCOVERY SWARM (Parallel)              | |
|  |  +----------------+ +---------------------+ +------------+ |
|  |  |   Customer     | |   Competitive       | |  Persona   | |
|  |  |   Research     | |   Intelligence      | |Development | |
|  |  +----------------+ +---------------------+ +------------+ |
|  +----------------------------------------------------------+ |
|                              |                                 |
|              Claim Extraction + Contradiction Check            |
|                              |                                 |
|  +---------------------------v------------------------------+ |
|  |              CONSTRAINT BROADCASTER (NEW)                 | |
|  |   Generates constraints from Discovery for Strategy       | |
|  +----------------------------------------------------------+ |
|                              |                                 |
|  +---------------------------v------------------------------+ |
|  |                   STRATEGY SWARM (Parallel)               | |
|  |  +----------------+ +---------------------+ +------------+ |
|  |  |   Business     | |      GTM            | | Financial  | |
|  |  |   Strategy     | |    Strategy         | |  Modeling  | |
|  |  +----------------+ +---------------------+ +------------+ |
|  +----------------------------------------------------------+ |
|                              |                                 |
|              Claim Extraction + Contradiction Check            |
|                              |                                 |
|  +---------------------------v------------------------------+ |
|  |              CONSTRAINT BROADCASTER (NEW)                 | |
|  |   Generates constraints from Strategy for Delivery        | |
|  +----------------------------------------------------------+ |
|                              |                                 |
|  +---------------------------v------------------------------+ |
|  |                   DELIVERY SWARM (Parallel)               | |
|  |  +--------+ +----------+ +-------+ +------------------+   | |
|  |  |  PRD   | | Tech     | | Legal | |      Risk        |   | |
|  |  |  Loop  | | Architect| |       | |   Assessment     |   | |
|  |  +--------+ +----------+ +-------+ +------------------+   | |
|  +----------------------------------------------------------+ |
|                              |                                 |
|  +---------------------------v------------------------------+ |
|  |                   QUALITY & SYNTHESIS                     | |
|  |  +-------------+    +-------------------+                 | |
|  |  |  Critique   |--->| Executive Summary |                 | |
|  |  +-------------+    +-------------------+                 | |
|  +----------------------------------------------------------+ |
+---------------------------------------------------------------+
                              |
              +---------------+---------------+
              |                               |
    +---------v---------+          +----------v----------+
    |   Google Gemini   |          |   Memory Pipeline   |
    |  Flash + Pro +    |          | (pgvector + Gemini  |
    |  Search Grounding |          |    Embeddings)      |
    +-------------------+          +---------------------+
```

### Swarm Execution Flow

#### 1. Facilitator Agent
The central coordinator that:
- Dispatches swarms in dependency order
- Detects contradictions between agent outputs
- Resolves conflicts by re-running specific agents with context
- Synthesizes final outputs

#### 2. Planning Phase
**Planning Agent** [Flash] -- Analyzes product idea, classifies domain (B2B SaaS, Consumer, Healthcare, etc.), identifies specific competitors, regulatory domains, and financial benchmarks.

#### 3. Discovery Swarm (Parallel)
Three agents run concurrently:
- **Customer Research** [Flash + Grounding] -- Market analysis, pain signals, competitive positioning chart data
- **Competitive Intelligence** [Flash + Grounding] -- Deep competitor profiles, market share, competitive moats
- **Persona Development** [Flash] -- Detailed user personas with psychographics, jobs-to-be-done

#### 4. Strategy Swarm (Parallel)
Three agents run concurrently:
- **Business Strategy** [Pro + Grounding] -- Lean Canvas, revenue model, strategic recommendations
- **GTM Strategy** [Pro] -- Go-to-market plan, launch strategy, channel analysis
- **Financial Modeling** [Pro] -- Detailed financial projections, unit economics, break-even analysis

#### 5. Delivery Swarm (Parallel)
Four agents run concurrently:
- **PRD Sub-Graph** -- Generator -> Critic -> Formatter loop with quality assurance
- **Technical Architect** [Flash] -- System design with Mermaid diagrams
- **Legal & Regulatory** [Pro + Grounding] -- Compliance review with specific regulations
- **Risk Assessment** [Flash] -- Risk matrix with likelihood/impact scoring

#### 6. Quality & Synthesis
- **Critique Agent** [Pro] -- Cross-validates with calibrated scoring
- **Executive Summary Generator** [Flash] -- Decision brief with key decisions

### Contradiction Detection

The Facilitator detects inconsistencies between agent outputs:
- **Market Size**: Compares TAM estimates across Customer Research and Business Strategy
- **Pricing**: Validates pricing consistency between Business Strategy and Financial Modeling
- **Target Customer**: Ensures GTM segment aligns with Customer Research segments

When contradictions are found, the Facilitator re-runs the affected agent with context about the inconsistency.

### Targeted Revision (New)

When critique score is below threshold (0.7), the system now uses **targeted revision**:
- Analyzes `section_scores` to find the first failing section
- Routes back to only that agent (not full pipeline restart)
- Preserves outputs from earlier passing agents
- Saves tokens and reduces latency

### PRD Sub-Graph (Quality Assurance Loop)

```
+-------------+     +-------------+     +-------------+
|    PRD      |---->|    PRD      |---->|    PRD      |
|  Generator  |     |   Critic    |     |  Formatter  |
+-------------+     +------+------+     +-------------+
                           |
                     Score < 0.75?
                           |
                    +------v------+
                    |   Revise    |-----+
                    |    PRD      |     |
                    +-------------+     |
                           ^            |
                           +------------+
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/manuzafar/urban-fortnight.git
   cd urban-fortnight
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

4. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Running Locally

1. **Start the backend** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

---

## Usage

### Step-by-Step

1. Open the app at http://localhost:5173
2. Click **"Generate Hypotheses"** on the landing page
3. Enter your product idea (minimum 10 characters) in the text area
4. Optionally add industry, target market, constraints, and additional context
5. Click **"Start Discovery"** to begin the multi-agent workflow
6. Watch real-time progress as each agent completes (typically 8-12 minutes)
7. Explore the results through the tabbed interface

### Example Input

```
A mobile app that helps small business owners manage their inventory
using smartphone cameras and AI-powered barcode scanning. The app should
work offline and sync when connectivity is restored.
```

**Optional fields:**
- Industry: `Retail / Inventory Management`
- Target Market: `Small businesses with under 50 employees`
- Constraints: `Must work offline, budget under $200K, 6-month timeline`

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/discovery/start` | Start a new discovery session |
| `GET` | `/api/discovery/session/{id}` | Get session status and results |
| `GET` | `/api/discovery/session/{id}/pack` | Get inception pack only |
| `GET` | `/api/discovery/sessions` | List all active sessions |
| `DELETE` | `/api/discovery/session/{id}` | Delete a session |
| `GET` | `/api/health` | Health check |

### Start Discovery Request

```bash
curl -X POST http://localhost:8000/api/discovery/start \
  -H "Content-Type: application/json" \
  -d '{
    "product_idea": "A mobile inventory management app with barcode scanning",
    "industry": "Retail",
    "target_market": "Small businesses",
    "constraints": ["Must work offline", "Budget under $200K"],
    "additional_context": "Competing with Sortly and Stockpile"
  }'
```

**Response:**
```json
{
  "session_id": "disc_20260205_abc12345",
  "status": "pending",
  "message": "Discovery session started. Use the session ID to check status.",
  "created_at": "2026-02-05T12:00:00.000000"
}
```

### Poll Session Status

```bash
curl http://localhost:8000/api/discovery/session/disc_20260205_abc12345
```

**Response (in progress):**
```json
{
  "session_id": "disc_20260205_abc12345",
  "status": "in_progress",
  "current_agent": "Business Strategist",
  "iteration": 1,
  "progress_percentage": 30,
  "inception_pack": null,
  "created_at": "2026-02-05T12:00:00.000000",
  "updated_at": "2026-02-05T12:02:30.000000"
}
```

**Response (completed):**
```json
{
  "session_id": "disc_20260205_abc12345",
  "status": "completed",
  "current_agent": "Complete",
  "iteration": 1,
  "progress_percentage": 100,
  "inception_pack": {
    "executive_summary": { ... },
    "customer_research": { ... },
    "business_case": { ... },
    "product_requirements_document": { ... },
    "technical_architecture": { ... },
    "legal_regulatory_review": { ... },
    "quality_assessment": { ... },
    "metadata": { ... }
  }
}
```

### Inception Pack Structure

| Section | Key Fields |
|---------|------------|
| `executive_summary` | `product_name`, `tagline`, `problem_statement`, `solution_overview`, `value_proposition`, `target_users`, `target_market_size`, `key_differentiators`, `competitive_landscape`, `funding_required`, `revenue_model`, `financial_projections`, `break_even_timeline`, `expected_roi`, `top_risks`, `regulatory_summary`, `gtm_strategy`, `key_milestones`, `success_metrics`, `recommendation`, **`key_decisions`** (NEW) |
| `customer_research` | `research_scope`, `job_to_be_done`, `current_behaviour`, `pain_signals`, `uncomfortable_insights`, `what_customers_dont_care_about`, `open_questions`, `competitive_landscape`, `market_context`, `research_quality_check`, `validation_reminder`, **`competitive_positioning`** (NEW - chart data) |
| `business_case` | `lean_canvas`, `revenue_streams`, `cost_structure`, `break_even_analysis`, `year_1_projection`, `year_3_projection`, `funding_requirement`, `roi_analysis`, `go_to_market_strategy`, `key_partnerships`, `risks_and_mitigations`, **`financial_projection`** (NEW - chart data), **`lean_canvas_visual`** (NEW) |
| `product_requirements_document` | `product_overview`, `scope`, `epics` (with `stories`, `acceptance_criteria`), `functional_requirements`, `non_functional_requirements`, `data_model`, `release_plan`, `risks`, `statistics` |
| `technical_architecture` | `architecture_style`, `technology_stack`, `system_components`, `integration_points`, `data_storage`, `security_architecture`, `scalability_approach`, `deployment_strategy`, `infrastructure_requirements`, `technical_risks`, `architecture_diagram_mermaid`, `sequence_diagram_mermaid` |
| `legal_regulatory_review` | `applicable_regulations`, `licensing_requirements`, `data_protection_requirements`, `legal_risks`, `intellectual_property`, `industry_specific_considerations`, `international_considerations`, `overall_risk_assessment`, `next_steps` |
| `quality_assessment` | `overall_score`, `passed`, `iteration`, `section_scores`, `strengths`, `weaknesses`, `critical_gaps`, `recommendations`, `ready_for_delivery` |

### Visual Data Schemas (NEW)

For frontend visualization, the following structured data is available:

| Schema | Description | Fields |
|--------|-------------|--------|
| `competitive_positioning` | Quadrant chart data | `competitors[]` (name, x_score, y_score), `x_axis_label`, `y_axis_label` |
| `financial_projection` | Time-series chart data | `monthly_data[]` (month, revenue, costs, profit, users, mrr), `break_even_month` |
| `lean_canvas_visual` | Canvas block data | `problem[]`, `solution[]`, `key_metrics[]`, `unique_value_proposition`, etc. |
| `key_decisions` | Executive decision framework | `decisions[]` (id, title, options, recommendation, confidence, impact_if_delayed) |

---

## Project Structure

```
seedcraft/
|
|-- backend/
|   |-- main.py                       # FastAPI application entry point
|   |-- config.py                     # Settings + AGENT_MODEL_CONFIG routing
|   |-- requirements.txt              # Python dependencies
|   |-- Dockerfile                    # Backend container config
|   |-- .env.example                  # Environment variable template
|   |
|   |-- agents/
|   |   |-- orchestrator.py           # LangGraph workflow + parallel execution
|   |   |-- facilitator.py            # Facilitator Agent (swarm coordination)
|   |   |-- planner.py                # Planning Agent (domain, competitors, regs)
|   |   |-- base_agent.py             # call_llm + call_llm_with_memory + self-reflection
|   |   |-- state.py                  # DiscoveryState with swarm outputs
|   |   |-- prompts.py                # All prompts with search protocols
|   |   |-- customer_research.py      # Customer Research [Flash + grounding]
|   |   |-- business_strategy.py      # Business Strategy [Pro + grounding]
|   |   |-- legal_regulatory.py       # Legal & Regulatory [Pro + grounding]
|   |   |-- technical_architect.py    # Technical Architect [Flash]
|   |   |-- critique.py               # Critique with calibrated scoring [Pro]
|   |   |-- prd_generator.py          # PRD generation [Flash]
|   |   |-- prd_critic.py             # PRD quality critic [Pro]
|   |   |-- prd_formatter.py          # PRD formatting [Flash]
|   |   |-- prd_subgraph.py           # PRD sub-workflow orchestration
|   |   |-- context_builder.py        # Evidence-aware context summaries (NEW)
|   |   |-- constraint_broadcaster.py # Pre-execution constraint generation (NEW)
|   |   |-- two_stage_reasoning.py    # Research/structure separation (NEW)
|   |   |-- versioning.py             # Output version tracking (NEW)
|   |   |-- confidence_calibrator.py  # Evidence-based confidence adjustment (NEW)
|   |   |-- claim_extractor.py        # Mandatory claim extraction with minimums
|   |   |-- __init__.py
|   |   |
|   |   +-- swarms/                   # Swarm implementations
|   |       |-- __init__.py           # Swarm exports
|   |       |-- base.py               # BaseSwarm (parallel execution)
|   |       |-- discovery_swarm.py    # Customer, Competitive, Persona agents
|   |       |-- strategy_swarm.py     # Business, GTM, Financial agents
|   |       +-- delivery_swarm.py     # PRD, Tech, Legal, Risk agents
|   |
|   |-- models/
|   |   |-- schemas.py                # Pydantic models (60+ types)
|   |   |-- visual_schemas.py         # Chart/visualization data models
|   |   +-- __init__.py
|   |
|   |-- services/                     # Cross-run learning services
|   |   |-- __init__.py
|   |   |-- embeddings.py             # Gemini embeddings + similarity search
|   |   +-- memory_pipeline.py        # Memory storage and retrieval
|   |
|   |-- migrations/
|   |   +-- 002_add_run_memories.sql  # pgvector schema for memories
|   |
|   |-- utils/
|   |   |-- helpers.py                # Session store, sanitization
|   |   |-- sse.py                    # Enhanced SSE event types
|   |   +-- __init__.py
|   |
|   +-- tests/
|       |-- unit/
|       |   |-- test_orchestrator_routing.py  # Targeted revision tests
|       |   |-- test_planner.py               # Planning agent tests
|       |   |-- test_visual_schemas.py        # Visual schema validation
|       |   |-- test_export_formatting.py     # Export formatting tests
|       |   |-- test_confidence_calibrator.py # Confidence calibration tests
|       |   |-- test_versioning.py            # Output versioning tests
|       |   |-- test_two_stage_reasoning.py   # Two-stage reasoning tests
|       |   |-- test_constraint_broadcaster.py # Constraint generation tests
|       |   +-- test_critique_retry.py        # Critique retry logic tests (NEW)
|       +-- integration/
|           +-- test_export_pipeline.py       # End-to-end export tests
|
|-- frontend/
|   |-- index.html                    # HTML entry point
|   |-- package.json                  # NPM dependencies
|   |-- vite.config.ts                # Vite build configuration
|   |-- tsconfig.json                 # TypeScript configuration
|   |-- Dockerfile                    # Frontend container config
|   |
|   +-- src/
|       |-- main.tsx                  # React entry point
|       |-- App.tsx                   # Main app component (state machine)
|       |-- App.css                   # Full application styles
|       |
|       |-- components/
|       |   |-- LandingPage.tsx       # Landing page with value proposition
|       |   |-- DiscoveryForm.tsx     # Product idea input form
|       |   |-- ProgressTracker.tsx   # Real-time agent progress display
|       |   |-- PackViewer.tsx        # Tabbed results viewer with charts
|       |   |
|       |   +-- charts/               # Visualization components
|       |       |-- index.ts
|       |       |-- charts.css
|       |       |-- CompetitivePositionChart.tsx  # Scatter plot
|       |       |-- FinancialProjectionChart.tsx  # Area chart
|       |       |-- RiskMatrixChart.tsx           # 5x5 heatmap
|       |       +-- LeanCanvasVisual.tsx          # Canvas grid
|       |
|       |-- api/
|       |   +-- client.ts            # API client with SSE support
|       |
|       +-- types/
|           +-- api.ts               # TypeScript type definitions
|
|-- docs/
|   |-- logo.svg
|   +-- seedcraft-evolution-roadmap.md  # Future roadmap
|
|-- README.md
|-- CONTRIBUTING.md
+-- LICENSE
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | -- | Yes |
| `LLM_MODEL` | Default Gemini model | `gemini-2.0-flash` | No |
| `LLM_PRO_MODEL` | Pro model for reasoning tasks | `gemini-2.5-pro` | No |
| `LLM_TEMPERATURE` | Generation temperature (0.0-1.0) | `0.7` | No |
| `LLM_MAX_TOKENS` | Max tokens per response | `8192` | No |
| `LLM_ENABLE_GROUNDING` | Enable Google Search grounding | `true` | No |
| `APP_ENV` | Environment (development/staging/production) | `development` | No |
| `API_HOST` | Backend host address | `0.0.0.0` | No |
| `API_PORT` | Backend port number | `8000` | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000,http://localhost:5173` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `MAX_REVISION_ITERATIONS` | Max quality revision loops | `3` | No |
| `MIN_QUALITY_SCORE` | Minimum quality score to pass (0.0-1.0) | `0.7` | No |
| `PRD_QUALITY_THRESHOLD` | Minimum PRD quality score | `0.75` | No |
| `PRD_MAX_ITERATIONS` | Max PRD revision iterations | `3` | No |
| `SESSION_EXPIRY_SECONDS` | Session TTL in seconds | `3600` | No |
| `MAX_CONCURRENT_SESSIONS` | Max parallel sessions (0=unlimited) | `100` | No |
| `MAX_CRITIQUE_RETRIES` | Max critique retry attempts before accepting | `2` | No |
| `VITE_API_URL` | Backend URL for frontend (set in frontend env) | `http://localhost:8000` | No |
| `ENABLE_MEMORY_AUGMENTATION` | Enable memory-augmented prompts | `true` | No |
| `ENABLE_TWO_STAGE_REASONING` | Enable two-stage grounded reasoning | `true` | No |
| `ENABLE_SELF_REFLECTION` | Enable agent self-reflection pattern | `true` | No |
| `MAX_REFLECTION_ROUNDS` | Max self-reflection iterations | `1` | No |

### Multi-Model Routing

Different agents use different models based on their needs:

| Model | Agents | Rationale |
|-------|--------|-----------|
| **Gemini Flash** | Planner, Customer Research, PRD Generator, PRD Formatter, Technical Architect, Executive Summary | Speed + cost efficiency for volume output |
| **Gemini Pro** | Business Strategy, PRD Critic, Legal & Regulatory, Critique | Deeper reasoning for financial analysis, quality evaluation, regulatory precision |

Model assignments are configured in `AGENT_MODEL_CONFIG` in `config.py`.

### Cross-Run Learning (Memory Pipeline)

High-quality outputs are stored with embeddings for future retrieval:

| Component | Description |
|-----------|-------------|
| **Memory Storage** | Outputs with quality score >= 0.8 are stored in `run_memories` table |
| **Embedding Model** | Gemini `text-embedding-004` (768 dimensions) |
| **Vector Search** | pgvector with cosine similarity, threshold 0.7 |
| **Memory Injection** | Top 3 similar examples injected into agent prompts |

**Database Setup:**
```sql
-- Run the migration in Supabase
-- backend/migrations/002_add_run_memories.sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Environment Variables:**
| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | -- |
| `SUPABASE_KEY` | Supabase anon key | -- |

### Google Search Grounding

Grounding is enabled for agents that benefit from real-world data validation. Each grounded agent has **mandatory search protocols**:

| Agent | Required Searches |
|-------|-------------------|
| Customer Research | Market size + year, competitor pricing, pain point surveys, recent funding rounds |
| Business Strategy | Competitor pricing tiers, revenue multiples, CAC/LTV benchmarks, unit economics |
| Legal & Regulatory | Regulation names + sections, penalty/enforcement data, certification timelines |

To disable grounding, set `LLM_ENABLE_GROUNDING=false` in your `.env` file.

**Note:** Grounding is not used for PRD Generator, Technical Architect, or Critique agents because it can interfere with structured JSON output generation.

---

## Evidence Tiers & Confidence Calibration

The system uses a tiered evidence system with confidence calibration to indicate reliability:

| Tier | Label | Weight | Example |
|------|-------|--------|---------|
| **E1** | Primary research | 1.0 | "User said: I spend 2 hours daily on this task" |
| **E2** | Verified external source | 0.85 | Usage analytics, documented competitor data with URL |
| **E3** | Industry data | 0.6 | Market reports, industry benchmarks |
| **E4** | Hypothesis/inference | 0.3 | Logical deduction from observed patterns |
| **E5** | Assumption | 0.1 | Unvalidated premise requiring validation |

### Confidence Calibration (NEW)

Raw confidence scores are calibrated based on evidence tier and source quality:

```
calibrated_confidence = raw_confidence × tier_weight + source_bonus
```

- **Tier Weight**: E1=1.0, E2=0.85, E3=0.6, E4=0.3, E5=0.1
- **Source Bonus**: +0.1 if claim has a verifiable source URL
- **Result**: E1/E2 claims with sources reach ~1.0; E5 claims without sources stay <0.2

This ensures downstream agents and the critique system appropriately weight claims based on evidence quality.

All outputs include a `validation_reminder` field reinforcing that findings are hypotheses requiring customer interviews for validation.

---

## Critique Calibration

The Critique Agent uses calibrated scoring with mandatory deductions to prevent score inflation.

### Retry Mechanism

When critique validation fails (due to LLM errors or malformed responses), the system retries before accepting:

| Behavior | Description |
|----------|-------------|
| **Retry on Failure** | Validation errors or LLM failures trigger automatic retry |
| **Max Retries** | Configurable via `MAX_CRITIQUE_RETRIES` (default: 2) |
| **Graceful Degradation** | After max retries, accepts with `QUALITY GATE BYPASSED` warning |
| **Clear Logging** | All retries and bypasses are logged for operator visibility |

This prevents silent quality gate bypass while avoiding infinite loops.

### Score Calibration

| Score | Standard |
|-------|----------|
| **0.90+** | Every claim sourced, financial projections benchmarked, 15+ user stories with Given/When/Then, Mermaid diagrams, specific regulations cited |
| **0.80-0.89** | Most claims sourced, reasonable financials with stated assumptions, adequate PRD coverage |
| **0.70-0.79** | Bare minimum - directional claims, ballpark financials, happy path PRD |
| **Below 0.70** | Fails - generic content, missing sections, unsupported claims |

### Mandatory Deductions

| Issue | Deduction |
|-------|-----------|
| Market size without source | -0.05 per instance |
| Financial projections without benchmarks | -0.10 |
| User stories missing acceptance criteria | -0.05 per story |
| No security considerations in architecture | -0.10 |
| Generic "consult a lawyer" without specific guidance | -0.10 |

---

## Evaluation System

A comprehensive eval framework validates agent outputs across 5 categories with 22 total evaluations.

### Quick Start

```bash
cd backend

# Run agent-specific evals
python -m evals.cli run test_outputs/state.json -t agent_specific

# Run consistency checks (cross-section)
python -m evals.cli run test_outputs/state.json -t consistency

# Run all evals with verbose output
python -m evals.cli run test_outputs/state.json --verbose
```

### Eval Categories

| Category | Evals | Purpose |
|----------|-------|---------|
| **Unit** | `schema_compliance`, `evidence_tier` | Fast, deterministic validation |
| **LLM Judge** | `multi_dimension_quality` | 6-dimension quality assessment |
| **Golden Set** | `golden_set_similarity` | Regression detection vs baselines |
| **Consistency** | `contradiction_detector`, `numerical_consistency` | Cross-section alignment |
| **Agent-Specific** | 16 evals (one per agent) | Tailored quality checks |

### Agent-Specific Requirements

| Agent | Key Checks |
|-------|------------|
| Customer Research | 3+ pain points, JTBD framework, uncomfortable insights |
| Competitive Analysis | Direct competitors, pricing data, market gaps |
| Business Strategy | Lean Canvas complete, 3+ risks with mitigation |
| Financial Model | 12 monthly projections, profit math validation |
| PRD | 3+ epics, 5+ stories, acceptance criteria |
| Technical Architecture | 3+ tech stack, real technologies, security |
| Legal/Regulatory | Real regulations (GDPR, HIPAA, etc.), risks |
| Wireframes | 3+ screens, React code, navigation |
| Prototype | useState, interactive elements, no placeholders |

### Scoring & Thresholds

| Severity | Meaning |
|----------|---------|
| **CRITICAL** | Blocks PR (schema violations, contradictions) |
| **WARNING** | Should review (low quality scores) |
| **INFO** | Informational |

**Pass Thresholds:**
- Schema Compliance: 100%
- Multi-Dimension Quality: >= 70%
- Consistency: >= 70% + no critical contradictions
- Agent-Specific: All checks must pass

### CLI Reference

```bash
python -m evals.cli run STATE_PATH [OPTIONS]

Options:
  -t, --type TYPE          # Filter: unit, llm_judge, golden, consistency, agent_specific
  -a, --agent AGENT        # Filter by agent (repeatable)
  -g, --golden-set ID      # Compare against golden set
  -o, --output FILE        # Save results
  -f, --format FORMAT      # Output: console, json, markdown
  -v, --verbose            # Detailed output
  --sequential             # Run sequentially (default: parallel)

# Golden set management
python -m evals.cli create-golden STATE_PATH ID --name "Name"
python -m evals.cli list-golden
python -m evals.cli compare STATE_PATH GOLDEN_ID
```

See [backend/README.md](backend/README.md) for complete eval documentation.

---

## Deploy to Railway

Deploy the full stack to [Railway](https://railway.app) with two services:

1. **Create a new Railway project**
   - Go to [railway.app](https://railway.app) and create a new project
   - Connect your GitHub repository

2. **Deploy the Backend**
   - Click "New Service" -> "GitHub Repo"
   - Select this repository
   - Set **Root Directory** to `backend`
   - Add environment variables:
     - `GOOGLE_API_KEY` = your Gemini API key
     - `APP_ENV` = `production`
     - `CORS_ORIGINS` = your frontend Railway URL

3. **Deploy the Frontend**
   - Click "New Service" -> "GitHub Repo"
   - Select this repository
   - Set **Root Directory** to `frontend`
   - Add environment variable:
     - `VITE_API_URL` = your backend Railway URL (e.g., `https://your-backend.up.railway.app`)

4. **Update CORS**
   - After both services deploy, update the backend's `CORS_ORIGINS` to include the frontend URL

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting PRs.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- Powered by [Google Gemini](https://deepmind.google/technologies/gemini/) (Flash + Pro) for AI capabilities
- Google Search grounding for real-world data validation
- Inspired by product discovery frameworks from Marty Cagan and Teresa Torres

---

## Roadmap

See [docs/seedcraft-evolution-roadmap.md](docs/seedcraft-evolution-roadmap.md) for planned features:

- [x] **Phase 1**: Targeted revision, multi-model routing, structured grounding
- [x] **Phase 2**: Planning Agent, parallel execution, enhanced SSE events
- [x] **Phase 3**: Visual data schemas and interactive charts (recharts)
- [x] **Phase 4**: Cross-run learning with embeddings (pgvector + Gemini embeddings)
- [x] **Phase 5**: Swarm architecture with Facilitator agent and contradiction detection
- [x] **Phase 6**: Agent Quality Improvement System
  - Evidence-aware context preservation (E1-E5 markers in summaries)
  - Pre-execution constraint broadcasting between phases
  - Two-stage grounded reasoning (research then structure)
  - Self-reflection pattern for agents
  - Confidence calibration based on evidence tiers
  - Structured revision framework with history tracking
  - Mandatory claim extraction with minimum thresholds
  - 73 new unit tests for quality modules
- [x] **Phase 7**: Critique Resilience & Quality Display
  - Critique retry mechanism prevents silent quality gate bypass
  - Configurable `MAX_CRITIQUE_RETRIES` setting (default: 2)
  - Clear `QUALITY GATE BYPASSED` warnings when retries exhausted
  - Fixed quality score display to show consistent percentages
  - 7 new unit tests for critique retry logic
- [x] **Phase 8**: Comprehensive Eval System (NEW)
  - 22 evaluations across 5 categories (unit, llm_judge, golden, consistency, agent_specific)
  - OUTPUT CHECKLIST added to all 16 agent prompts
  - Pre-output validation with `output_validator.py` (700+ validation rules)
  - Eval feedback bridge for revision loop integration
  - Strengthened constraint broadcasting (E4 → E2 evidence tier)
  - CLI interface: `python -m evals.cli run STATE_PATH`
  - Agent-specific eval score: 59.3% → 82.2%

---

<p align="center">
  Made with Multi-Agent AI by <a href="https://github.com/manuzafar">@manuzafar</a>
</p>
