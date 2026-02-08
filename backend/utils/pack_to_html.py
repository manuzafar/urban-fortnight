#!/usr/bin/env python3
"""
Inception Pack HTML Exporter

Converts a Seedcraft inception pack (JSON state) into a beautiful HTML document.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


def _safe_get(data, *keys, default=""):
    """Safely get nested dict values."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result else default


def _to_list(data):
    """Convert data to list safely."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return list(data.values())
    return []


def generate_pack_html(state: dict, output_path: Path) -> Path:
    """Generate an HTML document from an inception pack state."""

    product_idea = state.get("product_idea", "Unknown Product")
    session_id = state.get("session_id", "N/A")

    # Cross-reference data
    cr_index = state.get("cross_reference_index", {})
    total_claims = len(cr_index.get("claims", []))
    evidence_score = cr_index.get("evidence_score", 0)
    tier_dist = cr_index.get("tier_distribution", {})

    # Executive Summary - handle None gracefully
    exec_summary = state.get("executive_summary") or {}
    recommendation = exec_summary.get("recommendation", "N/A") if isinstance(exec_summary, dict) else "N/A"

    rec_colors = {
        "BUILD": ("green", "#dcfce7", "#166534"),
        "PIVOT": ("amber", "#fef3c7", "#92400e"),
        "KILL": ("red", "#fee2e2", "#991b1b"),
    }
    rec_bg, rec_text = rec_colors.get(recommendation, ("slate", "#f1f5f9", "#475569"))[1:]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inception Pack - {product_idea[:50]}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});</script>
    <style>
        .tier-E1 {{ background-color: #dcfce7; color: #166534; }}
        .tier-E2 {{ background-color: #dbeafe; color: #1e40af; }}
        .tier-E3 {{ background-color: #fef9c3; color: #854d0e; }}
        .tier-E4 {{ background-color: #fed7aa; color: #9a3412; }}
        .tier-E5 {{ background-color: #fecaca; color: #991b1b; }}
        pre code {{ font-size: 0.85em; }}
        .section-card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    </style>
</head>
<body class="bg-slate-100 min-h-screen">
    <!-- Header -->
    <header class="bg-white border-b sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-xl font-bold text-slate-800">Seedcraft Inception Pack</h1>
                    <p class="text-sm text-slate-500">Session: {session_id}</p>
                </div>
                <div class="flex items-center gap-4">
                    <span class="px-3 py-1 rounded-full text-sm font-medium" style="background:{rec_bg}; color:{rec_text}">
                        {recommendation}
                    </span>
                    <span class="text-sm text-slate-600">{total_claims} claims | {evidence_score:.0%} evidence</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-6 py-8">

        <!-- Product Idea -->
        <div class="section-card">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Product Idea</h2>
            <p class="text-slate-700 whitespace-pre-line">{product_idea.strip()}</p>
        </div>

        <!-- Evidence Overview -->
        <div class="section-card">
            <h2 class="text-lg font-semibold text-slate-800 mb-4">Evidence Overview</h2>
            <div class="flex gap-2 flex-wrap">
                <span class="tier-E1 px-4 py-2 rounded-lg text-sm font-medium">E1 Primary: {tier_dist.get("E1", 0)}</span>
                <span class="tier-E2 px-4 py-2 rounded-lg text-sm font-medium">E2 Verified: {tier_dist.get("E2", 0)}</span>
                <span class="tier-E3 px-4 py-2 rounded-lg text-sm font-medium">E3 Industry: {tier_dist.get("E3", 0)}</span>
                <span class="tier-E4 px-4 py-2 rounded-lg text-sm font-medium">E4 Hypothesis: {tier_dist.get("E4", 0)}</span>
                <span class="tier-E5 px-4 py-2 rounded-lg text-sm font-medium">E5 Assumption: {tier_dist.get("E5", 0)}</span>
            </div>
        </div>
"""

    # Add sections
    html += _build_executive_summary(state)
    html += _build_market_intelligence(state)
    html += _build_competitive_landscape(state)
    html += _build_personas(state)
    html += _build_business_case(state)
    html += _build_gtm(state)
    html += _build_financial_model(state)
    html += _build_prd(state)
    html += _build_tech_architecture(state)
    html += _build_regulatory(state)
    html += _build_risk(state)
    html += _build_wireframes(state)
    html += _build_prototype(state)
    html += _build_stakeholders(state)
    html += _build_validation(state)
    html += _build_claims(state)

    html += f"""
    </main>

    <footer class="bg-white border-t py-6">
        <div class="max-w-6xl mx-auto px-6 text-center text-slate-500 text-sm">
            Generated by Seedcraft v3.0 | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </footer>

    <script>hljs.highlightAll();</script>
</body>
</html>
"""

    with open(output_path, "w") as f:
        f.write(html)
    return output_path


def _build_executive_summary(state: dict) -> str:
    es = state.get("executive_summary") or {}
    if not es or not isinstance(es, dict):
        return ""

    recommendation = es.get("recommendation", "N/A")
    # Try multiple field names for narrative content
    narrative = (
        es.get("narrative_summary", "") or
        es.get("executive_summary", "") or
        es.get("summary", "") or
        es.get("solution_overview", "")
    )
    # If still empty, build from problem/solution/value
    if not narrative:
        parts = []
        if es.get("problem_statement"):
            parts.append(f"**Problem:** {es['problem_statement']}")
        if es.get("solution_overview"):
            parts.append(f"**Solution:** {es['solution_overview']}")
        if es.get("value_proposition"):
            parts.append(f"**Value:** {es['value_proposition']}")
        narrative = " ".join(parts)

    key_insights = _to_list(es.get("key_insights", [])) or _to_list(es.get("key_differentiators", []))
    critical_risks = _to_list(es.get("critical_risks", [])) or _to_list(es.get("risks", []))
    next_steps = (
        _to_list(es.get("next_steps", [])) or
        _to_list(es.get("recommended_next_steps", [])) or
        _to_list(es.get("target_users", []))  # Fallback to show something useful
    )

    html = f"""
        <div class="section-card" id="executive-summary">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Executive Summary</h2>

            <div class="mb-6 p-4 bg-slate-50 rounded-lg border-l-4 border-indigo-500">
                <p class="text-slate-700">{narrative}</p>
            </div>
"""

    if key_insights:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Key Insights</h3><ul class="space-y-2">'
        for item in key_insights[:5]:
            text = item.get("insight", str(item)) if isinstance(item, dict) else str(item)
            html += f'<li class="flex gap-2"><span class="text-green-500">✓</span><span class="text-slate-700">{text}</span></li>'
        html += '</ul></div>'

    if critical_risks:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Critical Risks</h3><ul class="space-y-2">'
        for item in critical_risks[:5]:
            text = item.get("risk", str(item)) if isinstance(item, dict) else str(item)
            html += f'<li class="flex gap-2"><span class="text-red-500">⚠</span><span class="text-slate-700">{text}</span></li>'
        html += '</ul></div>'

    if next_steps:
        html += '<div><h3 class="font-semibold text-slate-800 mb-3">Next Steps</h3><ol class="list-decimal list-inside space-y-1">'
        for item in next_steps[:5]:
            text = item.get("step", item.get("action", str(item))) if isinstance(item, dict) else str(item)
            html += f'<li class="text-slate-700">{text}</li>'
        html += '</ol></div>'

    html += '</div>'
    return html


def _build_market_intelligence(state: dict) -> str:
    mi = state.get("customer_research", {})
    if not mi:
        return ""

    # Handle different market_size structures - check both market_size and market_context
    market_size = mi.get("market_size", {}) or {}
    market_context = mi.get("market_context", {}) or {}

    if isinstance(market_size, str):
        tam = market_size
        sam = som = "N/A"
    else:
        # Try market_size first, then market_context
        tam = (
            _safe_get(market_size, "tam") or
            _safe_get(market_size, "total_addressable_market") or
            _safe_get(market_context, "total_addressable_market") or
            "N/A"
        )
        sam = (
            _safe_get(market_size, "sam") or
            _safe_get(market_size, "serviceable_addressable_market") or
            _safe_get(market_context, "serviceable_addressable_market") or
            "N/A"
        )
        som = (
            _safe_get(market_size, "som") or
            _safe_get(market_size, "serviceable_obtainable_market") or
            _safe_get(market_context, "serviceable_obtainable_market") or
            "N/A"
        )

    # Truncate long market size descriptions
    if len(str(tam)) > 150:
        tam = str(tam)[:150] + "..."
    if len(str(sam)) > 150:
        sam = str(sam)[:150] + "..."
    if len(str(som)) > 150:
        som = str(som)[:150] + "..."

    pain_signals = _to_list(mi.get("pain_signals", []))
    why_now = _to_list(mi.get("why_now", [])) or _to_list(mi.get("market_timing", []))

    html = f"""
        <div class="section-card" id="market-intelligence">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Market Intelligence</h2>

            <div class="grid md:grid-cols-3 gap-4 mb-6">
                <div class="bg-indigo-50 rounded-lg p-4 text-center">
                    <div class="text-xl font-bold text-indigo-600">{tam}</div>
                    <div class="text-sm text-slate-600">Total Addressable Market</div>
                </div>
                <div class="bg-indigo-50 rounded-lg p-4 text-center">
                    <div class="text-xl font-bold text-indigo-600">{sam}</div>
                    <div class="text-sm text-slate-600">Serviceable Market</div>
                </div>
                <div class="bg-indigo-50 rounded-lg p-4 text-center">
                    <div class="text-xl font-bold text-indigo-600">{som}</div>
                    <div class="text-sm text-slate-600">Target Market</div>
                </div>
            </div>
"""

    if pain_signals:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Pain Signals</h3><div class="space-y-2">'
        for signal in pain_signals[:5]:
            if isinstance(signal, dict):
                text = signal.get("signal", signal.get("pain_point", signal.get("description", str(signal))))
            else:
                text = str(signal)
            if text:
                html += f'<div class="border-l-4 border-red-400 bg-red-50 p-3 rounded-r"><p class="text-slate-700">{text}</p></div>'
        html += '</div></div>'

    if why_now:
        html += '<div><h3 class="font-semibold text-slate-800 mb-3">Why Now?</h3><div class="grid md:grid-cols-2 gap-2">'
        for factor in why_now[:4]:
            if isinstance(factor, dict):
                text = factor.get("factor", factor.get("reason", factor.get("description", str(factor))))
            else:
                text = str(factor)
            if text:
                html += f'<div class="bg-green-50 p-3 rounded-lg text-slate-700">{text}</div>'
        html += '</div></div>'

    html += '</div>'
    return html


