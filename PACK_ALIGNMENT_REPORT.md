# Pack Data Alignment Report

## Executive Summary

**Analysis Date:** 2026-02-26
**Session Analyzed:** disc_20260226_52244aba
**Status:** CRITICAL MISALIGNMENTS FOUND

The frontend PackViewer expects 16 sections with specific data structures. Comparison against actual pack data reveals **3 missing sections** and **multiple incomplete sections** that will cause empty UI displays.

---

## Frontend UI Structure

### Layout Architecture
```
┌──────────────────────────────────────────────────────────────┐
│ HEADER (57px) - Logo, Product Name, Status, Export Actions  │
├──────────────┬───────────────────────────────────────────────┤
│ SIDEBAR      │ MAIN CONTENT (max-width: 840px)              │
│ (260px)      │                                               │
│              │ ┌─────────────────────────────────────────┐   │
│ QualityScore │ │ Breadcrumb                              │   │
│              │ │ Section Header (Phase + Title)          │   │
│ SectionNav   │ │ ┌─────────────────────────────────────┐ │   │
│ (16 items)   │ │ │ Card Components                     │ │   │
│              │ │ │ - Lists, grids, tables, text        │ │   │
│ Evidence     │ │ └─────────────────────────────────────┘ │   │
│ Legend       │ │ Footer Navigation (Prev/Next/Export)   │   │
│              │ └─────────────────────────────────────────┘   │
└──────────────┴───────────────────────────────────────────────┘
```

### 16 Sections Expected by Frontend

| # | Section ID | Title | Phase | Status |
|---|------------|-------|-------|--------|
| 01 | `executive_summary` | Executive Summary | Overview | ✅ OK |
| 02 | `customer_research` | Customer Research | Discovery | ⚠️ EMPTY |
| 03 | `competitive_analysis` | Competitive Analysis | Discovery | ❌ MISSING |
| 04 | `personas` | Personas | Discovery | ❌ MISSING |
| 05 | `business_case` | Business Case | Strategy | ✅ OK |
| 06 | `gtm_strategy` | Go-to-Market | Strategy | ✅ OK |
| 07 | `financial_model` | Financial Model | Strategy | ⚠️ PARTIAL |
| 08 | `product_requirements` | Product Requirements | Delivery | ✅ OK |
| 09 | `technical_architecture` | Tech Architecture | Delivery | ✅ OK |
| 10 | `legal_regulatory` | Legal & Regulatory | Delivery | ✅ OK |
| 11 | `risk_assessment` | Risk Assessment | Delivery | ✅ OK |
| 12 | `wireframes` | Wireframes | Design | ✅ OK |
| 13 | `prototype` | Prototype | Design | ✅ OK |
| 14 | `stakeholder_views` | Stakeholder Views | Synthesis | ✅ OK |
| 15 | `validation_playbook` | Validation Playbook | Synthesis | ✅ OK |
| 16 | `quality_assessment` | Quality Assessment | Quality | ✅ OK |

---

## Critical Issues

### 1. MISSING SECTIONS (Will show "No data available")

#### competitive_analysis - COMPLETELY MISSING
**Frontend expects:** `pack.competitive_analysis`
- `competitors[]` or `direct_competitors[]`
- `market_gaps[]`
- `competitive_moat[]` or `competitive_moats[]`

**Pack contains:** Section not present at all

**UI Impact:** CompetitiveAnalysisSection shows empty competitor grid

---

#### detailed_personas - COMPLETELY MISSING
**Frontend expects:** `pack.detailed_personas`
- `personas[]` with: name, role, demographics, quote, goals, pain_points, jobs_to_be_done
- `key_insights[]`

**Pack contains:** Section not present at all

**UI Impact:** PersonasSection shows "No persona data available"

---

### 2. EMPTY/INCOMPLETE SECTIONS

#### customer_research - EMPTY (0 keys)
**Frontend expects:**
```
pack.customer_research.research_scope.segments_examined[]
pack.customer_research.uncomfortable_insights[]
pack.customer_research.job_to_be_done
pack.customer_research.current_behaviour
pack.customer_research.pain_signals[]
pack.customer_research.market_context
```

**Pack contains:** `customer_research: {}` (empty object)

**UI Impact:** CustomerResearchSection shows only fallback message "Customer research findings will appear here"

---

#### financial_model.projections - MISSING
**Frontend expects:**
```typescript
pack.financial_model.projections[]: {
  period: string,
  revenue: number,
  costs: number,
  profit: number,
  cumulative_profit: number
}
```

**Pack contains:**
```
summary: "" (empty string)
assumptions: LIST[3]
unit_economics: LIST[5]
break_even_analysis: "" (empty string)
funding_requirements: "Seed funding of approximately $500K-$1M"
sensitivity_analysis: DICT[3 keys]
```

**UI Impact:** Financial projections table will not render - no revenue/costs data

---

## Data Flow Analysis

