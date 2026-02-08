# Phase 1: Cross-Reference Infrastructure

**Goal:** Build the system that makes every claim traceable across sections — the backbone for evidence enforcement, stakeholder views, and validation playbooks.

**Why first:** Without claim IDs and a cross-reference index, everything else is just better-formatted documents. This is what makes Seedcraft structurally impossible to replicate with ChatGPT.

**Dependencies:** None (foundational)

---

## 1.1 Create the Cross-Reference Schema

**File:** `backend/models/cross_references.py` (NEW)

```python
"""
Cross-Reference System for Seedcraft Inception Packs.

Every substantive claim gets a unique claim_id: {section_prefix}-{number}
Claims reference other claims they depend on or support.
This creates a knowledge graph, not a document collection.

Section prefixes:
  MI = Market Intelligence       CL = Competitive Landscape
  CP = Customer Personas         BC = Business Case
  GM = Go-to-Market              FM = Financial Model
  PR = Product Requirements      TA = Technical Architecture
  RC = Regulatory & Compliance   RM = Risk Assessment
  ES = Executive Summary
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class EvidenceTier(str, Enum):
    """Evidence quality tiers — drives system behaviour, not just labels."""
    E1_PRIMARY = "E1"       # User-uploaded primary research
    E2_VERIFIED = "E2"      # Search-grounded with citation URL
    E3_INDUSTRY = "E3"      # Published reports, analyst estimates
    E4_HYPOTHESIS = "E4"    # LLM inference without direct evidence
    E5_ASSUMPTION = "E5"    # Structural assumption underlying analysis


class Claim(BaseModel):
    """A single traceable claim within the inception pack."""
    claim_id: str = Field(
        description="Unique ID: {section_prefix}-{number}, e.g. MI-1, BC-3"
    )
    section: str = Field(description="Section this claim belongs to")
    statement: str = Field(description="The claim text")
    evidence_tier: EvidenceTier
    confidence: float = Field(ge=0.0, le=1.0)
    source: Optional[str] = Field(
        default=None, description="URL or citation for E1-E3"
    )
    depends_on: list[str] = Field(
        default_factory=list,
        description="claim_ids this depends on (e.g. revenue projection depends on market size)"
    )
    supports: list[str] = Field(
        default_factory=list,
        description="claim_ids this provides evidence for"
    )
    validation_method: Optional[str] = Field(
        default=None,
        description="For E4/E5: exactly how to validate"
    )
    validation_effort: Optional[str] = Field(
        default=None,
        description="quick (1 day) | moderate (1 week) | significant (1 month+)"
    )


class CrossReferenceIndex(BaseModel):
    """
    Complete cross-reference index for an inception pack.
    Built incrementally as each agent produces output.
    """
    claims: list[Claim] = Field(default_factory=list)
    total_claims: int = 0
    tier_distribution: dict[str, int] = Field(
        default_factory=lambda: {"E1": 0, "E2": 0, "E3": 0, "E4": 0, "E5": 0}
    )
    evidence_score: float = Field(
        default=0.0,
        description="Weighted: E1=1.0, E2=0.85, E3=0.6, E4=0.3, E5=0.1"
    )
    unresolved_dependencies: list[str] = Field(default_factory=list)

    def add_claims(self, new_claims: list[Claim]) -> None:
        """Add claims and recompute summaries."""
        self.claims.extend(new_claims)
        self._recompute()

    def _recompute(self) -> None:
        """Recompute all summary fields."""
        self.total_claims = len(self.claims)
        self.tier_distribution = {"E1": 0, "E2": 0, "E3": 0, "E4": 0, "E5": 0}
        for claim in self.claims:
            tier_key = claim.evidence_tier.value
            self.tier_distribution[tier_key] = self.tier_distribution.get(tier_key, 0) + 1

        weights = {"E1": 1.0, "E2": 0.85, "E3": 0.6, "E4": 0.3, "E5": 0.1}
        if self.total_claims > 0:
            total_weight = sum(
                weights.get(c.evidence_tier.value, 0) for c in self.claims
            )
            self.evidence_score = round(total_weight / self.total_claims, 2)

        all_ids = {c.claim_id for c in self.claims}
        all_deps = set()
        for c in self.claims:
            all_deps.update(c.depends_on)
        self.unresolved_dependencies = list(all_deps - all_ids)

    def get_claims_for_section(self, section_prefix: str) -> list[Claim]:
        """Get all claims for a given section."""
        return [c for c in self.claims if c.claim_id.startswith(section_prefix)]

    def get_claim_graph(self, claim_id: str) -> dict:
        """Get the dependency graph for a specific claim."""
        claim = next((c for c in self.claims if c.claim_id == claim_id), None)
        if not claim:
            return {}
        return {
            "claim": claim.model_dump(),
            "depends_on": [
                c.model_dump() for c in self.claims
                if c.claim_id in claim.depends_on
            ],
            "supports": [
                c.model_dump() for c in self.claims
                if c.claim_id in claim.supports
            ],
            "supported_by": [
                c.model_dump() for c in self.claims
                if claim.claim_id in c.supports
            ],
        }

    def get_validation_priorities(self) -> list[Claim]:
        """E4/E5 claims sorted by number of dependents (most impactful first)."""
        e4_e5 = [
            c for c in self.claims
            if c.evidence_tier in (EvidenceTier.E4_HYPOTHESIS, EvidenceTier.E5_ASSUMPTION)
        ]

        def dependent_count(claim: Claim) -> int:
            return sum(1 for c in self.claims if claim.claim_id in c.depends_on)

        return sorted(e4_e5, key=dependent_count, reverse=True)
```

