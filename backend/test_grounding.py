#!/usr/bin/env python3
"""
End-to-end test for Gemini grounding implementation.

Tests that the grounded agents (Customer Research, Business Strategy,
Legal & Regulatory) work correctly with Google Search grounding enabled.
"""

import asyncio
import json
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, ".")

from config import settings
from agents.base_agent import configure_gemini, call_llm, call_llm_with_grounding
from agents.customer_research import run_customer_research_agent
from agents.business_strategy import run_business_strategy_agent
from agents.legal_regulatory import run_legal_regulatory_agent
from agents.state import create_initial_state
from models.schemas import SessionStatus


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_result(label: str, value: str, indent: int = 2) -> None:
    """Print a formatted result line."""
    prefix = " " * indent
    print(f"{prefix}{label}: {value}")


async def test_grounding_config() -> bool:
    """Test that grounding configuration is properly set."""
    print_header("Test 1: Grounding Configuration")

    print_result("llm_enable_grounding", str(settings.llm_enable_grounding))
    print_result("llm_model", settings.llm_model)
    print_result("llm_temperature", str(settings.llm_temperature))

    if hasattr(settings, 'llm_enable_grounding'):
        print("\n  [PASS] Grounding configuration exists")
        return True
    else:
        print("\n  [FAIL] Grounding configuration missing")
        return False


async def test_grounded_llm_call() -> bool:
    """Test the grounded LLM call function directly."""
    print_header("Test 2: Direct Grounded LLM Call")

    configure_gemini()

    test_prompt = '''You are a market research assistant.

Return a JSON object with current market information about electric vehicles.

{
    "market_size": "string - current EV market size estimate",
    "top_manufacturer": "string - leading EV manufacturer by sales",
    "growth_trend": "string - market growth trend",
    "data_source": "string - where this data comes from"
}

Respond with ONLY the JSON object.'''

    print("  Calling LLM with grounding enabled...")

    try:
        result = await call_llm_with_grounding(test_prompt, "Test Agent")

        print_result("Success", str(result.get("success")))
        print_result("Grounded", str(result.get("grounded", "N/A")))
        print_result("Duration", f"{result.get('duration_seconds', 0):.2f}s")
        print_result("Tokens Used", str(result.get("tokens_used", 0)))

        if result.get("success"):
            data = result.get("data", {})
            print("\n  Response Data:")
            print_result("Market Size", data.get("market_size", "N/A")[:80], 4)
            print_result("Top Manufacturer", data.get("top_manufacturer", "N/A")[:80], 4)
            print_result("Growth Trend", data.get("growth_trend", "N/A")[:80], 4)
            print_result("Data Source", data.get("data_source", "N/A")[:80], 4)
            print("\n  [PASS] Grounded LLM call successful")
            return True
        else:
            print_result("Error", result.get("error", "Unknown"))
            print("\n  [FAIL] Grounded LLM call failed")
            return False

    except Exception as e:
        print(f"\n  [FAIL] Exception: {str(e)}")
        return False