def _build_competitive_landscape(state: dict) -> str:
    cl = state.get("competitive_analysis", {})
    if not cl:
        return ""

    competitors = _to_list(cl.get("direct_competitors", [])) or _to_list(cl.get("competitors", []))
    differentiation = cl.get("differentiation_thesis", "") or cl.get("differentiation", "")
    positioning_map = cl.get("positioning_map", {})
    moat_analysis = cl.get("moat_analysis", {})
    competitive_gaps = _to_list(cl.get("competitive_gaps", []))

    html = f"""
        <div class="section-card" id="competitive-landscape">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Competitive Landscape</h2>
"""

    if differentiation:
        html += f'<div class="mb-6 p-4 bg-purple-50 rounded-lg border-l-4 border-purple-500"><strong>Differentiation Thesis:</strong> {differentiation}</div>'

    # Positioning Map
    if positioning_map and positioning_map.get("positions"):
        x_axis = positioning_map.get("x_axis", "X Axis")
        y_axis = positioning_map.get("y_axis", "Y Axis")
        white_space = positioning_map.get("white_space", "")
        positions = positioning_map.get("positions", [])

        html += f'''
            <div class="mb-6">
                <h3 class="font-semibold text-slate-800 mb-3">Competitive Positioning</h3>
                <div class="bg-white border rounded-lg p-4">
                    <div class="flex justify-between text-sm text-slate-500 mb-2">
                        <span>{y_axis}</span>
                    </div>
                    <div class="relative h-64 bg-slate-50 rounded border">
'''
        for pos in positions[:8]:
            x = pos.get("x_score", 5) * 10
            y = 100 - (pos.get("y_score", 5) * 10)
            name = pos.get("name", "?")[:10]
            is_us = pos.get("is_target_product", False)
            color = "indigo" if is_us else "slate"
            html += f'<div class="absolute w-3 h-3 rounded-full bg-{color}-500" style="left: {x}%; top: {y}%;" title="{name}"></div>'
            html += f'<span class="absolute text-xs text-{color}-600" style="left: {x}%; top: calc({y}% + 8px);">{name}</span>'
        html += f'''
                    </div>
                    <div class="text-center text-sm text-slate-500 mt-2">{x_axis}</div>
'''
        if white_space:
            html += f'<p class="mt-3 text-sm text-green-700 bg-green-50 p-2 rounded"><strong>White Space:</strong> {white_space}</p>'
        html += '</div></div>'

    # Competitor Table
    if competitors:
        html += '''
            <div class="overflow-x-auto mb-6">
                <table class="w-full text-sm">
                    <thead class="bg-slate-50">
                        <tr>
                            <th class="px-4 py-3 text-left font-medium text-slate-600">Competitor</th>
                            <th class="px-4 py-3 text-left font-medium text-slate-600">Strengths</th>
                            <th class="px-4 py-3 text-left font-medium text-slate-600">Weaknesses</th>
                            <th class="px-4 py-3 text-left font-medium text-slate-600">Threat</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
'''
        for comp in competitors[:6]:
            name = comp.get("name", comp.get("company", "Unknown"))
            strengths = _to_list(comp.get("strengths", []))
            weaknesses = _to_list(comp.get("weaknesses", []))
            threat = comp.get("threat_level", "")

            str_html = "".join(f"<li>{s}</li>" for s in strengths[:2]) if strengths else "-"
            weak_html = "".join(f"<li>{w}</li>" for w in weaknesses[:2]) if weaknesses else "-"

            threat_color = {"existential": "red", "significant": "orange", "moderate": "yellow", "low": "green"}.get(threat, "slate")

            html += f'''
                        <tr>
                            <td class="px-4 py-3 font-medium text-slate-800">{name}</td>
                            <td class="px-4 py-3"><ul class="list-disc list-inside text-slate-600">{str_html}</ul></td>
                            <td class="px-4 py-3"><ul class="list-disc list-inside text-slate-600">{weak_html}</ul></td>
                            <td class="px-4 py-3"><span class="px-2 py-1 rounded text-xs bg-{threat_color}-100 text-{threat_color}-700">{threat or '-'}</span></td>
                        </tr>
'''
        html += '</tbody></table></div>'

    # Moat Analysis
    if moat_analysis:
        defensible = moat_analysis.get("defensible", [])
        not_defensible = moat_analysis.get("not_defensible", [])
        strategy = moat_analysis.get("moat_building_strategy", "")

        if defensible or not_defensible or strategy:
            html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Moat Analysis</h3><div class="grid md:grid-cols-2 gap-4">'
            if defensible:
                html += '<div class="bg-green-50 rounded-lg p-4"><h4 class="font-medium text-green-800 mb-2">Defensible</h4><ul class="list-disc list-inside text-slate-700">'
                for d in defensible[:4]:
                    html += f'<li>{d}</li>'
                html += '</ul></div>'
            if not_defensible:
                html += '<div class="bg-amber-50 rounded-lg p-4"><h4 class="font-medium text-amber-800 mb-2">Not Defensible</h4><ul class="list-disc list-inside text-slate-700">'
                for d in not_defensible[:4]:
                    html += f'<li>{d}</li>'
                html += '</ul></div>'
            html += '</div>'
            if strategy:
                html += f'<p class="mt-3 text-sm text-slate-600"><strong>Strategy:</strong> {strategy}</p>'
            html += '</div>'

    # Competitive Gaps
    if competitive_gaps:
        html += '<div class="mb-4"><h3 class="font-semibold text-slate-800 mb-3">Competitive Gaps</h3><div class="space-y-2">'
        for gap in competitive_gaps[:4]:
            gap_text = gap.get("gap", str(gap) if not isinstance(gap, dict) else "")
            our_adv = gap.get("our_advantage", "")
            html += f'<div class="bg-blue-50 rounded-lg p-3"><p class="text-slate-800">{gap_text}</p>'
            if our_adv:
                html += f'<p class="text-sm text-blue-700 mt-1"><strong>Our advantage:</strong> {our_adv}</p>'
            html += '</div>'
        html += '</div></div>'

    html += '</div>'
    return html


