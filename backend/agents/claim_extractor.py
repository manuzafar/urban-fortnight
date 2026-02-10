"""
Claim Extractor — extracts structured claims from agent output.

This utility runs after every agent to identify claims, assign evidence tiers,
and track dependencies. It uses a fast (Flash) model for efficiency.

Enhanced with mandatory minimum enforcement (Quality Improvement System):
- Each section has a minimum required claim count
- If extraction falls short, re-extraction is attempted with emphasis
- Ensures adequate evidence tracking across all sections
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from models.cross_references import (
    Claim,
    EvidenceTier,
    CrossReferenceIndex,
    SECTION_PREFIXES,
)

logger = structlog.get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# MINIMUM CLAIMS PER SECTION (Quality Improvement System)
# ═══════════════════════════════════════════════════════════════════════════════

MIN_CLAIMS_PER_SECTION: dict[str, int] = {
    "Market Intelligence": 5,
    "Competitive Landscape": 4,
    "Customer Personas": 3,
    "Business Case": 5,
    "Go-to-Market": 4,
    "Financial Model": 4,
    "Product Requirements": 5,
    "Technical Architecture": 4,
    "Regulatory & Compliance": 3,
    "Risk Assessment": 3,
    "Executive Summary": 2,
    "Stakeholder Views": 3,
    "Validation Playbook": 3,
}


# Claim extraction prompt
CLAIM_EXTRACTION_PROMPT = """You are a claim extraction specialist. Analyze the following agent output and extract all factual claims.

## SECTION INFORMATION
Section Name: {section_name}
Section Prefix: {section_prefix}

## AGENT OUTPUT
{content}

## YOUR TASK
Extract all significant claims from this output. For each claim:

1. **claim_id**: Use format "{section_prefix}-N" where N starts at 1
2. **statement**: The actual claim (one clear sentence)
3. **evidence_tier**: Classify as:
   - E1: Primary research data (user-uploaded, survey results)
   - E2: Verified external source (has URL/citation)
   - E3: Industry data (published reports, analyst estimates)
   - E4: Hypothesis (LLM inference, reasoned conclusion)
   - E5: Assumption (structural premise, unvalidated)
4. **confidence**: Your confidence in this claim (0.0-1.0)
5. **source**: URL or reference if available (null otherwise)
6. **depends_on**: List of other claim_ids this relies on (e.g., ["MI-1", "BC-2"])
7. **validation_method**: How could this be validated?
8. **validation_effort**: "quick" (1 day), "moderate" (1 week), "significant" (1 month+)

## RULES
- Extract 5-15 claims per section (focus on key assertions)
- Market sizes, growth rates, and financial figures are ALWAYS claims
- Competitor information with sources is E2; without sources is E4
- User persona details are E4 unless from research
- Technical requirements derived from business needs reference BC-* claims
- Be specific in statements (include numbers, names, dates where present)

## OUTPUT FORMAT
Return a JSON object:
{{
  "claims": [
    {{
      "claim_id": "{section_prefix}-1",
      "statement": "The specific claim text",
      "evidence_tier": "E2",
      "confidence": 0.8,
      "source": "https://example.com/report",
      "depends_on": [],
      "validation_method": "Verify via industry report",
      "validation_effort": "quick"
    }}
  ]
}}

