# Seedcraft - Multi-Agent Product Discovery System

<p align="center">
  <img src="docs/logo.svg" alt="Seedcraft Logo" width="120" height="120">
</p>

<p align="center">
  <strong>Transform product ideas into decision-ready inception packs using 7 specialized AI agents with intelligent multi-model routing</strong>
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

Seedcraft is an AI-powered product discovery system that compresses weeks of discovery work into a single, structured inception pack. It uses a multi-agent architecture built on **LangGraph** and powered by **Google Gemini**, orchestrating 7 specialized agents with intelligent model routing (Flash for speed, Pro for reasoning).

The system follows a **hypothesis-first** approach: all outputs are framed as testable hypotheses requiring customer validation, not as market truths.

### What You Get

A complete inception pack containing 8 sections:

| # | Section | Agent | Model | Description |
|---|---------|-------|-------|-------------|
| 00 | **Research Plan** | Planning Agent | Flash | Domain classification, competitor list, regulatory focus |
| 01 | **Executive Summary** | Synthesizer | Flash | Decision brief with key decisions requiring executive action |
| 02 | **Market Hypotheses** | Market Hypothesis Generator | Flash | Evidence-tiered research with competitive positioning data |
| 03 | **Business Strategy** | Business Strategist | Pro | Lean Canvas, financials with chart-ready projections |
| 04 | **Product Requirements** | PRD Generator + Critic + Formatter | Mixed | Epics, user stories, acceptance criteria (quality-assured) |
| 05 | **Technical Architecture** | Technical Architect | Flash | System design with Mermaid diagrams |
| 06 | **Legal & Regulatory** | Legal & Regulatory Analyst | Pro | Specific regulations by name, penalties, compliance timeline |
| 07 | **Quality Assessment** | Critique Agent | Pro | Calibrated scoring with mandatory deductions |

---

## Features

### Intelligent Multi-Agent Orchestration
- **7 Specialized AI Agents** coordinated via LangGraph StateGraph
- **Planning Agent** runs first to classify domain and create targeted research plan
- **Multi-Model Routing**: Gemini Flash for speed, Gemini Pro for deep reasoning
- **Targeted Revision**: On quality failure, only failing agents re-run (not full pipeline)
- **PRD Quality Loop** with automatic revision cycles (Generator -> Critic -> Formatter)
- **Calibrated Critique** with mandatory deductions preventing score inflation

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
- Evidence tiering system (E1-E4) indicates confidence levels
- Uncomfortable insights and "what customers don't care about" sections challenge assumptions
- Validation reminders embedded throughout outputs

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
- **Testing**: pytest with 103 tests
- **Deployment**: Docker / Railway

---

## Architecture

### System Overview

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
|  |               LangGraph Orchestrator                      | |
|  |                                                           | |
|  |  +-----------+                                            | |
|  |  |  Planner  |  Creates research plan, identifies domain  | |
|  |  |  [Flash]  |  competitors, regulations, benchmarks      | |
|  |  +-----+-----+                                            | |
|  |        |                                                  | |
|  |        v                                                  | |
|  |  +------------+    +------------+    +--------------+     | |
|  |  | Customer   |--->| Business   |--->|     PRD      |     | |
|  |  | Research   |    | Strategy   |    |  Sub-Graph   |     | |
|  |  | [Flash]    |    | [Pro]      |    | (3 agents)   |     | |
|  |  +------------+    +------------+    +--------------+     | |
|  |                                             |             | |
|  |  +------------+    +------------+    +------v-------+     | |
|  |  | Executive  |<---| Critique   |<--+| Technical   |     | |
|  |  |  Summary   |    |   [Pro]    |   || Architect   |     | |
|  |  | [Flash]    |    +-----+------+   || [Flash]     |     | |
|  |  +------------+          |          |+--------------+     | |
|  |                          |          |                     | |
|  |                    Score < 0.7?     |  +--------------+   | |
|  |                    Targeted   <-----+--| Legal &      |   | |
|  |                    Revision           | Regulatory   |   | |
|  |                    (failing agent     | [Pro]        |   | |
|  |                     onwards only)     +--------------+   | |
|  +----------------------------------------------------------+ |
+---------------------------------------------------------------+
                              |
                    +---------+---------+
                    |  Google Gemini    |
                    |  Flash + Pro +    |
                    |  Search Grounding |
                    +------------------+