def _build_personas(state: dict) -> str:
    personas_data = state.get("detailed_personas", {})
    if not personas_data:
        return ""

    personas = _to_list(personas_data.get("personas", []))
    secondary = _to_list(personas_data.get("secondary_personas", []))
    primary = personas_data.get("primary_persona", {})
    persona_prioritisation = personas_data.get("persona_prioritisation", {})

    all_personas = ([primary] if primary else []) + personas + secondary

    if not all_personas:
        return ""

    html = """
        <div class="section-card" id="personas">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Customer Personas</h2>
"""

    # Persona prioritisation summary if available
    if persona_prioritisation:
        html += '<div class="mb-6 p-4 bg-indigo-50 rounded-lg grid md:grid-cols-3 gap-4">'
        for role, label in [("primary_buyer", "Primary Buyer"), ("primary_user", "Primary User"), ("primary_champion", "Internal Champion")]:
            val = persona_prioritisation.get(role, "")
            if val:
                html += f'<div><span class="text-xs font-medium text-indigo-600 uppercase">{label}</span><p class="text-slate-800 font-medium">{val}</p></div>'
        html += '</div>'

    html += '<div class="grid md:grid-cols-2 gap-4">'

    for persona in all_personas[:4]:
        if not persona:
            continue
        name = persona.get("name", "Unknown")
        role = persona.get("role", persona.get("title", ""))
        archetype = persona.get("archetype", "")
        goals = _to_list(persona.get("goals", [])) or _to_list(persona.get("jobs_to_be_done", []))
        pains = _to_list(persona.get("pain_points", [])) or _to_list(persona.get("frustrations", []))
        jtbd = _to_list(persona.get("jobs_to_be_done", []))
        # Support both nested and flat structures
        buying = persona.get("buying_behaviour", {})
        if not buying:
            # Flat structure
            buying = {
                "decision_authority": persona.get("decision_authority", ""),
                "discovery_channels": persona.get("discovery_channels", []),
                "evaluation_criteria": persona.get("evaluation_criteria", []),
                "typical_procurement_timeline": persona.get("procurement_timeline", ""),
                "procurement_blockers": persona.get("procurement_blockers", []),
            }
        politics = persona.get("internal_politics", {})
        if not politics:
            # Flat structure
            politics = {
                "champions_what": persona.get("champions_what", ""),
                "blockers": persona.get("internal_blockers", []),
            }

        html += f'''
                <div class="bg-slate-50 rounded-lg p-4">
                    <div class="flex items-center gap-3 mb-3">
                        <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">👤</div>
                        <div>
                            <h3 class="font-semibold text-slate-800">{name}</h3>
                            <p class="text-sm text-slate-500">{role}</p>
'''
        if archetype:
            html += f'<p class="text-xs text-indigo-600 italic">{archetype}</p>'
        html += '</div></div>'

        # Goals section
        if goals:
            html += '<div class="mb-2"><p class="text-xs font-medium text-slate-500 uppercase mb-1">Goals</p><ul class="text-sm space-y-1">'
            for g in goals[:3]:
                text = g.get("goal", g.get("job", str(g))) if isinstance(g, dict) else str(g)
                html += f'<li class="text-slate-700">• {text}</li>'
            html += '</ul></div>'

        # Jobs to be Done - support both nested dict and flat string formats
        if jtbd:
            html += '<div class="mb-2"><p class="text-xs font-medium text-slate-500 uppercase mb-1">Jobs to be Done</p>'
            for j in jtbd[:2]:
                if isinstance(j, dict) and j.get("situation"):
                    # Nested structure
                    situation = j.get("situation", "")
                    motivation = j.get("motivation", "")
                    outcome = j.get("outcome", "")
                    pain_level = j.get("pain_level", "")
                    html += f'<div class="text-sm text-slate-700 mb-1 bg-white p-2 rounded">'
                    html += f'<span class="text-slate-500">When</span> {situation} <span class="text-slate-500">I want to</span> {motivation}'
                    if outcome:
                        html += f' <span class="text-slate-500">so that</span> {outcome}'
                    if pain_level:
                        color = {"critical": "red", "high": "orange", "moderate": "amber", "low": "green"}.get(pain_level, "slate")
                        html += f' <span class="ml-2 px-1 rounded text-xs bg-{color}-100 text-{color}-700">{pain_level}</span>'
                    html += '</div>'
                else:
                    # Flat string format: "When [situation], I want to [action] so that [outcome]"
                    text = str(j) if not isinstance(j, dict) else j.get("job", str(j))
                    html += f'<div class="text-sm text-slate-700 mb-1 bg-white p-2 rounded">{text}</div>'
            html += '</div>'

        # Pain points
        if pains:
            html += '<div class="mb-2"><p class="text-xs font-medium text-slate-500 uppercase mb-1">Pain Points</p><ul class="text-sm space-y-1">'
            for p in pains[:3]:
                text = p.get("pain", str(p)) if isinstance(p, dict) else str(p)
                html += f'<li class="text-red-600">• {text}</li>'
            html += '</ul></div>'

        # Buying behaviour (collapsed for space)
        if buying and isinstance(buying, dict):
            decision_auth = buying.get("decision_authority", "")
            timeline = buying.get("typical_procurement_timeline", "")
            if decision_auth or timeline:
                html += f'<div class="mb-2 text-xs"><span class="font-medium text-slate-500">Buying:</span>'
                if decision_auth:
                    html += f' <span class="text-slate-700">{decision_auth.replace("_", " ").title()}</span>'
                if timeline:
                    html += f' • <span class="text-slate-500">Timeline:</span> {timeline}'
                html += '</div>'

        # Internal politics (collapsed for space)
        if politics and isinstance(politics, dict):
            champions = politics.get("champions_what", "")
            blockers = _to_list(politics.get("blockers", []))
            if champions or blockers:
                html += f'<div class="text-xs text-slate-600 bg-amber-50 p-2 rounded">'
                if champions:
                    html += f'<span class="font-medium">Champions:</span> {champions[:80]}... '
                if blockers:
                    html += f'<span class="font-medium">Blockers:</span> {", ".join(str(b) for b in blockers[:2])}'
                html += '</div>'

        html += '</div>'

    html += '</div></div>'
    return html


def _build_business_case(state: dict) -> str:
    bc = state.get("business_case", {})
    if not bc:
        return ""

    # Get lean canvas data
    lean_canvas = bc.get("lean_canvas", {}) or {}

    # Try multiple sources for value proposition
    value_prop = (
        bc.get("value_proposition", "") or
        lean_canvas.get("unique_value_proposition", "") or
        lean_canvas.get("value_proposition", "")
    )

    unit_economics = bc.get("unit_economics", {})
    year1 = bc.get("year_1_projection", "")
    year3 = bc.get("year_3_projection", "")
    break_even = bc.get("break_even_analysis", "")

    html = f"""
        <div class="section-card" id="business-case">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Business Case</h2>
"""

    if value_prop:
        html += f'<div class="mb-6 p-4 bg-green-50 rounded-lg border-l-4 border-green-500"><strong>Value Proposition:</strong> {value_prop}</div>'

    # Show Lean Canvas if available
    if lean_canvas:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Lean Canvas</h3><div class="grid md:grid-cols-3 gap-4">'
        lc_fields = [
            ("problem", "Problem"),
            ("solution", "Solution"),
            ("unfair_advantage", "Unfair Advantage"),
            ("customer_segments", "Customer Segments"),
            ("channels", "Channels"),
            ("key_metrics", "Key Metrics"),
        ]
        for key, label in lc_fields:
            val = lean_canvas.get(key, "")
            if val:
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val[:3])
                html += f'<div class="bg-slate-50 rounded-lg p-3"><h4 class="text-sm font-medium text-slate-600 mb-1">{label}</h4><p class="text-slate-800 text-sm">{str(val)[:150]}</p></div>'
        html += '</div></div>'

    # Show projections if available
    if year1 or year3:
        html += '<div class="grid md:grid-cols-2 gap-4">'
        if year1:
            html += f'<div class="bg-indigo-50 rounded-lg p-4"><h4 class="font-medium text-indigo-800 mb-2">Year 1 Projection</h4><p class="text-slate-700 text-sm">{str(year1)[:300]}</p></div>'
        if year3:
            html += f'<div class="bg-indigo-50 rounded-lg p-4"><h4 class="font-medium text-indigo-800 mb-2">Year 3 Projection</h4><p class="text-slate-700 text-sm">{str(year3)[:300]}</p></div>'
        html += '</div>'

    if break_even:
        html += f'<div class="mt-4 p-3 bg-amber-50 rounded-lg"><strong>Break-even:</strong> {str(break_even)[:200]}</div>'

    # Show unit economics if available
    if unit_economics and isinstance(unit_economics, dict) and unit_economics.keys():
        # Assessment badge if available
        assessment = unit_economics.get("assessment", "")
        if assessment:
            colors = {"healthy": ("green", "✓"), "warning": ("amber", "!"), "unhealthy": ("red", "✗")}
            color, icon = colors.get(assessment, ("slate", "?"))
            html += f'<div class="mb-4 inline-block px-4 py-2 bg-{color}-50 rounded-lg"><span class="font-medium text-{color}-800">{icon} Unit Economics: {assessment.upper()}</span></div>'

        html += '<div class="grid md:grid-cols-4 gap-4 mt-4">'
        metrics = [("cac", "CAC"), ("ltv", "LTV"), ("ltv_cac_ratio", "LTV:CAC"), ("payback_period_months", "Payback (months)")]
        for key, label in metrics:
            val = unit_economics.get(key, unit_economics.get("payback_period", "N/A") if key == "payback_period_months" else "N/A")
            if isinstance(val, dict):
                val = val.get("value", str(val))
            html += f'<div class="bg-slate-50 rounded-lg p-4 text-center"><div class="text-xl font-bold text-slate-800">{val}</div><div class="text-sm text-slate-600">{label}</div></div>'
        html += '</div>'

        # Gross margin if available
        gross_margin = unit_economics.get("gross_margin_percent")
        if gross_margin:
            html += f'<div class="mt-3 text-sm text-slate-600">Gross Margin: {gross_margin}%</div>'

    # Sensitivity analysis if available
    sensitivity = bc.get("sensitivity_analysis", {})
    if sensitivity and isinstance(sensitivity, dict):
        html += '<div class="mt-6"><h3 class="font-semibold text-slate-800 mb-3">Sensitivity Analysis</h3><div class="grid md:grid-cols-3 gap-4">'
        for case_name in ["base_case", "optimistic_case", "pessimistic_case"]:
            case = sensitivity.get(case_name, {})
            if case:
                label = case_name.replace("_", " ").title()
                y1_rev = case.get("year_1_revenue", "N/A")
                y3_rev = case.get("year_3_revenue", "N/A")
                color = "green" if case_name == "optimistic_case" else ("red" if case_name == "pessimistic_case" else "blue")
                html += f'<div class="bg-{color}-50 rounded-lg p-4"><h4 class="font-medium text-{color}-800 mb-2">{label}</h4><div class="text-sm text-slate-700"><div>Y1 Revenue: {y1_rev}</div><div>Y3 Revenue: {y3_rev}</div></div></div>'
        html += '</div>'

        kill_conditions = sensitivity.get("kill_conditions", "")
        if kill_conditions:
            html += f'<div class="mt-3 p-3 bg-red-50 rounded-lg border-l-4 border-red-500"><strong class="text-red-800">Kill Conditions:</strong> <span class="text-slate-700">{kill_conditions}</span></div>'
        html += '</div>'

    html += '</div>'
    return html


