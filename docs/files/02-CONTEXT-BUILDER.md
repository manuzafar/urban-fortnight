# Phase 2: Context Builder Utility

**Goal:** Build the helper that creates concise summaries of upstream agent outputs for injection into downstream agent prompts.

**Why second:** This is the plumbing that enables cross-referencing. Without it, later agents can't reference earlier agents' findings.

**Dependencies:** Phase 1 (for cross-reference index access)

---

## 2.1 Create Context Builder

**File:** `backend/agents/context_builder.py` (NEW)

→ **Full implementation:** Copy the complete Python code from `seedcraft-v3-prompts/17-context-builder.md`

The file must contain these functions:

### Core Functions

```python
"""
Context Builder — creates concise summaries of upstream agent outputs
for injection into downstream agent prompts.

Each summary extracts the highest-priority fields from a state field,
formats them readably, and truncates to fit within prompt token limits.
"""

import json
from typing import Any, Optional


# Priority fields to extract per section (ordered by importance)
SUMMARY_FIELDS = {
    "customer_research": [
        "market_definition", "market_size", "market_growth_rate",
        "pain_signals", "why_now", "demand_indicators",
    ],
    "competitive_analysis": [
        "differentiation_thesis", "direct_competitors", "competitive_gaps",
        "positioning_map", "moat_analysis",
    ],
    "detailed_personas": [
        "personas",  # Custom formatter extracts name, role, JTBD, buying behaviour
        "persona_prioritisation",
    ],
    "business_case": [
        "value_proposition", "problem_cost", "solution_value",
        "revenue_model", "unit_economics", "sensitivity_analysis",
    ],
    "gtm_plan": [
        "positioning_statement", "launch_phases", "channel_strategy",
        "messaging_by_persona", "metrics_dashboard",
    ],
    "financial_model": [
        "input_assumptions", "monthly_projections_year_1",
        "scenario_analysis", "funding_requirements",
    ],
    "product_requirements": [
        "product_name", "one_liner", "product_principles", "scope",
        "epics", "screen_map", "success_metrics",
    ],
    "technical_architecture": [
        "architecture_summary", "architecture_pattern", "data_model",
        "api_design", "tech_stack_recommendation", "deployment",
    ],
    "legal_regulatory_review": [
        "regulations", "compliance_requirements", "implementation_requirements",
        "compliance_timeline",
    ],
    "risk_assessment": [
        "risks",  # Custom formatter extracts name, likelihood, impact, mitigation
    ],
    "preliminary_legal_scan": [
        "regulatory_hints", "key_regulations", "compliance_considerations",
    ],
}


def build_context_summary(
    state: dict,
    field: str,
    max_chars: int = 4000,
) -> str:
    """
    Extract key fields from a state field and create a concise summary.

    Args:
        state: The DiscoveryState dict
        field: The state field to summarize (e.g., "customer_research")
        max_chars: Maximum characters for the summary

    Returns:
        Formatted string summary, or "Not yet available" if field is empty
    """
    data = state.get(field)
    if not data:
        return "Not yet available"

    if isinstance(data, str):
        return data[:max_chars]

    if not isinstance(data, dict):
        return json.dumps(data, indent=2, default=str)[:max_chars]

    priority_fields = SUMMARY_FIELDS.get(field, list(data.keys()))
    parts = []

    for key in priority_fields:
        if key not in data or data[key] is None:
            continue
        value = data[key]

        # Custom formatters for complex nested structures
        if field == "competitive_analysis" and key == "direct_competitors":
            formatted = _format_competitors(value)
        elif field == "detailed_personas" and key == "personas":
            formatted = _format_personas(value)
        elif field == "risk_assessment" and key == "risks":
            formatted = _format_risks(value)
        elif field == "customer_research" and key == "pain_signals":
            formatted = _format_pain_signals(value)
        elif field == "product_requirements" and key == "epics":
            formatted = _format_epics(value)
        elif field == "product_requirements" and key == "screen_map":
            formatted = _format_screen_map(value)
        elif isinstance(value, list):
            formatted = _format_list(key, value)
        elif isinstance(value, dict):
            formatted = _format_dict(key, value)
        else:
            formatted = f"**{key}:** {value}"

        parts.append(formatted)

        # Check length
        current = "\n\n".join(parts)
        if len(current) > max_chars:
            break

    result = "\n\n".join(parts)
    if len(result) > max_chars:
        result = result[:max_chars - 20] + "\n... [truncated]"

    return result


def build_full_pack_summary(state: dict, max_chars: int = 12000) -> str:
    """
    Build comprehensive summary across ALL sections.
    Used by: Stakeholder Views (11), Executive Summary (13)
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
        if summary != "Not yet available":
            parts.append(f"## {title}\n{summary}")

    return "\n\n---\n\n".join(parts)


def build_cross_reference_summary(state: dict, max_chars: int = 4000) -> str:
    """
    Build evidence snapshot from cross-reference index.
    Used by: Validation Playbook (12), Executive Summary (13), Critique (8)
    """
    index = state.get("cross_reference_index", {"claims": []})
    claims = index.get("claims", [])

    if not claims:
        return "No claims extracted yet."

    # Compute tier counts
    tier_counts = {"E1": 0, "E2": 0, "E3": 0, "E4": 0, "E5": 0}
    for c in claims:
        tier = c.get("evidence_tier", "E4") if isinstance(c, dict) else "E4"
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    total = len(claims)
    weights = {"E1": 1.0, "E2": 0.85, "E3": 0.6, "E4": 0.3, "E5": 0.1}
    score = round(
        sum(weights.get(c.get("evidence_tier", "E4") if isinstance(c, dict) else "E4", 0.3) for c in claims) / max(total, 1),
        2,
    )

    # Section distribution
    section_counts = {}
    for c in claims:
        cid = c.get("claim_id", "") if isinstance(c, dict) else ""
        prefix = cid.split("-")[0] if "-" in cid else "??"
        section_counts[prefix] = section_counts.get(prefix, 0) + 1

    # Find highest-impact E4/E5 claims (most dependents)
    dep_counts = {}
    for c in claims:
        if not isinstance(c, dict):
            continue
        cid = c.get("claim_id", "")
        for dep in c.get("depends_on", []):
            dep_counts[dep] = dep_counts.get(dep, 0) + 1

    e4_e5 = [c for c in claims if isinstance(c, dict) and c.get("evidence_tier") in ("E4", "E5")]
    e4_e5_sorted = sorted(e4_e5, key=lambda c: dep_counts.get(c.get("claim_id", ""), 0), reverse=True)

    parts = [
        f"**Evidence Score:** {score}/1.0 ({total} claims)",
        f"**Tier Distribution:** E1={tier_counts['E1']}, E2={tier_counts['E2']}, E3={tier_counts['E3']}, E4={tier_counts['E4']}, E5={tier_counts['E5']}",
        f"**Section Coverage:** {', '.join(f'{k}={v}' for k, v in sorted(section_counts.items()))}",
    ]

    if e4_e5_sorted[:5]:
        parts.append("**Highest-Impact Hypotheses (E4/E5, most dependents):**")
        for c in e4_e5_sorted[:5]:
            deps = dep_counts.get(c.get("claim_id", ""), 0)
            parts.append(f"  - {c.get('claim_id')}: {c.get('statement', '')[:100]} ({deps} dependents)")

    result = "\n".join(parts)
    return result[:max_chars]


# ═══ Custom formatters ═══

def _format_competitors(competitors: list) -> str:
    lines = ["**Key Competitors:**"]
    for comp in competitors[:5]:
        if isinstance(comp, dict):
            name = comp.get("name", "Unknown")
            one_liner = comp.get("one_liner", "")
            pricing = comp.get("pricing", {})
            if isinstance(pricing, dict):
                price_str = pricing.get("tiers", "Unknown pricing")
            else:
                price_str = str(pricing)
            threat = comp.get("threat_level", "moderate")
            lines.append(f"  - **{name}** ({threat} threat): {one_liner}. Pricing: {price_str}")
    return "\n".join(lines)


def _format_personas(personas: list) -> str:
    lines = ["**Personas:**"]
    for p in personas[:3]:
        if isinstance(p, dict):
            name = p.get("name", "Unknown")
            role = p.get("role", "")
            jtbd = p.get("jobs_to_be_done", [])
            jtbd_str = ""
            if jtbd and isinstance(jtbd[0], dict):
                jtbd_str = f" Primary JTBD: {jtbd[0].get('motivation', '')}"
            lines.append(f"  - **{name}** — {role}.{jtbd_str}")
    return "\n".join(lines)


def _format_risks(risks: list) -> str:
    lines = ["**Key Risks:**"]
    for r in risks[:6]:
        if isinstance(r, dict):
            name = r.get("risk", r.get("title", "Unknown"))
            likelihood = r.get("likelihood", "?")
            impact = r.get("impact", "?")
            lines.append(f"  - {name} (L={likelihood}, I={impact})")
    return "\n".join(lines)


def _format_pain_signals(signals: list) -> str:
    lines = ["**Pain Signals:**"]
    for s in signals[:5]:
        if isinstance(s, dict):
            pain = s.get("pain", "Unknown")
            severity = s.get("severity", "?")
            tier = s.get("evidence_tier", "E4")
            lines.append(f"  - [{tier}] {pain} (severity: {severity})")
    return "\n".join(lines)


def _format_epics(epics: list) -> str:
    lines = ["**Epics:**"]
    for e in epics[:6]:
        if isinstance(e, dict):
            eid = e.get("epic_id", "?")
            title = e.get("title", "Unknown")
            stories = e.get("user_stories", [])
            lines.append(f"  - {eid}: {title} ({len(stories)} stories)")
    return "\n".join(lines)


def _format_screen_map(screen_map: list) -> str:
    lines = ["**Screen Map:**"]
    for s in screen_map:
        if isinstance(s, dict):
            sid = s.get("screen_id", "?")
            name = s.get("screen_name", "Unknown")
            purpose = s.get("purpose", "")
            lines.append(f"  - {sid}: {name} — {purpose}")
    return "\n".join(lines)


def _format_list(key: str, items: list) -> str:
    if not items:
        return f"**{key}:** (empty)"
    if isinstance(items[0], str):
        return f"**{key}:** {', '.join(items[:8])}"
    # List of dicts — show first few as JSON
    return f"**{key}:**\n{json.dumps(items[:4], indent=2, default=str)}"


def _format_dict(key: str, value: dict) -> str:
    return f"**{key}:**\n{json.dumps(value, indent=2, default=str)}"
```

