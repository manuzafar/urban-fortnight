"""
Prototype Agent — generates single interactive React component.

This agent creates a polished, interactive prototype based on wireframes.
Uses full color, typography, and interactive elements.
"""

import json
from datetime import datetime

import structlog

from agents.base_agent import call_llm
from agents.context_builder import build_context_summary
from agents.state import DiscoveryState
from models.schemas import SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Prototype Generator"

PROTOTYPE_PROMPT = """You are a senior frontend engineer and product designer building an interactive prototype that will be shown to investors and enterprise stakeholders. This prototype must look and feel like a REAL PRODUCT — not a wireframe, not a mockup. When someone clicks through it, they should forget they're looking at a prototype.

## PRODUCT IDEA
{product_idea}

## INDUSTRY
{industry}

## WIREFRAMES (your prototype must implement these screens with full visual polish)
{wireframe_summary}

## PRIMARY PERSONA (your prototype tells THIS person's story)
{primary_persona}

## KEY USER STORY (the prototype walks through THIS journey)
{key_user_story}

## DATA MODEL (use realistic data based on these entities)
{data_model_summary}

## YOUR TASK

Generate a SINGLE React component (300-600 lines) that implements an interactive prototype with:

### VISUAL REQUIREMENTS
1. **Looks like a shipping product.** Professional colour palette appropriate to the industry:
   - Fintech/Banking: Navy (#1a365d), forest green for positive, muted red for alerts, white backgrounds, subtle gray borders
   - Healthcare: Calming blues (#2b6cb0), soft teals, warm grays, generous whitespace
   - B2B SaaS: Professional grays, single strong accent colour (#4f46e5 indigo or #2563eb blue), clean borders
   - Insurance: Deep blue (#1e3a5f), gold accents, authoritative typography

2. **Typography hierarchy:**
   - Use system fonts: `font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
   - Clear hierarchy: text-2xl font-bold for page titles, text-lg font-semibold for section headers, text-sm text-gray-500 for metadata

3. **Micro-interactions:**
   - Hover states on all clickable elements (hover:bg-gray-50, hover:shadow-md)
   - Active states for current navigation items
   - Transition effects: transition-all duration-200

4. **Layout polish:**
   - Proper sidebar navigation with active state indication
   - Content area with appropriate max-width and padding
   - Cards with subtle shadows (shadow-sm) and borders
   - Proper spacing rhythm (space-y-6 for major sections, space-y-3 for related items)

### INTERACTIVITY REQUIREMENTS
1. Use useState for navigation between 3-5 screens
2. Current screen state: `const [currentScreen, setCurrentScreen] = useState('dashboard')`
3. Clickable navigation items that change screens
4. At least one data-rich screen (table, chart representation, or detail view)
5. At least one form/input screen (even if it doesn't submit — show the UI)
6. Smooth transitions between screens

### DATA REQUIREMENTS
1. ALL data must be realistic and tell the product story
2. Use the primary persona's context: their company name, their metrics, their scenarios
3. For charts, use realistic-looking data arrays (no Chart.js needed — use styled divs for bar charts or Tailwind to create visual representations)
4. For tables, show 5-8 rows of realistic data
5. Numbers must be plausible: "$47,250 projected shortfall" not "$999,999"

### STORY REQUIREMENTS
The prototype MUST walk through a narrative:
1. **Screen 1 (Dashboard):** The persona logs in and sees their overview. Something catches their attention — an alert, a metric, a notification.
2. **Screen 2 (Detail):** They drill into the item that caught their attention. They see the full picture.
3. **Screen 3 (Action):** They take action — create something, configure something, approve something.
4. **Screen 4+ (Result/Confirmation):** The result of their action. The "aha moment" — the product just did something valuable.

### TECHNICAL CONSTRAINTS
- Single functional component with default export
- Import React and useState: `import React, {{ useState }} from 'react'`
- Import Lucide icons as needed: `import {{ Home, Settings, AlertTriangle, TrendingUp, Check }} from 'lucide-react'`
- Tailwind CSS only — no custom CSS, no styled-components
- No external API calls
- No localStorage or sessionStorage
- No external dependencies beyond React, Tailwind, Lucide
- 300-600 lines total — quality over quantity

## OUTPUT FORMAT

Return valid JSON:

{{
  "prototype_name": "string - name of this prototype",
  "primary_persona": "string - Name — role",
  "key_user_story": "string - what journey it demonstrates",
  "color_palette": {{
    "primary": "#hex - primary brand color",
    "secondary": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "text": "#hex"
  }},
  "react_component_code": "import React, {{ useState }} from 'react';\\nimport {{ Home, Settings }} from 'lucide-react';\\n\\nexport default function Prototype() {{\\n  const [screen, setScreen] = useState('dashboard');\\n  ...\\n}}",
  "screens_included": ["dashboard", "detail", "action", "confirmation"],
  "story_summary": "string - In 2-3 sentences, what story does this prototype tell? What's the 'aha moment'?",
  "css_code": "string - any additional CSS if needed (usually empty with Tailwind)",
  "state_management_notes": "string - what state is managed and why",
  "interactivity_notes": [
    "string - interactive feature 1",
    "string - interactive feature 2"
  ],
  "demo_scenario": "string - step-by-step demo script walking through the narrative",
  "design_notes": "string - key design decisions and why"
}}

## OUTPUT CHECKLIST (MANDATORY)

Before finalizing your response, verify ALL of the following:

[ ] PROTOTYPE NAME: Named prototype (not placeholder)
[ ] REACT CODE: react_component_code with 100+ chars of valid React
[ ] VALID REACT STRUCTURE:
    - function/const component definition with default export
    - JSX return statement
    - useState for state management (navigation between screens)
[ ] INTERACTIVE ELEMENTS: onClick, onSubmit, buttons, or forms present
[ ] NO PLACEHOLDERS: No "Lorem ipsum", "TODO", "TBD", "placeholder", "Item 1"
[ ] PRIMARY PERSONA: Target persona specified (actual name from research)
[ ] KEY USER STORY: 20+ char user story description
[ ] DEMO SCENARIO: 30+ char walkthrough script
[ ] COLOR PALETTE: Defined with primary, secondary, background colors
[ ] SCREENS INCLUDED: 3+ screens in screens_included array

## CRITICAL REMINDERS
- This must look like a REAL PRODUCT. If it looks like gray boxes with placeholder text, it fails.
- The story matters. The prototype walks a persona through a journey that ends with an "aha" moment.
- Use the ACTUAL persona name and company from the personas section. Not "User" or "Acme Corp."
- Navigation must WORK. Clicking sidebar items must change screens.
- Data must be REALISTIC. Not round numbers, not placeholder text, not "Item 1."
- Colour palette must match the industry. A fintech prototype should not look like a healthcare app.
- This prototype will be rendered in a sandboxed iframe — it must be valid, renderable React with no external dependencies.
"""


