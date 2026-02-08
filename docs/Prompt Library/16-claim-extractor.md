# 16 — Claim Extraction Utility

**Purpose:** Lightweight utility that extracts claims from any agent's output to build the cross-reference index.
**Model:** Flash (fast, cheap — runs after every agent)
**File:** `backend/agents/claim_extractor.py`

---

## Prompt

```python
CLAIM_EXTRACTION_PROMPT = """Extract the key factual claims from the following section of a product inception pack. For each claim, identify its evidence tier, confidence, and dependencies on other claims.

## SECTION
Section name: {section_name}
Section prefix: {section_prefix}

## CONTENT TO EXTRACT FROM
{section_content}

## SECTION PREFIX MAPPING (for cross-references)
MI = Market Intelligence
CL = Competitive Landscape  
CP = Customer Personas
BC = Business Case
GM = Go-to-Market
FM = Financial Model
PR = Product Requirements
TA = Technical Architecture
RC = Regulatory & Compliance
RM = Risk Matrix
ES = Executive Summary

## EVIDENCE TIER DEFINITIONS
- E1: Based on user-uploaded primary research (interviews, surveys, analytics)
- E2: Verified by search with specific citation URL
- E3: Published industry reports with named source
- E4: LLM inference without direct evidence — hypothesis
- E5: Structural assumption the analysis depends on

## RULES
1. Extract 8-20 claims per section. Focus on SUBSTANTIVE claims — things that could be true or false, not structural statements.
2. Each claim gets an ID: {section_prefix}-1, {section_prefix}-2, etc.
3. Assign the evidence tier that appears in the original content. If no tier is marked, default to E4.
4. For depends_on: which claims from OTHER sections does this claim rely on? Use the section prefix to reference them. If a business case claim references market size, it depends on MI claims.
5. Confidence is 0.0-1.0: E1=0.9, E2=0.8, E3=0.6, E4=0.3, E5=0.2 as baseline, adjusted by specificity.

## WHAT IS A CLAIM (extract these)
- Market size numbers: "Australian SME lending market is $132B" → claim
- Growth rates: "Growing at 7.2% CAGR" → claim
- Competitor facts: "Competitor X has 40+ bank integrations" → claim  
- Pain assertions: "SME owners spend 4.2 hours/week on cash flow" → claim
- Financial projections: "Break-even in Month 14" → claim
- Technical assertions: "System handles 1,000 concurrent users" → claim
- Regulatory requirements: "CPS 234 requires encryption at rest" → claim

## WHAT IS NOT A CLAIM (skip these)
- Structural statements: "This section covers market intelligence" → skip
- Hedging language: "It's important to consider..." → skip
- Formatting instructions: "See below for details" → skip
- Generic truisms: "The market is competitive" → skip

Return valid JSON:

{{
  "claims": [
    {{
      "claim_id": "{section_prefix}-1",
      "claim": "The specific factual assertion in one sentence",
      "evidence_tier": "E1|E2|E3|E4|E5",
      "confidence": 0.8,
      "source": "URL, report name, or null",
      "depends_on": ["MI-3", "CL-2"],
      "depended_on_by": [],
      "section": "{section_name}",
      "validation_method": "How this claim could be validated if it's E4/E5 — or null if E1/E2/E3"
    }}
  ]
}}

Extract claims now. Be thorough but selective — quality over quantity. 8-20 claims per section.
"""
```

---

## Integration Notes

This utility runs after every agent produces output. The pattern:

```python
# In each agent's main function, after producing output:
async def run_market_intelligence(state, config):
    # ... generate market intelligence output ...
    output = await call_llm(...)
    
    # Extract claims for cross-reference index
    claims = await extract_claims(
        section_name="Market Intelligence",
        section_prefix="MI",
        section_content=json.dumps(output)
    )
    
    # Merge into state
    state["cross_reference_index"]["claims"].extend(claims)
    
    return state
```

The `extract_claims` function is a lightweight wrapper that:
1. Formats the `CLAIM_EXTRACTION_PROMPT` with section content
2. Calls Flash model (cheap, fast)
3. Parses the JSON response
4. Returns list of claim dicts

After ALL agents complete, a post-processing step resolves `depended_on_by` (reverse links) by scanning all `depends_on` references across the full index.