---

## 1.2 Create the Claim Extraction Utility

**File:** `backend/agents/claim_extractor.py` (NEW)

→ **Prompt source:** Copy `CLAIM_EXTRACTION_PROMPT` from `seedcraft-v3-prompts/16-claim-extractor.md`

```python
"""
Claim Extraction Utility.
Called after every agent to extract substantive claims with evidence tiers.
Uses Flash model for speed — this is extraction, not reasoning.
"""

import json
import structlog
from agents.base_agent import call_llm

logger = structlog.get_logger("claim_extractor")

# ═══════════════════════════════════════════════════════════
# IMPORTANT: Copy the complete prompt from
# seedcraft-v3-prompts/16-claim-extractor.md
# ═══════════════════════════════════════════════════════════
CLAIM_EXTRACTION_PROMPT = """You are a rigorous research analyst extracting claims from a product analysis section.

## INPUT
Section: {section_name} (prefix: {section_prefix})
Content:
{content}

## TASK
Extract every substantive claim — any statement of fact, projection, recommendation,
or assumption that a stakeholder might question or want to verify.

For each claim, determine:
1. **claim_id**: {section_prefix}-1, {section_prefix}-2, etc.
2. **statement**: The claim in one clear sentence.
3. **evidence_tier**:
   - E1: Based on primary research uploaded by the user
   - E2: Verified by specific, citable source (include URL)
   - E3: Based on general industry knowledge from published sources
   - E4: Hypothesis generated by reasoning without direct evidence — REQUIRES VALIDATION
   - E5: Structural assumption that underlies the analysis
4. **confidence**: 0.0 to 1.0
5. **source**: For E1-E3, the specific source. For E2, include URL.
6. **depends_on**: List of claim_ids from OTHER sections this claim relies on.
   Use prefixes: MI, CL, CP, BC, GM, FM, PR, TA, RC, RM.
   Leave empty if self-contained.
7. **validation_method**: For E4/E5 only. SPECIFIC method, not "do more research".
8. **validation_effort**: For E4/E5 only. "quick" (1 day), "moderate" (1 week), "significant" (1 month+)

## RULES
- Extract 8-20 claims per section. Focus on consequential assertions, not every sentence.
- Be STRICT about evidence tiers. No specific source = E4 or E5.
- Claims from Google Search grounding with URLs = E2. General industry knowledge = E3.
- Cross-references (depends_on) are CRITICAL. What assumptions from other sections does this require?

## OUTPUT FORMAT
Return a JSON array of claim objects:
[
  {{
    "claim_id": "{section_prefix}-1",
    "section": "{section_name}",
    "statement": "...",
    "evidence_tier": "E1|E2|E3|E4|E5",
    "confidence": 0.85,
    "source": "URL or reference or null",
    "depends_on": ["MI-2", "BC-5"],
    "supports": [],
    "validation_method": "Interview 5 SME owners asking about willingness to pay",
    "validation_effort": "moderate"
  }}
]
"""


async def extract_claims(
    section_name: str,
    section_prefix: str,
    content: dict | str,
    agent_name: str = "claim_extractor",
) -> list[dict]:
    """
    Extract claims from agent output using LLM.
    Non-blocking: returns empty list on failure.
    """
    if isinstance(content, dict):
        content_str = json.dumps(content, indent=2, default=str)
    else:
        content_str = str(content)

    # Truncate to stay under token limits
    if len(content_str) > 15000:
        content_str = content_str[:15000] + "\n... [truncated]"

    prompt = CLAIM_EXTRACTION_PROMPT.format(
        section_name=section_name,
        section_prefix=section_prefix,
        content=content_str,
    )

    try:
        result = await call_llm(prompt, agent_name)
        if result["success"] and isinstance(result["data"], list):
            return result["data"]
    except Exception as e:
        logger.warning("claim_extraction_failed", section=section_name, error=str(e))

    return []
```

