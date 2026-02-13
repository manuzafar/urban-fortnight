"""
Wireframe Agent — generates React screen wireframes from PRD.

This agent creates grayscale wireframe screens based on the PRD's
screen map and user stories. Uses React/Tailwind for rendering.
"""

import json
from datetime import datetime

import structlog

from agents.base_agent import call_llm
from agents.context_builder import build_context_summary
from agents.state import DiscoveryState
from models.schemas import SessionStatus

logger = structlog.get_logger(__name__)

AGENT_NAME = "Wireframe Designer"

WIREFRAME_PROMPT = """You are a senior UI/UX designer at a top product design agency. You create wireframes that communicate information architecture and user flow clearly — not pixel-perfect designs, but structural layouts that make the product's UX immediately understandable.

## PRODUCT IDEA
{product_idea}

## PRODUCT REQUIREMENTS — SCREEN MAP
{screen_map}

## USER STORIES (your wireframes must support these exact flows)
{user_stories}

## PERSONAS (use realistic data that matches these people)
{personas_summary}

## TECHNICAL ARCHITECTURE — DATA MODEL (your wireframes must show data that exists)
{data_model}

## YOUR TASK

Generate one React/JSX wireframe component per screen in the screen map. Each wireframe must:

1. Be a complete, self-contained React functional component with default export
2. Use ONLY Tailwind CSS utility classes — no custom CSS, no CSS-in-JS
3. Use a grayscale palette: bg-white, bg-gray-50, bg-gray-100, bg-gray-200, border-gray-200, border-gray-300, text-gray-900, text-gray-600, text-gray-400
4. Include realistic placeholder data derived from the data model and personas — NOT "Lorem ipsum" or "Item 1, Item 2"
5. Show proper layout structure: navigation/header, sidebar (if applicable), main content, footer
6. Use Lucide React icons where appropriate: import {{ Search, Bell, Settings, ChevronRight, Plus, Filter, BarChart3, Users, FileText, AlertTriangle }} from 'lucide-react'
7. Include onClick handlers as comments showing intended behaviour: {{/* onClick: navigate to /forecast/{{id}} */}}
8. NO external API calls, NO useState/useEffect (these are static wireframes), NO routing
9. Be 80-150 lines of clean JSX

## REALISTIC DATA EXAMPLES

For a fintech cash flow tool, DON'T use:
- "Item 1", "User A", "Category"
- "$XXX", "NN%", "Date"

DO use:
- "Melbourne Plumbing Co.", "Sarah Chen — CFO", "Operating Expenses"
- "$47,250", "12.3% above forecast", "Due: 15 Mar 2026"

The data should tell the product's story. When a stakeholder sees the wireframe, they should immediately understand what the product does and for whom.

## ALSO GENERATE: USER FLOW DIAGRAMS

For 2-3 key user journeys, generate Mermaid flowchart diagrams:

```
flowchart TD
    A[User opens dashboard S1] --> B{{Has existing forecasts?}}
    B -->|Yes| C[View forecast list S1]
    B -->|No| D[Empty state with CTA S1]
    C --> E[Click forecast S2]
    E --> F[View forecast detail S2]
    F --> G[Click 'Take Action' S3]
    G --> H[Action recommendation panel S3]
```

Each flow must:
- Reference screen IDs from the screen map (S1, S2, etc.)
- Show decision points with diamond shapes
- Follow one specific persona through a realistic scenario
- Include both happy path and one error/edge case path

## OUTPUT FORMAT

Return valid JSON:

{{
  "screens": [
    {{
      "screen_id": "S1",
      "screen_name": "Dashboard",
      "purpose": "string - what this screen accomplishes",
      "user_stories_covered": ["US-001", "US-002"],
      "key_components": ["Header with navigation", "Data cards", "Action buttons"],
      "navigation_to": ["S2", "S3"],
      "react_code": "import {{ Search, Bell, Settings }} from 'lucide-react';\\n\\nexport default function Dashboard() {{\\n  return (\\n    <div className=\\"min-h-screen bg-gray-50\\">\\n      ...\\n    </div>\\n  );\\n}}",
      "notes": "Design decisions: used card layout for forecasts because persona needs quick scanning"
    }}
  ],
  "user_flows": [
    {{
      "flow_name": "New User Creates First Forecast",
      "persona": "Sarah Chen",
      "mermaid_code": "flowchart TD\\n    A[Open Dashboard] --> B{{Has forecasts?}}\\n    B -->|No| C[Empty State]\\n    C --> D[Click Create]",
      "screens_referenced": ["S1", "S2", "S4"],
      "notes": "Happy path takes 3 clicks from dashboard to first forecast"
    }}
  ],
  "user_flow_description": "string - overall user flow description",
  "user_flow_mermaid": "string - combined Mermaid diagram",
  "design_system_notes": [
    "Typography: text-2xl for headings, text-sm for metadata",
    "Spacing: space-y-4 between sections, p-4 for cards",
    "Icons: Lucide React for all icons"
  ],
  "responsive_notes": "string - how screens should adapt to mobile"
}}

## OUTPUT CHECKLIST (MANDATORY)

Before finalizing your response, verify ALL of the following:

[ ] SCREEN COUNT: 3+ screens minimum
[ ] REACT CODE: 70%+ screens have react_code with valid JSX (80+ lines each)
[ ] NAVIGATION: Each screen has navigation_to array with target screen IDs
[ ] KEY COMPONENTS: Each screen lists 3-5 key_components
[ ] USER FLOWS: 2-3 Mermaid flowchart user_flows with screens_referenced
[ ] CORE SCREENS: MUST include Dashboard or Landing screen
[ ] DESIGN SYSTEM: design_system_notes with typography and spacing
[ ] NO PLACEHOLDERS: No "Lorem ipsum", "Item 1", "TODO" in react_code
[ ] VALID REACT: Each react_code is a complete, renderable component

## CRITICAL REMINDERS
- Generate one wireframe per screen in the screen_map. Don't skip screens.
- Wireframes must be STRUCTURALLY complete — header, nav, content area, proper spacing.
- Data must be REALISTIC and tell the product story. No placeholder text.
- Tailwind only. No inline styles. No className strings that aren't real Tailwind classes.
- User flows must reference actual screen IDs.
- These wireframes will be rendered in a sandboxed iframe — they must be valid, renderable React.
"""


