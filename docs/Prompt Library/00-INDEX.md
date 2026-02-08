# Seedcraft v3.0 — Prompt Library

**Date:** February 7, 2026
**Purpose:** Every agent prompt, written in full, ready for implementation.
**Usage:** These prompts replace the existing prompts in `backend/agents/prompts.py`

---

## Files

| # | File | Agent | Model | Replaces |
|---|------|-------|-------|----------|
| 01 | `01-market-intelligence.md` | Market Intelligence | Flash + Grounding | `CUSTOMER_RESEARCH_PROMPT` |
| 02 | `02-competitive-landscape.md` | Competitive Landscape | Flash + Grounding | Competitive section in `discovery_swarm.py` |
| 03 | `03-customer-personas.md` | Customer Personas | Flash | Persona section in `discovery_swarm.py` |
| 04 | `04-business-case.md` | Business Case | Pro + Grounding | `BUSINESS_STRATEGY_PROMPT` |
| 05 | `05-go-to-market.md` | Go-to-Market Strategy | Pro | New agent |
| 06 | `06-financial-model.md` | Financial Model | Pro | New agent |
| 07 | `07-product-requirements.md` | Product Requirements | Flash (Pro for critic) | `PRD_GENERATOR_PROMPT` |
| 08 | `08-technical-architecture.md` | Technical Architecture | Flash | `TECHNICAL_ARCHITECT_PROMPT` |
| 09 | `09-regulatory-compliance.md` | Regulatory & Compliance | Pro + Grounding | `LEGAL_REGULATORY_PROMPT` |
| 10 | `10-risk-assessment.md` | Risk Assessment | Flash | `CRITIQUE_PROMPT` (partial) |
| 11 | `11-stakeholder-views.md` | Stakeholder Views | Pro | New agent |
| 12 | `12-validation-playbook.md` | Validation Playbook | Pro | New agent |
| 13 | `13-narrative-executive-summary.md` | Executive Summary | Flash | New agent |
| 14 | `14-wireframe-agent.md` | Wireframe Generator | Flash | New agent |
| 15 | `15-prototype-agent.md` | Prototype Generator | Pro | New agent |
| 16 | `16-claim-extractor.md` | Claim Extraction (utility) | Flash | New utility |
| 17 | `17-context-builder.md` | Context injection helper | N/A (code) | New utility |

---

## Prompt Design Principles

Every prompt in this library follows these rules:

1. **Role framing:** The agent is a senior specialist at a top-tier firm, not a generic AI assistant.
2. **Radical specificity mandate:** Every prompt explicitly bans generic output and provides examples of what "specific" looks like.
3. **Evidence tier enforcement:** Every prompt requires E1-E5 tagging on substantive claims.
4. **Cross-reference awareness:** Every prompt tells the agent what other sections exist and that claims should reference dependencies.
5. **Anti-pattern examples:** Every prompt includes examples of BAD output to avoid.
6. **Output format:** Every prompt specifies exact JSON structure.

---

## Evidence Tier Definitions (shared across all agents)

| Tier | Meaning | Source | Colour |
|------|---------|--------|--------|
| E1 | Primary research uploaded by the user | Interviews, surveys, analytics | Green |
| E2 | Verified by Google Search with URL | Search-grounded, citable | Blue |
| E3 | Published industry reports | Named reports, benchmark data | Yellow |
| E4 | LLM hypothesis — no direct evidence | AI inference | Orange |
| E5 | Structural assumption | Foundational, untested | Red |

**Rule:** If you don't have a specific source URL or report name, it's E4 — no matter how confident you feel.

---

## Context Injection Pattern

Later agents need summaries of earlier agents' outputs. See `17-context-builder.md` for the helper code and the full variable mapping table showing which prompt variables come from which state fields.

---

## Prompt Variable Mapping (Quick Reference)

| Prompt Variable | Source State Field | Used By Agents |
|----------------|-------------------|----------------|
| `{market_intelligence_summary}` | `customer_research` | 02, 04, 05, 10, 11, 13 |
| `{competitive_landscape_summary}` | `competitive_analysis` | 04, 05, 10, 11, 13 |
| `{personas_summary}` | `detailed_personas` | 05, 07, 14, 15 |
| `{business_case_summary}` | `business_case` | 06, 05, 10, 11, 13 |
| `{prd_summary}` | `product_requirements` | 08, 09, 14, 15 |
| `{tech_arch_summary}` | `technical_architecture` | 09, 10, 14, 15 |
| `{regulatory_hints}` | `preliminary_legal_scan` | 01, 07, 08 |
| `{gtm_summary}` | `gtm_plan` | 06 |
| `{regulatory_summary}` | `legal_regulatory_review` | 10 |
| `{full_pack_summary}` | All fields combined | 11, 13 |
| `{cross_reference_summary}` | `cross_reference_index` | 11, 12, 13 |
| `{memory_context}` | Memory retrieval | 01 (and any memory-enabled agent) |
