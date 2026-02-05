# Seedform - Multi-Agent Product Discovery System

<p align="center">
  <img src="docs/logo.svg" alt="Seedform Logo" width="120" height="120">
</p>

<p align="center">
  <strong>Transform product ideas into decision-ready inception packs using 6 specialized AI agents</strong>
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

Seedform is an AI-powered product discovery system that compresses weeks of discovery work into a single, structured inception pack. It uses a multi-agent architecture built on **LangGraph** and powered by **Google Gemini**, orchestrating 6 specialized agents that each produce a section of the final deliverable.

The system follows a **hypothesis-first** approach: all outputs are framed as testable hypotheses requiring customer validation, not as market truths.

### What You Get

A complete inception pack containing 7 sections:

| # | Section | Agent | Description |
|---|---------|-------|-------------|
| 01 | **Executive Summary** | Synthesizer | 20-field decision brief with financials, risks, and GTM |
| 02 | **Market Hypotheses** | Market Hypothesis Generator | Evidence-tiered research with uncomfortable insights |
| 03 | **Business Strategy** | Business Strategist | Lean Canvas, revenue model, financial projections |
| 04 | **Product Requirements** | PRD Generator + Critic + Formatter | Epics, user stories, acceptance criteria (quality-assured) |
| 05 | **Technical Architecture** | Technical Architect | System design, tech stack, scalability approach |
| 06 | **Legal & Regulatory** | Legal & Regulatory Analyst | Compliance, licensing, data protection, IP considerations |
| 07 | **Quality Assessment** | Critique Agent | Cross-validation, gap analysis, revision recommendations |

---

## Features

### Multi-Agent Orchestration
- **6 Specialized AI Agents** coordinated via LangGraph StateGraph
- **PRD Quality Loop** with automatic revision cycles (Generator -> Critic -> Formatter)
- **Critique-driven revision** across all agents with configurable quality thresholds
- **Sequential pipeline** ensuring each agent builds on previous outputs

### Google Search Grounding
Three agents (Market Hypotheses, Business Strategy, Legal & Regulatory) use **Google Search grounding** for real-world data validation:
- Market size estimates backed by actual data
- Competitor analysis referencing real companies
- Current regulatory and compliance information
- Automatic fallback to non-grounded calls if grounding fails

### Hypothesis-First Approach
Inspired by product thought leaders (Marty Cagan, Teresa Torres):
- All market research outputs are framed as **hypotheses requiring validation**
- Evidence tiering system (E1-E4) indicates confidence levels
- Uncomfortable insights and "what customers don't care about" sections challenge assumptions
- Validation reminders embedded throughout outputs

### Modern Tech Stack
- **Backend**: Python 3.11+ / FastAPI / LangGraph / Google Gemini API
- **Frontend**: React 18 / TypeScript / Vite
- **Validation**: Pydantic v2 with strict schema enforcement
- **Deployment**: Docker / Railway

### Frontend Experience
- **Landing page** with clear value proposition
- **Discovery form** with real-time validation feedback
- **Live progress tracking** as each agent completes
- **Tabbed results viewer** for navigating all inception pack sections
- **Responsive design** with dark theme

---

## Architecture

### System Overview

```
+---------------------------------------------------------------+
|                     Frontend (React + TypeScript)               |
|  +-------------+  +--------------+  +---------------------+   |
|  | LandingPage |  |DiscoveryForm |  |InceptionPackViewer  |   |
|  +-------------+  +--------------+  +---------------------+   |
|                    |ProgressTracker|                            |
|                    +--------------+                            |
+---------------------------------------------------------------+
                              |
                         REST API
                              |
+---------------------------------------------------------------+
|                     Backend (FastAPI)                           |
|  +----------------------------------------------------------+ |
|  |               LangGraph Orchestrator                      | |
|  |                                                           | |
|  |  +------------+    +------------+    +--------------+     | |
|  |  | Market     |--->| Business   |--->|     PRD      |     | |
|  |  | Hypotheses |    | Strategy   |    |  Sub-Graph   |     | |
|  |  | [grounded] |    | [grounded] |    | (3 agents)   |     | |
|  |  +------------+    +------------+    +--------------+     | |
|  |                                             |             | |
|  |  +------------+    +------------+    +------v-------+     | |
|  |  | Executive  |<---| Critique   |<--+| Technical   |     | |
|  |  |  Summary   |    |   Agent    |   || Architect   |     | |
|  |  +------------+    +-----+------+   |+--------------+     | |
|  |                          |          |                     | |
|  |                    Score < 0.7?     |  +--------------+   | |
|  |                    Revise all  <----+--| Legal &      |   | |
|  |                                       | Regulatory   |   | |
|  |                                       | [grounded]   |   | |
|  |                                       +--------------+   | |
|  +----------------------------------------------------------+ |
+---------------------------------------------------------------+
                              |
                    +---------+---------+
                    |  Google Gemini    |
                    |  API + Search    |
                    |  Grounding       |
                    +------------------+
```

### Agent Pipeline