```

### Agent Pipeline

1. **Planning Agent** [Flash] -- Analyzes product idea, classifies domain (B2B SaaS, Consumer, Healthcare, etc.), identifies specific competitors, regulatory domains, and financial benchmarks.

2. **Customer Research Agent** [Flash + Grounding] -- Analyzes target market, pain signals, competitors. Mandatory searches for market size, competitor pricing, pain point surveys. Outputs include competitive positioning chart data.

3. **Business Strategy Agent** [Pro + Grounding] -- Builds Lean Canvas, revenue model, financial projections. Mandatory searches for pricing benchmarks, revenue multiples, CAC/LTV. Outputs include chart-ready monthly projections.

4. **PRD Sub-Graph** -- Three-agent loop:
   - PRD Generator [Flash] creates epics, stories, and requirements
   - PRD Critic [Pro] scores and provides feedback
   - If score < 0.75, revises (up to 3 iterations)
   - PRD Formatter [Flash] produces the final structured document

5. **Technical Architect** [Flash] -- Designs system architecture, tech stack, deployment. Generates Mermaid diagrams for architecture and sequence flows.

6. **Legal & Regulatory Analyst** [Pro + Grounding] -- Reviews compliance with mandatory searches for specific regulations, penalty ranges, certification timelines.

7. **Critique Agent** [Pro] -- Cross-validates with calibrated scoring. Mandatory deductions prevent score inflation (e.g., -0.05 for unsourced market claims).

8. **Executive Summary Generator** [Flash] -- Synthesizes all outputs into decision brief with 3-5 key decisions requiring executive action.

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
|   |   |-- orchestrator.py           # LangGraph workflow + targeted revision
|   |   |-- planner.py                # Planning Agent (domain, competitors, regs)
|   |   |-- base_agent.py             # call_llm with multi-model routing
|   |   |-- state.py                  # DiscoveryState with research_plan
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
|   |   +-- __init__.py
|   |
|   |-- models/
|   |   |-- schemas.py                # Pydantic models (60+ types)
|   |   |-- visual_schemas.py         # Chart/visualization data models
|   |   +-- __init__.py
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
|       |   +-- test_export_formatting.py     # Export formatting tests
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
|       |   +-- InceptionPackViewer.tsx  # Tabbed results viewer
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
| `VITE_API_URL` | Backend URL for frontend (set in frontend env) | `http://localhost:8000` | No |

### Multi-Model Routing

Different agents use different models based on their needs:

| Model | Agents | Rationale |
|-------|--------|-----------|
| **Gemini Flash** | Planner, Customer Research, PRD Generator, PRD Formatter, Technical Architect, Executive Summary | Speed + cost efficiency for volume output |
| **Gemini Pro** | Business Strategy, PRD Critic, Legal & Regulatory, Critique | Deeper reasoning for financial analysis, quality evaluation, regulatory precision |

Model assignments are configured in `AGENT_MODEL_CONFIG` in `config.py`.

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

## Evidence Tiers (Customer Research)

The market hypothesis generator uses a tiered evidence system to indicate confidence:

| Tier | Label | Confidence | Example |
|------|-------|------------|---------|
| **E1** | Direct observation | Highest | "User said: I spend 2 hours daily on this task" |
| **E2** | Behavioral data | High | Usage analytics, click patterns, churn data |
| **E3** | Market/industry data | Medium | Market reports, competitor filings, industry benchmarks |
| **E4** | Hypothesis/inference | Lowest | Logical deduction from observed patterns |

All outputs include a `validation_reminder` field reinforcing that findings are hypotheses requiring customer interviews for validation.

---

## Critique Calibration

The Critique Agent uses calibrated scoring with mandatory deductions to prevent score inflation:

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
- [x] **Phase 2**: Planning Agent, enhanced SSE events
- [x] **Phase 3**: Visual data schemas for charts and dashboards
- [ ] **Phase 4**: Cross-run learning with embeddings (memory pipeline)
- [ ] **Phase 5**: Swarm architecture with parallel agent execution

---

<p align="center">
  Made with Multi-Agent AI by <a href="https://github.com/manuzafar">@manuzafar</a>
</p>