---

## 1.3 Add Helper to Base Agent

**File:** `backend/agents/base_agent.py` (MODIFY — add this function)

```python
async def extract_and_store_claims(
    state: dict,
    section_name: str,
    section_prefix: str,
    content: dict | str,
) -> dict:
    """
    Extract claims from agent output and merge into cross-reference index.

    Usage at end of any agent:
        state["customer_research"] = result["data"]
        state = await extract_and_store_claims(
            state, "Market Intelligence", "MI", result["data"]
        )
    """
    from agents.claim_extractor import extract_claims

    try:
        claims = await extract_claims(section_name, section_prefix, content)
        if state.get("cross_reference_index") is None:
            state["cross_reference_index"] = {"claims": []}
        state["cross_reference_index"].setdefault("claims", []).extend(claims)
    except Exception as e:
        import structlog
        structlog.get_logger("claim_extractor").warning(
            "claim_storage_failed", section=section_name, error=str(e)
        )

    return state
```

---

## 1.4 Add State Fields

**File:** `backend/agents/state.py` (MODIFY)

```python
# ─── Add import ───
from models.cross_references import CrossReferenceIndex

# ─── Add reducer ───
def merge_cross_references(current: dict | None, new: dict | None) -> dict | None:
    """Merge cross-reference indices from parallel agents."""
    if current is None and new is None:
        return None
    if current is None:
        return new
    if new is None:
        return current
    current_claims = current.get("claims", [])
    new_claims = new.get("claims", [])
    return {"claims": current_claims + new_claims}


# ─── Add these fields to DiscoveryState TypedDict ───

    # ═══ CROSS-REFERENCE INDEX (accumulates across all agents) ═══
    cross_reference_index: Annotated[Optional[dict[str, Any]], merge_cross_references]

    # ═══ DESIGN PHASE OUTPUTS ═══
    wireframes: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    prototype: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══ SYNTHESIS PHASE OUTPUTS ═══
    stakeholder_views: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    validation_playbook: Annotated[Optional[dict[str, Any]], keep_first_non_none]
```

---

## 1.5 Integrate Claim Extraction Into Every Existing Agent

**Pattern:** Add one call after setting output in state.

```python
# Example: customer_research.py
if result["success"]:
    state["customer_research"] = result["data"]
    # ← ADD THIS LINE:
    state = await extract_and_store_claims(
        state, "Market Intelligence", "MI", result["data"]
    )
return state
```

**Apply to ALL agents:**

| Agent File | Section Name | Prefix | State Field |
|-----------|-------------|--------|-------------|
| `customer_research.py` | Market Intelligence | MI | `customer_research` |
| `swarms/discovery_swarm.py` (competitive) | Competitive Landscape | CL | `competitive_analysis` |
| `swarms/discovery_swarm.py` (persona) | Customer Personas | CP | `detailed_personas` |
| `business_strategy.py` | Business Case | BC | `business_case` |
| `swarms/strategy_swarm.py` (gtm) | Go-to-Market | GM | `gtm_plan` |
| `swarms/strategy_swarm.py` (financial) | Financial Model | FM | `financial_model` |
| `prd_generator.py` | Product Requirements | PR | `product_requirements` |
| `technical_architect.py` | Technical Architecture | TA | `technical_architecture` |
| `legal_regulatory.py` | Regulatory & Compliance | RC | `legal_regulatory_review` |
| `swarms/delivery_swarm.py` (risk) | Risk Assessment | RM | `risk_assessment` |

---

## 1.6 Add Model Routing

**File:** `backend/config.py` (MODIFY)

```python
AGENT_MODEL_CONFIG = {
    # ... existing entries ...
    "claim_extractor": "flash",  # Speed + cost efficiency for extraction
}
```

---

## Test Phase 1

1. Run a discovery session with any product idea
2. Verify `state["cross_reference_index"]` exists and contains claims
3. Verify claims span multiple section prefixes (MI, CL, BC, etc.)
4. Verify evidence tiers are assigned (search for "E1", "E2", etc.)
5. Verify `depends_on` is populated for at least some claims
6. Verify the system doesn't crash if claim extraction fails for one agent
