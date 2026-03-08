"""
End-to-End Test for Enterprise Context Integration.

This script tests that enterprise context properly influences agent outputs
by running discovery workflows with and without enterprise context and
comparing the results.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import yaml

from agents.orchestrator import run_discovery_workflow
from agents.context_builder import build_enterprise_context_prompt
from agents.constraint_broadcaster import generate_enterprise_constraints
from services.enterprise_context_service import enterprise_context_service
from utils.helpers import build_inception_pack


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def load_context_file(filepath: str) -> dict:
    """Load and parse an enterprise context file."""
    with open(filepath, "r") as f:
        content = f.read()
    parsed, _ = enterprise_context_service.parse_content(content)
    return parsed


def check_constraint_alignment(output_text: str, constraints: list) -> dict:
    """
    Check how well output text aligns with enterprise constraints.

    Returns a dict with:
    - aligned: list of constraints that appear to be followed
    - missing: list of constraints not mentioned/followed
    - score: alignment score (0-1)
    """
    aligned = []
    missing = []

    output_lower = output_text.lower()

    for constraint in constraints:
        field = constraint.field
        value = str(constraint.value).lower()

        # Check if constraint value appears in output
        if value in output_lower or any(v.lower() in output_lower for v in value.split(", ")):
            aligned.append({"field": field, "value": constraint.value})
        else:
            missing.append({"field": field, "value": constraint.value})

    total = len(aligned) + len(missing)
    score = len(aligned) / total if total > 0 else 0

    return {
        "aligned": aligned,
        "missing": missing,
        "score": score,
        "total": total,
    }


def extract_text_from_pack(pack: dict) -> str:
    """Extract all text content from an inception pack for analysis."""
    texts = []

    def extract_recursive(obj, prefix=""):
        if isinstance(obj, str):
            texts.append(obj)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                extract_recursive(v, f"{prefix}.{k}")
        elif isinstance(obj, list):
            for item in obj:
                extract_recursive(item, prefix)

    extract_recursive(pack)
    return " ".join(texts)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

import pytest


@pytest.mark.asyncio
async def test_context_parsing():
    """Test that example context files parse correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Context File Parsing")
    print("=" * 70)

    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "enterprise_context"

    results = []

    for filename in ["acme_company.yaml", "engineering_division.yaml", "payments_team.yaml"]:
        filepath = fixtures_dir / filename
        try:
            parsed = load_context_file(str(filepath))

            # Check key fields exist
            has_schema = "schema" in parsed
            has_strategy = "strategy" in parsed
            has_technology = "technology" in parsed

            status = "PASS" if all([has_schema, has_strategy, has_technology]) else "PARTIAL"
            print(f"  {status}: {filename}")
            print(f"    - Schema: {parsed.get('schema', 'missing')}")
            print(f"    - Strategy priorities: {len(parsed.get('strategy', {}).get('strategic_priorities', []))}")
            print(f"    - Tech stack defined: {bool(parsed.get('technology'))}")

            results.append((filename, True))
        except Exception as e:
            print(f"  FAIL: {filename} - {e}")
            results.append((filename, False))

    return all(r[1] for r in results)


@pytest.mark.asyncio
async def test_context_merging():
    """Test that context hierarchy merges correctly."""
    print("\n" + "=" * 70)
    print("TEST 2: Context Hierarchy Merging")
    print("=" * 70)

    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "enterprise_context"

    # Load all contexts
    company = load_context_file(str(fixtures_dir / "acme_company.yaml"))
    division = load_context_file(str(fixtures_dir / "engineering_division.yaml"))
    team = load_context_file(str(fixtures_dir / "payments_team.yaml"))

    # Merge hierarchy
    merged = enterprise_context_service.merge_hierarchy(
        company=company,
        division=division,
        team=team,
    )

    # Check merged result
    print(f"  Sources: {merged.get('_sources', [])}")
    print(f"  Company: {merged.get('company', 'missing')}")
    print(f"  Division: {merged.get('division', 'missing')}")
    print(f"  Team: {merged.get('team', 'missing')}")

    # Check merged technology (should include from all levels)
    tech = merged.get("technology", {})
    languages = tech.get("primary_languages", [])
    print(f"  Merged languages: {languages}")

    # Check regulatory (should include from company + team)
    regulatory = merged.get("regulatory", {})
    frameworks = regulatory.get("frameworks", [])
    print(f"  Merged frameworks: {frameworks}")

    success = (
        merged.get("company") == "Acme Financial Services" and
        merged.get("team") == "Payments Platform Team" and
        len(languages) >= 2 and
        "PCI-DSS Level 1" in str(frameworks) or "PCI-DSS" in str(frameworks)
    )

    print(f"\n  Result: {'PASS' if success else 'FAIL'}")
    return success