---

## 2.2 Usage Pattern

Every downstream agent formats its prompt using the context builder:

```python
from agents.context_builder import build_context_summary

# Example: Business Case agent
prompt = BUSINESS_CASE_PROMPT.format(
    product_idea=state["product_idea"],
    industry=state.get("industry", ""),
    market_intelligence_summary=build_context_summary(state, "customer_research"),
    competitive_landscape_summary=build_context_summary(state, "competitive_analysis"),
    personas_summary=build_context_summary(state, "detailed_personas"),
    # ...
)
```

---

## 2.3 Prompt Variable → Builder Call Mapping

| Prompt Variable | Builder Call |
|----------------|-------------|
| `{market_intelligence_summary}` | `build_context_summary(state, "customer_research")` |
| `{competitive_landscape_summary}` | `build_context_summary(state, "competitive_analysis")` |
| `{personas_summary}` | `build_context_summary(state, "detailed_personas")` |
| `{business_case_summary}` | `build_context_summary(state, "business_case")` |
| `{gtm_summary}` | `build_context_summary(state, "gtm_plan")` |
| `{prd_summary}` | `build_context_summary(state, "product_requirements")` |
| `{tech_arch_summary}` | `build_context_summary(state, "technical_architecture")` |
| `{regulatory_summary}` | `build_context_summary(state, "legal_regulatory_review")` |
| `{regulatory_hints}` | `build_context_summary(state, "preliminary_legal_scan", 2000)` |
| `{full_pack_summary}` | `build_full_pack_summary(state)` |
| `{cross_reference_summary}` | `build_cross_reference_summary(state)` |
| `{memory_context}` | `state.get("memory_context", "")` |

---

## Test Phase 2

1. After a completed run, call `build_context_summary(state, "customer_research")` — verify readable string under 4000 chars
2. Verify `build_full_pack_summary(state)` produces coherent multi-section output
3. Verify `build_cross_reference_summary(state)` shows tier distribution and claim counts
4. Verify truncation works correctly (no crashes on very large outputs)
5. Verify `build_context_summary` returns "Not yet available" for empty fields