1. **Market Hypothesis Generator** -- Analyzes target market, pain signals, competitors, and market context. Uses Google Search grounding for real data.
2. **Business Strategist** -- Builds Lean Canvas, revenue model, cost structure, and financial projections. Uses Google Search grounding.
3. **PRD Sub-Graph** -- Three-agent loop:
   - PRD Generator creates epics, stories, and requirements
   - PRD Critic scores and provides feedback
   - If score < 0.75, revises (up to 3 iterations)
   - PRD Formatter produces the final structured document
4. **Technical Architect** -- Designs system architecture, tech stack, and deployment strategy based on PRD.
5. **Legal & Regulatory Analyst** -- Reviews compliance requirements, licensing, data protection, and IP. Uses Google Search grounding.
6. **Critique Agent** -- Cross-validates all outputs, identifies gaps and inconsistencies, assigns quality score.
7. **Executive Summary Generator** -- Synthesizes all outputs into a 20-field decision brief.

If the critique score is below the threshold (default 0.7) and max iterations (default 3) haven't been reached, the entire pipeline reruns with critique feedback.

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
| `executive_summary` | `product_name`, `tagline`, `problem_statement`, `solution_overview`, `value_proposition`, `target_users`, `target_market_size`, `key_differentiators`, `competitive_landscape`, `funding_required`, `revenue_model`, `financial_projections`, `break_even_timeline`, `expected_roi`, `top_risks`, `regulatory_summary`, `gtm_strategy`, `key_milestones`, `success_metrics`, `recommendation` |
| `customer_research` | `research_scope`, `job_to_be_done`, `current_behaviour`, `pain_signals`, `uncomfortable_insights`, `what_customers_dont_care_about`, `open_questions`, `competitive_landscape`, `market_context`, `research_quality_check`, `validation_reminder` |
| `business_case` | `lean_canvas`, `revenue_streams`, `cost_structure`, `break_even_analysis`, `year_1_projection`, `year_3_projection`, `funding_requirement`, `roi_analysis`, `go_to_market_strategy`, `key_partnerships`, `risks_and_mitigations` |
| `product_requirements_document` | `product_overview`, `scope`, `epics` (with `stories`, `acceptance_criteria`), `functional_requirements`, `non_functional_requirements`, `data_model`, `release_plan`, `risks`, `statistics` |
| `technical_architecture` | `architecture_style`, `technology_stack`, `system_components`, `integration_points`, `data_storage`, `security_architecture`, `scalability_approach`, `deployment_strategy`, `infrastructure_requirements`, `technical_risks` |
| `legal_regulatory_review` | `applicable_regulations`, `licensing_requirements`, `data_protection_requirements`, `legal_risks`, `intellectual_property`, `industry_specific_considerations`, `international_considerations`, `overall_risk_assessment`, `next_steps` |
| `quality_assessment` | `overall_score`, `passed`, `iteration`, `section_scores`, `strengths`, `weaknesses`, `critical_gaps`, `recommendations`, `ready_for_delivery` |

---

## Project Structure

```
urban-fortnight/
|
|-- backend/
|   |-- main.py                       # FastAPI application entry point
|   |-- config.py                     # Pydantic Settings configuration
|   |-- requirements.txt              # Python dependencies
|   |-- Dockerfile                    # Backend container config
|   |-- .env.example                  # Environment variable template
|   |
|   |-- agents/
|   |   |-- orchestrator.py           # LangGraph workflow orchestration
|   |   |-- base_agent.py             # call_llm + call_llm_with_grounding
|   |   |-- state.py                  # DiscoveryState TypedDict
|   |   |-- prompts.py                # All agent prompt templates
|   |   |-- customer_research.py      # Market Hypothesis Generator [grounded]
|   |   |-- business_strategy.py      # Business Strategist [grounded]
|   |   |-- legal_regulatory.py       # Legal & Regulatory Analyst [grounded]
|   |   |-- technical_architect.py    # Technical Architect
|   |   |-- critique.py               # Cross-validation critique agent
|   |   |-- prd_generator.py          # PRD generation agent
|   |   |-- prd_critic.py             # PRD quality critic
|   |   |-- prd_formatter.py          # PRD formatting agent
|   |   |-- prd_subgraph.py           # PRD sub-workflow orchestration
|   |   +-- __init__.py
|   |
|   |-- models/
|   |   |-- schemas.py                # Pydantic models (50+ types)
|   |   +-- __init__.py
|   |
|   +-- utils/
|       |-- helpers.py                # Session store, sanitization, utilities
|       +-- __init__.py
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
|       |   +-- client.ts            # API client with polling
|       |
|       +-- types/
|           +-- api.ts               # TypeScript type definitions
|
|-- docs/
|   +-- logo.svg
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
| `LLM_MODEL` | Gemini model identifier | `gemini-2.0-flash` | No |
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

### Google Search Grounding

Grounding is enabled by default for agents that benefit from real-world data. It allows agents to use Google Search during generation to validate:

- Market size estimates (TAM/SAM/SOM)
- Competitor information
- Industry trends and benchmarks
- Regulatory and compliance data

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
- Powered by [Google Gemini](https://deepmind.google/technologies/gemini/) for AI capabilities
- Google Search grounding for real-world data validation

---

<p align="center">
  Made with Multi-Agent AI
</p>