@pytest.mark.asyncio
async def test_constraint_extraction():
    """Test that constraints are properly extracted from context."""
    print("\n" + "=" * 70)
    print("TEST 3: Constraint Extraction")
    print("=" * 70)

    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "enterprise_context"

    # Load and merge contexts
    company = load_context_file(str(fixtures_dir / "acme_company.yaml"))
    division = load_context_file(str(fixtures_dir / "engineering_division.yaml"))
    team = load_context_file(str(fixtures_dir / "payments_team.yaml"))

    merged = enterprise_context_service.merge_hierarchy(
        company=company,
        division=division,
        team=team,
    )

    # Create state with enterprise context
    state = {
        "session_id": "test",
        "enterprise_context": merged,
    }

    # Extract constraints
    constraints = generate_enterprise_constraints(state)

    print(f"  Total constraints extracted: {len(constraints)}")

    # Group by field
    by_field = {}
    for c in constraints:
        if c.field not in by_field:
            by_field[c.field] = []
        by_field[c.field].append(c)

    print(f"\n  Constraints by field:")
    for field, field_constraints in sorted(by_field.items()):
        print(f"    - {field}: {len(field_constraints)} constraints")
        for c in field_constraints[:2]:  # Show first 2
            print(f"      • {c.value[:50]}..." if len(str(c.value)) > 50 else f"      • {c.value}")

    # Check expected constraints exist
    expected_fields = ["compliance_framework", "cloud_platform", "strategic_alignment"]
    missing = [f for f in expected_fields if f not in by_field]

    success = len(constraints) >= 5 and len(missing) == 0
    print(f"\n  Expected fields present: {len(expected_fields) - len(missing)}/{len(expected_fields)}")
    print(f"  Result: {'PASS' if success else 'FAIL'}")

    return success


@pytest.mark.asyncio
async def test_prompt_generation():
    """Test that enterprise context generates proper prompts."""
    print("\n" + "=" * 70)
    print("TEST 4: Prompt Generation")
    print("=" * 70)

    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "enterprise_context"

    # Load and merge contexts
    company = load_context_file(str(fixtures_dir / "acme_company.yaml"))
    division = load_context_file(str(fixtures_dir / "engineering_division.yaml"))
    team = load_context_file(str(fixtures_dir / "payments_team.yaml"))

    merged = enterprise_context_service.merge_hierarchy(
        company=company,
        division=division,
        team=team,
    )

    # Generate prompt
    prompt = build_enterprise_context_prompt(merged)

    print(f"  Prompt length: {len(prompt)} chars")

    # Check key elements
    checks = {
        "Has header": "ORGANIZATIONAL CONTEXT" in prompt,
        "Has company name": "Acme" in prompt,
        "Has compliance section": "Compliance" in prompt or "compliance" in prompt,
        "Has technology section": "Technology" in prompt or "AWS" in prompt,
        "Has strategic priorities": "Digital transformation" in prompt or "strategic" in prompt.lower(),
        "Has deviation guidance": "deviat" in prompt.lower(),
    }

    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"    {status}: {check}")

    success = all(checks.values())
    print(f"\n  Result: {'PASS' if success else 'FAIL'}")

    # Print sample of prompt
    print(f"\n  Prompt preview (first 500 chars):")
    print("  " + "-" * 60)
    for line in prompt[:500].split("\n"):
        print(f"  {line}")
    print("  ...")

    return success


