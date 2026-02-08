# 17 — Context Builder Utility

**Purpose:** Helper code that builds summaries of upstream agent outputs for injection into downstream agent prompts.
**File:** `backend/agents/context_builder.py`

---

## The Problem

Later agents need summaries of earlier agents' outputs. The Financial Model agent needs the Business Case unit economics. The Wireframe agent needs the PRD screen map. The Stakeholder Views agent needs everything.

But you can't dump the entire JSON of every upstream agent into a prompt — it would exceed token limits and drown the signal in noise.

The Context Builder extracts the most important fields from each upstream output and builds concise summaries.

---

## Code

```python
"""
Context Builder — builds concise summaries of upstream agent outputs
for injection into downstream agent prompts.
"""

import json
from typing import Any, Dict, Optional


# Fields to extract for each section's summary (ordered by importance)
SUMMARY_FIELDS = {
    "customer_research": [  # Market Intelligence
        "market_definition",
        "market_size",
        "market_growth_rate",
        "pain_signals",
        "why_now",
        "demand_indicators",
    ],
    "competitive_analysis": [  # Competitive Landscape
        "differentiation_thesis",
        "moat_analysis",
        "positioning_map",
        "direct_competitors",  # truncated to name + one_liner + pricing
        "competitive_gaps",
    ],
    "detailed_personas": [  # Customer Personas
        "personas",  # truncated to name + role + archetype + goals + jobs_to_be_done
        "persona_prioritisation",
    ],
    "business_case": [  # Business Case
        "value_proposition",
        "revenue_model",
        "unit_economics",
        "sensitivity_analysis",
        "beachhead_market",
    ],
    "gtm_plan": [  # Go-to-Market
        "positioning_statement",
        "launch_phases",
        "channel_strategy",
        "messaging_by_persona",
    ],
    "financial_model": [  # Financial Model
        "input_assumptions",
        "revenue_model",
        "scenario_analysis",
        "funding_requirements",
    ],
    "product_requirements": [  # PRD
        "product_name",
        "one_liner",
        "product_principles",
        "scope",
        "epics",  # truncated to epic_id + title + user stories with screen refs
        "screen_map",
    ],
    "technical_architecture": [  # Technical Architecture
        "architecture_summary",
        "architecture_pattern",
        "data_model",
        "api_design",
        "tech_stack_recommendation",
        "deployment",
    ],
    "legal_regulatory_review": [  # Regulatory & Compliance
        "regulatory_landscape",
        "applicable_frameworks",
        "compliance_requirements",
        "data_handling_requirements",
    ],
    "risk_assessment": [  # Risk Assessment
        "top_3_risks_summary",
        "overall_risk_assessment",
        "risks",  # truncated to risk_id + risk + category + likelihood + impact
    ],
}


def build_context_summary(
    state: Dict[str, Any],
    field: str,
    max_chars: int = 4000,
) -> str:
    """
    Build a concise summary of a state field for injection into a downstream prompt.
    
    Args:
        state: The full discovery state dict
        field: The state field key (e.g., "customer_research", "business_case")
        max_chars: Maximum character length for the summary
        
    Returns:
        A string summary suitable for prompt injection
    """
    data = state.get(field)
    if not data:
        return "Not yet available — this section has not been generated yet."
    
    if isinstance(data, str):
        return data[:max_chars]
    
    if not isinstance(data, dict):
        return str(data)[:max_chars]
    
    # Get priority fields for this section
    priority_fields = SUMMARY_FIELDS.get(field, [])
    
    parts = []
    chars_used = 0
    
    for key in priority_fields:
        if key not in data:
            continue
            
        value = data[key]
        formatted = _format_field(key, value)
        
        if chars_used + len(formatted) > max_chars:
            # Truncate this field to fit
            remaining = max_chars - chars_used - 50  # leave room for truncation note
            if remaining > 200:
                parts.append(formatted[:remaining] + "\n[... truncated]")
            break
        
        parts.append(formatted)
        chars_used += len(formatted)
    
    if not parts:
        # Fallback: dump the whole thing, truncated
        return json.dumps(data, default=str, indent=2)[:max_chars]
    
    return "\n\n".join(parts)


def _format_field(key: str, value: Any) -> str:
    """Format a single field for human-readable summary."""
    
    if isinstance(value, str):
        return f"**{_humanize(key)}:** {value}"
    
    if isinstance(value, list):
        if len(value) == 0:
            return f"**{_humanize(key)}:** (empty)"
        
        # For competitor lists, truncate to essentials
        if key == "direct_competitors":
            items = []
            for comp in value[:6]:  # max 6 competitors
                if isinstance(comp, dict):
                    name = comp.get("name", "Unknown")
                    liner = comp.get("one_liner", "")
                    pricing = comp.get("pricing", {})
                    if isinstance(pricing, dict):
                        pricing_str = pricing.get("tiers", "pricing unknown")
                    else:
                        pricing_str = str(pricing)
                    items.append(f"- {name}: {liner} (Pricing: {pricing_str})")
                else:
                    items.append(f"- {comp}")
            return f"**{_humanize(key)}:**\n" + "\n".join(items)
        
        # For persona lists, truncate to essentials
        if key == "personas":
            items = []
            for p in value[:3]:
                if isinstance(p, dict):
                    name = p.get("name", "Unknown")
                    role = p.get("role", "")
                    archetype = p.get("archetype", "")
                    goals = p.get("goals", [])
                    goals_str = "; ".join(goals[:3]) if goals else ""
                    items.append(f"- {name} ({role}) — {archetype}. Goals: {goals_str}")
            return f"**{_humanize(key)}:**\n" + "\n".join(items)
        
        # For risk lists, truncate to essentials
        if key == "risks":
            items = []
            for r in value[:8]:
                if isinstance(r, dict):
                    rid = r.get("risk_id", "?")
                    risk = r.get("risk", "")
                    cat = r.get("category", "")
                    like = r.get("likelihood", "")
                    impact = r.get("impact", "")
                    items.append(f"- [{rid}] ({cat}) {risk} — Likelihood: {like}, Impact: {impact}")
            return f"**{_humanize(key)}:**\n" + "\n".join(items)
        
        # For pain signals, show pain + severity
        if key == "pain_signals":
            items = []
            for ps in value[:6]:
                if isinstance(ps, dict):
                    pain = ps.get("pain", "")
                    sev = ps.get("severity", "")
                    tier = ps.get("evidence_tier", "")
                    items.append(f"- [{tier}] ({sev}) {pain}")
                else:
                    items.append(f"- {ps}")
            return f"**{_humanize(key)}:**\n" + "\n".join(items)
        
        # Default list formatting
        items = []
        for item in value[:8]:
            if isinstance(item, dict):
                items.append(f"- {json.dumps(item, default=str)[:200]}")
            else:
                items.append(f"- {item}")
        return f"**{_humanize(key)}:**\n" + "\n".join(items)
    
    if isinstance(value, dict):
        return f"**{_humanize(key)}:**\n{json.dumps(value, default=str, indent=2)[:800]}"
    
    return f"**{_humanize(key)}:** {value}"


def _humanize(key: str) -> str:
    """Convert snake_case to Title Case."""
    return key.replace("_", " ").title()


def build_full_pack_summary(state: Dict[str, Any], max_chars: int = 12000) -> str:
    """
    Build a comprehensive summary of the entire inception pack.
    Used by Stakeholder Views and Executive Summary agents.
    """
    sections = [
        ("Market Intelligence", "customer_research"),
        ("Competitive Landscape", "competitive_analysis"),
        ("Customer Personas", "detailed_personas"),
        ("Business Case", "business_case"),
        ("Go-to-Market", "gtm_plan"),
        ("Financial Model", "financial_model"),
        ("Product Requirements", "product_requirements"),
        ("Technical Architecture", "technical_architecture"),
        ("Regulatory & Compliance", "legal_regulatory_review"),
        ("Risk Assessment", "risk_assessment"),
    ]
    
    per_section_budget = max_chars // len(sections)
    parts = []
    
    for title, field in sections:
        summary = build_context_summary(state, field, max_chars=per_section_budget)
        parts.append(f"## {title}\n{summary}")
    
    return "\n\n---\n\n".join(parts)


def build_cross_reference_summary(state: Dict[str, Any], max_chars: int = 4000) -> str:
    """
    Build a summary of the cross-reference index for agents that need claim awareness.
    """
    index = state.get("cross_reference_index", {})
    claims = index.get("claims", [])
    
    if not claims:
        return "No claims indexed yet."
    
    # Count by tier
    tier_counts = {}
    for c in claims:
        tier = c.get("evidence_tier", "E4")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    # Build summary
    lines = [
        f"Total claims: {len(claims)}",
        f"Distribution: " + ", ".join(f"{k}: {v}" for k, v in sorted(tier_counts.items())),
        "",
        "Key claims (E1/E2 — strongest evidence):",
    ]
    
    strong_claims = [c for c in claims if c.get("evidence_tier") in ("E1", "E2")]
    for c in strong_claims[:10]:
        lines.append(f"  [{c['claim_id']}] {c['claim']} [{c['evidence_tier']}]")
    
    lines.append("")
    lines.append("High-risk claims (E4/E5 with most dependents):")
    
    # Find E4/E5 claims with most downstream dependencies
    weak_claims = [c for c in claims if c.get("evidence_tier") in ("E4", "E5")]
    # Sort by number of things that depend on them
    for c in weak_claims:
        c["_dep_count"] = len(c.get("depended_on_by", []))
    weak_claims.sort(key=lambda x: x["_dep_count"], reverse=True)
    
    for c in weak_claims[:10]:
        deps = c.get("_dep_count", 0)
        lines.append(f"  [{c['claim_id']}] {c['claim']} [{c['evidence_tier']}] — {deps} downstream claims depend on this")
    
    result = "\n".join(lines)
    return result[:max_chars]
```