def _build_gtm(state: dict) -> str:
    gtm = state.get("gtm_plan", {})
    if not gtm:
        return ""

    # Get market entry strategy - format if dict
    entry_strategy_raw = gtm.get("market_entry_strategy", "")
    if isinstance(entry_strategy_raw, dict):
        parts = []
        if entry_strategy_raw.get("approach"):
            parts.append(f"<strong>Approach:</strong> {entry_strategy_raw['approach']}")
        if entry_strategy_raw.get("initial_segment"):
            parts.append(f"<strong>Initial Segment:</strong> {entry_strategy_raw['initial_segment']}")
        if entry_strategy_raw.get("beachhead_market"):
            parts.append(f"<strong>Beachhead Market:</strong> {entry_strategy_raw['beachhead_market']}")
        expansion = entry_strategy_raw.get("expansion_path", [])
        if expansion:
            parts.append(f"<strong>Expansion Path:</strong> {', '.join(expansion[:3])}")
        entry_strategy = " | ".join(parts)
    else:
        entry_strategy = str(entry_strategy_raw)[:500] if entry_strategy_raw else ""

    # Get channel strategy - handle both dict and list formats
    channel_data = gtm.get("channel_strategy", {})
    if isinstance(channel_data, dict):
        channels = channel_data.get("primary_channels", [])
        channel_rationale = channel_data.get("channel_mix_rationale", "")
    else:
        channels = _to_list(channel_data)
        channel_rationale = ""

    # Get launch plan
    launch_plan = gtm.get("launch_plan", {})
    phases = launch_plan.get("phases", []) if isinstance(launch_plan, dict) else _to_list(gtm.get("launch_phases", []))

    # Get growth tactics
    growth_tactics = _to_list(gtm.get("growth_tactics", []))

    html = f"""
        <div class="section-card" id="gtm">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Go-to-Market Strategy</h2>
"""

    if entry_strategy:
        html += f'<div class="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">{str(entry_strategy)[:500]}</div>'

    # Channel Strategy Table
    if channels:
        html += '''
            <div class="mb-6">
                <h3 class="font-semibold text-slate-800 mb-3">Channel Strategy</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-slate-50">
                            <tr>
                                <th class="px-4 py-3 text-left font-medium text-slate-600">Channel</th>
                                <th class="px-4 py-3 text-left font-medium text-slate-600">Role</th>
                                <th class="px-4 py-3 text-left font-medium text-slate-600">Expected CAC</th>
                                <th class="px-4 py-3 text-left font-medium text-slate-600">Time to Scale</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-200">
'''
        for ch in channels[:8]:
            if isinstance(ch, dict):
                name = ch.get("channel", ch.get("name", ""))
                role = ch.get("role", "")
                cac = ch.get("expected_cac", "")
                time = ch.get("time_to_scale", "")
                html += f'<tr><td class="px-4 py-3 font-medium text-slate-800">{name}</td><td class="px-4 py-3 text-slate-600">{role}</td><td class="px-4 py-3 text-green-600">{cac}</td><td class="px-4 py-3 text-slate-600">{time}</td></tr>'
            else:
                html += f'<tr><td class="px-4 py-3 text-slate-800" colspan="4">{str(ch)}</td></tr>'
        html += '</tbody></table></div>'
        if channel_rationale:
            html += f'<p class="mt-3 text-sm text-slate-600 italic">{channel_rationale[:300]}</p>'
        html += '</div>'

    # Launch Phases
    if phases:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Launch Plan</h3><div class="space-y-3">'
        for i, phase in enumerate(phases[:5]):
            if isinstance(phase, dict):
                name = phase.get("phase_name", phase.get("phase", phase.get("name", f"Phase {i+1}")))
                duration = phase.get("duration", "")
                goals = phase.get("key_objectives", phase.get("goals", []))
                activities = phase.get("key_activities", phase.get("activities", []))
                html += f'<div class="border rounded-lg p-4"><div class="flex justify-between items-center mb-2"><h4 class="font-medium text-slate-800">{name}</h4>'
                if duration:
                    html += f'<span class="text-sm text-slate-500">{duration}</span>'
                html += '</div>'
                if goals:
                    goals_list = goals if isinstance(goals, list) else [goals]
                    html += '<ul class="list-disc list-inside text-sm text-slate-600">'
                    for g in goals_list[:3]:
                        html += f'<li>{g}</li>'
                    html += '</ul>'
                html += '</div>'
            else:
                html += f'<div class="border rounded-lg p-4"><p class="text-slate-700">{str(phase)}</p></div>'
        html += '</div></div>'

    # Growth Tactics
    if growth_tactics:
        html += '<div><h3 class="font-semibold text-slate-800 mb-3">Growth Tactics</h3><div class="grid md:grid-cols-2 gap-3">'
        for tactic in growth_tactics[:6]:
            if isinstance(tactic, dict):
                name = tactic.get("tactic", tactic.get("name", ""))
                desc = tactic.get("description", "")
                html += f'<div class="bg-slate-50 rounded-lg p-3"><h4 class="font-medium text-slate-800">{name}</h4><p class="text-sm text-slate-600">{str(desc)[:150]}</p></div>'
            else:
                html += f'<div class="bg-slate-50 rounded-lg p-3 text-slate-700">{str(tactic)[:200]}</div>'
        html += '</div></div>'

    html += '</div>'
    return html


def _build_financial_model(state: dict) -> str:
    fm = state.get("financial_model", {})
    if not fm:
        return ""

    projections = _to_list(fm.get("monthly_projections_year_1", []))
    funding = fm.get("funding_requirements", {})

    html = """
        <div class="section-card" id="financial-model">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Financial Model</h2>
"""

    if projections:
        html += '''
            <div class="mb-6">
                <h3 class="font-semibold text-slate-800 mb-3">12-Month Projections</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-slate-50">
                            <tr>
                                <th class="px-3 py-2 text-left">Month</th>
                                <th class="px-3 py-2 text-right">Revenue</th>
                                <th class="px-3 py-2 text-right">Costs</th>
                                <th class="px-3 py-2 text-right">Customers</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-200">
'''
        for proj in projections[:12]:
            month = proj.get("month", "")
            revenue = proj.get("revenue", proj.get("mrr", ""))
            costs = proj.get("total_costs", proj.get("costs", ""))
            customers = proj.get("customers", proj.get("active_customers", ""))
            html += f'<tr><td class="px-3 py-2">{month}</td><td class="px-3 py-2 text-right text-green-600">{revenue}</td><td class="px-3 py-2 text-right text-red-600">{costs}</td><td class="px-3 py-2 text-right">{customers}</td></tr>'
        html += '</tbody></table></div></div>'

    if funding:
        total = funding.get("total_required", funding.get("amount", "N/A"))
        html += f'<div class="bg-amber-50 rounded-lg p-4"><h3 class="font-semibold text-slate-800">Funding Required</h3><p class="text-2xl font-bold text-amber-600">{total}</p></div>'

    html += '</div>'
    return html


def _build_prd(state: dict) -> str:
    prd = state.get("product_requirements", {})
    if not prd:
        return ""

    product_name = prd.get("product_name", "")
    epics = _to_list(prd.get("epics", []))

    html = f"""
        <div class="section-card" id="prd">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Product Requirements</h2>
            {"<p class='text-lg text-indigo-600 mb-4'>" + product_name + "</p>" if product_name else ""}
"""

    if epics:
        html += '<div class="space-y-4">'
        for epic in epics[:5]:
            title = epic.get("title", epic.get("name", ""))
            stories = _to_list(epic.get("stories", []))

            html += f'<div class="border rounded-lg p-4"><h3 class="font-semibold text-slate-800 mb-3">{title}</h3>'
            if stories:
                html += '<div class="space-y-2">'
                for story in stories[:5]:
                    sid = story.get("id", story.get("story_id", ""))
                    stitle = story.get("title", "")
                    priority = story.get("priority", "medium")
                    pcolor = "red" if priority in ["critical", "high"] else "amber" if priority == "medium" else "slate"
                    html += f'<div class="flex items-center gap-2 text-sm"><span class="text-slate-400">{sid}</span><span class="text-slate-700 flex-1">{stitle}</span><span class="px-2 py-0.5 rounded text-xs bg-{pcolor}-100 text-{pcolor}-700">{priority}</span></div>'
                html += '</div>'
            html += '</div>'
        html += '</div>'

    html += '</div>'
    return html


