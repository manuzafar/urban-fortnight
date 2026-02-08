# File Change Summary

Complete inventory of every file created or modified across all 10 phases.

---

## New Files (18)

| File | Phase | Purpose |
|------|-------|---------|
| `backend/models/cross_references.py` | 1 | Claim, EvidenceTier, CrossReferenceIndex schemas |
| `backend/agents/claim_extractor.py` | 1 | Extract claims from agent output with evidence tiers |
| `backend/agents/context_builder.py` | 2 | Build upstream summaries for downstream prompt injection |
| `backend/agents/gtm_agent.py` | 5 | Go-to-Market strategy agent |
| `backend/agents/financial_model_agent.py` | 5 | Financial projections agent (monthly Y1, quarterly Y2-3) |
| `backend/agents/wireframe_agent.py` | 6 | Generate React/JSX wireframe screens from PRD |
| `backend/agents/prototype_agent.py` | 6 | Generate interactive prototype as single React component |
| `backend/agents/stakeholder_agent.py` | 7 | Generate 3-4 stakeholder-specific views with objections |
| `backend/agents/validation_agent.py` | 7 | Generate validation playbook with specific experiments |
| `backend/agents/executive_summary_agent.py` | 7 | Narrative executive summary with recommendation |
| `frontend/src/components/PackViewer/EvidenceBadge.tsx` | 10 | E1-E5 coloured badge component |
| `frontend/src/components/PackViewer/EvidenceBar.tsx` | 10 | Tier distribution horizontal bar |
| `frontend/src/components/PackViewer/design/WireframeViewer.tsx` | 10 | Sandboxed iframe wireframe renderer |
| `frontend/src/components/PackViewer/design/PrototypeViewer.tsx` | 10 | Sandboxed iframe prototype renderer |
| `frontend/src/components/PackViewer/design/UserFlowDiagram.tsx` | 10 | Mermaid diagram renderer |
| `frontend/src/components/PackViewer/stakeholders/StakeholderViewSelector.tsx` | 10 | Stakeholder view dropdown/tabs |
| `frontend/src/components/PackViewer/validation/ValidationPlaybook.tsx` | 10 | Validation playbook view |
| `frontend/src/components/charts/EvidenceDistributionChart.tsx` | 10 | Evidence tier donut/bar chart |

---

## Modified Files (16)

| File | Phase(s) | Changes |
|------|----------|---------|
| `backend/agents/state.py` | 1 | Add `cross_reference_index`, `wireframes`, `prototype`, `stakeholder_views`, `validation_playbook` fields + `merge_cross_references` reducer |
| `backend/agents/base_agent.py` | 1 | Add `extract_and_store_claims()` helper function |
| `backend/config.py` | 1, 4 | Add model routing for all 18 agents (Flash vs Pro) |
| `backend/agents/prompts.py` | 4 | Replace ALL agent prompts with versions from prompt library |
| `backend/models/schemas.py` | 3 | Replace/extend all section Pydantic models (Market Intelligence, Competitive Landscape, Customer Personas, Business Case, GTM, Financial Model, PRD, Tech Arch, Regulatory, Risk, Stakeholder, Validation, Exec Summary, Wireframes, Prototype) |
| `backend/agents/customer_research.py` | 1, 4 | Add claim extraction + use new prompt + context builder |
| `backend/agents/business_strategy.py` | 1, 4 | Add claim extraction + use new prompt + context builder |
| `backend/agents/prd_generator.py` | 1, 4 | Add claim extraction + use new prompt + context builder |
| `backend/agents/technical_architect.py` | 1, 4 | Add claim extraction + use new prompt + context builder |
| `backend/agents/legal_regulatory.py` | 1, 4 | Add claim extraction + use new prompt + context builder |
| `backend/agents/critique.py` | 1, 8 | Add claim extraction + 5-dimension evidence-aware critique |
| `backend/agents/swarms/discovery_swarm.py` | 1, 4 | Add claim extraction + new prompts for competitive + persona agents |
| `backend/agents/swarms/strategy_swarm.py` | 1, 4, 5 | Add claim extraction + GTM + Financial Model integration |
| `backend/agents/swarms/delivery_swarm.py` | 1, 4 | Add claim extraction + risk assessment prompt |
| `backend/agents/facilitator.py` | 9 | Complete pipeline redesign: 7 phases with parallel/sequential orchestration |
| `backend/utils/sse.py` | 6 | Add `WIREFRAME_READY`, `PROTOTYPE_READY`, `DESIGN_PHASE` event types |

