# Seedform - AI-Powered Multi-Agent Product Discovery System

## Project Overview

Seedform transforms product ideas into comprehensive inception packs using a multi-agent AI system. It generates market research, business strategy, PRD, technical architecture, and more in under 15 minutes.

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
│   │
│   ├── services/                # Cross-run learning
│   │   ├── embeddings.py        # Vector embeddings
│   │   └── memory_pipeline.py   # Memory augmentation
│   │
│   ├── api/
│   │   └── discovery_v4_routes.py  # V4 API (30+ endpoints)
│   ├── models/
│   │   ├── schemas.py           # 60+ Pydantic models
│   │   └── discovery_v4_schemas.py
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
| Constraint Broadcaster | `constraint_broadcaster.py` | Pre-execution constraints between phases |
| Output Validator | `output_validator.py` | 700+ validation rules, placeholder detection |
| Confidence Calibrator | `confidence_calibrator.py` | Evidence-weighted confidence scoring |
| Context Builder | `context_builder.py` | Evidence-aware context for agents |
| Two-Stage Reasoning | `two_stage_reasoning.py` | Research then structure pattern |

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

## Swarm Architecture

Parallel agent execution groups for improved performance:

### Discovery Swarm
- Customer Research Agent
- Competitive Intelligence
- Persona Development
- Executes in parallel, results merged via state reducers

### Strategy Swarm
- Business Strategy Agent
- GTM Strategy Agent
- Financial Model Agent
- Parallel execution, ~30-40% latency reduction

### Delivery Swarm
- PRD Generator/Critic/Formatter
- Technical Architect
- Legal/Regulatory
- Risk Assessment
- Parallel with dependency ordering

## Services Layer

### Memory Augmentation
- `services/embeddings.py` - Vector embeddings for similarity search
- `services/memory_pipeline.py` - Cross-run learning from past sessions
- Uses pgvector for efficient similarity queries
- Retrieves relevant past insights before agent execution

## Quality System

### 8-Component Framework

1. **Evidence-Aware Context** - E1-E5 tier markers preserved
2. **Constraint Broadcasting** - Pre-execution constraints
3. **Two-Stage Reasoning** - Research then structure
4. **Self-Reflection** - Agent self-critique
5. **Confidence Calibration** - Evidence-weighted scores
6. **Output Validation** - 700+ rules in `output_validator.py`
7. **Structured Revisions** - Re-run failing sections
8. **Claim Extraction** - Minimum claims per section

### Evidence Tiers

| Tier | Description | Confidence |
|------|-------------|------------|
| E1 | Direct customer quote | ~1.0 |
| E2 | Industry report/study | ~0.85 |
| E3 | Expert opinion | ~0.7 |
| E4 | Market inference | ~0.5 |
| E5 | AI hypothesis | ~0.1 |

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

## V4 Discovery System

### Three Modes

| Mode | Description | Time | Evidence |
|------|-------------|------|----------|
| Quick | AI generates everything | 3-5 min | E3-E4 |
| Guided | AI + checkpoints | 5-8 min | E2-E4 |
| Deep | User interviews + AI synthesis | Days | E1-E2 |

### 5 Stages

1. **Problem Love** - Problem validation (Uri Levine)
2. **Customer Truth** - Interview synthesis (Teresa Torres)
3. **Opportunity Mapping** - Four Forces model
4. **Solution Design** - DHM scoring
5. **Validation Plan** - Experiment ladder

### V4 API Flow

```bash
# 1. Create session
POST /api/discovery/v4/test/sessions
{"product_idea": "...", "mode": "guided"}

# 2. Run stages
POST /api/discovery/v4/test/sessions/{id}/stages/problem_love/run
POST /api/discovery/v4/test/sessions/{id}/stages/customer_truth/run
# ... etc

# 3. Get state
GET /api/discovery/v4/test/sessions/{id}
```

## Key Files Reference

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app, all endpoints |
| `backend/agents/orchestrator.py` | LangGraph workflow |
| `backend/agents/prompts.py` | All agent prompts |
| `backend/agents/state.py` | State definition |
| `backend/models/schemas.py` | Pydantic models |
| `backend/utils/db.py` | Supabase session store |
| `backend/utils/sse.py` | Real-time streaming |
| `backend/config.py` | Settings & env vars |
| `frontend/src/App.tsx` | Main React app |
| `frontend/src/api/client.ts` | API client |

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

## Architecture Decisions

1. **LangGraph over LangChain** - Better state management for multi-agent workflows
2. **Swarm Pattern** - Parallel execution for speed
3. **SSE over WebSockets** - Simpler, works through proxies
4. **Supabase** - Auth + DB + realtime in one
5. **Evidence Tiers** - Explicit confidence tracking
6. **Output Checklists** - Mandatory requirements in prompts