async def run_wireframe_agent(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the Wireframe Designer Agent.

    Creates wireframe screens based on the PRD screen map and user stories.

    Args:
        state: Current discovery state with product_requirements.

    Returns:
        DiscoveryState: Updated state with wireframes.
    """
    logger.info(
        "agent_start",
        agent=AGENT_NAME,
        session_id=state["session_id"],
    )

    state["current_agent"] = AGENT_NAME
    state["status"] = SessionStatus.IN_PROGRESS
    state["updated_at"] = datetime.utcnow().isoformat()

    # Get PRD data
    prd = state.get("product_requirements", {})
    screen_map = prd.get("screen_map", [])
    if not screen_map:
        # Generate screen map from epics if not present
        epics = prd.get("epics", [])
        screen_map = _extract_screens_from_epics(epics)

    # Get user stories
    user_stories = _extract_user_stories(prd)

    # Get data model from tech architecture
    tech_arch = state.get("technical_architecture", {})
    data_model = tech_arch.get("data_model", tech_arch.get("data_storage", "Not available"))

    # Get personas summary for realistic data
    personas = state.get("detailed_personas", {})
    personas_summary = build_context_summary(state, "detailed_personas", 1500)

    prompt = WIREFRAME_PROMPT.format(
        product_idea=state["product_idea"],
        screen_map=json.dumps(screen_map, indent=2, default=str),
        user_stories=json.dumps(user_stories[:15], indent=2, default=str),  # Limit to 15
        personas_summary=personas_summary,
        data_model=json.dumps(data_model, indent=2, default=str)[:2000],
    )

    result = await call_llm(prompt, AGENT_NAME)

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        state["wireframes"] = result["data"]

        screens = result["data"].get("screens", [])
        logger.info(
            "agent_success",
            agent=AGENT_NAME,
            session_id=state["session_id"],
            screens_generated=len(screens),
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
        state["wireframes"] = {
            "screens": [],
            "user_flow_description": "Wireframe generation failed",
            "error": error_msg,
        }

    state["updated_at"] = datetime.utcnow().isoformat()
    return state


def _extract_screens_from_epics(epics: list) -> list[dict]:
    """Extract potential screens from epics and stories."""
    screens = []
    screen_id = 1

    for epic in epics[:5]:  # Limit to first 5 epics
        screens.append({
            "screen_id": f"S{screen_id}",
            "name": epic.get("title", f"Screen {screen_id}"),
            "purpose": epic.get("description", ""),
        })
        screen_id += 1

    return screens


def _extract_user_stories(prd: dict) -> list[dict]:
    """Extract user stories from PRD."""
    stories = []

    for epic in prd.get("epics", []):
        for story in epic.get("stories", []):
            stories.append({
                "id": story.get("id", ""),
                "title": story.get("title", ""),
                "as_a": story.get("as_a", ""),
                "i_want": story.get("i_want", ""),
                "so_that": story.get("so_that", ""),
            })

    return stories
