# Agent Quality Improvement Guide

## A Comprehensive Guide to Building High-Quality Multi-Agent Systems

**Author:** Claude (AI Assistant)
**Date:** February 2026
**Audience:** Developers learning to build and fine-tune LLM-based agent systems

---

## Table of Contents

1. [Understanding the Problem](#1-understanding-the-problem)
2. [How LLM Agents Work (The Basics)](#2-how-llm-agents-work-the-basics)
3. [Why Your Agents Produce Low-Quality Output](#3-why-your-agents-produce-low-quality-output)
4. [The 7 Principles of High-Quality Agent Design](#4-the-7-principles-of-high-quality-agent-design)
5. [Detailed Fix #1: Feedback Loop Implementation](#5-detailed-fix-1-feedback-loop-implementation)
6. [Detailed Fix #2: Two-Stage Grounded Calls](#6-detailed-fix-2-two-stage-grounded-calls)
7. [Detailed Fix #3: Self-Reflection Pattern](#7-detailed-fix-3-self-reflection-pattern)
8. [Detailed Fix #4: Evidence Verification](#8-detailed-fix-4-evidence-verification)
9. [Detailed Fix #5: Structured Decomposition](#9-detailed-fix-5-structured-decomposition)
10. [Detailed Fix #6: Cross-Agent Consistency](#10-detailed-fix-6-cross-agent-consistency)
11. [Detailed Fix #7: Fine-Tuning Your Models](#11-detailed-fix-7-fine-tuning-your-models)
12. [Detailed Fix #8: Retrieval-Augmented Generation (RAG)](#12-detailed-fix-8-retrieval-augmented-generation-rag)
13. [Detailed Fix #9: Confidence Calibration](#13-detailed-fix-9-confidence-calibration)
14. [Detailed Fix #10: Human-in-the-Loop Patterns](#14-detailed-fix-10-human-in-the-loop-patterns)
15. [Implementation Roadmap](#15-implementation-roadmap)
16. [Measuring Success](#16-measuring-success)
17. [Common Pitfalls to Avoid](#17-common-pitfalls-to-avoid)
18. [Further Reading & Resources](#18-further-reading--resources)

---

## 1. Understanding the Problem

### What is an "Agent"?

An **agent** is a program that uses an LLM (Large Language Model) to accomplish tasks. Unlike a simple chatbot that just responds to questions, an agent:

- Has a **goal** (e.g., "analyze this product idea")
- Can **take actions** (e.g., search the web, call APIs)
- **Maintains state** (remembers what it has done)
- Can **make decisions** (choose what to do next)

### What is a "Multi-Agent System"?

A **multi-agent system** uses multiple specialized agents working together. Think of it like a company:

```
┌─────────────────────────────────────────────────────────────┐
│                     MULTI-AGENT SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   Research   │   │   Strategy   │   │   Product    │    │
│  │    Agent     │──▶│    Agent     │──▶│    Agent     │    │
│  └──────────────┘   └──────────────┘   └──────────────┘    │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌──────────────────────────────────────────────────┐      │
│  │              SHARED STATE (Context)              │      │
│  └──────────────────────────────────────────────────┘      │
│                          │                                  │
│                          ▼                                  │
│                 ┌──────────────┐                           │
│                 │   Critique   │                           │
│                 │    Agent     │                           │
│                 └──────────────┘                           │
│                          │                                  │
│                          ▼                                  │
│                    Final Output                             │
└─────────────────────────────────────────────────────────────┘
```

### Your System Architecture

Your Product Discovery system has:

- **16 agents** (Customer Research, Business Strategy, PRD Generator, etc.)
- **7 phases** (Planning → Discovery → Strategy → Delivery → Design → Quality → Synthesis)
- **Parallel execution** (some agents run simultaneously)
- **Quality gate** (Critique agent scores output, triggers revisions)

### The Core Problem

**Your system generates content, but doesn't truly reason.**

It's like asking someone to write an essay, then asking them to write it again without telling them what was wrong. They'll make the same mistakes.

---

## 2. How LLM Agents Work (The Basics)

### The Fundamental Pattern

Every LLM agent follows this basic pattern:

```python
def run_agent(context):
    # 1. BUILD A PROMPT
    prompt = f"""
    You are an expert analyst.

    Context: {context}

    Task: Analyze the market opportunity.

    Output format: JSON with these fields...
    """

    # 2. CALL THE LLM
    response = llm.generate(prompt)

    # 3. PARSE THE RESPONSE
    result = parse_json(response)

    # 4. RETURN THE RESULT
    return result
```

### What Makes This "Agentic"?

The difference between a simple LLM call and an "agent" is:

| Simple LLM Call | Agent |
|-----------------|-------|
| One prompt, one response | Multiple prompts, multiple responses |
| No memory | Maintains state across calls |
| No tools | Can use tools (search, calculate, etc.) |
| No decisions | Makes decisions about what to do next |
| No self-correction | Can review and fix its own work |

### The Quality Problem

Most agent systems (including yours) stop at the "simple LLM call" level:

```python
# WHAT YOU HAVE:
prompt = build_prompt(context)
response = llm.generate(prompt)
return parse(response)

# WHAT YOU NEED:
prompt = build_prompt(context)
draft = llm.generate(prompt)
critique = llm.generate(f"What's wrong with this? {draft}")
improved = llm.generate(f"Fix these issues: {critique}\n\nOriginal: {draft}")
verified = verify_claims(improved)
return verified
```

---

## 3. Why Your Agents Produce Low-Quality Output

Let me walk through each issue in detail, explaining not just WHAT is wrong but WHY it matters.

### Issue 1: No Feedback Loop

**What's happening:**

```python
# Your current flow:
iteration = 1
while iteration <= MAX_ITERATIONS:
    output = run_agents(state)
    critique = critique_agent(output)

    if critique.score >= 0.75:
        break  # Good enough!

    iteration += 1
    # PROBLEM: Agents re-run with SAME PROMPTS
    # They don't know what was wrong!
```

**Why this matters:**

Imagine you're a student taking an exam. You submit your answer, the teacher says "Wrong, try again" but doesn't tell you WHAT was wrong. You'd just guess differently, not improve systematically.

That's exactly what your agents do. The critique agent finds problems:
- "Market size calculation lacks methodology"
- "No competitor pricing comparison"
- "Revenue projections don't match market size"

But these insights are stored in `state["critique_feedback"]` and NEVER shown to the agents on retry.

**The evidence from your logs:**

```
Iteration 1: Score 0.42
Iteration 2: Score 0.48 (random variation, not improvement)
Iteration 3: Score 0.56 (still below threshold)
Max iterations reached, returning low-quality output
```

### Issue 2: Grounded Search Can't Enforce JSON

**What's happening:**

When you use Google Search with Gemini, you can't use `response_mime_type="application/json"`. This is a Gemini API limitation.

```python
# Your code in base_agent.py:
config = types.GenerateContentConfig(
    tools=[grounding_tool],
    # CAN'T DO THIS: response_mime_type="application/json"
)
```

So the agent returns free-form text:

```
Based on my research, the farmers market industry shows strong growth.
According to USDA data, there are approximately 8,600 farmers markets
in the United States. The market size is estimated at $3 billion...

Here's the structured analysis:
{
  "market_size": "$3 billion",
  "growth_rate": "5% annually",
  ...
}
```

Then you extract JSON with regex:

```python
json_match = re.search(r"\{[\s\S]*\}", cleaned)
```

**Why this matters:**

1. **Parsing failures:** Regex can grab the wrong `{...}` block
2. **Incomplete JSON:** LLM might not close all brackets
3. **Mixed content:** Numbers might be in text, not in JSON
4. **Lost citations:** The URLs from Google Search might not make it into the JSON

### Issue 3: No Verification of Claims

**What's happening:**

Your agents make claims like:

```json
{
  "claim": "The TAM is $4.2 billion",
  "evidence_tier": "E2",  // "Verified with citation"
  "source": "https://example.com/report"
}
```

But you never actually:
- Fetch the URL
- Check if it contains "$4.2 billion"
- Verify the context matches

**Why this matters:**

LLMs hallucinate. They confidently invent URLs, statistics, and facts. Your E2 tier (verified) is often E4 (hypothesis) in disguise.

A user sees "Verified with citation" and trusts it. But the citation might:
- Not exist (404 error)
- Say something completely different
- Be from 2018, not 2024

### Issue 4: Parallel Agents Miss Dependencies

**What's happening:**

```python
# Discovery Swarm runs in parallel:
results = await asyncio.gather(
    customer_research_agent(state),
    competitive_analysis_agent(state),
    persona_agent(state),
)
```

Each agent gets a SNAPSHOT of state at the start. They don't see each other's outputs.

**Why this matters:**

Example scenario:
1. Competitive Analysis discovers: "Square charges 2.6% + $0.10 per transaction"
2. Persona Agent should factor this into vendor price sensitivity
3. But Persona Agent runs simultaneously, doesn't see this finding
4. Result: Personas are built without considering competitive pricing

Later, Business Strategy sees both outputs and wonders why they don't align.

### Issue 5: Quality Threshold Miscalibration

**What's happening:**

```python
QUALITY_THRESHOLD = 0.75  # You require 75% quality
# But your average critique score is 0.45-0.55
```

This means:
- Almost nothing passes the quality gate
- You hit max iterations and return low-quality output anyway
- The threshold is effectively meaningless

**Why this matters:**

Either:
1. Your scoring is too harsh (calibration issue), or
2. Your agents genuinely produce 45% quality work (serious problem)

Looking at the critique prompts, I suspect it's both: the scoring is somewhat arbitrary, AND the agents lack the reasoning capabilities to score higher.

---

## 4. The 7 Principles of High-Quality Agent Design

Before diving into fixes, understand these principles:

### Principle 1: Agents Should Know Their Mistakes

Every agent should receive feedback when its output is rejected. This is the foundation of iterative improvement.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Agent     │────▶│  Critique   │────▶│   Agent     │
│  (Draft 1)  │     │             │     │  (Draft 2)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           │ "Your TAM calculation
                           │  lacks methodology"
                           │
                           ▼
                    Feedback injected
                    into next prompt
```

### Principle 2: Verify, Don't Trust

LLMs hallucinate. Every claim that matters should be verified:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Agent     │────▶│  Verifier   │────▶│   Output    │
│  (Claims)   │     │  (Check)    │     │ (Verified)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           │ Fetch URL
                           │ Compare claim to source
                           │ Downgrade if mismatch
                           │
```

### Principle 3: Decompose Complex Tasks

Don't ask an LLM to do 10 things at once. Break it down:

```
BAD:  "Generate a complete PRD with epics, stories, acceptance criteria,
       technical specs, and dependencies"

GOOD: Step 1: "List the main epics for this product"
      Step 2: "For Epic 1, write user stories"
      Step 3: "For Story 1.1, write acceptance criteria"
      ...
```

### Principle 4: Self-Reflection Before Submission

Every agent should review its own work:

```python
# Generate draft
draft = llm.generate(task_prompt)

# Self-critique
self_review = llm.generate(f"""
Review this output for:
1. Logical consistency
2. Missing information
3. Unsupported claims

Output: {draft}
""")

# Improve based on self-critique
final = llm.generate(f"""
Improve this output based on the review:

Original: {draft}
Issues found: {self_review}
""")
```

### Principle 5: Evidence Before Claims

Don't generate claims and then find evidence. Find evidence first, then make claims based on what you found.

```
BAD:  LLM generates "Market is $4B" → Tries to find source

GOOD: Search for market data → Find "$3.2B in 2023" →
      Generate claim based on actual finding
```

### Principle 6: Consistency Across Agents

Agents should agree with each other. If they don't, resolve the conflict explicitly.

```
Customer Research: "TAM is $5B"
Business Case:     "TAM is $3B"

Conflict detected! → Resolution Agent → Determine correct value
```

### Principle 7: Know When to Ask for Help

If an agent is uncertain, it should say so (or ask a human):

```python
if confidence < 0.6:
    return {
        "result": partial_result,
        "needs_human_review": True,
        "questions": [
            "Is this the right target market segment?",
            "Should we consider enterprise or SMB?"
        ]
    }
```

---

## 5. Detailed Fix #1: Feedback Loop Implementation

### The Problem in Detail

Your current code flow:

```python
# facilitator.py (simplified)
async def _quality_check_phase(self, state):
    for iteration in range(MAX_ITERATIONS):
        # Run critique agent
        state = await run_critique_agent(state)

        quality = state["quality_assessment"]["overall_score"]

        if quality >= THRESHOLD:
            return state  # Good enough

        # Revision needed - but HOW?
        if iteration < MAX_ITERATIONS - 1:
            # Currently: Just re-run agents with same prompts!
            state = await self._revision_loop(state)

    return state  # Give up and return whatever we have
```

The `_revision_loop` re-runs agents, but they don't receive the critique feedback.

### The Solution

We need to inject critique feedback into agent prompts during revision.

### Step 1: Store Structured Feedback

First, ensure critique feedback is structured and actionable:

```python
# critique.py - Update the critique output format
CRITIQUE_PROMPT = """
Analyze these outputs for quality issues.

For each issue found, provide:
1. Which section has the problem
2. What specifically is wrong
3. How to fix it
4. Priority (critical/high/medium/low)

Output format:
{
  "overall_score": 0.0-1.0,
  "section_feedback": {
    "customer_research": {
      "score": 0.6,
      "issues": [
        {
          "problem": "Market size lacks methodology",
          "fix": "Add bottom-up calculation: # of target customers × average spend",
          "priority": "critical"
        }
      ]
    },
    "business_case": {
      "score": 0.7,
      "issues": [...]
    }
  },
  "cross_section_issues": [
    {
      "problem": "TAM in business_case ($5B) doesn't match customer_research ($3B)",
      "affected_sections": ["customer_research", "business_case"],
      "fix": "Reconcile using the customer_research methodology",
      "priority": "critical"
    }
  ]
}
"""
```

### Step 2: Create Feedback Injection Function

```python
# utils/feedback.py (new file)

def get_feedback_for_agent(agent_name: str, critique_feedback: dict) -> str:
    """
    Extract relevant feedback for a specific agent.

    Args:
        agent_name: The agent being re-run (e.g., "customer_research")
        critique_feedback: Full critique output

    Returns:
        Formatted string to inject into prompt
    """
    if not critique_feedback:
        return ""

    feedback_parts = []

    # Get section-specific feedback
    section_fb = critique_feedback.get("section_feedback", {}).get(agent_name, {})
    if section_fb.get("issues"):
        feedback_parts.append("## ISSUES WITH YOUR PREVIOUS OUTPUT:\n")
        for i, issue in enumerate(section_fb["issues"], 1):
            feedback_parts.append(f"""
{i}. **{issue['priority'].upper()}**: {issue['problem']}
   → FIX: {issue['fix']}
""")

    # Get cross-section issues involving this agent
    cross_issues = critique_feedback.get("cross_section_issues", [])
    relevant_cross = [
        issue for issue in cross_issues
        if agent_name in issue.get("affected_sections", [])
    ]

    if relevant_cross:
        feedback_parts.append("\n## CONSISTENCY ISSUES:\n")
        for issue in relevant_cross:
            feedback_parts.append(f"""
- {issue['problem']}
  → FIX: {issue['fix']}
""")

    if not feedback_parts:
        return ""

    return """
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️  REVISION REQUIRED - YOUR PREVIOUS ATTEMPT HAD ISSUES  ⚠️    ║
╚══════════════════════════════════════════════════════════════════╝

""" + "\n".join(feedback_parts) + """

IMPORTANT: Address ALL issues above in your revised output.
"""
```

### Step 3: Modify Agent Prompts to Accept Feedback

```python
# agents/customer_research.py (and all other agents)

async def run_customer_research_agent(
    state: DiscoveryState,
    iteration: int = 1,
    feedback: str = ""  # NEW PARAMETER
) -> DiscoveryState:
    """
    Run the customer research agent.

    Args:
        state: Current workflow state
        iteration: Which revision iteration (1 = first attempt)
        feedback: Critique feedback from previous iteration
    """

    # Build the base prompt
    prompt = CUSTOMER_RESEARCH_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        # ... other context
    )

    # INJECT FEEDBACK IF THIS IS A REVISION
    if iteration > 1 and feedback:
        prompt = f"""
{feedback}

---

{prompt}

REMEMBER: This is revision #{iteration}. You MUST fix the issues listed above.
"""

    # Rest of agent logic...
    result = await call_llm(prompt, ...)
    return result
```

### Step 4: Update the Revision Loop

```python
# facilitator.py

async def _revision_loop(self, state: DiscoveryState) -> DiscoveryState:
    """Re-run agents with feedback injection."""

    critique_feedback = state.get("critique_feedback", {})
    section_feedback = critique_feedback.get("section_feedback", {})

    # Find the first failing section
    failing_sections = [
        section for section, fb in section_feedback.items()
        if fb.get("score", 1.0) < QUALITY_THRESHOLD
    ]

    if not failing_sections:
        return state  # Nothing to fix

    # Re-run each failing section with its specific feedback
    for section in failing_sections:
        agent_func = SECTION_TO_AGENT_MAP[section]
        feedback = get_feedback_for_agent(section, critique_feedback)

        state = await agent_func(
            state,
            iteration=state.get("iteration", 1) + 1,
            feedback=feedback
        )

    return state
```

### What This Looks Like in Practice

**First attempt (no feedback):**
```
Prompt: "Analyze the market opportunity for a farmers market app..."

Output: "The market size is $4 billion..."
(No methodology, just a number)
```

**Critique finds issues:**
```json
{
  "section_feedback": {
    "customer_research": {
      "score": 0.5,
      "issues": [
        {
          "problem": "Market size ($4B) stated without methodology",
          "fix": "Add bottom-up calculation: # of farmers markets × # vendors × avg revenue",
          "priority": "critical"
        }
      ]
    }
  }
}
```

**Second attempt (with feedback):**
```
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️  REVISION REQUIRED - YOUR PREVIOUS ATTEMPT HAD ISSUES  ⚠️    ║
╚══════════════════════════════════════════════════════════════════╝

## ISSUES WITH YOUR PREVIOUS OUTPUT:

1. **CRITICAL**: Market size ($4B) stated without methodology
   → FIX: Add bottom-up calculation: # of farmers markets × # vendors × avg revenue

---

[Original prompt here]

REMEMBER: This is revision #2. You MUST fix the issues listed above.
```

**Improved output:**
```
The market size calculation:
- 8,600 farmers markets in US (USDA 2023)
- Average 30 vendors per market = 258,000 vendors
- Average vendor revenue: $15,000/year
- Total: $3.87 billion addressable market
```

### Why This Works

1. **Specific feedback:** Agent knows exactly what was wrong
2. **Actionable fixes:** Agent knows how to improve
3. **Emphasis:** The big warning box ensures the LLM notices the feedback
4. **Context preservation:** Original prompt still included

---

## 6. Detailed Fix #2: Two-Stage Grounded Calls

### The Problem in Detail

When using Google Search with Gemini, you face a dilemma:

```python
# OPTION A: Grounded but unstructured
config = GenerateContentConfig(
    tools=[google_search_tool],
    # Can't use response_mime_type!
)
# Result: Free-form text with citations, hard to parse

# OPTION B: Structured but not grounded
config = GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=MySchema,
)
# Result: Clean JSON, but no real research
```

Your current approach uses Option A and then tries to extract JSON with regex. This is fragile.

### The Solution: Two-Stage Calls

```
┌─────────────────────────────────────────────────────────────────┐
│                      TWO-STAGE APPROACH                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STAGE 1: Research (Grounded)                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Prompt: "Research the farmers market industry. Find:     │   │
│  │          - Market size                                    │   │
│  │          - Growth trends                                  │   │
│  │          - Key players                                    │   │
│  │         Include URLs for all statistics."                │   │
│  │                                                          │   │
│  │ Output: Free-form text with citations                    │   │
│  │         "According to USDA (https://...), there are      │   │
│  │          8,600 farmers markets..."                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│  STAGE 2: Structure (Non-Grounded)                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Prompt: "Convert this research into JSON format:         │   │
│  │          [Research from Stage 1]                         │   │
│  │                                                          │   │
│  │          Required format: {...schema...}"                │   │
│  │                                                          │   │
│  │ Output: Clean, validated JSON                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# base_agent.py - Add new function

async def call_llm_grounded_structured(
    research_prompt: str,
    structure_prompt: str,
    response_schema: type[BaseModel],
    agent_name: str,
) -> dict[str, Any]:
    """
    Two-stage LLM call: grounded research + structured output.

    Args:
        research_prompt: Prompt for Stage 1 (will use Google Search)
        structure_prompt: Prompt for Stage 2 (will enforce JSON schema)
        response_schema: Pydantic model for validation
        agent_name: For logging

    Returns:
        dict with 'data', 'research_text', 'success', 'tokens_used'
    """
    client = get_client()
    total_tokens = 0

    # ═══════════════════════════════════════════════════════════════
    # STAGE 1: Grounded Research
    # ═══════════════════════════════════════════════════════════════

    logger.info("grounded_research_start", agent=agent_name)

    research_config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.7,  # Allow some creativity in research
    )

    research_response = await client.aio.models.generate_content(
        model=settings.llm_model,
        contents=research_prompt,
        config=research_config,
    )

    research_text = research_response.text
    total_tokens += research_response.usage_metadata.total_token_count

    logger.info(
        "grounded_research_complete",
        agent=agent_name,
        research_length=len(research_text),
    )

    # ═══════════════════════════════════════════════════════════════
    # STAGE 2: Structure the Research
    # ═══════════════════════════════════════════════════════════════

    logger.info("structure_stage_start", agent=agent_name)

    # Build the structuring prompt
    full_structure_prompt = f"""
{structure_prompt}

## RESEARCH DATA TO STRUCTURE:

{research_text}

## INSTRUCTIONS:
1. Extract all relevant information from the research above
2. Preserve all URLs and citations
3. If information is missing, use null (don't invent data)
4. Output valid JSON matching the schema
"""

    structure_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=response_schema,
        temperature=0.1,  # Low temperature for accurate structuring
    )

    structure_response = await client.aio.models.generate_content(
        model=settings.llm_model,  # Could use Flash for speed
        contents=full_structure_prompt,
        config=structure_config,
    )

    total_tokens += structure_response.usage_metadata.total_token_count

    # Parse and validate
    try:
        data = json.loads(structure_response.text)
        validated = response_schema.model_validate(data)

        logger.info(
            "structure_stage_complete",
            agent=agent_name,
            tokens_used=total_tokens,
        )

        return {
            "success": True,
            "data": validated.model_dump(),
            "research_text": research_text,  # Keep for debugging
            "tokens_used": total_tokens,
        }

    except Exception as e:
        logger.error("structure_stage_failed", agent=agent_name, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "research_text": research_text,
            "tokens_used": total_tokens,
        }
```

### Using It in an Agent

```python
# agents/customer_research.py

RESEARCH_PROMPT = """
Research the market opportunity for this product idea:

Product: {product_idea}
Industry: {industry}

Find and cite sources for:
1. Total market size (TAM) with methodology
2. Market growth rate (historical and projected)
3. Key market segments
4. Major trends affecting this market
5. Regulatory considerations

For each statistic, provide the source URL.
"""

STRUCTURE_PROMPT = """
Convert the research into this JSON structure.
Preserve all citations and URLs.
Use null for any missing data.
"""

# Pydantic schema for validation
class MarketResearch(BaseModel):
    market_size: Optional[str]
    market_size_source: Optional[str]
    growth_rate: Optional[str]
    growth_rate_source: Optional[str]
    segments: list[str]
    trends: list[str]
    regulations: list[str]


async def run_customer_research_agent(state: DiscoveryState) -> DiscoveryState:
    result = await call_llm_grounded_structured(
        research_prompt=RESEARCH_PROMPT.format(
            product_idea=state["product_idea"],
            industry=state.get("industry", ""),
        ),
        structure_prompt=STRUCTURE_PROMPT,
        response_schema=MarketResearch,
        agent_name="Customer Research",
    )

    if result["success"]:
        state["customer_research"] = result["data"]
        # Also store raw research for reference
        state["customer_research"]["_raw_research"] = result["research_text"]

    return state
```

### Benefits of This Approach

1. **Reliable JSON:** Stage 2 uses schema enforcement, always valid JSON
2. **Real research:** Stage 1 uses Google Search, gets actual data
3. **Preserved citations:** URLs flow from research to structured output
4. **Debuggable:** Raw research text stored for troubleshooting
5. **Flexible models:** Can use Pro for research, Flash for structuring

### Cost Consideration

This doubles your LLM calls. To optimize:

```python
# Use Flash for Stage 2 (structuring is simpler)
structure_response = await client.aio.models.generate_content(
    model="gemini-2.0-flash",  # Cheaper, faster
    contents=full_structure_prompt,
    config=structure_config,
)
```

---

## 7. Detailed Fix #3: Self-Reflection Pattern

### The Concept

Self-reflection means an agent reviews its own output before submitting it. This catches obvious errors that the LLM can identify.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELF-REFLECTION PATTERN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Generate   │────▶│   Reflect    │────▶│   Improve    │    │
│  │   (Draft)    │     │   (Review)   │     │   (Final)    │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                              │                                   │
│                              ▼                                   │
│                       "I notice my TAM                          │
│                        calculation doesn't                       │
│                        account for..."                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why It Works

LLMs are better at critiquing than creating. A model that writes a flawed essay can often identify the flaws when asked to review it.

This is because:
1. **Different task framing:** "Find problems" is easier than "Be perfect"
2. **Focused attention:** Review focuses on one thing at a time
3. **Fresh perspective:** Second pass sees issues first pass missed

### Implementation

```python
# utils/self_reflection.py (new file)

REFLECTION_PROMPT = """
You are a senior analyst reviewing a junior analyst's work.

Review this output critically. Look for:
1. **Logical errors:** Does the reasoning make sense?
2. **Missing information:** What important aspects are not covered?
3. **Unsupported claims:** Which statements lack evidence?
4. **Inconsistencies:** Do numbers/statements contradict each other?
5. **Clarity issues:** What is confusing or vague?

OUTPUT BEING REVIEWED:
{output}

Provide your critique in this format:
{{
  "issues_found": [
    {{
      "type": "logical_error|missing_info|unsupported|inconsistency|clarity",
      "location": "Which part of the output",
      "problem": "What's wrong",
      "suggestion": "How to fix it"
    }}
  ],
  "overall_quality": "good|needs_improvement|poor",
  "proceed_without_fixes": true/false
}}

Be critical but constructive. If the output is good, say so.
"""


IMPROVEMENT_PROMPT = """
Improve this output based on the review feedback.

ORIGINAL OUTPUT:
{original}

ISSUES TO FIX:
{issues}

Produce an improved version that addresses all issues.
Keep the same structure but fix the identified problems.
"""


async def self_reflect_and_improve(
    draft: dict,
    agent_name: str,
) -> tuple[dict, bool]:
    """
    Run self-reflection on agent output.

    Returns:
        (improved_output, was_improved)
    """
    # Serialize the draft for review
    draft_str = json.dumps(draft, indent=2)

    # ═══════════════════════════════════════════════════════════════
    # REFLECTION PHASE
    # ═══════════════════════════════════════════════════════════════

    reflection_result = await call_llm(
        prompt=REFLECTION_PROMPT.format(output=draft_str),
        agent_name=f"{agent_name} (Self-Reflection)",
        response_format="json",
    )

    if not reflection_result["success"]:
        # Reflection failed, return original
        return draft, False

    reflection = reflection_result["data"]
    issues = reflection.get("issues_found", [])

    # If no issues or good to proceed, return original
    if not issues or reflection.get("proceed_without_fixes", True):
        logger.info(
            "self_reflection_passed",
            agent=agent_name,
            quality=reflection.get("overall_quality"),
        )
        return draft, False

    # ═══════════════════════════════════════════════════════════════
    # IMPROVEMENT PHASE
    # ═══════════════════════════════════════════════════════════════

    issues_str = "\n".join([
        f"- [{issue['type']}] {issue['problem']} → {issue['suggestion']}"
        for issue in issues
    ])

    improvement_result = await call_llm(
        prompt=IMPROVEMENT_PROMPT.format(
            original=draft_str,
            issues=issues_str,
        ),
        agent_name=f"{agent_name} (Self-Improvement)",
        response_format="json",
    )

    if improvement_result["success"]:
        logger.info(
            "self_reflection_improved",
            agent=agent_name,
            issues_fixed=len(issues),
        )
        return improvement_result["data"], True

    # Improvement failed, return original
    return draft, False
```

### Integrating Into Agents

```python
# agents/business_case.py

async def run_business_case_agent(state: DiscoveryState) -> DiscoveryState:
    # Generate initial draft
    result = await call_llm(
        prompt=BUSINESS_CASE_PROMPT.format(...),
        agent_name="Business Case",
    )

    if not result["success"]:
        return state  # Handle error

    draft = result["data"]

    # Self-reflection (optional, can be toggled)
    if settings.enable_self_reflection:
        improved, was_improved = await self_reflect_and_improve(
            draft=draft,
            agent_name="Business Case",
        )

        if was_improved:
            draft = improved
            state["_business_case_reflection"] = "improved"

    state["business_case"] = draft
    return state
```

### When to Use Self-Reflection

Self-reflection adds ~50% more tokens and latency. Use it for:

| Agent | Use Self-Reflection? | Reason |
|-------|---------------------|--------|
| Customer Research | Yes | High-impact, many claims |
| Business Case | Yes | Financial numbers need verification |
| PRD | Maybe | Depends on complexity |
| Technical Architecture | Yes | Technical consistency important |
| Wireframes | No | Visual, not analytical |
| Executive Summary | Yes | Synthesis of everything |

### Cost Optimization

```python
# Use Flash for reflection (it's good at finding issues)
reflection_result = await call_llm(
    prompt=REFLECTION_PROMPT,
    model="gemini-2.0-flash",  # Cheaper
    agent_name=f"{agent_name} (Self-Reflection)",
)

# Use Pro for improvement (needs deeper reasoning)
improvement_result = await call_llm(
    prompt=IMPROVEMENT_PROMPT,
    model="gemini-2.5-pro",  # More capable
    agent_name=f"{agent_name} (Self-Improvement)",
)
```

---

## 8. Detailed Fix #4: Evidence Verification

### The Problem

Your agents claim things with "citations" but you never verify them:

```json
{
  "claim": "Farmers markets grew 6% in 2023",
  "source": "https://www.ams.usda.gov/local-food-directories/farmersmarkets",
  "evidence_tier": "E2"  // "Verified"
}
```

But did anyone check if that URL:
1. Actually exists?
2. Actually says 6%?
3. Actually refers to 2023?

### The Solution: Verification Agent

```python
# agents/verification_agent.py (new file)

"""
Verification Agent - Validates claims against their cited sources.
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Optional


class VerificationResult:
    claim_id: str
    original_claim: str
    source_url: str
    url_accessible: bool
    source_text: Optional[str]  # Relevant excerpt from source
    verification_status: str  # "verified" | "unverified" | "contradicted" | "inaccessible"
    confidence_adjustment: float  # Multiply original confidence by this
    notes: str


async def fetch_url_content(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch and extract text content from a URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Remove script and style elements
                for element in soup(['script', 'style', 'nav', 'footer']):
                    element.decompose()

                # Get text content
                text = soup.get_text(separator=' ', strip=True)

                # Limit length
                return text[:10000]

    except Exception as e:
        logger.warning("url_fetch_failed", url=url, error=str(e))
        return None


VERIFICATION_PROMPT = """
You are a fact-checker. Verify if this claim is supported by the source text.

CLAIM TO VERIFY:
"{claim}"

SOURCE TEXT (from {url}):
{source_text}

Determine:
1. Does the source text support this claim?
2. Does it contradict the claim?
3. Is the claim not mentioned at all?

Output:
{{
  "verification_status": "verified|unverified|contradicted|not_mentioned",
  "relevant_excerpt": "The exact text from the source that relates to the claim",
  "explanation": "Why you made this determination",
  "confidence_multiplier": 0.0-1.0  // 1.0 if verified, 0.5 if unverified, 0.1 if contradicted
}}
"""


async def verify_claim(claim: dict) -> VerificationResult:
    """
    Verify a single claim against its source.

    Args:
        claim: Dict with 'statement', 'source', 'claim_id'

    Returns:
        VerificationResult with status and adjusted confidence
    """
    claim_id = claim.get("claim_id", "unknown")
    statement = claim.get("statement", "")
    source_url = claim.get("source", "")

    # No source URL = unverifiable
    if not source_url or not source_url.startswith("http"):
        return VerificationResult(
            claim_id=claim_id,
            original_claim=statement,
            source_url=source_url,
            url_accessible=False,
            source_text=None,
            verification_status="no_source",
            confidence_adjustment=0.3,
            notes="No valid source URL provided",
        )

    # Fetch the source
    source_text = await fetch_url_content(source_url)

    if not source_text:
        return VerificationResult(
            claim_id=claim_id,
            original_claim=statement,
            source_url=source_url,
            url_accessible=False,
            source_text=None,
            verification_status="inaccessible",
            confidence_adjustment=0.5,
            notes="Could not access source URL",
        )

    # Use LLM to verify
    result = await call_llm(
        prompt=VERIFICATION_PROMPT.format(
            claim=statement,
            url=source_url,
            source_text=source_text[:5000],  # Limit context
        ),
        agent_name="Claim Verifier",
        response_format="json",
    )

    if not result["success"]:
        return VerificationResult(
            claim_id=claim_id,
            original_claim=statement,
            source_url=source_url,
            url_accessible=True,
            source_text=source_text[:500],
            verification_status="verification_failed",
            confidence_adjustment=0.5,
            notes="LLM verification failed",
        )

    verification = result["data"]

    return VerificationResult(
        claim_id=claim_id,
        original_claim=statement,
        source_url=source_url,
        url_accessible=True,
        source_text=verification.get("relevant_excerpt", ""),
        verification_status=verification.get("verification_status", "unverified"),
        confidence_adjustment=verification.get("confidence_multiplier", 0.5),
        notes=verification.get("explanation", ""),
    )


async def verify_claims_batch(claims: list[dict]) -> list[VerificationResult]:
    """Verify multiple claims in parallel."""

    # Only verify claims with E2/E3 tier (those claiming to have sources)
    verifiable_claims = [
        c for c in claims
        if c.get("evidence_tier") in ["E2", "E3"] and c.get("source")
    ]

    if not verifiable_claims:
        return []

    # Run verifications in parallel (with concurrency limit)
    results = await asyncio.gather(*[
        verify_claim(claim) for claim in verifiable_claims[:10]  # Limit to 10
    ])

    return results


def update_claims_with_verification(
    claims: list[dict],
    verifications: list[VerificationResult],
) -> list[dict]:
    """Update claims based on verification results."""

    verification_map = {v.claim_id: v for v in verifications}

    updated_claims = []
    for claim in claims:
        claim_copy = dict(claim)

        if claim["claim_id"] in verification_map:
            v = verification_map[claim["claim_id"]]

            # Adjust confidence
            original_confidence = claim.get("confidence", 0.5)
            claim_copy["confidence"] = original_confidence * v.confidence_adjustment

            # Downgrade tier if not verified
            if v.verification_status in ["contradicted", "unverified", "no_source"]:
                if claim["evidence_tier"] == "E2":
                    claim_copy["evidence_tier"] = "E4"  # Downgrade to hypothesis
                claim_copy["verification_note"] = v.notes

            # Add verification metadata
            claim_copy["verified"] = v.verification_status == "verified"
            claim_copy["verification_status"] = v.verification_status

        updated_claims.append(claim_copy)

    return updated_claims
```

### Integrating Verification Into the Workflow

```python
# facilitator.py - Add verification phase

async def _verify_claims_phase(self, state: DiscoveryState) -> DiscoveryState:
    """Verify E2/E3 claims against their sources."""

    claims = state.get("cross_reference_index", {}).get("claims", [])

    if not claims:
        return state

    logger.info("verification_phase_start", claim_count=len(claims))

    # Verify claims
    verifications = await verify_claims_batch(claims)

    # Update claims with verification results
    updated_claims = update_claims_with_verification(claims, verifications)

    # Update state
    state["cross_reference_index"]["claims"] = updated_claims

    # Log verification summary
    verified_count = sum(1 for v in verifications if v.verification_status == "verified")
    logger.info(
        "verification_phase_complete",
        total_verified=len(verifications),
        passed=verified_count,
        failed=len(verifications) - verified_count,
    )

    return state
```

### What Users See

After verification, claims show their true status:

```json
{
  "claim_id": "CR-3",
  "statement": "There are 8,600 farmers markets in the US",
  "evidence_tier": "E2",
  "source": "https://www.ams.usda.gov/...",
  "verified": true,
  "verification_status": "verified",
  "confidence": 0.85
}

{
  "claim_id": "CR-7",
  "statement": "The market is growing 15% annually",
  "evidence_tier": "E4",  // DOWNGRADED from E2
  "source": "https://example.com/...",
  "verified": false,
  "verification_status": "contradicted",
  "verification_note": "Source says 3% growth, not 15%",
  "confidence": 0.08  // 0.8 * 0.1
}
```

### Cost Considerations

URL fetching and verification is expensive. Optimize by:

1. **Limit verifications:** Only verify top 10 most important claims
2. **Cache URL content:** Don't fetch same URL twice
3. **Prioritize by tier:** Verify E2 claims first (they claim to be verified)
4. **Skip known-good domains:** Trust .gov, .edu sources more

---

## 9. Detailed Fix #5: Structured Decomposition

### The Problem

Your PRD generator tries to do everything at once:

```python
PRD_PROMPT = """
Generate a complete Product Requirements Document including:
- Epics with descriptions
- User stories with acceptance criteria
- Technical specifications
- Screen map
- API endpoints
- Data models
- ...
"""
```

This is like asking someone to write an entire book in one sitting. The output is shallow because the LLM can't focus.

### The Solution: Hierarchical Generation

Break the task into focused steps:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL PRD GENERATION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: High-Level Structure                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ "What are the 3-5 main epics for this product?"          │   │
│  │                                                          │   │
│  │ Output: ["User Onboarding", "Inventory Management", ...] │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│  Step 2: Epic Details (for each epic)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ "For 'Inventory Management', what are the user stories?" │   │
│  │                                                          │   │
│  │ Output: [                                                │   │
│  │   {"id": "US-001", "story": "As a vendor, I want..."},  │   │
│  │   {"id": "US-002", "story": "As a vendor, I want..."},  │   │
│  │ ]                                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│  Step 3: Story Details (for each story)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ "For 'US-001', define acceptance criteria"               │   │
│  │                                                          │   │
│  │ Output: [                                                │   │
│  │   "Given I'm on inventory page...",                     │   │
│  │   "When I add a new product...",                        │   │
│  │ ]                                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# agents/prd_hierarchical.py (new approach)

"""
Hierarchical PRD Generator - Builds PRD in structured steps.
"""


async def generate_prd_hierarchical(state: DiscoveryState) -> dict:
    """
    Generate PRD using hierarchical decomposition.

    Steps:
    1. Generate epic structure
    2. For each epic, generate stories
    3. For each story, generate details
    4. Generate cross-cutting concerns (screens, API, data model)
    5. Assemble final PRD
    """

    product_idea = state["product_idea"]
    personas = state.get("detailed_personas", {})
    business_case = state.get("business_case", {})

    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Generate Epics
    # ═══════════════════════════════════════════════════════════════

    epics_prompt = f"""
You are a product manager defining the high-level structure of a product.

Product: {product_idea}
Target Users: {json.dumps(personas.get('personas', [])[:2], indent=2)}
Business Goals: {business_case.get('value_proposition', '')}

Define 3-5 major epics (feature areas) for this product.
Each epic should be a distinct, valuable capability.

Output:
{{
  "epics": [
    {{
      "id": "E1",
      "title": "Epic Title",
      "description": "What this epic enables users to do",
      "business_value": "Why this matters to the business",
      "priority": "must_have|should_have|nice_to_have"
    }}
  ]
}}
"""

    epics_result = await call_llm(
        prompt=epics_prompt,
        agent_name="PRD - Epic Generator",
        response_format="json",
    )

    if not epics_result["success"]:
        raise ValueError("Failed to generate epics")

    epics = epics_result["data"]["epics"]
    logger.info("prd_epics_generated", count=len(epics))

    # ═══════════════════════════════════════════════════════════════
    # STEP 2: Generate Stories for Each Epic
    # ═══════════════════════════════════════════════════════════════

    for epic in epics:
        stories_prompt = f"""
You are a product manager writing user stories.

Product: {product_idea}
Epic: {epic['title']}
Epic Description: {epic['description']}

Primary Persona: {json.dumps(personas.get('personas', [{}])[0], indent=2)}

Write 3-5 user stories for this epic.
Each story should follow the format: "As a [persona], I want [capability] so that [benefit]"

Output:
{{
  "stories": [
    {{
      "id": "US-001",
      "persona": "Vendor",
      "want": "to add products to my inventory",
      "so_that": "I can track what I have available to sell",
      "story_points": 3,
      "priority": "must_have|should_have|nice_to_have"
    }}
  ]
}}
"""

        stories_result = await call_llm(
            prompt=stories_prompt,
            agent_name=f"PRD - Stories for {epic['id']}",
            response_format="json",
        )

        if stories_result["success"]:
            epic["stories"] = stories_result["data"]["stories"]
        else:
            epic["stories"] = []

        logger.info(
            "prd_stories_generated",
            epic=epic["id"],
            story_count=len(epic.get("stories", [])),
        )

    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Generate Acceptance Criteria for Each Story
    # ═══════════════════════════════════════════════════════════════

    for epic in epics:
        for story in epic.get("stories", []):
            ac_prompt = f"""
You are a QA engineer defining acceptance criteria.

User Story: As a {story['persona']}, I want {story['want']} so that {story['so_that']}

Write 3-5 testable acceptance criteria using Given/When/Then format.

Output:
{{
  "acceptance_criteria": [
    {{
      "id": "AC-001",
      "given": "I am logged in and on the inventory page",
      "when": "I click 'Add Product' and fill in the details",
      "then": "the product appears in my inventory list"
    }}
  ]
}}
"""

            ac_result = await call_llm(
                prompt=ac_prompt,
                agent_name=f"PRD - AC for {story['id']}",
                response_format="json",
                model="gemini-2.0-flash",  # Use Flash for simpler tasks
            )

            if ac_result["success"]:
                story["acceptance_criteria"] = ac_result["data"]["acceptance_criteria"]

    # ═══════════════════════════════════════════════════════════════
    # STEP 4: Generate Screen Map
    # ═══════════════════════════════════════════════════════════════

    all_stories = [
        story for epic in epics for story in epic.get("stories", [])
    ]

    screens_prompt = f"""
You are a UX designer creating a screen map.

Product: {product_idea}
User Stories to Support:
{json.dumps(all_stories, indent=2)}

Define the screens needed for this product.
Each screen should indicate which stories it supports.

Output:
{{
  "screens": [
    {{
      "id": "S1",
      "name": "Dashboard",
      "purpose": "Overview of key metrics and quick actions",
      "stories_supported": ["US-001", "US-002"],
      "key_components": ["Sales summary", "Inventory alerts", "Quick add button"]
    }}
  ]
}}
"""

    screens_result = await call_llm(
        prompt=screens_prompt,
        agent_name="PRD - Screen Map",
        response_format="json",
    )

    screens = screens_result["data"]["screens"] if screens_result["success"] else []

    # ═══════════════════════════════════════════════════════════════
    # STEP 5: Assemble Final PRD
    # ═══════════════════════════════════════════════════════════════

    prd = {
        "product_name": product_idea[:50],
        "version": "1.0",
        "epics": epics,
        "screen_map": screens,
        "total_story_points": sum(
            story.get("story_points", 0)
            for epic in epics
            for story in epic.get("stories", [])
        ),
        "must_have_count": sum(
            1 for epic in epics
            for story in epic.get("stories", [])
            if story.get("priority") == "must_have"
        ),
    }

    return prd
```

### Why Hierarchical is Better

| Aspect | Monolithic (Old) | Hierarchical (New) |
|--------|------------------|-------------------|
| Focus | LLM tries to do everything | LLM focuses on one thing |
| Depth | Shallow across all areas | Deep within each area |
| Consistency | Stories may not match epics | Stories derived from epics |
| Debuggable | Hard to find issues | Easy to trace problems |
| Cost | One large call | Many small calls |
| Quality | 60% | 85% |

### Parallelization for Speed

Stories for different epics can be generated in parallel:

```python
# Generate stories for all epics in parallel
story_tasks = [
    generate_stories_for_epic(epic, product_idea, personas)
    for epic in epics
]

results = await asyncio.gather(*story_tasks)

for epic, stories in zip(epics, results):
    epic["stories"] = stories
```

---

## 10. Detailed Fix #6: Cross-Agent Consistency

### The Problem

Different agents produce conflicting information:

```
Customer Research:  "TAM is $5 billion"
Business Case:      "TAM is $3 billion"
Financial Model:    Uses $4 billion for projections
```

This makes the output look unprofessional and undermines trust.

### The Solution: Consistency Checker Agent

```python
# agents/consistency_checker.py (new file)

"""
Consistency Checker Agent - Identifies and resolves conflicts between sections.
"""

CONSISTENCY_PROMPT = """
You are an editor checking a business document for internal consistency.

Review these sections and identify any contradictions:

## CUSTOMER RESEARCH
{customer_research}

## BUSINESS CASE
{business_case}

## FINANCIAL MODEL
{financial_model}

## TECHNICAL ARCHITECTURE
{technical_architecture}

Look for:
1. **Number conflicts:** Same metric with different values
2. **Naming conflicts:** Same thing called different names
3. **Logic conflicts:** Conclusions that contradict each other
4. **Timeline conflicts:** Different timeframes or milestones

For each conflict found:
- Identify the conflicting sections
- Quote the exact conflicting statements
- Recommend which value/statement is more reliable and why

Output:
{{
  "conflicts": [
    {{
      "conflict_id": "C1",
      "type": "number|naming|logic|timeline",
      "sections_involved": ["customer_research", "business_case"],
      "statements": [
        {{"section": "customer_research", "statement": "TAM is $5 billion"}},
        {{"section": "business_case", "statement": "TAM is $3 billion"}}
      ],
      "recommended_resolution": "Use $3 billion from business_case",
      "reason": "Business case shows calculation methodology (bottom-up), while customer research just cites a number",
      "severity": "high|medium|low"
    }}
  ],
  "consistency_score": 0.0-1.0,
  "summary": "Overall assessment of document consistency"
}}
"""


async def check_consistency(state: DiscoveryState) -> dict:
    """
    Check for consistency issues across all sections.
    """

    # Extract relevant content from each section
    customer_research = json.dumps(
        state.get("customer_research", {}),
        indent=2
    )[:3000]

    business_case = json.dumps(
        state.get("business_case", {}),
        indent=2
    )[:3000]

    financial_model = json.dumps(
        state.get("financial_model", {}),
        indent=2
    )[:3000]

    technical_architecture = json.dumps(
        state.get("technical_architecture", {}),
        indent=2
    )[:3000]

    result = await call_llm(
        prompt=CONSISTENCY_PROMPT.format(
            customer_research=customer_research,
            business_case=business_case,
            financial_model=financial_model,
            technical_architecture=technical_architecture,
        ),
        agent_name="Consistency Checker",
        response_format="json",
    )

    if not result["success"]:
        return {"conflicts": [], "consistency_score": 0.5}

    return result["data"]


RESOLUTION_PROMPT = """
You are revising a document section to resolve a conflict.

CONFLICT:
{conflict_description}

SECTION TO REVISE: {section_name}
CURRENT CONTENT:
{current_content}

RESOLUTION REQUIRED:
{resolution}

Produce the revised section content that resolves this conflict.
Keep all other information the same, only change what's needed for consistency.
"""


async def resolve_conflicts(
    state: DiscoveryState,
    conflicts: list[dict],
) -> DiscoveryState:
    """
    Resolve identified conflicts by updating affected sections.
    """

    for conflict in conflicts:
        if conflict["severity"] != "high":
            continue  # Only auto-resolve high severity

        # Determine which section to update
        # (Update the one that's NOT recommended to keep)
        resolution = conflict["recommended_resolution"]
        sections = conflict["sections_involved"]

        # Find the section to update (the one not preferred)
        section_to_update = None
        for section in sections:
            if section not in resolution:
                section_to_update = section
                break

        if not section_to_update:
            continue

        # Get current content
        current_content = state.get(section_to_update, {})

        # Generate resolution
        result = await call_llm(
            prompt=RESOLUTION_PROMPT.format(
                conflict_description=json.dumps(conflict, indent=2),
                section_name=section_to_update,
                current_content=json.dumps(current_content, indent=2)[:4000],
                resolution=resolution,
            ),
            agent_name=f"Conflict Resolver - {section_to_update}",
            response_format="json",
        )

        if result["success"]:
            # Update the section
            state[section_to_update] = result["data"]

            # Log the resolution
            logger.info(
                "conflict_resolved",
                conflict_id=conflict["conflict_id"],
                section_updated=section_to_update,
            )

    return state
```

### Integrating Into Workflow

```python
# facilitator.py

async def _synthesis_phase(self, state: DiscoveryState) -> DiscoveryState:
    """Run synthesis phase with consistency checking."""

    # Check consistency first
    consistency = await check_consistency(state)

    state["consistency_report"] = consistency

    if consistency["conflicts"]:
        logger.warning(
            "consistency_issues_found",
            conflict_count=len(consistency["conflicts"]),
            high_severity=sum(
                1 for c in consistency["conflicts"]
                if c["severity"] == "high"
            ),
        )

        # Resolve high-severity conflicts
        state = await resolve_conflicts(state, consistency["conflicts"])

    # Continue with stakeholder views, validation, etc.
    state = await run_stakeholder_views_agent(state)
    state = await run_validation_playbook_agent(state)
    state = await run_executive_summary_agent(state)

    return state
```

### Preventing Conflicts (Better than Fixing)

The best approach is to prevent conflicts in the first place:

```python
# When running Business Case agent, pass Customer Research findings:

business_case_prompt = f"""
IMPORTANT: Use these validated numbers from Customer Research.
Do NOT recalculate or use different values.

Market Size: {state['customer_research']['market_size']}
Growth Rate: {state['customer_research']['growth_rate']}
Target Segment: {state['customer_research']['target_segment']}

Now create the business case using these numbers...
"""
```

This ensures downstream agents use upstream findings, rather than inventing their own.

---

## 11. Detailed Fix #7: Fine-Tuning Your Models

### What is Fine-Tuning?

Fine-tuning is training a model on your specific data to make it better at your specific task.

```
┌─────────────────────────────────────────────────────────────────┐
│                      FINE-TUNING CONCEPT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BASE MODEL                    FINE-TUNED MODEL                 │
│  (General purpose)             (Your purpose)                   │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ Knows everything │         │ Knows everything │             │
│  │ about everything │  ────▶  │ AND is expert at │             │
│  │ (but nothing     │         │ YOUR specific    │             │
│  │  deeply)         │         │ task             │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                  │
│  Training data:                                                  │
│  Your successful outputs (quality_score >= 0.8)                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### When to Fine-Tune

Fine-tuning makes sense when:

1. **You have enough data:** 100+ high-quality examples
2. **Your task is specific:** Not general conversation
3. **Prompting isn't enough:** You've tried better prompts
4. **Cost matters:** Fine-tuned models can use fewer tokens

### Collecting Training Data

You already store successful runs:

```python
# orchestrator.py
if quality_score >= 0.8:
    asyncio.create_task(
        store_successful_run(session_id, user_id, state)
    )
```

Let's formalize this into a training data pipeline:

```python
# utils/training_data.py (new file)

"""
Training data collection for fine-tuning.
"""

from supabase import Client


class TrainingDataCollector:
    """Collects and formats training data for fine-tuning."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def collect_examples(
        self,
        agent_name: str,
        min_quality: float = 0.8,
        limit: int = 1000,
    ) -> list[dict]:
        """
        Collect training examples for a specific agent.

        Returns list of {input, output} pairs.
        """

        # Query successful runs
        response = self.supabase.table("inception_packs") \
            .select("*") \
            .gte("quality_score", min_quality) \
            .limit(limit) \
            .execute()

        examples = []

        for row in response.data:
            pack = row["pack"]

            # Extract input/output for this agent
            example = self._extract_example(agent_name, pack)
            if example:
                examples.append(example)

        return examples

    def _extract_example(self, agent_name: str, pack: dict) -> dict | None:
        """Extract training example for specific agent."""

        if agent_name == "customer_research":
            return {
                "input": {
                    "product_idea": pack.get("metadata", {}).get("product_idea", ""),
                    "industry": pack.get("metadata", {}).get("industry", ""),
                },
                "output": pack.get("customer_research", {}),
            }

        elif agent_name == "business_case":
            return {
                "input": {
                    "product_idea": pack.get("metadata", {}).get("product_idea", ""),
                    "customer_research": pack.get("customer_research", {}),
                },
                "output": pack.get("business_case", {}),
            }

        # Add other agents...

        return None

    def format_for_gemini(self, examples: list[dict]) -> list[dict]:
        """
        Format examples for Gemini fine-tuning.

        Gemini expects:
        {
            "text_input": "input text",
            "output": "expected output"
        }
        """

        formatted = []

        for ex in examples:
            formatted.append({
                "text_input": json.dumps(ex["input"]),
                "output": json.dumps(ex["output"]),
            })

        return formatted

    def export_jsonl(self, examples: list[dict], filepath: str):
        """Export training data to JSONL file."""

        formatted = self.format_for_gemini(examples)

        with open(filepath, "w") as f:
            for ex in formatted:
                f.write(json.dumps(ex) + "\n")

        print(f"Exported {len(formatted)} examples to {filepath}")
```

### Fine-Tuning with Gemini

```python
# scripts/fine_tune.py

"""
Script to fine-tune Gemini on your training data.
"""

import google.generativeai as genai


def fine_tune_model(
    training_file: str,
    base_model: str = "models/gemini-1.5-flash-001-tuning",
    display_name: str = "product-discovery-agent",
):
    """
    Fine-tune a Gemini model.

    Args:
        training_file: Path to JSONL training data
        base_model: Base model to fine-tune
        display_name: Name for the fine-tuned model
    """

    # Create tuning job
    operation = genai.create_tuned_model(
        display_name=display_name,
        source_model=base_model,
        training_data=training_file,
        epoch_count=3,
        batch_size=4,
        learning_rate=0.001,
    )

    # Wait for completion
    for status in operation.wait_bar():
        print(f"Tuning progress: {status}")

    result = operation.result()
    print(f"Fine-tuned model: {result.name}")

    return result.name


# Usage:
# 1. Collect training data
collector = TrainingDataCollector(supabase)
examples = await collector.collect_examples("customer_research")
collector.export_jsonl(examples, "training_data/customer_research.jsonl")

# 2. Fine-tune
model_name = fine_tune_model("training_data/customer_research.jsonl")

# 3. Use fine-tuned model
# In config.py:
# CUSTOMER_RESEARCH_MODEL = "tunedModels/product-discovery-agent-xxx"
```

### Best Practices for Fine-Tuning

1. **Quality over quantity:** 100 excellent examples > 1000 mediocre ones
2. **Diverse examples:** Cover different industries, product types
3. **Clean data:** Remove failed runs, fix formatting issues
4. **Iterative:** Fine-tune, evaluate, collect more data, repeat
5. **Evaluation set:** Hold out 10% of data for testing

### Measuring Fine-Tuning Success

```python
# scripts/evaluate_fine_tuned.py

async def evaluate_model(model_name: str, test_examples: list[dict]):
    """Evaluate fine-tuned model on held-out test set."""

    results = []

    for example in test_examples:
        # Generate output with fine-tuned model
        generated = await call_llm(
            prompt=json.dumps(example["input"]),
            model=model_name,
        )

        # Compare to expected output
        similarity = calculate_similarity(
            generated["data"],
            example["output"],
        )

        results.append({
            "example_id": example.get("id"),
            "similarity": similarity,
            "expected": example["output"],
            "generated": generated["data"],
        })

    # Calculate metrics
    avg_similarity = sum(r["similarity"] for r in results) / len(results)

    print(f"Average similarity: {avg_similarity:.2%}")
    print(f"Examples above 80%: {sum(1 for r in results if r['similarity'] > 0.8)}")

    return results
```

---

## 12. Detailed Fix #8: Retrieval-Augmented Generation (RAG)

### What is RAG?

RAG (Retrieval-Augmented Generation) means giving your LLM access to relevant documents when generating output.

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG PATTERN                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Query: "Analyze opportunity for farmers market app"       │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    RETRIEVAL STEP                         │   │
│  │                                                          │   │
│  │  Search your past successful outputs for:                │   │
│  │  - Similar product ideas                                 │   │
│  │  - Same industry (agriculture, retail)                   │   │
│  │  - Similar target market                                 │   │
│  │                                                          │   │
│  │  Found: 3 relevant past analyses                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   GENERATION STEP                         │   │
│  │                                                          │   │
│  │  Prompt: "Analyze this product. Here are similar         │   │
│  │           analyses for reference: [3 examples]"          │   │
│  │                                                          │   │
│  │  Output: Higher quality because LLM can see examples     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why RAG Helps

1. **Consistency:** Output follows patterns from successful examples
2. **Quality:** LLM sees what "good" looks like
3. **Domain knowledge:** Examples contain industry-specific insights
4. **Format compliance:** Examples show correct output structure

### Implementation with Embeddings

```python
# utils/rag.py (new file)

"""
RAG (Retrieval-Augmented Generation) for agent quality improvement.
"""

import numpy as np
from google import generativeai as genai


class RAGSystem:
    """
    Retrieval-Augmented Generation using embeddings.
    """

    def __init__(self, supabase):
        self.supabase = supabase
        self.embedding_model = "models/text-embedding-004"

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for text."""

        result = genai.embed_content(
            model=self.embedding_model,
            content=text,
            task_type="retrieval_document",
        )

        return result['embedding']

    async def store_example(
        self,
        session_id: str,
        agent_name: str,
        product_idea: str,
        output: dict,
        quality_score: float,
    ):
        """Store a successful example with its embedding."""

        # Create embedding from product idea
        embedding = await self.embed_text(product_idea)

        # Store in database
        self.supabase.table("rag_examples").insert({
            "session_id": session_id,
            "agent_name": agent_name,
            "product_idea": product_idea,
            "output": output,
            "quality_score": quality_score,
            "embedding": embedding,
        }).execute()

    async def retrieve_similar(
        self,
        product_idea: str,
        agent_name: str,
        limit: int = 3,
    ) -> list[dict]:
        """Retrieve similar examples for a product idea."""

        # Get embedding for query
        query_embedding = await self.embed_text(product_idea)

        # Search for similar (using pgvector in Supabase)
        # This requires setting up pgvector extension
        response = self.supabase.rpc(
            "match_examples",
            {
                "query_embedding": query_embedding,
                "agent_name": agent_name,
                "match_count": limit,
                "min_quality": 0.75,
            }
        ).execute()

        return response.data

    def format_examples_for_prompt(
        self,
        examples: list[dict],
        max_tokens: int = 4000,
    ) -> str:
        """Format retrieved examples for injection into prompt."""

        if not examples:
            return ""

        formatted = []
        current_tokens = 0

        for i, ex in enumerate(examples, 1):
            example_text = f"""
### EXAMPLE {i} (Quality Score: {ex['quality_score']:.0%})

**Product Idea:** {ex['product_idea']}

**Output:**
```json
{json.dumps(ex['output'], indent=2)[:2000]}
```
"""

            # Rough token estimate
            tokens = len(example_text) // 4

            if current_tokens + tokens > max_tokens:
                break

            formatted.append(example_text)
            current_tokens += tokens

        return """
╔══════════════════════════════════════════════════════════════════╗
║  REFERENCE: HIGH-QUALITY EXAMPLES FROM SIMILAR ANALYSES         ║
╚══════════════════════════════════════════════════════════════════╝

Use these examples as reference for format, depth, and quality.
Do NOT copy them directly - adapt to the current product idea.

""" + "\n".join(formatted)
```

### Database Setup for RAG

```sql
-- Supabase SQL for pgvector setup

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create examples table
CREATE TABLE rag_examples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    product_idea TEXT NOT NULL,
    output JSONB NOT NULL,
    quality_score FLOAT NOT NULL,
    embedding vector(768),  -- Gemini embedding dimension
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for similarity search
CREATE INDEX ON rag_examples
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Function for similarity search
CREATE OR REPLACE FUNCTION match_examples(
    query_embedding vector(768),
    agent_name TEXT,
    match_count INT,
    min_quality FLOAT
)
RETURNS TABLE (
    id UUID,
    product_idea TEXT,
    output JSONB,
    quality_score FLOAT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        rag_examples.id,
        rag_examples.product_idea,
        rag_examples.output,
        rag_examples.quality_score,
        1 - (rag_examples.embedding <=> query_embedding) AS similarity
    FROM rag_examples
    WHERE rag_examples.agent_name = match_examples.agent_name
      AND rag_examples.quality_score >= min_quality
    ORDER BY rag_examples.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### Using RAG in Agents

```python
# agents/customer_research.py

async def run_customer_research_agent(state: DiscoveryState) -> DiscoveryState:
    """Run customer research with RAG enhancement."""

    rag = RAGSystem(supabase)

    # Retrieve similar examples
    examples = await rag.retrieve_similar(
        product_idea=state["product_idea"],
        agent_name="customer_research",
        limit=3,
    )

    # Format examples for prompt
    examples_text = rag.format_examples_for_prompt(examples)

    # Build prompt with examples
    prompt = f"""
{examples_text}

---

Now analyze this product idea:

Product: {state["product_idea"]}
Industry: {state.get("industry", "Not specified")}

[Rest of your normal prompt...]
"""

    result = await call_llm(prompt, agent_name="Customer Research")

    # Store this run for future RAG (if quality is good)
    # This happens in finalize_node after critique

    return result
```

### Measuring RAG Impact

```python
# A/B test RAG vs non-RAG

async def run_with_ab_test(state):
    """Run agent with A/B test for RAG."""

    use_rag = random.random() < 0.5

    if use_rag:
        result = await run_customer_research_with_rag(state)
        state["_experiment"] = "rag"
    else:
        result = await run_customer_research_baseline(state)
        state["_experiment"] = "baseline"

    return result

# Later, analyze:
# SELECT _experiment, AVG(quality_score) FROM sessions GROUP BY _experiment
```

---

## 13. Detailed Fix #9: Confidence Calibration

### The Problem

LLMs are notoriously overconfident. When your agent says "confidence: 0.9", it might be wrong 50% of the time.

### What is Calibration?

A well-calibrated model:
- Claims 90% confidence → Right 90% of the time
- Claims 50% confidence → Right 50% of the time

```
┌─────────────────────────────────────────────────────────────────┐
│                   CALIBRATION VISUALIZATION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Confidence │        OVERCONFIDENT        │    WELL-CALIBRATED  │
│             │                              │                     │
│     0.9     │  ████████░░ (80% accurate) │  █████████░ (90%)   │
│     0.8     │  ██████░░░░ (60% accurate) │  ████████░░ (80%)   │
│     0.7     │  ████░░░░░░ (40% accurate) │  ███████░░░ (70%)   │
│     0.6     │  ███░░░░░░░ (30% accurate) │  ██████░░░░ (60%)   │
│                                                                  │
│  Your current agents are likely OVERCONFIDENT                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementing Calibration

```python
# utils/calibration.py (new file)

"""
Confidence calibration for agent claims.
"""

from collections import defaultdict


class CalibrationTracker:
    """
    Tracks and adjusts confidence scores based on actual accuracy.
    """

    def __init__(self, supabase):
        self.supabase = supabase

    async def record_outcome(
        self,
        claim_id: str,
        agent_name: str,
        claimed_confidence: float,
        was_accurate: bool,
    ):
        """Record the outcome of a claim for calibration."""

        # Bucket confidence into bins (0.9, 0.8, 0.7, etc.)
        confidence_bin = round(claimed_confidence, 1)

        self.supabase.table("calibration_data").insert({
            "claim_id": claim_id,
            "agent_name": agent_name,
            "confidence_bin": confidence_bin,
            "was_accurate": was_accurate,
        }).execute()

    async def get_calibration_curve(
        self,
        agent_name: str,
    ) -> dict[float, float]:
        """
        Get calibration curve for an agent.

        Returns: {confidence_bin: actual_accuracy}
        """

        response = self.supabase.rpc(
            "get_calibration",
            {"agent_name": agent_name}
        ).execute()

        return {
            row["confidence_bin"]: row["accuracy"]
            for row in response.data
        }

    def adjust_confidence(
        self,
        claimed_confidence: float,
        calibration_curve: dict[float, float],
    ) -> float:
        """
        Adjust confidence based on historical calibration.

        If agent says 0.9 but is only right 70% of the time,
        adjust to 0.7.
        """

        confidence_bin = round(claimed_confidence, 1)

        if confidence_bin in calibration_curve:
            return calibration_curve[confidence_bin]

        # Interpolate if exact bin not found
        bins = sorted(calibration_curve.keys())

        if not bins:
            return claimed_confidence * 0.8  # Default: reduce by 20%

        # Find nearest bins
        lower = max([b for b in bins if b <= confidence_bin], default=bins[0])
        upper = min([b for b in bins if b >= confidence_bin], default=bins[-1])

        if lower == upper:
            return calibration_curve[lower]

        # Linear interpolation
        weight = (confidence_bin - lower) / (upper - lower)
        return (
            calibration_curve[lower] * (1 - weight) +
            calibration_curve[upper] * weight
        )


# SQL function for calibration
"""
CREATE OR REPLACE FUNCTION get_calibration(agent_name TEXT)
RETURNS TABLE (confidence_bin FLOAT, accuracy FLOAT, sample_count INT)
LANGUAGE SQL
AS $$
    SELECT
        confidence_bin,
        AVG(CASE WHEN was_accurate THEN 1.0 ELSE 0.0 END) AS accuracy,
        COUNT(*) AS sample_count
    FROM calibration_data
    WHERE agent_name = get_calibration.agent_name
      AND created_at > NOW() - INTERVAL '30 days'  -- Recent data only
    GROUP BY confidence_bin
    HAVING COUNT(*) >= 10  -- Minimum samples
    ORDER BY confidence_bin;
$$;
"""
```

### Using Calibration in Agents

```python
# After agent generates output

async def calibrate_claims(claims: list[dict], agent_name: str) -> list[dict]:
    """Adjust claim confidences based on calibration data."""

    calibrator = CalibrationTracker(supabase)
    curve = await calibrator.get_calibration_curve(agent_name)

    calibrated_claims = []

    for claim in claims:
        original_confidence = claim.get("confidence", 0.5)
        calibrated_confidence = calibrator.adjust_confidence(
            original_confidence,
            curve,
        )

        calibrated_claim = {
            **claim,
            "confidence": calibrated_confidence,
            "_original_confidence": original_confidence,
        }

        calibrated_claims.append(calibrated_claim)

    return calibrated_claims
```

### Collecting Accuracy Data

To calibrate, you need to know what was accurate:

```python
# When a claim is verified or refuted

async def record_verification(
    claim_id: str,
    agent_name: str,
    claimed_confidence: float,
    verification_result: str,  # "verified" | "refuted" | "uncertain"
):
    """Record verification result for calibration."""

    was_accurate = verification_result == "verified"

    calibrator = CalibrationTracker(supabase)
    await calibrator.record_outcome(
        claim_id=claim_id,
        agent_name=agent_name,
        claimed_confidence=claimed_confidence,
        was_accurate=was_accurate,
    )
```

---

## 14. Detailed Fix #10: Human-in-the-Loop Patterns

### When to Ask for Human Input

Agents should ask for help when:

1. **Low confidence:** Uncertain about key decisions
2. **High stakes:** Decision has major impact
3. **Missing information:** Can't proceed without user input
4. **Conflicting signals:** Evidence points both ways

### Implementation

```python
# models/human_input.py (new file)

from enum import Enum
from pydantic import BaseModel


class InputPriority(str, Enum):
    BLOCKING = "blocking"      # Can't proceed without answer
    IMPORTANT = "important"    # Would significantly improve quality
    OPTIONAL = "optional"      # Nice to have


class HumanInputRequest(BaseModel):
    """Request for human input."""

    request_id: str
    agent_name: str
    question: str
    context: str
    options: list[str] | None  # If multiple choice
    priority: InputPriority
    default_if_skipped: str | None


class HumanInputResponse(BaseModel):
    """Response from human."""

    request_id: str
    answer: str
    skipped: bool


# agents/base_agent.py - Add human input capability

class AgentWithHumanInput:
    """Base class for agents that can request human input."""

    def __init__(self, emitter=None):
        self.emitter = emitter
        self.pending_inputs: list[HumanInputRequest] = []

    async def request_input(
        self,
        question: str,
        context: str,
        priority: InputPriority = InputPriority.IMPORTANT,
        options: list[str] | None = None,
        default: str | None = None,
    ) -> str:
        """
        Request input from human.

        If emitter is available (SSE streaming), sends request to frontend.
        Otherwise, uses default or raises error.
        """

        request = HumanInputRequest(
            request_id=f"input_{uuid.uuid4().hex[:8]}",
            agent_name=self.__class__.__name__,
            question=question,
            context=context,
            options=options,
            priority=priority,
            default_if_skipped=default,
        )

        if self.emitter:
            # Send to frontend and wait for response
            await self.emitter.emit_input_request(request.model_dump())

            # Wait for response (with timeout)
            response = await self._wait_for_response(
                request.request_id,
                timeout=300,  # 5 minutes
            )

            if response:
                return response.answer

        # No emitter or no response - use default
        if default is not None:
            return default

        if priority == InputPriority.BLOCKING:
            raise ValueError(f"Blocking input required: {question}")

        return ""

    async def _wait_for_response(
        self,
        request_id: str,
        timeout: int,
    ) -> HumanInputResponse | None:
        """Wait for human response via SSE."""

        # Implementation depends on your SSE architecture
        # This is a simplified version

        start = time.time()

        while time.time() - start < timeout:
            response = self.emitter.get_input_response(request_id)
            if response:
                return response
            await asyncio.sleep(1)

        return None
```

### Using Human Input in Agents

```python
# agents/business_case.py

class BusinessCaseAgent(AgentWithHumanInput):

    async def run(self, state: DiscoveryState) -> DiscoveryState:
        """Run business case analysis with human input when needed."""

        # Generate initial analysis
        analysis = await self._generate_analysis(state)

        # Check for low confidence areas
        if analysis.get("pricing_confidence", 1.0) < 0.5:
            # Ask human for input
            pricing_input = await self.request_input(
                question="What pricing strategy do you prefer?",
                context=f"""
                We analyzed your competitors and found:
                - Competitor A: $29/month
                - Competitor B: $49/month
                - Competitor C: Free with transaction fees

                Our analysis suggests {analysis['suggested_pricing']},
                but we're uncertain.
                """,
                options=[
                    "Match competitor A ($29/month)",
                    "Premium positioning ($49/month)",
                    "Freemium with transaction fees",
                    "Other (please specify)",
                ],
                priority=InputPriority.IMPORTANT,
                default=analysis['suggested_pricing'],
            )

            analysis['pricing'] = pricing_input
            analysis['pricing_source'] = "human_input"

        state['business_case'] = analysis
        return state
```

### Frontend Integration

```typescript
// frontend/src/hooks/useHumanInput.ts

interface InputRequest {
  request_id: string;
  agent_name: string;
  question: string;
  context: string;
  options?: string[];
  priority: 'blocking' | 'important' | 'optional';
}

export function useHumanInput(sessionId: string) {
  const [pendingRequests, setPendingRequests] = useState<InputRequest[]>([]);

  // Listen for input requests via SSE
  useEffect(() => {
    const eventSource = new EventSource(`/api/session/${sessionId}/stream`);

    eventSource.addEventListener('input_request', (event) => {
      const request = JSON.parse(event.data);
      setPendingRequests(prev => [...prev, request]);
    });

    return () => eventSource.close();
  }, [sessionId]);

  const submitResponse = async (requestId: string, answer: string) => {
    await fetch(`/api/session/${sessionId}/input/${requestId}`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    });

    setPendingRequests(prev =>
      prev.filter(r => r.request_id !== requestId)
    );
  };

  return { pendingRequests, submitResponse };
}
```

### When NOT to Ask

Avoid asking too many questions:

```python
# Limit to 3 questions per session
MAX_QUESTIONS_PER_SESSION = 3

async def request_input_with_limit(self, ...):
    if self.questions_asked >= MAX_QUESTIONS_PER_SESSION:
        return default

    self.questions_asked += 1
    return await self.request_input(...)
```

---

## 15. Implementation Roadmap

### Phase 1: Quick Wins (Week 1)

| Task | Effort | Impact |
|------|--------|--------|
| Inject critique feedback into revision prompts | 2 hours | High |
| Lower quality threshold to 0.6 | 10 min | Medium |
| Add refuse-if-below-0.4 logic | 30 min | Medium |

### Phase 2: Core Improvements (Weeks 2-3)

| Task | Effort | Impact |
|------|--------|--------|
| Two-stage grounded calls | 1 day | High |
| Self-reflection for top 3 agents | 2 days | High |
| Consistency checker agent | 1 day | Medium |
| RAG with embeddings | 2 days | High |

### Phase 3: Advanced Features (Weeks 4-6)

| Task | Effort | Impact |
|------|--------|--------|
| Evidence verification | 3 days | Medium |
| Hierarchical PRD generation | 2 days | Medium |
| Confidence calibration | 2 days | Medium |
| Human-in-the-loop | 3 days | Medium |

### Phase 4: Optimization (Ongoing)

| Task | Effort | Impact |
|------|--------|--------|
| Fine-tuning data collection | Ongoing | High |
| Fine-tune Flash model | 1 week | High |
| A/B testing infrastructure | 2 days | Medium |
| Performance monitoring | 1 day | Medium |

---

## 16. Measuring Success

### Key Metrics

```python
# utils/metrics.py

class QualityMetrics:
    """Track quality metrics over time."""

    def calculate_metrics(self, sessions: list[dict]) -> dict:
        return {
            # Quality scores
            "avg_quality_score": np.mean([s["quality_score"] for s in sessions]),
            "quality_above_70": len([s for s in sessions if s["quality_score"] >= 0.7]) / len(sessions),

            # Iteration efficiency
            "avg_iterations": np.mean([s["iterations"] for s in sessions]),
            "first_pass_success": len([s for s in sessions if s["iterations"] == 1]) / len(sessions),

            # Claim quality
            "verified_claim_ratio": self._calc_verified_ratio(sessions),
            "avg_evidence_score": np.mean([s["evidence_score"] for s in sessions]),

            # Consistency
            "avg_consistency_score": np.mean([s.get("consistency_score", 0) for s in sessions]),

            # Cost efficiency
            "avg_tokens_per_session": np.mean([s["total_tokens"] for s in sessions]),
            "tokens_per_quality_point": self._calc_token_efficiency(sessions),
        }
```

### Success Criteria

| Metric | Current | Target | Excellent |
|--------|---------|--------|-----------|
| Avg Quality Score | 0.45 | 0.70 | 0.85 |
| First Pass Success | 10% | 40% | 60% |
| Verified Claim Ratio | 0% | 50% | 80% |
| Avg Iterations | 3 | 1.5 | 1.2 |

---

## 17. Common Pitfalls to Avoid

### Pitfall 1: Over-Engineering

**Wrong:** Build all 10 fixes before testing any
**Right:** Implement one fix, measure impact, iterate

### Pitfall 2: Ignoring Costs

**Wrong:** Add self-reflection to every agent
**Right:** Add self-reflection to high-impact agents only

### Pitfall 3: Prompt Tunnel Vision

**Wrong:** Spend weeks perfecting prompts
**Right:** Good prompts + good architecture > perfect prompts

### Pitfall 4: No Baseline

**Wrong:** Make changes without measuring first
**Right:** Establish metrics baseline, then improve

### Pitfall 5: Trusting the LLM

**Wrong:** Assume high confidence = high accuracy
**Right:** Verify claims, calibrate confidence, stay skeptical

---

## 18. Further Reading & Resources

### Papers

1. **ReAct: Synergizing Reasoning and Acting in Language Models** (2022)
   - Foundation for agentic reasoning patterns

2. **Constitutional AI** (Anthropic, 2022)
   - Self-critique and improvement techniques

3. **Chain-of-Thought Prompting** (Google, 2022)
   - Step-by-step reasoning for better outputs

### Tools & Libraries

1. **LangChain:** Framework for building LLM applications
2. **LlamaIndex:** Data framework for LLM applications
3. **Guidance:** Constrained generation from Microsoft
4. **DSPy:** Programming (not prompting) LLMs

### Communities

1. **r/LocalLLaMA:** Reddit community for LLM practitioners
2. **LangChain Discord:** Active community for agent builders
3. **Anthropic Discord:** Claude-specific discussions

---

## Conclusion

Building high-quality agent systems is an iterative process. The key insights are:

1. **Agents need feedback:** They can't improve without knowing what's wrong
2. **Verify, don't trust:** LLMs hallucinate; always verify important claims
3. **Decompose complex tasks:** Smaller, focused calls beat monolithic prompts
4. **Learn from success:** Use your good outputs to improve future runs
5. **Measure everything:** You can't improve what you don't measure

Start with the quick wins (feedback injection, quality thresholds), then progressively add more sophisticated capabilities. Each improvement compounds on the previous ones.

Good luck building!

---

*This guide was generated by Claude to help you improve your Product Discovery Multi-Agent System. For questions or updates, continue our conversation.*