---

## Prompt Variable Mapping (Complete Reference)

| Prompt Variable | Built By | Source State Field | Used By Agents |
|----------------|----------|-------------------|----------------|
| `{market_intelligence_summary}` | `build_context_summary(state, "customer_research")` | `customer_research` | 02, 04, 05, 10, 11, 13 |
| `{competitive_landscape_summary}` | `build_context_summary(state, "competitive_analysis")` | `competitive_analysis` | 04, 05, 10, 11, 13 |
| `{personas_summary}` | `build_context_summary(state, "detailed_personas")` | `detailed_personas` | 05, 07, 14, 15 |
| `{business_case_summary}` | `build_context_summary(state, "business_case")` | `business_case` | 06, 05, 10, 11, 13 |
| `{prd_summary}` | `build_context_summary(state, "product_requirements")` | `product_requirements` | 08, 09, 14, 15 |
| `{tech_arch_summary}` | `build_context_summary(state, "technical_architecture")` | `technical_architecture` | 09, 10, 14, 15 |
| `{regulatory_hints}` | `build_context_summary(state, "preliminary_legal_scan")` | `preliminary_legal_scan` | 01, 07, 08 |
| `{gtm_summary}` | `build_context_summary(state, "gtm_plan")` | `gtm_plan` | 06 |
| `{regulatory_summary}` | `build_context_summary(state, "legal_regulatory_review")` | `legal_regulatory_review` | 10 |
| `{full_pack_summary}` | `build_full_pack_summary(state)` | All fields | 11, 13 |
| `{cross_reference_summary}` | `build_cross_reference_summary(state)` | `cross_reference_index` | 11, 12, 13 |
| `{cross_reference_index}` | `json.dumps(state["cross_reference_index"])` | `cross_reference_index` | 12 |
| `{memory_context}` | From memory retrieval system | Memory store | 01 (and any memory-enabled agent) |
| `{screen_map}` | `json.dumps(state["product_requirements"]["screen_map"])` | `product_requirements.screen_map` | 14 |
| `{user_stories}` | Extracted from PRD epics | `product_requirements.epics` | 14 |
| `{data_model_summary}` | `json.dumps(state["technical_architecture"]["data_model"])` | `technical_architecture.data_model` | 14, 15 |
| `{wireframe_summary}` | Summary of wireframe screens | `wireframes` | 15 |
| `{primary_persona}` | First persona from prioritisation | `detailed_personas.personas[0]` | 15 |
| `{key_user_story}` | Highest-priority must-have story | `product_requirements.epics[0].user_stories[0]` | 15 |
| `{evidence_score}` | Computed from cross-reference index | Calculated | 12, 13 |
| `{total_claims}` | `len(state["cross_reference_index"]["claims"])` | Calculated | 12, 13 |
| `{e1_count}` through `{e5_count}` | Counted from claims | Calculated | 12, 13 |
| `{validation_priorities}` | Top 3 experiments from playbook | `validation_playbook.experiments[:3]` | 13 |
| `{stakeholder_view_names}` | List of generated views | `stakeholder_views.views` | 13 |