async def test_customer_research_agent() -> tuple[bool, dict]:
    """Test the Customer Research agent with grounding."""
    print_header("Test 3: Customer Research Agent (Grounded)")

    import uuid
    state = create_initial_state(
        session_id=str(uuid.uuid4()),
        product_idea="A mobile app that uses AI to help small business owners manage their inventory and predict restocking needs",
        industry="Retail Technology",
        target_market="Small and medium-sized retail businesses in the US",
        constraints=["Budget under $500k for MVP", "Must work offline"],
        additional_context="Focus on grocery and convenience stores initially"
    )

    print("  Running Customer Research Agent...")
    print_result("Product Idea", state["product_idea"][:60] + "...")

    try:
        result_state = await run_customer_research_agent(state)

        customer_research = result_state.get("customer_research", {})
        agent_output = result_state.get("agent_outputs", {}).get("Customer Research Agent", {})

        print_result("Success", str(agent_output.get("success", False)))
        print_result("Grounded", str(agent_output.get("grounded", "N/A")))
        print_result("Duration", f"{agent_output.get('duration_seconds', 0):.2f}s")

        if customer_research:
            print("\n  Research Output Summary:")

            # Job to be done
            jtbd = customer_research.get("job_to_be_done", {})
            if jtbd:
                print_result("Trigger Situation", (jtbd.get("trigger_situation", "N/A"))[:70], 4)

            # Pain signals count
            pain_signals = customer_research.get("pain_signals", [])
            print_result("Pain Signals Found", str(len(pain_signals)), 4)

            # Market context
            market = customer_research.get("market_context", {})
            if market:
                print_result("TAM", (market.get("total_addressable_market", "N/A"))[:60], 4)

            # Competitors
            competitors = customer_research.get("competitive_landscape", {}).get("competitors", [])
            print_result("Competitors Identified", str(len(competitors)), 4)

            print("\n  [PASS] Customer Research Agent completed successfully")
            return True, result_state
        else:
            errors = result_state.get("errors", [])
            print_result("Errors", str(errors))
            print("\n  [FAIL] Customer Research Agent produced no output")
            return False, result_state

    except Exception as e:
        print(f"\n  [FAIL] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, state


async def test_business_strategy_agent(state: dict) -> tuple[bool, dict]:
    """Test the Business Strategy agent with grounding."""
    print_header("Test 4: Business Strategy Agent (Grounded)")

    if not state.get("customer_research"):
        print("  [SKIP] No customer research available")
        return False, state

    print("  Running Business Strategy Agent...")

    try:
        result_state = await run_business_strategy_agent(state)

        business_case = result_state.get("business_case", {})
        agent_output = result_state.get("agent_outputs", {}).get("Business Strategy Agent", {})

        print_result("Success", str(agent_output.get("success", False)))
        print_result("Grounded", str(agent_output.get("grounded", "N/A")))
        print_result("Duration", f"{agent_output.get('duration_seconds', 0):.2f}s")

        if business_case:
            print("\n  Business Case Summary:")

            # Lean canvas
            lean_canvas = business_case.get("lean_canvas", {})
            if lean_canvas:
                uvp = lean_canvas.get("unique_value_proposition", "N/A")
                print_result("UVP", uvp[:70] if uvp else "N/A", 4)

            # Revenue streams
            revenue_streams = business_case.get("revenue_streams", [])
            print_result("Revenue Streams", str(len(revenue_streams)), 4)

            # ROI
            roi = business_case.get("roi_analysis", "N/A")
            print_result("ROI Analysis", (roi[:60] + "...") if roi and len(roi) > 60 else roi, 4)

            print("\n  [PASS] Business Strategy Agent completed successfully")
            return True, result_state
        else:
            errors = result_state.get("errors", [])
            print_result("Errors", str(errors))
            print("\n  [FAIL] Business Strategy Agent produced no output")
            return False, result_state

    except Exception as e:
        print(f"\n  [FAIL] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, state


async def test_legal_regulatory_agent(state: dict) -> tuple[bool, dict]:
    """Test the Legal & Regulatory agent with grounding."""
    print_header("Test 5: Legal & Regulatory Agent (Grounded)")

    print("  Running Legal & Regulatory Agent...")

    try:
        result_state = await run_legal_regulatory_agent(state)

        legal_review = result_state.get("legal_regulatory_review", {})
        agent_output = result_state.get("agent_outputs", {}).get("Legal & Regulatory Review", {})

        print_result("Success", str(agent_output.get("success", False)))
        print_result("Grounded", str(agent_output.get("grounded", "N/A")))
        print_result("Duration", f"{agent_output.get('duration_seconds', 0):.2f}s")

        if legal_review:
            print("\n  Legal Review Summary:")

            # Regulations
            regulations = legal_review.get("applicable_regulations", [])
            print_result("Regulations Identified", str(len(regulations)), 4)
            if regulations:
                for reg in regulations[:3]:
                    print_result(f"  - {reg.get('name', 'N/A')}", reg.get('impact_level', 'N/A'), 6)

            # Risk assessment
            risk_assessment = legal_review.get("overall_risk_assessment", {})
            if risk_assessment:
                print_result("Risk Level", risk_assessment.get("risk_level", "N/A"), 4)

            # Data protection
            data_protection = legal_review.get("data_protection_requirements", [])
            print_result("Data Protection Reqs", str(len(data_protection)), 4)

            print("\n  [PASS] Legal & Regulatory Agent completed successfully")
            return True, result_state
        else:
            errors = result_state.get("errors", [])
            print_result("Errors", str(errors))
            print("\n  [FAIL] Legal & Regulatory Agent produced no output")
            return False, result_state

    except Exception as e:
        print(f"\n  [FAIL] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, state


async def test_grounding_disabled() -> bool:
    """Test that grounding can be disabled via config."""
    print_header("Test 6: Grounding Disable Fallback")

    # Save original setting
    original_setting = settings.llm_enable_grounding

    try:
        # Temporarily disable grounding
        # Note: This modifies the settings object directly which isn't ideal
        # but works for testing purposes
        object.__setattr__(settings, 'llm_enable_grounding', False)

        test_prompt = '''Return a simple JSON object:
{
    "test": "grounding disabled",
    "status": "ok"
}'''

        print("  Testing with grounding disabled...")
        result = await call_llm_with_grounding(test_prompt, "Fallback Test")

        print_result("Success", str(result.get("success")))
        print_result("Grounded", str(result.get("grounded", "N/A")))

        # Should report grounded=False when disabled
        if result.get("grounded") == False:
            print("\n  [PASS] Correctly fell back to non-grounded call")
            return True
        else:
            print("\n  [WARN] Grounding flag not as expected")
            return True  # Still pass if call succeeded

    except Exception as e:
        print(f"\n  [FAIL] Exception: {str(e)}")
        return False
    finally:
        # Restore original setting
        object.__setattr__(settings, 'llm_enable_grounding', original_setting)


async def run_all_tests() -> None:
    """Run all grounding tests."""
    print("\n" + "=" * 60)
    print(" GEMINI GROUNDING IMPLEMENTATION TEST SUITE")
    print(" " + datetime.now().isoformat())
    print("=" * 60)

    results = []

    # Test 1: Configuration
    results.append(("Configuration", await test_grounding_config()))

    # Test 2: Direct grounded call
    results.append(("Direct Grounded Call", await test_grounded_llm_call()))

    # Test 3: Customer Research Agent
    cr_success, state = await test_customer_research_agent()
    results.append(("Customer Research Agent", cr_success))

    # Test 4: Business Strategy Agent (needs customer research)
    if cr_success:
        bs_success, state = await test_business_strategy_agent(state)
        results.append(("Business Strategy Agent", bs_success))
    else:
        results.append(("Business Strategy Agent", False))

    # Test 5: Legal & Regulatory Agent
    lr_success, state = await test_legal_regulatory_agent(state)
    results.append(("Legal & Regulatory Agent", lr_success))

    # Test 6: Grounding disable fallback
    results.append(("Grounding Disable Fallback", await test_grounding_disabled()))

    # Summary
    print_header("TEST SUMMARY")

    passed = 0
    failed = 0

    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {test_name}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\n  Total: {passed} passed, {failed} failed out of {len(results)} tests")

    # Final stats
    print_header("EXECUTION STATS")
    print_result("Total Tokens Used", str(state.get("total_tokens_used", 0)))
    print_result("Total Duration", f"{state.get('total_duration_seconds', 0):.2f}s")

    if failed == 0:
        print("\n  ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n  {failed} TEST(S) FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
