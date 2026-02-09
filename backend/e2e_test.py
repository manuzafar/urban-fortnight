"""
End-to-End Test for Frontend-Backend Section Alignment

This script runs a full discovery workflow locally and validates
that all transformed sections match frontend expectations.
"""

import asyncio
import json
from datetime import datetime

from agents.orchestrator import run_discovery_workflow
from utils.helpers import build_inception_pack


async def run_e2e_test():
    """Run a complete discovery workflow and validate output."""

    print("=" * 70)
    print("E2E TEST: Frontend-Backend Section Alignment")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Test product idea
    product_idea = "Mobile app for local farmers markets to manage inventory, track sales, and accept digital payments from customers"
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"Session ID: {session_id}")
    print(f"Product Idea: {product_idea[:80]}...")
    print()
    print("Running discovery workflow (this will take several minutes)...")
    print("-" * 70)

    # Run the workflow
    final_state = await run_discovery_workflow(
        session_id=session_id,
        product_idea=product_idea,
        industry="Agriculture/Retail",
        target_market="Small farmers market vendors",
    )

    print("-" * 70)
    print("Workflow complete. Building inception pack...")
    print()

    # Build the pack (this applies all transformations)
    pack = build_inception_pack(final_state)

    # Save raw pack for inspection
    output_file = f"test_outputs/e2e_test_{session_id}.json"
    import os
    os.makedirs("test_outputs", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(pack, f, indent=2, default=str)
    print(f"Pack saved to: {output_file}")
    print()

    # Generate test report
    print("=" * 70)
    print("TEST REPORT: Section Validation")
    print("=" * 70)
    print()

    results = []

    # Test 1: GTM Strategy
    print("1. GTM STRATEGY")
    print("-" * 40)
    gtm = pack.get("gtm_strategy")
    gtm_tests = {
        "gtm_strategy exists": gtm is not None,
        "positioning_statement is string": isinstance(gtm.get("positioning_statement"), str) if gtm else False,
        "launch_phases is list": isinstance(gtm.get("launch_phases"), list) if gtm else False,
        "channel_strategy is list": isinstance(gtm.get("channel_strategy"), list) if gtm else False,
        "target_segments is list": isinstance(gtm.get("target_segments"), list) if gtm else False,
    }
    for test, passed in gtm_tests.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test}")
        results.append(("GTM", test, passed))
    if gtm:
        print(f"  → positioning_statement: {gtm.get('positioning_statement', '')[:60]}...")
        print(f"  → launch_phases count: {len(gtm.get('launch_phases', []))}")
        print(f"  → channel_strategy count: {len(gtm.get('channel_strategy', []))}")
    print()

    # Test 2: Detailed Personas
    print("2. DETAILED PERSONAS")
    print("-" * 40)
    personas = pack.get("detailed_personas")
    personas_tests = {
        "detailed_personas exists": personas is not None,
        "personas is list": isinstance(personas.get("personas"), list) if personas else False,
        "personas has items": len(personas.get("personas", [])) > 0 if personas else False,
        "key_insights is list": isinstance(personas.get("key_insights"), list) if personas else False,
        "prioritization is string": isinstance(personas.get("prioritization"), str) if personas else False,
    }
    for test, passed in personas_tests.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test}")
        results.append(("Personas", test, passed))
    if personas and personas.get("personas"):
        p = personas["personas"][0]
        print(f"  → First persona: {p.get('name', 'N/A')} ({p.get('role', 'N/A')})")
        print(f"  → Total personas: {len(personas.get('personas', []))}")
    print()

    # Test 3: Financial Model
    print("3. FINANCIAL MODEL")
    print("-" * 40)
    financial = pack.get("financial_model")
    financial_tests = {
        "financial_model exists": financial is not None,
        "summary is string": isinstance(financial.get("summary"), str) if financial else False,
        "unit_economics is list": isinstance(financial.get("unit_economics"), list) if financial else False,
        "projections is list": isinstance(financial.get("projections"), list) if financial else False,
        "funding_requirements is string": isinstance(financial.get("funding_requirements"), str) if financial else False,
        "sensitivity_analysis is dict": isinstance(financial.get("sensitivity_analysis"), dict) if financial else False,
    }
    for test, passed in financial_tests.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test}")
        results.append(("Financial", test, passed))
    if financial:
        print(f"  → funding_requirements: {financial.get('funding_requirements', 'N/A')[:60]}...")
        print(f"  → unit_economics count: {len(financial.get('unit_economics', []))}")
    print()

    # Test 4: Wireframes
    print("4. WIREFRAMES")
    print("-" * 40)
    wireframes = pack.get("wireframes")
    wireframes_tests = {
        "wireframes exists": wireframes is not None,
        "screens is list": isinstance(wireframes.get("screens"), list) if wireframes else False,
        "screens has items": len(wireframes.get("screens", [])) > 0 if wireframes else False,
        "user_flows is list": isinstance(wireframes.get("user_flows"), list) if wireframes else False,
        "user_flows[].screens is list": all(
            isinstance(f.get("screens"), list) for f in wireframes.get("user_flows", [])
        ) if wireframes and wireframes.get("user_flows") else True,
    }
    for test, passed in wireframes_tests.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test}")
        results.append(("Wireframes", test, passed))
    if wireframes:
        print(f"  → screens count: {len(wireframes.get('screens', []))}")
        print(f"  → user_flows count: {len(wireframes.get('user_flows', []))}")
    print()

    # Test 5: Other sections (existence check)
    print("5. OTHER SECTIONS")
    print("-" * 40)
    other_sections = [
        ("executive_summary", "Executive Summary"),
        ("customer_research", "Customer Research"),
        ("business_case", "Business Case"),
        ("competitive_analysis", "Competitive Analysis"),
        ("product_requirements_document", "PRD"),
        ("technical_architecture", "Technical Architecture"),
        ("legal_regulatory_review", "Legal Review"),
        ("risk_assessment", "Risk Assessment"),
        ("prototype", "Prototype"),
        ("stakeholder_views", "Stakeholder Views"),
        ("validation_playbook", "Validation Playbook"),
    ]
    for key, name in other_sections:
        exists = pack.get(key) is not None
        status = "✓ PASS" if exists else "✗ FAIL"
        print(f"  {status}: {name} exists")
        results.append(("Other", f"{name} exists", exists))
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total = len(results)
    passed = sum(1 for _, _, p in results if p)
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    print()

    if failed > 0:
        print("FAILED TESTS:")
        for section, test, p in results:
            if not p:
                print(f"  ✗ [{section}] {test}")
    print()

    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 70)

    return pack, results


if __name__ == "__main__":
    pack, results = asyncio.run(run_e2e_test())
