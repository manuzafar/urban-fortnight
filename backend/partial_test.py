"""
Partial Test - Planning, Discovery, Strategy phases only
Uses the facilitator approach but stops early
"""

import asyncio
from datetime import datetime

from agents.state import DiscoveryState
from agents.planner import run_planner_agent
from agents.swarms import DiscoverySwarm, StrategySwarm
from agents.constraint_broadcaster import generate_phase_constraints

import structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
)


async def run_partial_test():
    """Run planning, discovery, and strategy phases."""

    print("=" * 70)
    print("PARTIAL TEST: Planning + Discovery + Strategy")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    product_idea = "Mobile app for local farmers markets to manage inventory, track sales, and accept digital payments"
    session_id = f"partial_{datetime.now().strftime('%H%M%S')}"
    industry = "Agriculture/Retail"
    target_market = "Small farmers market vendors"

    print(f"Session ID: {session_id}")
    print(f"Product Idea: {product_idea[:60]}...")
    print()

    # Initialize state
    state: DiscoveryState = {
        "session_id": session_id,
        "product_idea": product_idea,
        "target_market": target_market,
        "industry": industry,
        "company_size": None,
        "tech_stack": None,
        "budget_range": None,
        "timeline": None,
        "funding_stage": None,
        "regulations": [],
        "stakeholders": [],
    }

    # Phase 1: Planning
    print("=" * 70)
    print("PHASE 1: PLANNING")
    print("=" * 70)

    state = await run_planner_agent(state)
    planning_result = state.get("planning_context", {})

    print(f"\n✓ Planning complete")
    print(f"  - Domain type: {planning_result.get('domain_type', 'N/A')}")
    print(f"  - Questions: {len(planning_result.get('critical_questions', []))}")
    print(f"  - Competitors to analyze: {len(planning_result.get('competitors_to_analyze', []))}")
    print()

    # Phase 2: Discovery Swarm
    print("=" * 70)
    print("PHASE 2: DISCOVERY SWARM")
    print("=" * 70)

    discovery_swarm = DiscoverySwarm()
    state = await discovery_swarm.run(state)

    print(f"\n✓ Discovery Swarm complete")
    print(f"  - Customer Research: {'✓' if state.get('customer_research') else '✗'}")
    print(f"  - Competitive Analysis: {'✓' if state.get('competitive_analysis') else '✗'}")
    print(f"  - Personas: {'✓' if state.get('detailed_personas') else '✗'}")
    print()

    # Phase 3: Strategy Swarm
    print("=" * 70)
    print("PHASE 3: STRATEGY SWARM")
    print("=" * 70)

    # Generate constraints from discovery
    strategy_constraints = await generate_phase_constraints(state, target_phase="strategy")
    print(f"  - Constraints injected: {len(strategy_constraints)}")
    state["upstream_constraints"] = strategy_constraints

    strategy_swarm = StrategySwarm()
    state = await strategy_swarm.run(state)

    print(f"\n✓ Strategy Swarm complete")
    print(f"  - Business Case: {'✓' if state.get('business_case') else '✗'}")
    print(f"  - GTM Strategy: {'✓' if state.get('gtm_strategy') else '✗'}")
    print(f"  - Financial Model (from swarm): {'✓' if state.get('financial_model') else '✗'}")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    sections = [
        "planning_context",
        "customer_research",
        "competitive_analysis",
        "detailed_personas",
        "business_case",
        "gtm_strategy",
        "financial_model",
    ]

    print(f"\nGenerated sections:")
    for key in sections:
        val = state.get(key)
        if val:
            if isinstance(val, dict):
                print(f"  ✓ {key} ({len(val)} keys)")
            else:
                print(f"  ✓ {key}")
        else:
            print(f"  ✗ {key}")

    print()
    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 70)

    # Save output to file
    import json
    import os
    os.makedirs("test_outputs", exist_ok=True)
    output_file = f"test_outputs/partial_test_{session_id}.json"

    # Filter to only serializable data
    output_data = {}
    for key, val in state.items():
        if val is not None and key not in ["emitter"]:
            try:
                json.dumps(val, default=str)
                output_data[key] = val
            except:
                output_data[key] = str(val)

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\nOutput saved to: {output_file}")

    return state


if __name__ == "__main__":
    asyncio.run(run_partial_test())
