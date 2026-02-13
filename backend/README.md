# Product LifeCycle Backend

Multi-agent product discovery system that generates comprehensive inception packs for product ideas.

## Architecture Overview

The backend uses a **swarm-based multi-agent architecture** with 16 specialized agents coordinated by a Facilitator agent.

### Agent Pipeline (7 Phases)

```
1. Planning       → Planner Agent
2. Discovery      → Customer Research + Competitive Intelligence + Persona Development (parallel)
3. Strategy       → Business Strategy + GTM Strategy (parallel) → Financial Model (sequential)
4. Delivery       → PRD + Technical Architecture + Legal/Regulatory (parallel) → Risk Assessment
5. Design         → Wireframes → Prototype (sequential)
6. Quality Check  → Critique Agent (with revision loop)
7. Synthesis      → Stakeholder Views + Validation Playbook (parallel) → Executive Summary
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `agents/facilitator.py` | Orchestrates all phases, handles contradictions |
| `agents/constraint_broadcaster.py` | Enforces cross-section consistency |
| `agents/output_validator.py` | Pre-output validation with retry |
| `agents/eval_feedback_bridge.py` | Converts eval failures to revision feedback |

---

## Evaluation System

The eval system is a comprehensive, modular framework for validating agent outputs.

### Quick Start

```bash
# Run all agent-specific evals
python -m evals.cli run test_outputs/state.json -t agent_specific

# Run consistency checks
python -m evals.cli run test_outputs/state.json -t consistency

# Run with verbose output
python -m evals.cli run test_outputs/state.json --verbose

# Get state summary
python -m evals.cli summary test_outputs/state.json
```

### Eval Types (5 Categories, 22 Evals)

#### 1. Unit Evals (Fast, Deterministic)

| Eval | Severity | What it Checks |
|------|----------|----------------|
| `schema_compliance` | CRITICAL | Validates outputs against Pydantic schemas |
| `evidence_tier_distribution` | WARNING | E1-E3 >= 30%, E1-E2 >= 10% |

#### 2. LLM Judge Evals (Qualitative)

| Eval | Pass Threshold | Dimensions |
|------|----------------|------------|
| `multi_dimension_quality` | >= 0.7 | Accuracy (20%), Relevance (20%), Actionability (15%), Evidence (15%), Completeness (15%), Coherence (15%) |

#### 3. Golden Set Evals (Regression Detection)

| Eval | Metrics | Purpose |
|------|---------|---------|
| `golden_set_similarity` | Key overlap, Content similarity, Field coverage | Compare against curated baselines |

#### 4. Consistency Evals (Cross-Section)

| Eval | Severity | Checks |
|------|----------|--------|
| `contradiction_detector` | CRITICAL | Market size, pricing, customer definitions, timelines |
| `numerical_consistency` | WARNING | Funding variance <=20%, Revenue variance <=30% |

#### 5. Agent-Specific Evals (16 Evals)

| Agent | Key Requirements |
|-------|------------------|
| Customer Research | 3+ pain points, JTBD framework, uncomfortable insights |
| Competitive Analysis | Direct/indirect competitors, pricing data, market gaps |
| Persona Development | 3+ personas, behaviors, frustrations |
| Business Strategy | Lean Canvas, revenue streams, 3+ risks |
| GTM Strategy | Channels, launch phases, metrics dashboard |
| Financial Model | 12 monthly projections, profit math, scenarios |
| PRD | 3+ epics, 5+ stories, acceptance criteria |
| Technical Architecture | 3+ tech stack, real technologies, security |
| Legal/Regulatory | Real regulations, risks with mitigation |
| Risk Assessment | 5+ risks, probability/impact ratings |
| Executive Summary | Key decisions, differentiators, recommendation |
| Stakeholder Views | 3+ perspectives, objections, recommendations |
| Validation Playbook | 3+ experiments, success/failure criteria |
| Wireframes | 3+ screens, React code, navigation |
| Prototype | useState, interactive elements, no placeholders |
| Planner | Research questions, competitor targets |

### CLI Commands

```bash
# Run evaluations
python -m evals.cli run STATE_PATH [OPTIONS]

Options:
  -t, --type TYPE          Filter: unit, llm_judge, golden, consistency, agent_specific
  -a, --agent AGENT        Filter by agent name (can repeat)
  -g, --golden-set ID      Compare against golden set
  -o, --output FILE        Save results to file
  -f, --format FORMAT      Output: console, json, markdown
  -v, --verbose            Show detailed output
  --sequential             Run evals sequentially