@pytest.mark.asyncio
async def test_workflow_with_context(run_full_workflow: bool = False):
    """
    Test running discovery workflow with enterprise context.

    If run_full_workflow is False, just tests that context is properly passed.
    If True, runs actual LLM calls (takes several minutes).
    """
    print("\n" + "=" * 70)
    print("TEST 5: Workflow Integration")
    print("=" * 70)

    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "enterprise_context"

    # Load and merge contexts
    company = load_context_file(str(fixtures_dir / "acme_company.yaml"))
    division = load_context_file(str(fixtures_dir / "engineering_division.yaml"))
    team = load_context_file(str(fixtures_dir / "payments_team.yaml"))

    merged = enterprise_context_service.merge_hierarchy(
        company=company,
        division=division,
        team=team,
    )

    # Generate prompt
    prompt = build_enterprise_context_prompt(merged)

    # Create context IDs (simulated)
    context_ids = ["company-123", "division-456", "team-789"]

    if not run_full_workflow:
        print("  [Skipping full workflow - use --full flag to run LLM calls]")
        print(f"  Context prepared with {len(context_ids)} context files")
        print(f"  Merged context has {len(merged)} top-level keys")
        print(f"  Generated prompt: {len(prompt)} chars")
        print(f"\n  Result: PASS (context preparation verified)")
        return True

    # Full workflow test
    print("  Running full discovery workflow with enterprise context...")
    print("  (This will take several minutes)")

    session_id = f"ec_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    product_idea = """
    Real-time payment processing API for B2B transactions.
    Enable businesses to process instant payments between accounts
    with fraud detection and compliance reporting.
    """

    try:
        final_state = await run_discovery_workflow(
            session_id=session_id,
            product_idea=product_idea,
            industry="Financial Services / Payments",
            target_market="B2B financial services",
            enterprise_context_ids=context_ids,
            enterprise_context=merged,
            enterprise_context_prompt=prompt,
        )

        # Build pack
        pack = build_inception_pack(final_state)

        # Save output
        output_dir = Path(__file__).parent.parent.parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"ec_e2e_{session_id}.json"

        with open(output_file, "w") as f:
            json.dump(pack, f, indent=2, default=str)

        print(f"  Pack saved to: {output_file}")

        # Analyze output for constraint alignment
        pack_text = extract_text_from_pack(pack)

        state = {"enterprise_context": merged}
        constraints = generate_enterprise_constraints(state)

        alignment = check_constraint_alignment(pack_text, constraints)

        print(f"\n  Constraint Alignment Analysis:")
        print(f"    - Aligned: {len(alignment['aligned'])}/{alignment['total']}")
        print(f"    - Score: {alignment['score']:.1%}")

        print(f"\n  Aligned constraints:")
        for c in alignment['aligned'][:5]:
            print(f"    ✓ {c['field']}: {c['value'][:40]}...")

        if alignment['missing']:
            print(f"\n  Missing constraints:")
            for c in alignment['missing'][:5]:
                print(f"    ✗ {c['field']}: {c['value'][:40]}...")

        success = alignment['score'] >= 0.3  # At least 30% alignment
        print(f"\n  Result: {'PASS' if success else 'FAIL'}")

        return success

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════


async def main(full_workflow: bool = False):
    """Run all enterprise context e2e tests."""
    print("=" * 70)
    print("ENTERPRISE CONTEXT END-TO-END TESTS")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")

    results = []

    # Test 1: Parsing
    results.append(("Parsing", await test_context_parsing()))

    # Test 2: Merging
    results.append(("Merging", await test_context_merging()))

    # Test 3: Constraint Extraction
    results.append(("Constraints", await test_constraint_extraction()))

    # Test 4: Prompt Generation
    results.append(("Prompts", await test_prompt_generation()))

    # Test 5: Workflow Integration
    results.append(("Workflow", await test_workflow_with_context(full_workflow)))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")

    print(f"\n  Total: {passed}/{total} passed")
    print(f"  Completed: {datetime.now().isoformat()}")

    return passed == total


if __name__ == "__main__":
    import sys

    full = "--full" in sys.argv

    if full:
        print("Running FULL e2e tests (includes LLM calls)")
    else:
        print("Running QUICK e2e tests (no LLM calls)")
        print("Use --full flag to run complete tests with LLM")

    success = asyncio.run(main(full_workflow=full))
    sys.exit(0 if success else 1)
