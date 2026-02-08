# Phase 8: Critique Agent Revamp

**Goal:** Transform the Critique agent from text-quality checker to evidence-aware quality enforcement system.

**Dependencies:** Phases 1-2 (needs cross-reference index and context builder)

---

## 8.1 New Critique Dimensions

**File:** `backend/agents/critique.py` (MODIFY)

The Critique agent now evaluates on 5 dimensions instead of generic text quality:

### Dimension 1: Evidence Quality Score
- Compute weighted score across all claims in cross-reference index
- Weights: E1=1.0, E2=0.85, E3=0.6, E4=0.3, E5=0.1
- Flag if overall score is below 0.5
- Per-section breakdown: which sections are weakest?

### Dimension 2: Cross-Reference Consistency
- Are dependency chains logically sound?
- Flag circular dependencies (A depends on B, B depends on A)
- Flag missing dependencies (claim references a claim_id that doesn't exist)
- Flag contradictory claims (section A says X, section B says not-X)

### Dimension 3: Section Coherence
- Do sections reference each other's findings?
- Does the financial model use the same market size as market intelligence?
- Does the PRD account for regulatory requirements?
- Does the tech architecture support the PRD's non-functional requirements?

### Dimension 4: Generic Output Detection
Flag sections containing obviously generic phrases:
- "the market is growing rapidly"
- "consider GDPR compliance"
- "use a microservices architecture"
- "implement industry-standard security"
- Any claim without specific numbers, names, or dates

### Dimension 5: Stakeholder Readiness
- Would each stakeholder-relevant section survive a review meeting?
- Are there enough E1/E2 claims for critical assertions?
- Are regulatory claims specific enough (section numbers, not just regulation names)?
- Are financial projections defensible (derivations shown)?

---

## 8.2 Updated Critique Prompt

```python
EVIDENCE_CRITIQUE_PROMPT = """You are a senior quality reviewer for enterprise product inception packs.
Your job is to identify weaknesses that would cause stakeholder rejection.

## CROSS-REFERENCE INDEX
{cross_reference_summary}

## FULL PACK SUMMARY
{full_pack_summary}

## EVALUATE ON THESE 5 DIMENSIONS (score each 0-10):

### 1. Evidence Quality (0-10)
- What percentage of claims are E1-E3 vs E4-E5?
- Are E4/E5 claims honestly marked or masquerading as E2/E3?
- Which sections have the weakest evidence?

### 2. Cross-Reference Consistency (0-10)
- Do dependency chains make logical sense?
- Are there circular dependencies?
- Do referenced claim_ids actually exist?
- Are there contradictions between sections?

### 3. Section Coherence (0-10)
- Does the financial model use the market intelligence TAM?
- Does the PRD account for regulatory requirements?
- Does the tech architecture support the PRD requirements?
- Do stakeholder views reference actual pack content?

### 4. Generic Output Detection (0-10)
- Flag any phrases that are generic filler rather than specific analysis
- Flag sections where numbers lack derivation or source
- Flag recommendations that could apply to ANY product

### 5. Stakeholder Readiness (0-10)
- Would a CFO accept the financial projections?
- Would a CISO accept the security analysis?
- Would an ARB accept the technical architecture?
- What's missing that would cause rejection?

## OUTPUT FORMAT
Return JSON:
{{
  "dimensions": {{
    "evidence_quality": {{
      "score": 7,
      "findings": ["Financial Model has 8 claims, 7 are E4", "..."],
      "recommendation": "..."
    }},
    "cross_reference_consistency": {{
      "score": 6,
      "findings": ["BC-3 depends on MI-2 but they contradict on market size", "..."],
      "recommendation": "..."
    }},
    "section_coherence": {{
      "score": 8,
      "findings": ["..."],
      "recommendation": "..."
    }},
    "generic_output": {{
      "score": 5,
      "findings": ["Technical Architecture section 3 says 'use industry-standard practices'", "..."],
      "flagged_phrases": ["...", "..."],
      "recommendation": "..."
    }},
    "stakeholder_readiness": {{
      "score": 7,
      "findings": ["CISO view lacks specific data handling assessment", "..."],
      "recommendation": "..."
    }}
  }},
  "overall_score": 6.6,
  "sections_needing_revision": ["financial_model", "technical_architecture"],
  "critical_issues": ["Financial projections not defensible — 7/8 claims are hypotheses"],
  "revision_priority": [
    {{
      "section": "financial_model",
      "issue": "7 of 8 claims are E4 hypotheses",
      "action": "Re-run with grounding to find comparable SaaS benchmarks"
    }}
  ]
}}
"""
```

---

## 8.3 Critique-Driven Revision Loop

The existing critique loop pattern (auto-revise sections below threshold) should be updated:

```python
async def _run_quality_check(self, state: DiscoveryState) -> DiscoveryState:
    """Run critique and optionally revise weak sections."""

    # 1. Run evidence-aware critique
    critique_result = await run_critique_agent(state)
    state["critique"] = critique_result

    overall_score = critique_result.get("overall_score", 10)
    if overall_score < 6.0:
        # 2. Identify sections needing revision
        sections_to_revise = critique_result.get("sections_needing_revision", [])

        # 3. Re-run only those agents (max 2 revision rounds)
        for section in sections_to_revise[:3]:  # Cap at 3 sections
            agent_func = SECTION_TO_AGENT_MAP.get(section)
            if agent_func:
                self.logger.info("revising_section", section=section)
                state = await agent_func(state)

        # 4. Re-run critique to verify improvement
        state["critique"] = await run_critique_agent(state)

    return state
```

---

## 8.4 Section-to-Agent Mapping

```python
SECTION_TO_AGENT_MAP = {
    "customer_research": run_market_intelligence_agent,
    "competitive_analysis": run_competitive_landscape_agent,
    "detailed_personas": run_personas_agent,
    "business_case": run_business_case_agent,
    "gtm_plan": run_gtm_agent,
    "financial_model": run_financial_model_agent,
    "product_requirements": run_prd_agent,
    "technical_architecture": run_tech_arch_agent,
    "legal_regulatory_review": run_regulatory_agent,
    "risk_assessment": run_risk_agent,
}
```

---

## Test Phase 8

1. Run a pack and verify critique produces scores for all 5 dimensions
2. Verify generic output is flagged with specific phrases
3. Verify evidence quality assessment references actual tier distribution
4. Verify revision loop re-runs the weakest section(s)
5. Verify second critique shows improvement (or at least doesn't regress)