def _build_tech_architecture(state: dict) -> str:
    ta = state.get("technical_architecture", {})
    if not ta:
        return ""

    arch_style = ta.get("architecture_style", ta.get("architecture_pattern", ""))
    arch_desc = ta.get("architecture_diagram_description", "")
    arch_mermaid = ta.get("architecture_diagram_mermaid", "")
    seq_mermaid = ta.get("sequence_diagram_mermaid", "")
    tech_stack = _to_list(ta.get("tech_stack", [])) or _to_list(ta.get("technology_stack", []))
    components = _to_list(ta.get("system_components", []))
    integrations = _to_list(ta.get("integration_points", []))
    security = ta.get("security_architecture", {})

    html = f"""
        <div class="section-card" id="tech-architecture">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Technical Architecture</h2>
"""

    if arch_style:
        html += f'<div class="mb-4 p-4 bg-indigo-50 rounded-lg border-l-4 border-indigo-500"><strong>Architecture Style:</strong> {str(arch_style)}</div>'

    if arch_desc:
        html += f'<p class="text-slate-700 mb-6">{str(arch_desc)[:500]}</p>'

    # Architecture Diagram (Mermaid)
    if arch_mermaid:
        html += f'''
            <div class="mb-6">
                <h3 class="font-semibold text-slate-800 mb-3">System Architecture</h3>
                <div class="bg-white border rounded-lg p-4">
                    <div class="mermaid">{arch_mermaid}</div>
                </div>
            </div>
'''

    # System Components
    if components:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">System Components</h3><div class="grid md:grid-cols-2 gap-4">'
        for comp in components[:8]:
            if isinstance(comp, dict):
                name = comp.get("component_name", comp.get("name", ""))
                purpose = comp.get("purpose", comp.get("description", ""))
                tech = comp.get("technology", "")
                html += f'<div class="border rounded-lg p-4"><h4 class="font-medium text-slate-800">{name}</h4><p class="text-sm text-slate-600 mt-1">{str(purpose)[:150]}</p>'
                if tech:
                    html += f'<span class="inline-block mt-2 px-2 py-1 bg-slate-100 rounded text-xs text-slate-600">{tech}</span>'
                html += '</div>'
            else:
                html += f'<div class="border rounded-lg p-4 text-slate-700">{str(comp)[:200]}</div>'
        html += '</div></div>'

    # Tech Stack
    if tech_stack:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Technology Stack</h3><div class="flex flex-wrap gap-2">'
        for tech in tech_stack[:15]:
            name = tech.get("technology", tech.get("name", str(tech))) if isinstance(tech, dict) else str(tech)
            html += f'<span class="px-3 py-1 bg-indigo-100 rounded-full text-sm text-indigo-700">{name}</span>'
        html += '</div></div>'

    # Integration Points
    if integrations:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">Integration Points</h3><div class="space-y-2">'
        for integ in integrations[:6]:
            if isinstance(integ, dict):
                name = integ.get("integration_name", integ.get("name", ""))
                system = integ.get("external_system", integ.get("system", ""))
                purpose = integ.get("purpose", "")
                html += f'<div class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg"><span class="font-medium text-slate-800">{name}</span><span class="text-slate-400">→</span><span class="text-slate-600">{system}</span></div>'
            else:
                html += f'<div class="p-3 bg-slate-50 rounded-lg text-slate-700">{str(integ)[:150]}</div>'
        html += '</div></div>'

    # Security Architecture
    if security and isinstance(security, dict):
        html += '<div><h3 class="font-semibold text-slate-800 mb-3">Security Architecture</h3><div class="grid md:grid-cols-2 gap-3">'
        security_fields = [("authentication", "Authentication"), ("authorization", "Authorization"), ("data_encryption", "Encryption"), ("audit_logging", "Audit Logging")]
        for key, label in security_fields:
            val = security.get(key, "")
            if val:
                html += f'<div class="bg-green-50 rounded-lg p-3"><h4 class="text-sm font-medium text-green-800">{label}</h4><p class="text-sm text-slate-700">{str(val)[:150]}</p></div>'
        html += '</div></div>'

    html += '</div>'
    return html


def _build_regulatory(state: dict) -> str:
    reg = state.get("legal_regulatory_review", {})
    if not reg:
        return ""

    regulations = _to_list(reg.get("applicable_regulations", [])) or _to_list(reg.get("regulations", []))
    risk_assessment = reg.get("overall_risk_assessment", {})
    risk_level = risk_assessment.get("risk_level", "medium") if isinstance(risk_assessment, dict) else "medium"

    color = "red" if risk_level == "high" else "amber" if risk_level == "medium" else "green"

    html = f"""
        <div class="section-card" id="regulatory">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Regulatory & Compliance</h2>
            <div class="mb-4 px-4 py-2 bg-{color}-50 rounded-lg inline-block">
                <span class="font-medium text-{color}-800">Risk Level: {str(risk_level).upper()}</span>
            </div>
"""

    if regulations:
        html += '<div class="space-y-2">'
        for r in regulations[:6]:
            name = r.get("regulation", r.get("name", str(r))) if isinstance(r, dict) else str(r)
            html += f'<div class="border-l-4 border-indigo-400 bg-indigo-50 p-3 rounded-r text-slate-700">{name}</div>'
        html += '</div>'

    html += '</div>'
    return html


def _build_risk(state: dict) -> str:
    ra = state.get("risk_assessment", {})
    if not ra:
        return ""

    risks = _to_list(ra.get("risks", [])) or _to_list(ra.get("identified_risks", []))
    overall = ra.get("overall_risk_level", ra.get("overall_level", "medium"))

    color = "red" if overall == "high" else "amber" if overall == "medium" else "green"

    html = f"""
        <div class="section-card" id="risk">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Risk Assessment</h2>
            <div class="mb-4 px-4 py-2 bg-{color}-50 rounded-lg inline-block">
                <span class="font-medium text-{color}-800">Overall: {str(overall).upper()}</span>
            </div>
"""

    if risks:
        html += '<div class="space-y-3">'
        for risk in risks[:8]:
            title = risk.get("risk", risk.get("title", risk.get("name", str(risk)))) if isinstance(risk, dict) else str(risk)
            mitigation = risk.get("mitigation", risk.get("mitigation_strategy", "")) if isinstance(risk, dict) else ""
            html += f'<div class="border rounded-lg p-4"><h4 class="font-medium text-slate-800">{title}</h4>'
            if mitigation:
                html += f'<p class="text-sm text-slate-600 mt-2"><strong>Mitigation:</strong> {mitigation}</p>'
            html += '</div>'
        html += '</div>'

    html += '</div>'
    return html