async def run_prototype_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Prototype Generator Agent.

    Creates a polished, interactive prototype based on wireframes.
    Runs AFTER wireframe agent.

    Args:
        state: Current discovery state with wireframes.

    Returns:
        DiscoveryState: Updated state with prototype.
    """
    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Get wireframes
    wireframes = state.get("wireframes", {})
    wireframe_summary = _summarize_wireframes(wireframes)

    # Get primary persona
    personas = state.get("detailed_personas", {})
    primary_persona = personas.get("primary_persona", {})
    persona_summary = json.dumps(primary_persona, indent=2, default=str)[:1500]

    # Get key user story
    prd = state.get("product_requirements", {})
    key_story = _get_key_user_story(prd)

    # Get data model summary for realistic data
    tech_arch = state.get("technical_architecture", {})
    data_model = tech_arch.get("data_model", tech_arch.get("data_storage", "Not available"))
    data_model_summary = json.dumps(data_model, indent=2, default=str)[:1500]

    # Get industry
    industry = state.get("industry", "Not specified")

    prompt = PROTOTYPE_PROMPT.format(
        product_idea=state["product_idea"],
        industry=industry,
        wireframe_summary=wireframe_summary,
        primary_persona=persona_summary,
        key_user_story=json.dumps(key_story, indent=2, default=str),
        data_model_summary=data_model_summary,
    )

    result = await call_llm(prompt, AGENT_NAME)

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["prototype"] = result["data"]

        logger.info(
            "agent_success",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            prototype_name=result["data"].get("prototype_name", "Unnamed"),
        )
    else:
        error_msg = result.get("error", "Unknown error")
        logger.error(
            "agent_failed",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            error=error_msg,
        )
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"{AGENT_NAME}: {error_msg}")

        # Create minimal fallback
        state["prototype"] = {
            "prototype_name": "Prototype generation failed",
            "error": error_msg,
        }

    state["updated_at"] = datetime.utcnow().isoformat()
    return state


def _summarize_wireframes(wireframes: dict) -> str:
    """Create a summary of wireframes for the prototype prompt."""
    screens = wireframes.get("screens", [])
    if not screens:
        return "No wireframes available."

    summary_parts = []
    for screen in screens[:5]:
        summary_parts.append(
            f"- {screen.get('screen_id', '?')}: {screen.get('screen_name', 'Unknown')} - "
            f"{screen.get('purpose', 'No purpose')}"
        )

    flow = wireframes.get("user_flow_description", "")
    summary = "**Screens:**\n" + "\n".join(summary_parts)
    if flow:
        summary += f"\n\n**User Flow:** {flow}"

    return summary


def _get_key_user_story(prd: dict) -> dict:
    """Get the most important user story from the PRD."""
    epics = prd.get("epics", [])

    # Try to find a critical or high priority story
    for epic in epics:
        for story in epic.get("stories", []):
            priority = story.get("priority", "").lower()
            if priority in ("critical", "high"):
                return {
                    "id": story.get("id", ""),
                    "title": story.get("title", ""),
                    "as_a": story.get("as_a", ""),
                    "i_want": story.get("i_want", ""),
                    "so_that": story.get("so_that", ""),
                }

    # Fall back to first story
    if epics and epics[0].get("stories"):
        story = epics[0]["stories"][0]
        return {
            "id": story.get("id", ""),
            "title": story.get("title", ""),
            "as_a": story.get("as_a", ""),
            "i_want": story.get("i_want", ""),
            "so_that": story.get("so_that", ""),
        }

    return {"title": "Core user journey", "i_want": "see the main value proposition"}