Extract claims now:"""


async def extract_claims(
    section_name: str,
    section_prefix: str,
    content: dict | str,
    existing_claim_count: int = 0,
) -> list[Claim]:
    """
    Extract claims from agent output using Flash model.

    Args:
        section_name: Full section name (e.g., "Market Intelligence")
        section_prefix: Two-letter prefix (e.g., "MI")
        content: Agent output (dict or JSON string)
        existing_claim_count: Number of existing claims for this section (for ID continuity)

    Returns:
        List of extracted Claim objects
    """
    # Convert content to string if needed
    if isinstance(content, dict):
        content_str = json.dumps(content, indent=2, default=str)
    else:
        content_str = str(content)

    # Truncate if too long (keep first 15000 chars for claim extraction)
    if len(content_str) > 15000:
        content_str = content_str[:15000] + "\n... [truncated for claim extraction]"

    prompt = CLAIM_EXTRACTION_PROMPT.format(
        section_name=section_name,
        section_prefix=section_prefix,
        content=content_str,
    )

    try:
        result = await call_llm(prompt, "claim_extractor")

        if not result.get("success"):
            logger.warning(
                "claim_extraction_failed",
                section=section_name,
                error=result.get("error"),
            )
            return []

        data = result.get("data", {})
        raw_claims = data.get("claims", [])

        # Parse claims into Claim objects
        claims: list[Claim] = []
        for i, raw in enumerate(raw_claims):
            try:
                # Adjust claim ID if continuing from existing claims
                if existing_claim_count > 0:
                    new_num = existing_claim_count + i + 1
                    raw["claim_id"] = f"{section_prefix}-{new_num}"

                # Parse evidence tier
                tier_str = raw.get("evidence_tier", "E4")
                tier = EvidenceTier(tier_str)

                claim = Claim(
                    claim_id=raw.get("claim_id", f"{section_prefix}-{i + 1}"),
                    section=section_name,
                    statement=raw.get("statement", ""),
                    evidence_tier=tier,
                    confidence=float(raw.get("confidence", 0.5)),
                    source=raw.get("source"),
                    depends_on=raw.get("depends_on", []),
                    supports=raw.get("supports", []),
                    validation_method=raw.get("validation_method"),
                    validation_effort=raw.get("validation_effort"),
                )
                claims.append(claim)

            except Exception as e:
                logger.warning(
                    "claim_parse_error",
                    section=section_name,
                    claim_index=i,
                    error=str(e),
                )
                continue

        logger.info(
            "claims_extracted",
            section=section_name,
            count=len(claims),
            tiers={tier.value: sum(1 for c in claims if c.evidence_tier == tier) for tier in EvidenceTier},
        )

        return claims

    except Exception as e:
        logger.error(
            "claim_extraction_error",
            section=section_name,
            error=str(e),
            exc_info=True,
        )
        return []


async def extract_and_store_claims(
    state: dict[str, Any],
    section_name: str,
    section_prefix: str,
    content: dict | str,
    enforce_minimum: bool = True,
) -> dict[str, Any]:
    """
    Extract claims from content and merge into state's cross_reference_index.

    Enhanced with minimum claim enforcement (Quality Improvement System):
    - Checks if extracted claims meet minimum threshold
    - Re-extracts with emphasis if below threshold
    - Logs warning if still insufficient

    This is the main function to call after each agent stores its output.

    Args:
        state: Current workflow state
        section_name: Full section name
        section_prefix: Two-letter prefix
        content: Agent output to extract claims from
        enforce_minimum: Whether to enforce minimum claim count

    Returns:
        Updated state with claims merged into cross_reference_index
    """
    # Get or create cross-reference index
    existing_index = state.get("cross_reference_index")
    if existing_index is None:
        index = CrossReferenceIndex()
    elif isinstance(existing_index, dict):
        index = CrossReferenceIndex(**existing_index)
    else:
        index = existing_index

    # Count existing claims for this section (for ID continuity)
    existing_section_claims = len(index.get_claims_by_section(section_prefix))

    # Extract new claims
    new_claims = await extract_claims(
        section_name=section_name,
        section_prefix=section_prefix,
        content=content,
        existing_claim_count=existing_section_claims,
    )

    # Check minimum enforcement
    if enforce_minimum:
        min_required = MIN_CLAIMS_PER_SECTION.get(section_name, 3)
        if len(new_claims) < min_required:
            logger.warning(
                "insufficient_claims_initial",
                section=section_name,
                extracted=len(new_claims),
                required=min_required,
            )

            # Re-extract with emphasis
            additional_claims = await _extract_with_emphasis(
                content=content,
                section_name=section_name,
                section_prefix=section_prefix,
                min_required=min_required,
                already_extracted=len(new_claims),
                existing_claim_count=existing_section_claims + len(new_claims),
            )

            if additional_claims:
                new_claims.extend(additional_claims)
                logger.info(
                    "additional_claims_extracted",
                    section=section_name,
                    additional=len(additional_claims),
                    total=len(new_claims),
                )

            # Log final count if still insufficient
            if len(new_claims) < min_required:
                logger.warning(
                    "insufficient_claims_final",
                    section=section_name,
                    extracted=len(new_claims),
                    required=min_required,
                )

    if new_claims:
        index.add_claims(new_claims)

    # Store back as dict for serialization
    state["cross_reference_index"] = index.model_dump()

    return state


# Re-extraction prompt for when initial extraction falls short
EMPHASIS_EXTRACTION_PROMPT = """You are a claim extraction specialist. The initial extraction found only {already_extracted} claims, but we need at least {min_required}.

## SECTION: {section_name}
## PREFIX: {section_prefix}

## CONTENT TO ANALYZE:
{content}

## EXTRACTION REQUIREMENTS:
You MUST extract at least {remaining_needed} MORE claims. Look harder for:
- Numerical data (market sizes, percentages, growth rates)
- Competitor information
- User behavior assumptions
- Technical requirements
- Financial projections
- Regulatory considerations
- Risk factors

Even if a claim seems minor, include it if it's a factual assertion.