def _build_wireframes(state: dict) -> str:
    wf = state.get("wireframes", {})
    if not wf:
        return ""

    screens = _to_list(wf.get("screens", []))
    user_flow = wf.get("user_flow_description", "")
    user_flow_mermaid = wf.get("user_flow_mermaid", "")
    user_flows = _to_list(wf.get("user_flows", []))

    html = f"""
        <div class="section-card" id="wireframes">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Wireframes</h2>
            {"<p class='text-slate-600 mb-4'>" + user_flow + "</p>" if user_flow else ""}
"""

    # User Flow Diagrams (new format with multiple flows)
    if user_flows:
        html += '<div class="mb-6"><h3 class="font-semibold text-slate-800 mb-3">User Flows</h3><div class="space-y-4">'
        for flow in user_flows[:5]:
            flow_name = flow.get("flow_name", "User Flow")
            persona = flow.get("persona", "")
            mermaid_code = flow.get("mermaid_code", "")
            screens_ref = flow.get("screens_referenced", [])
            notes = flow.get("notes", "")

            html += f'''
                <div class="bg-white border rounded-lg p-4">
                    <div class="flex justify-between items-center mb-3">
                        <h4 class="font-medium text-slate-800">{flow_name}</h4>
                        {"<span class='text-sm text-slate-500'>Persona: " + persona + "</span>" if persona else ""}
                    </div>
'''
            if mermaid_code:
                html += f'<div class="mermaid">{mermaid_code}</div>'
            if screens_ref:
                html += '<div class="mt-2 flex gap-1">'
                for sid in screens_ref:
                    html += f'<span class="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded text-xs">{sid}</span>'
                html += '</div>'
            if notes:
                html += f'<p class="mt-2 text-sm text-slate-600 italic">{notes}</p>'
            html += '</div>'
        html += '</div></div>'

    # Legacy: Single user flow diagram
    elif user_flow_mermaid:
        html += f'''
            <div class="mb-6">
                <h3 class="font-semibold text-slate-800 mb-3">User Flow</h3>
                <div class="bg-white border rounded-lg p-4 overflow-x-auto">
                    <div class="mermaid">{user_flow_mermaid}</div>
                </div>
            </div>
'''

    html += '<div class="grid md:grid-cols-2 gap-6">'

    for i, screen in enumerate(screens[:8]):
        sid = screen.get("screen_id", f"S{i+1}")
        name = screen.get("screen_name", "")
        purpose = screen.get("purpose", "")
        code = screen.get("react_code", "")
        components = _to_list(screen.get("key_components", []))

        # Create a sandboxed iframe to render the React component
        # Escape the code for embedding in JS template literal (backticks)
        # Only escape: backslashes, backticks, and ${} template expressions
        code_for_iframe = code.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

        html += f'''
                <div class="border rounded-lg overflow-hidden bg-white">
                    <div class="bg-slate-100 px-4 py-2 border-b flex justify-between items-center">
                        <div>
                            <span class="font-mono text-sm text-slate-500">{sid}</span>
                            <span class="font-medium text-slate-800 ml-2">{name}</span>
                        </div>
                    </div>
                    <div class="p-4">
                        <p class="text-sm text-slate-600 mb-3">{purpose}</p>
'''

        # Key components list
        if components:
            html += '<div class="mb-3"><p class="text-xs font-medium text-slate-500 uppercase mb-1">Components</p><div class="flex flex-wrap gap-1">'
            for comp in components[:5]:
                comp_name = comp.get("component", str(comp)) if isinstance(comp, dict) else str(comp)
                html += f'<span class="px-2 py-0.5 bg-slate-100 rounded text-xs text-slate-600">{comp_name}</span>'
            html += '</div></div>'

        # Rendered wireframe in iframe
        if code:
            iframe_id = f"wireframe-{sid}"
            # Extract the function name from the code
            func_match = re.search(r'function\s+([A-Z][a-zA-Z0-9]*)', code)
            const_match = re.search(r'const\s+([A-Z][a-zA-Z0-9]*)\s*=', code)
            component_name = func_match.group(1) if func_match else (const_match.group(1) if const_match else "Component")

            # Clean up the code for browser execution:
            # 1. Remove import statements (lucide-react icons are provided globally)
            # 2. Convert "export default function X" to "function X"
            # 3. Convert "export default X" to nothing (component already defined)
            cleaned_code = re.sub(r'^import\s+.*?[\'"].*?[\'"];?\s*$', '', code, flags=re.MULTILINE)
            cleaned_code = re.sub(r'export\s+default\s+function\s+', 'function ', cleaned_code)
            cleaned_code = re.sub(r'export\s+default\s+\w+;?\s*$', '', cleaned_code, flags=re.MULTILINE)
            cleaned_code_for_iframe = cleaned_code.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

            html += f'''
                        <div class="border rounded-lg overflow-hidden bg-gray-50">
                            <iframe id="{iframe_id}" class="w-full" style="height: 300px; border: none;"></iframe>
                        </div>
                        <script>
                            (function() {{
                                const code = `{cleaned_code_for_iframe}`;
                                const componentName = "{component_name}";
                                const iframe = document.getElementById("{iframe_id}");
                                const doc = iframe.contentDocument || iframe.contentWindow.document;
                                doc.open();
                                doc.write(`
                                    <!DOCTYPE html>
                                    <html>
                                    <head>
                                        <script src="https://unpkg.com/react@18/umd/react.development.js"><\\/script>
                                        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"><\\/script>
                                        <script src="https://unpkg.com/@babel/standalone/babel.min.js"><\\/script>
                                        <script src="https://cdn.tailwindcss.com"><\\/script>
                                        <style>body {{ margin: 0; padding: 8px; font-family: system-ui, sans-serif; background: #f9fafb; }} .error {{ color: #991b1b; background: #fee2e2; padding: 16px; border-radius: 8px; }}</style>
                                    </head>
                                    <body>
                                        <div id="root"></div>
                                        <script type="text/babel">
                                            // Simple SVG icon components (Lucide-style)
                                            const createIcon = (paths) => ({{ className, ...props }}) =>
                                                React.createElement('svg', {{
                                                    xmlns: 'http://www.w3.org/2000/svg',
                                                    width: 24, height: 24, viewBox: '0 0 24 24',
                                                    fill: 'none', stroke: 'currentColor', strokeWidth: 2,
                                                    strokeLinecap: 'round', strokeLinejoin: 'round',
                                                    className, ...props
                                                }}, ...paths.map((d, i) => React.createElement('path', {{ key: i, d }})));

                                            const Search = createIcon(['M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z']);
                                            const Bell = createIcon(['M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9', 'M13.73 21a2 2 0 01-3.46 0']);
                                            const Settings = createIcon(['M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42']);
                                            const Plus = createIcon(['M12 5v14', 'M5 12h14']);
                                            const Filter = createIcon(['M22 3H2l8 9.46V19l4 2v-8.54L22 3z']);
                                            const BarChart3 = createIcon(['M18 20V10', 'M12 20V4', 'M6 20v-6']);
                                            const ChevronRight = createIcon(['M9 18l6-6-6-6']);
                                            const ChevronDown = createIcon(['M6 9l6 6 6-6']);
                                            const ChevronUp = createIcon(['M18 15l-6-6-6 6']);
                                            const ChevronLeft = createIcon(['M15 18l-6-6 6-6']);
                                            const AlertTriangle = createIcon(['M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z', 'M12 9v4', 'M12 17h.01']);
                                            const TrendingUp = createIcon(['M23 6l-9.5 9.5-5-5L1 18']);
                                            const TrendingDown = createIcon(['M23 18l-9.5-9.5-5 5L1 6']);
                                            const ArrowRight = createIcon(['M5 12h14', 'M12 5l7 7-7 7']);
                                            const ArrowLeft = createIcon(['M19 12H5', 'M12 19l-7-7 7-7']);
                                            const Check = createIcon(['M20 6L9 17l-5-5']);
                                            const X = createIcon(['M18 6L6 18', 'M6 6l12 12']);
                                            const Menu = createIcon(['M3 12h18', 'M3 6h18', 'M3 18h18']);
                                            const Home = createIcon(['M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z']);
                                            const User = createIcon(['M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2', 'M12 3a4 4 0 100 8 4 4 0 000-8z']);
                                            const Users = createIcon(['M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2', 'M23 21v-2a4 4 0 00-3-3.87', 'M16 3.13a4 4 0 010 7.75', 'M9 7a4 4 0 100 8 4 4 0 000-8z']);
                                            const Mail = createIcon(['M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z', 'M22 6l-10 7L2 6']);
                                            const Calendar = createIcon(['M19 4H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2z', 'M16 2v4', 'M8 2v4', 'M3 10h18']);
                                            const Clock = createIcon(['M12 2a10 10 0 100 20 10 10 0 000-20z', 'M12 6v6l4 2']);
                                            const Edit = createIcon(['M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7', 'M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z']);
                                            const Trash = createIcon(['M3 6h18', 'M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2']);
                                            const Save = createIcon(['M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z', 'M17 21v-8H7v8', 'M7 3v5h8']);
                                            const Download = createIcon(['M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4', 'M7 10l5 5 5-5', 'M12 15V3']);
                                            const Upload = createIcon(['M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4', 'M17 8l-5-5-5 5', 'M12 3v12']);
                                            const RefreshCw = createIcon(['M23 4v6h-6', 'M1 20v-6h6', 'M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15']);
                                            const Eye = createIcon(['M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z', 'M12 9a3 3 0 100 6 3 3 0 000-6z']);
                                            const Info = createIcon(['M12 2a10 10 0 100 20 10 10 0 000-20z', 'M12 16v-4', 'M12 8h.01']);
                                            const AlertCircle = createIcon(['M12 2a10 10 0 100 20 10 10 0 000-20z', 'M12 8v4', 'M12 16h.01']);
                                            const CheckCircle = createIcon(['M22 11.08V12a10 10 0 11-5.93-9.14', 'M22 4L12 14.01l-3-3']);
                                            const DollarSign = createIcon(['M12 1v22', 'M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6']);
                                            const CreditCard = createIcon(['M21 4H3a2 2 0 00-2 2v12a2 2 0 002 2h18a2 2 0 002-2V6a2 2 0 00-2-2z', 'M1 10h22']);
                                            const PieChart = createIcon(['M21.21 15.89A10 10 0 118 2.83', 'M22 12A10 10 0 0012 2v10z']);
                                            const LineChart = createIcon(['M23 6l-9.5 9.5-5-5L1 18']);
                                            const Activity = createIcon(['M22 12h-4l-3 9L9 3l-3 9H2']);
                                            const Zap = createIcon(['M13 2L3 14h9l-1 8 10-12h-9l1-8z']);
                                            const Wallet = createIcon(['M21 5H3a2 2 0 00-2 2v10a2 2 0 002 2h18a2 2 0 002-2V7a2 2 0 00-2-2z', 'M1 10h22']);
                                            const Phone = createIcon(['M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z']);
                                            const Star = createIcon(['M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z']);
                                            const Heart = createIcon(['M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z']);
                                            const ExternalLink = createIcon(['M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6', 'M15 3h6v6', 'M10 14L21 3']);
                                            const Link = createIcon(['M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71', 'M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71']);
                                            const MoreHorizontal = createIcon(['M12 13a1 1 0 100-2 1 1 0 000 2z', 'M19 13a1 1 0 100-2 1 1 0 000 2z', 'M5 13a1 1 0 100-2 1 1 0 000 2z']);
                                            const Loader = createIcon(['M12 2v4', 'M12 18v4', 'M4.93 4.93l2.83 2.83', 'M16.24 16.24l2.83 2.83', 'M2 12h4', 'M18 12h4', 'M4.93 19.07l2.83-2.83', 'M16.24 7.76l2.83-2.83']);
                                            const Play = createIcon(['M5 3l14 9-14 9V3z']);
                                            const Pause = createIcon(['M6 4h4v16H6z', 'M14 4h4v16h-4z']);
                                            const Copy = createIcon(['M20 9h-9a2 2 0 00-2 2v9a2 2 0 002 2h9a2 2 0 002-2v-9a2 2 0 00-2-2z', 'M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1']);
                                            const Share = createIcon(['M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8', 'M16 6l-4-4-4 4', 'M12 2v13']);
                                            const Lock = createIcon(['M19 11H5a2 2 0 00-2 2v7a2 2 0 002 2h14a2 2 0 002-2v-7a2 2 0 00-2-2z', 'M7 11V7a5 5 0 0110 0v4']);
                                            const Unlock = createIcon(['M19 11H5a2 2 0 00-2 2v7a2 2 0 002 2h14a2 2 0 002-2v-7a2 2 0 00-2-2z', 'M7 11V7a5 5 0 019.9-1']);

                                            try {{
                                                // Define the component
                                                ${{code}}
                                                // Render it
                                                const root = ReactDOM.createRoot(document.getElementById('root'));
                                                root.render(React.createElement(${{componentName}}));
                                            }} catch(e) {{
                                                document.getElementById('root').innerHTML = '<div class="error"><strong>Render Error:</strong> ' + e.message + '</div>';
                                                console.error('Wireframe error:', e);
                                            }}
                                        <\\/script>
                                    </body>
                                    </html>
                                `);
                                doc.close();
                            }})();
                        </script>
'''

        html += '</div></div>'

    html += '</div></div>'
    return html


