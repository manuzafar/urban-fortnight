# Phase 6: Design Agents — Wireframes + Prototype

**Goal:** Generate interactive wireframe screens and a working prototype as React/JSX components.

**Dependencies:** Phases 1-4 (needs PRD with screen_map, Tech Arch with data_model, Personas)

---

## 6.1 Wireframe Agent

**File:** `backend/agents/wireframe_agent.py` (NEW)

→ **Prompt:** `seedcraft-v3-prompts/14-wireframe-agent.md`

```python
"""
Wireframe Agent — generates React wireframe screens from PRD + Tech Architecture.

Inputs:
  - PRD: screen_map, user_stories, epics
  - Technical Architecture: data_model
  - Customer Personas: names, roles, JTBD

Output: state["wireframes"] — WireframeSet with 5-8 screens + user flows
Model: Flash
"""

import json
import structlog
from datetime import datetime
from agents.base_agent import call_llm
from agents.context_builder import build_context_summary

logger = structlog.get_logger("wireframe_agent")

# ═══════════════════════════════════════════════════════════
# Copy from seedcraft-v3-prompts/14-wireframe-agent.md
# ═══════════════════════════════════════════════════════════
WIREFRAME_AGENT_PROMPT = """..."""  # ← REPLACE WITH FULL PROMPT


async def run_wireframe_agent(state: dict) -> dict:
    """Generate wireframe screens as React components."""
    logger.info("wireframe_agent_start", session_id=state.get("session_id"))

    prd = state.get("product_requirements", {})

    # Extract screen_map for the prompt
    screen_map = json.dumps(prd.get("screen_map", []), indent=2, default=str)

    # Extract user stories (flatten from epics), truncate to fit prompt
    all_stories = []
    for epic in prd.get("epics", []):
        for story in epic.get("user_stories", []):
            all_stories.append({
                "story_id": story.get("story_id"),
                "persona": story.get("persona"),
                "story": story.get("story"),
                "screen_references": story.get("screen_references", []),
                "priority": story.get("priority"),
            })
    user_stories_str = json.dumps(all_stories[:20], indent=2, default=str)[:6000]

    # Extract data model
    data_model = state.get("technical_architecture", {}).get("data_model", {})
    data_model_str = json.dumps(data_model, indent=2, default=str)[:4000]

    prompt = WIREFRAME_AGENT_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        screen_map=screen_map,
        user_stories=user_stories_str,
        personas_summary=build_context_summary(state, "detailed_personas", 2000),
        data_model=data_model_str,
    )

    result = await call_llm(prompt, "Wireframe Designer")

    if result["success"]:
        state["wireframes"] = result["data"]
        screen_count = len(result["data"].get("screens", result["data"].get("wireframes", [])))
        logger.info("wireframe_agent_complete", screen_count=screen_count)
    else:
        logger.error("wireframe_agent_failed", error=result.get("error"))

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

---

## 6.2 Prototype Agent

**File:** `backend/agents/prototype_agent.py` (NEW)

→ **Prompt:** `seedcraft-v3-prompts/15-prototype-agent.md`

**Critical:** Runs AFTER wireframes (sequential). The prototype takes wireframe layouts and applies visual polish, colour, interactive navigation, and realistic data.

```python
"""
Prototype Agent — generates a single interactive React component.

This is the "holy shit" moment. The prototype should look like a real product,
not a wireframe. Colour, typography, realistic data, smooth interactions.

Inputs:
  - Wireframes: screen layouts and component structure
  - PRD: user stories and core journey
  - Technical Architecture: data model for realistic data
  - Customer Personas: who we're designing for

Output: state["prototype"] — single React/JSX component
Model: Pro (needs strong code generation + design reasoning)
"""

import json
import structlog
from datetime import datetime
from agents.base_agent import call_llm
from agents.context_builder import build_context_summary

logger = structlog.get_logger("prototype_agent")

# ═══════════════════════════════════════════════════════════
# Copy from seedcraft-v3-prompts/15-prototype-agent.md
# ═══════════════════════════════════════════════════════════
PROTOTYPE_AGENT_PROMPT = """..."""  # ← REPLACE WITH FULL PROMPT


def _summarize_wireframes(wireframes: dict) -> str:
    """Extract key layout info from wireframes for the prototype prompt."""
    screens = wireframes.get("screens", wireframes.get("wireframes", []))
    parts = []
    for s in screens[:6]:
        if isinstance(s, dict):
            sid = s.get("screen_id", "?")
            name = s.get("screen_name", "?")
            stype = s.get("screen_type", "?")
            components = [c.get("component_type", "?") for c in s.get("components", [])]
            parts.append(f"  {sid} ({name}, {stype}): {', '.join(components)}")
    return "Wireframe screens:\n" + "\n".join(parts) if parts else "No wireframes available"


async def run_prototype_agent(state: dict) -> dict:
    """Generate working interactive prototype."""
    logger.info("prototype_agent_start", session_id=state.get("session_id"))

    wireframes = state.get("wireframes", {})
    personas = state.get("detailed_personas", {})
    prd = state.get("product_requirements", {})
    tech_arch = state.get("technical_architecture", {})

    # Get primary persona
    persona_list = personas.get("personas", [])
    primary_persona = json.dumps(persona_list[0], indent=2, default=str)[:3000] if persona_list else "{}"

    # Get first epic's first user story as the key journey
    epics = prd.get("epics", [])
    first_story = "{}"
    if epics and epics[0].get("user_stories"):
        first_story = json.dumps(epics[0]["user_stories"][0], indent=2, default=str)[:2000]

    prompt = PROTOTYPE_AGENT_PROMPT.format(
        product_idea=state["product_idea"],
        industry=state.get("industry", ""),
        wireframe_summary=_summarize_wireframes(wireframes),
        primary_persona=primary_persona,
        key_user_story=first_story,
        data_model_summary=json.dumps(
            tech_arch.get("data_model", {}), indent=2, default=str
        )[:3000],
    )

    result = await call_llm(prompt, "Prototype Generator")

    if result["success"]:
        state["prototype"] = result["data"]
        logger.info("prototype_agent_complete")
    else:
        logger.error("prototype_agent_failed", error=result.get("error"))

    state["updated_at"] = datetime.utcnow().isoformat()
    return state
```

---

## 6.3 Add SSE Events

**File:** `backend/utils/sse.py` (MODIFY)

```python
class StreamEventType(str, Enum):
    # ... existing events ...
    WIREFRAME_READY = "wireframe_ready"
    PROTOTYPE_READY = "prototype_ready"
    DESIGN_PHASE = "design_phase"
```

---

## Test Phase 6

1. Verify `state["wireframes"]` contains 5-8 screens with non-empty `react_code`
2. Copy one screen's `react_code` to a React playground — verify it renders
3. Verify screens reference PRD screen_ids (S1, S2, etc.)
4. Verify user flows have valid Mermaid diagram syntax
5. Verify wireframes use grayscale palette only (bg-gray-*, text-gray-*, border-gray-*)
6. Verify data in wireframes is realistic (not "Lorem ipsum" or "John Doe")
7. Verify `state["prototype"]` contains a single React component with `useState` navigation
8. Verify prototype has colour, typography, and looks like a real product
9. Verify prototype uses data from the primary persona's context