## OUTPUT FORMAT (JSON):
{{
  "claims": [
    {{
      "claim_id": "{section_prefix}-N",
      "statement": "The specific claim",
      "evidence_tier": "E2|E3|E4|E5",
      "confidence": 0.0-1.0,
      "source": "URL or null",
      "depends_on": [],
      "validation_method": "How to validate",
      "validation_effort": "quick|moderate|significant"
    }}
  ]
}}

Extract additional claims now:"""


async def _extract_with_emphasis(
    content: dict | str,
    section_name: str,
    section_prefix: str,
    min_required: int,
    already_extracted: int,
    existing_claim_count: int,
) -> list[Claim]:
    """
    Re-extract claims with emphasis on finding more.

    Called when initial extraction falls short of minimum.

    Args:
        content: Agent output to analyze
        section_name: Full section name
        section_prefix: Two-letter prefix
        min_required: Minimum claims needed
        already_extracted: Number already extracted
        existing_claim_count: Total existing claims (for ID numbering)

    Returns:
        List of additional Claim objects
    """
    # Convert content to string if needed
    if isinstance(content, dict):
        content_str = json.dumps(content, indent=2, default=str)
    else:
        content_str = str(content)

    # Truncate if too long
    if len(content_str) > 15000:
        content_str = content_str[:15000] + "\n... [truncated]"

    remaining_needed = min_required - already_extracted

    prompt = EMPHASIS_EXTRACTION_PROMPT.format(
        section_name=section_name,
        section_prefix=section_prefix,
        content=content_str,
        min_required=min_required,
        already_extracted=already_extracted,
        remaining_needed=remaining_needed,
    )

    try:
        result = await call_llm(prompt, "claim_extractor_emphasis")

        if not result.get("success"):
            logger.warning(
                "emphasis_extraction_failed",
                section=section_name,
                error=result.get("error"),
            )
            return []

        data = result.get("data", {})
        raw_claims = data.get("claims", [])

        # Parse claims
        claims: list[Claim] = []
        for i, raw in enumerate(raw_claims):
            try:
                # Adjust claim ID for continuity
                new_num = existing_claim_count + i + 1
                raw["claim_id"] = f"{section_prefix}-{new_num}"

                # Parse evidence tier
                tier_str = raw.get("evidence_tier", "E4")
                try:
                    tier = EvidenceTier(tier_str)
                except ValueError:
                    tier = EvidenceTier.E4

                claim = Claim(
                    claim_id=raw.get("claim_id", f"{section_prefix}-{new_num}"),
                    section=section_name,
                    statement=raw.get("statement", ""),
                    evidence_tier=tier,
                    confidence=float(raw.get("confidence", 0.5)),
                    source=raw.get("source"),
                    depends_on=raw.get("depends_on", []),
                    supports=raw.get("supports", []),
                    validation_method=raw.get("validation_method"),
                    validation_effort=raw.get("validation_effort"),
                )
                claims.append(claim)

            except Exception as e:
                logger.warning(
                    "emphasis_claim_parse_error",
                    section=section_name,
                    claim_index=i,
                    error=str(e),
                )
                continue

        return claims

    except Exception as e:
        logger.error(
            "emphasis_extraction_error",
            section=section_name,
            error=str(e),
            exc_info=True,
        )
        return []


def get_section_prefix(section_name: str) -> str:
    """
    Get the two-letter prefix for a section name.

    Args:
        section_name: Full section name or agent name

    Returns:
        Two-letter prefix (defaults to "XX" if not found)
    """
    # Direct lookup
    if section_name in SECTION_PREFIXES:
        return SECTION_PREFIXES[section_name]

    # Try matching by partial name
    section_lower = section_name.lower()
    for full_name, prefix in SECTION_PREFIXES.items():
        if full_name.lower() in section_lower or section_lower in full_name.lower():
            return prefix

    # Map common agent names
    agent_mapping = {
        "customer_research": "MI",
        "Customer Research Agent": "MI",
        "competitive_analysis": "CL",
        "Competitive Intelligence Agent": "CL",
        "detailed_personas": "CP",
        "Persona Development Agent": "CP",
        "business_case": "BC",
        "business_strategy": "BC",
        "Business Strategy Agent": "BC",
        "gtm_plan": "GM",
        "GTM Strategy Agent": "GM",
        "financial_model": "FM",
        "Financial Modeling Agent": "FM",
        "product_requirements": "PR",
        "Product Requirements Agent": "PR",
        "PRD Generator": "PR",
        "technical_architecture": "TA",
        "Technical Architect Agent": "TA",
        "legal_regulatory_review": "RC",
        "Legal & Regulatory Review Agent": "RC",
        "risk_assessment": "RM",
        "Risk Assessment Agent": "RM",
        "executive_summary": "ES",
        "Executive Summary Generator": "ES",
    }

    return agent_mapping.get(section_name, "XX")