# Golden set management
python -m evals.cli create-golden STATE_PATH ID --name "Name" --version "1.0"
python -m evals.cli list-golden
python -m evals.cli delete-golden ID --yes
python -m evals.cli compare STATE_PATH GOLDEN_ID
```

### Scoring System

| Level | Meaning |
|-------|---------|
| CRITICAL | Blocks PR (schema violations, contradictions) |
| WARNING | Should review (low quality scores) |
| INFO | Informational |

**Pass Thresholds:**
- Schema Compliance: 100%
- Multi-Dimension Quality: >= 70%
- Consistency: >= 70% + no critical contradictions
- Agent-Specific: All checks must pass

---

## Agent Quality System

### Output Checklists

Every agent prompt includes a mandatory OUTPUT CHECKLIST that enforces:
- Required field counts (e.g., "3+ pain points")
- Field completeness (e.g., "JTBD framework complete")
- Content quality (e.g., "no placeholder text")

### Pre-Output Validation

`agents/output_validator.py` validates outputs before storing:

```python
from agents.output_validator import validate_agent_output

result = validate_agent_output("Financial Model", output)
if not result.valid:
    print(result.fix_instructions)
```

### Constraint Broadcasting

`agents/constraint_broadcaster.py` enforces cross-section consistency:

- **Evidence Tiers**: E2 default (upgraded from E4)
- **Constraint Types**: must_use, must_align, must_reference, must_not_exceed
- **Override Requirements**: E1-E2 evidence required to override constraints

### Revision Loop

The Facilitator runs a revision loop when quality checks fail:
1. Critique agent scores all sections
2. Low-scoring sections flagged for revision
3. Validation failures injected as feedback
4. Agents re-run with fix instructions
5. Max 2 revision iterations

---

## Running Tests

```bash
# E2E test (full workflow)
python -m e2e_test

# Run evals on test output
python -m evals.cli run test_outputs/e2e_test_*.json -t agent_specific
```

---

## Project Structure

```
backend/
├── agents/
│   ├── facilitator.py           # Main orchestrator
│   ├── constraint_broadcaster.py # Cross-section consistency
│   ├── output_validator.py      # Pre-output validation
│   ├── eval_feedback_bridge.py  # Eval-to-revision integration
│   ├── prompts.py               # Agent prompts with checklists
│   ├── planner.py               # Planning agent
│   ├── business_strategy.py     # Business strategy agent
│   ├── gtm_agent.py             # GTM strategy agent
│   ├── financial_model_agent.py # Financial modeling agent
│   ├── technical_architect.py   # Technical architecture agent
│   ├── legal_regulatory.py      # Legal review agent
│   ├── executive_summary_agent.py
│   ├── stakeholder_agent.py
│   ├── validation_agent.py
│   ├── wireframe_agent.py
│   ├── prototype_agent.py
│   └── swarms/                  # Parallel agent execution
├── evals/
│   ├── cli.py                   # CLI interface
│   ├── base.py                  # Core types (EvalResult, BaseEval)
│   ├── runner.py                # Eval orchestration
│   ├── reporter.py              # Output formatting
│   ├── unit/                    # Schema, evidence tier evals
│   ├── llm_judge/               # Multi-dimension quality eval
│   ├── golden/                  # Golden set comparison
│   ├── consistency/             # Contradiction detection
│   └── agents/                  # 16 agent-specific evals
├── models/
│   └── schemas.py               # Pydantic schemas
└── config.py                    # Settings
```

---

## Environment Variables

```bash
GEMINI_API_KEY=           # Required: Gemini API key
OPENAI_API_KEY=           # Optional: For OpenAI models
MODEL_PROVIDER=gemini     # gemini or openai
LOG_LEVEL=INFO
```

---

## Recent Changes

### Agent Quality Improvement (v3.1)

- Added OUTPUT CHECKLIST to all 16 agent prompts
- Created `output_validator.py` with 700+ lines of validation rules
- Created `eval_feedback_bridge.py` for revision loop integration
- Strengthened constraints (E4 → E2 evidence tier)
- Integrated validation with facilitator.py

**Results:** Agent-specific eval score improved from 59.3% to 82.2%