def _build_prototype(state: dict) -> str:
    proto = state.get("prototype", {})
    if not proto:
        return ""

    name = proto.get("prototype_name", "")
    code = proto.get("react_component_code", "")
    css_code = proto.get("css_code", "")
    demo = proto.get("demo_scenario", "")
    persona = proto.get("primary_persona", "")
    user_story = proto.get("key_user_story", "")
    color_palette = proto.get("color_palette", {})
    screens = _to_list(proto.get("screens_included", []))
    interactivity = proto.get("interactivity_notes", "")

    html = f"""
        <div class="section-card" id="prototype">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Interactive Prototype</h2>
            {"<h3 class='text-lg font-semibold text-indigo-600 mb-2'>" + name + "</h3>" if name else ""}
"""

    # Context info
    if persona or user_story:
        html += '<div class="mb-4 grid md:grid-cols-2 gap-4">'
        if persona:
            html += f'<div class="bg-slate-50 rounded-lg p-3"><span class="text-xs font-medium text-slate-500 uppercase">Primary Persona</span><p class="text-slate-800">{persona}</p></div>'
        if user_story:
            html += f'<div class="bg-slate-50 rounded-lg p-3"><span class="text-xs font-medium text-slate-500 uppercase">User Story</span><p class="text-slate-800">{str(user_story)[:200]}</p></div>'
        html += '</div>'

    if demo:
        html += f'<div class="mb-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500"><strong>Demo Scenario:</strong> {demo}</div>'

    # Color palette
    if color_palette and isinstance(color_palette, dict):
        colors = color_palette.get("colors", color_palette)
        if colors:
            html += '<div class="mb-4"><span class="text-xs font-medium text-slate-500 uppercase">Color Palette</span><div class="flex gap-2 mt-2">'
            color_items = list(colors.items()) if isinstance(colors, dict) else []
            for name_c, value in color_items[:6]:
                if isinstance(value, str) and value.startswith("#"):
                    html += f'<div class="flex flex-col items-center"><div class="w-10 h-10 rounded-lg shadow-sm" style="background-color: {value}"></div><span class="text-xs text-slate-500 mt-1">{name_c}</span></div>'
            html += '</div></div>'

    # Rendered prototype in iframe
    if code:
        # Pre-process the code for browser compatibility
        processed_code = code

        # Remove ALL import statements (React/lucide loaded globally)
        processed_code = re.sub(r'^import\s+.*?[\'"].*?[\'"];?\s*$', '', processed_code, flags=re.MULTILINE)

        # Remove export statements
        processed_code = re.sub(r"export\s+default\s+function\s+", "function ", processed_code)
        processed_code = re.sub(r"export\s+default\s+\w+;?\s*\n?", "", processed_code)
        processed_code = re.sub(r"export\s+\{[^}]+\};?\s*\n?", "", processed_code)

        # Replace destructured hooks with React.* versions
        processed_code = re.sub(r'\buseState\b', 'React.useState', processed_code)
        processed_code = re.sub(r'\buseEffect\b', 'React.useEffect', processed_code)
        processed_code = re.sub(r'\buseRef\b', 'React.useRef', processed_code)
        processed_code = re.sub(r'\buseMemo\b', 'React.useMemo', processed_code)
        processed_code = re.sub(r'\buseCallback\b', 'React.useCallback', processed_code)

        # Extract component name
        func_match = re.search(r'function\s+([A-Z][a-zA-Z0-9]*)', processed_code)
        const_match = re.search(r'const\s+([A-Z][a-zA-Z0-9]*)\s*=', processed_code)
        component_name = func_match.group(1) if func_match else (const_match.group(1) if const_match else "App")

        # Escape the code for embedding in JS template literal
        # Only escape: backslashes, backticks, and ${} template expressions
        code_for_iframe = processed_code.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        css_for_iframe = css_code.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${") if css_code else ""

        html += f'''
            <div class="mb-4">
                <h3 class="font-semibold text-slate-800 mb-3">Live Preview</h3>
                <div class="border-2 border-indigo-200 rounded-xl overflow-hidden shadow-lg">
                    <iframe id="prototype-frame" class="w-full" style="height: 600px; border: none;"></iframe>
                </div>
            </div>
            <script>
                (function() {{
                    const code = `{code_for_iframe}`;
                    const componentName = "{component_name}";
                    const cssCode = `{css_for_iframe}`;
                    const iframe = document.getElementById("prototype-frame");
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    doc.open();
                    doc.write(`
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <script src="https://unpkg.com/react@18/umd/react.development.js"><\\/script>
                            <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"><\\/script>
                            <script src="https://unpkg.com/@babel/standalone/babel.min.js"><\\/script>
                            <script src="https://cdn.tailwindcss.com"><\\/script>
                            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                            <style>
                                body {{ margin: 0; font-family: 'Inter', system-ui, sans-serif; }}
                                .error {{ color: #991b1b; background: #fee2e2; padding: 20px; border-radius: 8px; margin: 20px; }}
                                ${{cssCode}}
                            </style>
                        </head>
                        <body>
                            <div id="root"></div>
                            <script type="text/babel">
                                // Simple SVG icon components (Lucide-style)
                                const createIcon = (paths) => ({{ className, ...props }}) =>
                                    React.createElement('svg', {{
                                        xmlns: 'http://www.w3.org/2000/svg',
                                        width: 24, height: 24, viewBox: '0 0 24 24',
                                        fill: 'none', stroke: 'currentColor', strokeWidth: 2,
                                        strokeLinecap: 'round', strokeLinejoin: 'round',
                                        className, ...props
                                    }}, ...paths.map((d, i) => React.createElement('path', {{ key: i, d }})));

                                // Common icons
                                const Search = createIcon(['M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z']);
                                const Bell = createIcon(['M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9', 'M13.73 21a2 2 0 01-3.46 0']);
                                const Settings = createIcon(['M12.22 2h-.44a2 2 0 00-2 2v.18a2 2 0 01-1 1.73l-.43.25a2 2 0 01-2 0l-.15-.08a2 2 0 00-2.73.73l-.22.38a2 2 0 00.73 2.73l.15.1a2 2 0 011 1.72v.51a2 2 0 01-1 1.74l-.15.09a2 2 0 00-.73 2.73l.22.38a2 2 0 002.73.73l.15-.08a2 2 0 012 0l.43.25a2 2 0 011 1.73V20a2 2 0 002 2h.44a2 2 0 002-2v-.18a2 2 0 011-1.73l.43-.25a2 2 0 012 0l.15.08a2 2 0 002.73-.73l.22-.39a2 2 0 00-.73-2.73l-.15-.08a2 2 0 01-1-1.74v-.5a2 2 0 011-1.74l.15-.09a2 2 0 00.73-2.73l-.22-.38a2 2 0 00-2.73-.73l-.15.08a2 2 0 01-2 0l-.43-.25a2 2 0 01-1-1.73V4a2 2 0 00-2-2z', 'M12 8a4 4 0 100 8 4 4 0 000-8z']);
                                const Plus = createIcon(['M12 5v14', 'M5 12h14']);
                                const Filter = createIcon(['M22 3H2l8 9.46V19l4 2v-8.54L22 3z']);
                                const BarChart3 = createIcon(['M18 20V10', 'M12 20V4', 'M6 20v-6']);
                                const ChevronRight = createIcon(['M9 18l6-6-6-6']);
                                const ChevronDown = createIcon(['M6 9l6 6 6-6']);
                                const ChevronUp = createIcon(['M18 15l-6-6-6 6']);
                                const ChevronLeft = createIcon(['M15 18l-6-6 6-6']);
                                const AlertTriangle = createIcon(['M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z', 'M12 9v4', 'M12 17h.01']);
                                const TrendingUp = createIcon(['M23 6l-9.5 9.5-5-5L1 18']);
                                const TrendingDown = createIcon(['M23 18l-9.5-9.5-5 5L1 6']);
                                const ArrowRight = createIcon(['M5 12h14', 'M12 5l7 7-7 7']);
                                const ArrowLeft = createIcon(['M19 12H5', 'M12 19l-7-7 7-7']);
                                const Check = createIcon(['M20 6L9 17l-5-5']);
                                const X = createIcon(['M18 6L6 18', 'M6 6l12 12']);
                                const Menu = createIcon(['M3 12h18', 'M3 6h18', 'M3 18h18']);
                                const Home = createIcon(['M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z']);
                                const User = createIcon(['M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2', 'M12 3a4 4 0 100 8 4 4 0 000-8z']);
                                const Users = createIcon(['M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2', 'M23 21v-2a4 4 0 00-3-3.87', 'M16 3.13a4 4 0 010 7.75', 'M9 7a4 4 0 100 8 4 4 0 000-8z']);
                                const Mail = createIcon(['M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z', 'M22 6l-10 7L2 6']);
                                const Calendar = createIcon(['M19 4H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2z', 'M16 2v4', 'M8 2v4', 'M3 10h18']);
                                const Clock = createIcon(['M12 2a10 10 0 100 20 10 10 0 000-20z', 'M12 6v6l4 2']);
                                const Edit = createIcon(['M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7', 'M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z']);
                                const Trash = createIcon(['M3 6h18', 'M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2']);
                                const Save = createIcon(['M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z', 'M17 21v-8H7v8', 'M7 3v5h8']);
                                const Download = createIcon(['M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4', 'M7 10l5 5 5-5', 'M12 15V3']);
                                const Upload = createIcon(['M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4', 'M17 8l-5-5-5 5', 'M12 3v12']);
                                const RefreshCw = createIcon(['M23 4v6h-6', 'M1 20v-6h6', 'M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15']);
                                const Eye = createIcon(['M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z', 'M12 9a3 3 0 100 6 3 3 0 000-6z']);
                                const Info = createIcon(['M12 2a10 10 0 100 20 10 10 0 000-20z', 'M12 16v-4', 'M12 8h.01']);
                                const AlertCircle = createIcon(['M12 2a10 10 0 100 20 10 10 0 000-20z', 'M12 8v4', 'M12 16h.01']);
                                const CheckCircle = createIcon(['M22 11.08V12a10 10 0 11-5.93-9.14', 'M22 4L12 14.01l-3-3']);
                                const CheckCircle2 = createIcon(['M12 2a10 10 0 100 20 10 10 0 000-20z', 'M9 12l2 2 4-4']);
                                const DollarSign = createIcon(['M12 1v22', 'M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6']);
                                const CreditCard = createIcon(['M21 4H3a2 2 0 00-2 2v12a2 2 0 002 2h18a2 2 0 002-2V6a2 2 0 00-2-2z', 'M1 10h22']);
                                const PieChart = createIcon(['M21.21 15.89A10 10 0 118 2.83', 'M22 12A10 10 0 0012 2v10z']);
                                const LineChart = createIcon(['M23 6l-9.5 9.5-5-5L1 18']);
                                const Activity = createIcon(['M22 12h-4l-3 9L9 3l-3 9H2']);
                                const Zap = createIcon(['M13 2L3 14h9l-1 8 10-12h-9l1-8z']);
                                const Wallet = createIcon(['M21 5H3a2 2 0 00-2 2v10a2 2 0 002 2h18a2 2 0 002-2V7a2 2 0 00-2-2z', 'M1 10h22']);
                                const Banknote = createIcon(['M2 6h20v12H2z', 'M12 12a3 3 0 100-1 3 3 0 000 1z']);
                                const LayoutDashboard = createIcon(['M3 3h7v9H3z', 'M14 3h7v5h-7z', 'M14 12h7v9h-7z', 'M3 16h7v5H3z']);
                                const FileCog = createIcon(['M4 6V4a2 2 0 012-2h8.5L20 7.5V20a2 2 0 01-2 2H6a2 2 0 01-2-2v-2', 'M14 2v6h6', 'M12 12a3 3 0 100 6 3 3 0 000-6z']);
                                const Plug = createIcon(['M12 22v-5', 'M9 8V2', 'M15 8V2', 'M18 8v5a6 6 0 01-12 0V8z']);
                                const Phone = createIcon(['M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z']);
                                const Star = createIcon(['M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z']);
                                const Heart = createIcon(['M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z']);
                                const ExternalLink = createIcon(['M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6', 'M15 3h6v6', 'M10 14L21 3']);
                                const Link = createIcon(['M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71', 'M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71']);
                                const MoreHorizontal = createIcon(['M12 13a1 1 0 100-2 1 1 0 000 2z', 'M19 13a1 1 0 100-2 1 1 0 000 2z', 'M5 13a1 1 0 100-2 1 1 0 000 2z']);
                                const Loader = createIcon(['M12 2v4', 'M12 18v4', 'M4.93 4.93l2.83 2.83', 'M16.24 16.24l2.83 2.83', 'M2 12h4', 'M18 12h4', 'M4.93 19.07l2.83-2.83', 'M16.24 7.76l2.83-2.83']);

                                try {{
                                    // Define the component
                                    ${{code}}
                                    // Render it
                                    const root = ReactDOM.createRoot(document.getElementById('root'));
                                    root.render(React.createElement(${{componentName}}));
                                }} catch(e) {{
                                    document.getElementById('root').innerHTML = '<div class="error"><strong>Prototype Render Error:</strong> ' + e.message + '</div>';
                                    console.error('Prototype error:', e);
                                }}
                            <\\/script>
                        </body>
                        </html>
                    `);
                    doc.close();
                }})();
            </script>
'''

    # Interactivity notes
    if interactivity:
        html += f'<div class="mt-4 p-3 bg-slate-50 rounded-lg"><span class="text-xs font-medium text-slate-500 uppercase">Interactivity</span><p class="text-sm text-slate-700 mt-1">{str(interactivity)[:300]}</p></div>'

    html += '</div>'
    return html


def _build_stakeholders(state: dict) -> str:
    sv = state.get("stakeholder_views", {})
    if not sv:
        return ""

    views = _to_list(sv.get("views", []))
    if not views:
        return ""

    icons = {"CFO": "💰", "CISO": "🔒", "ARB": "🏛️", "VP Product": "📦", "CTO": "⚙️"}

    html = """
        <div class="section-card" id="stakeholders">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Stakeholder Views</h2>
            <div class="space-y-4">
"""

    for view in views[:4]:
        role = view.get("stakeholder_role", "")
        summary = view.get("tailored_summary", view.get("summary", ""))
        objections = _to_list(view.get("anticipated_objections", []))
        icon = icons.get(role, "👤")

        html += f'''
                <div class="border rounded-lg p-4">
                    <div class="flex items-center gap-3 mb-3">
                        <span class="text-2xl">{icon}</span>
                        <h3 class="text-lg font-semibold text-slate-800">{role}</h3>
                    </div>
                    <p class="text-slate-700 mb-4">{summary}</p>
'''
        if objections:
            html += '<div><h4 class="font-medium text-slate-800 mb-2">Anticipated Objections</h4><div class="space-y-2">'
            for obj in objections[:3]:
                objection = obj.get("objection", str(obj)) if isinstance(obj, dict) else str(obj)
                response = obj.get("response", obj.get("counter", "")) if isinstance(obj, dict) else ""
                html += f'<div class="border-l-4 border-amber-400 bg-amber-50 p-3 rounded-r"><p class="text-slate-800"><strong>Q:</strong> {objection}</p>'
                if response:
                    html += f'<p class="text-slate-600 mt-1"><strong>A:</strong> {response}</p>'
                html += '</div>'
            html += '</div></div>'
        html += '</div>'

    html += '</div></div>'
    return html


def _build_validation(state: dict) -> str:
    vp = state.get("validation_playbook", {})
    if not vp:
        return ""

    experiments = _to_list(vp.get("experiments", []))
    if not experiments:
        return ""

    html = """
        <div class="section-card" id="validation">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Validation Playbook</h2>
            <div class="space-y-4">
"""

    for i, exp in enumerate(experiments[:8]):
        name = exp.get("experiment_name", exp.get("name", f"Experiment {i+1}"))
        hypothesis = exp.get("hypothesis_claim_id", exp.get("hypothesis", ""))
        instructions = exp.get("specific_instructions", exp.get("method", ""))
        success = exp.get("success_criteria", "")
        failure = exp.get("failure_criteria", "")

        html += f'''
                <div class="border rounded-lg p-4">
                    <div class="flex items-center gap-3 mb-3">
                        <span class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold">{i+1}</span>
                        <h3 class="font-semibold text-slate-800">{name}</h3>
                    </div>
                    {"<p class='text-sm text-slate-500 mb-2'>Validates: " + hypothesis + "</p>" if hypothesis else ""}
                    <p class="text-slate-700 mb-3">{instructions}</p>
                    <div class="grid md:grid-cols-2 gap-3">
                        {"<div class='bg-green-50 p-3 rounded'><strong class='text-green-800'>Success:</strong> " + success + "</div>" if success else ""}
                        {"<div class='bg-red-50 p-3 rounded'><strong class='text-red-800'>Failure:</strong> " + failure + "</div>" if failure else ""}
                    </div>
                </div>
'''

    html += '</div></div>'
    return html


def _build_claims(state: dict) -> str:
    cr = state.get("cross_reference_index", {})
    claims = _to_list(cr.get("claims", []))

    if not claims:
        return ""

    html = """
        <div class="section-card" id="claims">
            <h2 class="text-2xl font-bold text-slate-800 mb-4">Cross-Reference Claims</h2>
            <p class="text-slate-600 mb-4">All claims extracted with evidence grading.</p>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-slate-50">
                        <tr>
                            <th class="px-3 py-2 text-left">ID</th>
                            <th class="px-3 py-2 text-left">Claim</th>
                            <th class="px-3 py-2 text-center">Tier</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200">
"""

    for claim in claims[:30]:
        cid = claim.get("claim_id", "")
        statement = str(claim.get("statement", ""))[:120]
        tier = claim.get("evidence_tier", "E5")
        html += f'<tr><td class="px-3 py-2 font-mono text-slate-500">{cid}</td><td class="px-3 py-2 text-slate-700">{statement}...</td><td class="px-3 py-2 text-center"><span class="tier-{tier} px-2 py-0.5 rounded text-xs font-medium">{tier}</span></td></tr>'

    if len(claims) > 30:
        html += f'<tr><td colspan="3" class="px-3 py-2 text-center text-slate-500">... and {len(claims) - 30} more claims</td></tr>'

    html += '</tbody></table></div></div>'
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m utils.pack_to_html <state_json> [output.html]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix(".html")

    with open(input_path) as f:
        state = json.load(f)

    html_file = generate_pack_html(state, output_path)
    print(f"Generated: {html_file}")
    print(f"Open: file://{html_file.absolute()}")


if __name__ == "__main__":
    main()