---

## Prompt Library Files (17 reference files)

These files in `seedcraft-v3-prompts/` are the source of truth for all prompts. Each contains a production-ready prompt constant to be copied into the appropriate agent file.

| File | Agent | Model |
|------|-------|-------|
| `01-market-intelligence.md` | Market Intelligence | Flash + Grounding |
| `02-competitive-landscape.md` | Competitive Landscape | Flash + Grounding |
| `03-customer-personas.md` | Customer Personas | Flash |
| `04-business-case.md` | Business Case | Pro + Grounding |
| `05-go-to-market.md` | Go-to-Market | Pro |
| `06-financial-model.md` | Financial Model | Pro |
| `07-product-requirements.md` | Product Requirements | Flash |
| `08-technical-architecture.md` | Technical Architecture | Flash |
| `09-regulatory-compliance.md` | Regulatory & Compliance | Pro + Grounding |
| `10-risk-assessment.md` | Risk Assessment | Flash |
| `11-stakeholder-views.md` | Stakeholder Views | Pro |
| `12-validation-playbook.md` | Validation Playbook | Pro |
| `13-narrative-executive-summary.md` | Executive Summary | Flash |
| `14-wireframe-agent.md` | Wireframe Generator | Flash |
| `15-prototype-agent.md` | Prototype Generator | Pro |
| `16-claim-extractor.md` | Claim Extraction Utility | Flash |
| `17-context-builder.md` | Context Builder (Python code) | N/A |

---

## State Field Inventory

Complete list of `DiscoveryState` fields after all phases:

| Field | Type | Written By | Read By |
|-------|------|-----------|---------|
| `product_idea` | str | User input | All agents |
| `industry` | str | Planning | All agents |
| `target_market` | str | Planning | Discovery agents |
| `competitors` | str | Planning | MI, CL |
| `preliminary_legal_scan` | dict | Planning | MI, PRD, TA |
| `memory_context` | str | Memory system | MI |
| `customer_research` | dict | MI agent | CL, CP, BC, GTM, FM, Risk, Stakeholder, Exec |
| `competitive_analysis` | dict | CL agent | BC, GTM, Risk, Stakeholder, Exec |
| `detailed_personas` | dict | CP agent | GTM, PRD, Wireframes, Prototype, Stakeholder, Exec |
| `business_case` | dict | BC agent | FM, GTM, Risk, Stakeholder, Exec |
| `gtm_plan` | dict | GTM agent | FM, Risk, Stakeholder, Exec |
| `financial_model` | dict | FM agent | Risk, Stakeholder, Exec |
| `product_requirements` | dict | PRD agent | TA, RC, Wireframes, Prototype, Risk, Stakeholder, Exec |
| `technical_architecture` | dict | TA agent | RC, Wireframes, Prototype, Risk, Stakeholder, Exec |
| `legal_regulatory_review` | dict | RC agent | Risk, Stakeholder, Exec |
| `risk_assessment` | dict | Risk agent | Stakeholder, Exec |
| `wireframes` | dict | Wireframe agent | Prototype, Frontend |
| `prototype` | dict | Prototype agent | Frontend |
| `cross_reference_index` | dict | All agents (via claim extractor) | Critique, Stakeholder, Validation, Exec |
| `stakeholder_views` | dict | Stakeholder agent | Exec, Frontend |
| `validation_playbook` | dict | Validation agent | Exec, Frontend |
| `executive_summary` | dict | Exec Summary agent | Frontend |
| `critique` | dict | Critique agent | Facilitator (revision loop) |