### What Should Happen (Expected)
```
Discovery Swarm (Parallel)
  ├── Customer Research Agent → pack.customer_research
  ├── Competitive Intelligence Agent → pack.competitive_analysis
  └── Persona Development Agent → pack.detailed_personas
```

### What Actually Happened (Actual)
```
Discovery Swarm
  ├── Customer Research Agent → {} (empty)
  ├── Competitive Intelligence Agent → NOT RUN / NO OUTPUT
  └── Persona Development Agent → NOT RUN / NO OUTPUT
```

---

## Section-by-Section Field Mapping

### ✅ Working Sections

| Section | Required Fields | Status |
|---------|----------------|--------|
| executive_summary | product_name, tagline, problem_statement, solution_overview, value_proposition, target_users, target_market_size, key_differentiators | All present |
| business_case | lean_canvas, revenue_streams, cost_structure, break_even_analysis | All present |
| gtm_strategy | positioning_statement, target_segments, launch_phases, channel_strategy | All present |
| product_requirements_document | epics, functional_requirements, non_functional_requirements | All present |
| technical_architecture | architecture_style, technology_stack, system_components, architecture_diagram_mermaid | All present |
| legal_regulatory_review | executive_summary, applicable_regulations, legal_risks, overall_risk_assessment | All present |
| risk_assessment | risk_matrix, top_3_risks, risk_summary | Present (uses risk_matrix fallback) |
| wireframes | screens, user_flows, design_system_notes | All present |
| prototype | prototype_name, react_component_code, css_code | Present (uses react_component_code) |
| stakeholder_views | views, common_concerns | All present |
| validation_playbook | experiments | Present (uses experiments, not validation_experiments) |
| quality_assessment | overall_score, section_scores, strengths, weaknesses | All present |

### ❌ Broken/Empty Sections

| Section | Expected | Actual | Fix Required |
|---------|----------|--------|--------------|
| customer_research | 6+ nested objects | Empty {} | Backend agent not populating |
| competitive_analysis | competitors array | NULL | Section not generated |
| detailed_personas | personas array | NULL | Section not generated |
| financial_model.projections | Array of projections | Missing | Backend not providing projections |

---

## Frontend Fallback Behavior

The frontend gracefully handles missing data with these patterns:

```typescript
// Pattern 1: Optional chaining with conditional render
{analysis?.competitors && analysis.competitors.length > 0 && (
  <Card title="Competitors">...</Card>
)}

// Pattern 2: Fallback message
if (!prd) {
  return <Card title="Product Requirements">
    <p>No PRD data available.</p>
  </Card>;
}

// Pattern 3: Try multiple field names
const competitors = analysis?.competitors || analysis?.direct_competitors || [];
const experiments = playbook.experiments || playbook.validation_experiments;
```

---

## Recommendations

### Immediate Fixes Required

1. **Fix Customer Research Agent** - Agent is not populating output
   - Check `backend/agents/customer_research.py`
   - Verify state key `customer_research` is being written

2. **Enable Competitive Intelligence Agent**
   - Check `backend/agents/swarms/discovery_swarm.py`
   - Verify `competitive_analysis` state key is populated

3. **Enable Persona Development Agent**
   - Check persona agent execution
   - Verify `detailed_personas` state key is populated

4. **Add Financial Projections**
   - `financial_model.projections` array needed for table render
   - Monthly/quarterly data with revenue, costs, profit

### Frontend Improvements (Optional)

1. Add loading/empty state indicators per section
2. Add "Section incomplete" warnings instead of hiding content
3. Consider showing partial data when available

---

## Files to Investigate

| File | Purpose | Check For |
|------|---------|-----------|
| `backend/agents/customer_research.py` | Customer research | Output population |
| `backend/agents/swarms/discovery_swarm.py` | Discovery parallelization | Agent execution |
| `backend/agents/financial_model_agent.py` | Financial modeling | projections field |
| `backend/agents/orchestrator.py` | Workflow execution | Discovery swarm invocation |
| `backend/agents/facilitator.py` | V3 orchestration | Swarm coordination |

---

## Appendix: Actual Pack Structure

```
pack
├── business_case: DICT[15 keys] ✅
├── cross_reference_index: DICT[7 keys] ✅
├── customer_research: DICT[0 keys] ⚠️ EMPTY
├── executive_summary: DICT[21 keys] ✅
├── financial_model: DICT[6 keys] ⚠️ PARTIAL
├── gtm_strategy: DICT[7 keys] ✅
├── legal_regulatory_review: DICT[12 keys] ✅
├── metadata: DICT[9 keys] ✅
├── product_requirements_document: DICT[14 keys] ✅
├── prototype: DICT[12 keys] ✅
├── quality_assessment: DICT[9 keys] ✅
├── risk_assessment: DICT[6 keys] ✅
├── stakeholder_views: DICT[3 keys] ✅
├── technical_architecture: DICT[14 keys] ✅
├── validation_playbook: DICT[6 keys] ✅
├── wireframes: DICT[6 keys] ✅
├── competitive_analysis: ❌ MISSING
└── detailed_personas: ❌ MISSING
```
