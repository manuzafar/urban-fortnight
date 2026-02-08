#!/usr/bin/env python3
"""
Single Pack Test for Seedcraft v3.0

Tests the complete discovery workflow with the banking showcase pack.
Uses unbuffered output for real-time progress visibility.

Run with: python -m tests.single_pack_test
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70, flush=True)
print("SEEDCRAFT v3.0 - SINGLE PACK TEST", flush=True)
print("=" * 70, flush=True)
print(f"Start Time: {datetime.now().isoformat()}", flush=True)
print(flush=True)

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Check API key
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ GOOGLE_API_KEY not set in environment", flush=True)
    sys.exit(1)

print("✅ Environment loaded", flush=True)

# Import after environment is loaded
import structlog
from agents.orchestrator import run_discovery_workflow
from utils.helpers import generate_session_id

# Configure simple logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# Banking showcase pack
BANKING_PACK = {
    "product_idea": """
AI-powered cash flow forecasting platform for SME banking customers. The platform
integrates with accounting software (Xero, MYOB, QuickBooks) and bank transaction
data to provide:
- 90-day cash flow predictions with confidence intervals
- Early warning alerts for potential cash shortfalls
- Scenario modeling for business decisions
- Automated recommendations for credit line adjustments

Target market: Australian SME banking sector (businesses with $1M-$50M annual revenue)
Key stakeholders: CFOs, Bank relationship managers, Credit risk teams
    """,
    "industry": "Financial Services / Banking",
    "target_market": "Australian SME banking customers",
    "constraints": [
        "Must comply with APRA prudential standards",
        "Open Banking (CDR) integration required",
        "Data residency must be Australia",
    ],
}


async def run_test():
    """Run the single pack test."""
    session_id = generate_session_id()

    print(f"\n📦 Testing: AI Cash Flow Forecasting for SME Banking", flush=True)
    print(f"Session ID: {session_id}", flush=True)
    print("-" * 70, flush=True)

    start_time = datetime.now()

    try:
        # Run the discovery workflow
        print("\n🚀 Starting discovery workflow...", flush=True)

        final_state = await run_discovery_workflow(
            session_id=session_id,
            product_idea=BANKING_PACK["product_idea"],
            industry=BANKING_PACK["industry"],
            target_market=BANKING_PACK["target_market"],
            constraints=BANKING_PACK["constraints"],
            additional_context=None,
            event_emitter=None,
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n{'=' * 70}", flush=True)
        print("TEST RESULTS", flush=True)
        print(f"{'=' * 70}", flush=True)

        # Status
        status = final_state.get("status", "unknown")
        status_emoji = "✅" if status == "completed" else "❌"
        print(f"\nStatus: {status_emoji} {status}", flush=True)
        print(f"Duration: {duration:.1f} seconds", flush=True)
        print(f"Iterations: {final_state.get('iteration', 1)}", flush=True)

        # Cross-reference index
        print(f"\n📊 Cross-Reference Index:", flush=True)
        cr_index = final_state.get("cross_reference_index", {})
        if cr_index:
            claims = cr_index.get("claims", [])
            print(f"   Total Claims: {len(claims)}", flush=True)
            print(f"   Evidence Score: {cr_index.get('evidence_score', 0):.1%}", flush=True)

            # Tier distribution
            tier_dist = cr_index.get("tier_distribution", {})
            if tier_dist:
                print(f"   Tier Distribution:", flush=True)
                for tier in ["E1", "E2", "E3", "E4", "E5"]:
                    count = tier_dist.get(tier, 0)
                    if count > 0:
                        print(f"      {tier}: {count}", flush=True)

            # Section prefixes
            prefixes = set()
            for claim in claims:
                cid = claim.get("claim_id", "")
                if "-" in cid:
                    prefixes.add(cid.split("-")[0])
            if prefixes:
                print(f"   Section Prefixes: {', '.join(sorted(prefixes))}", flush=True)
        else:
            print("   No cross-reference index found", flush=True)

        # Sections present
        print(f"\n📄 Sections:", flush=True)
        sections = [
            ("customer_research", "Market Intelligence"),
            ("competitive_analysis", "Competitive Landscape"),
            ("detailed_personas", "Customer Personas"),
            ("business_case", "Business Case"),
            ("gtm_plan", "Go-to-Market"),
            ("financial_model", "Financial Model"),
            ("product_requirements", "Product Requirements"),
            ("technical_architecture", "Technical Architecture"),
            ("legal_regulatory_review", "Regulatory & Compliance"),
            ("wireframes", "Wireframes"),
            ("prototype", "Prototype"),
            ("stakeholder_views", "Stakeholder Views"),
            ("validation_playbook", "Validation Playbook"),
            ("executive_summary", "Executive Summary"),
        ]

        present = []
        missing = []
        for key, name in sections:
            if final_state.get(key):
                present.append(name)
                # Show extra details for key sections
                if key == "wireframes":
                    screens = final_state[key].get("screens", [])
                    print(f"   ✅ {name} ({len(screens)} screens)", flush=True)
                elif key == "stakeholder_views":
                    views = final_state[key].get("views", [])
                    roles = [v.get("stakeholder_role", "?") for v in views]
                    print(f"   ✅ {name} ({', '.join(roles)})", flush=True)
                elif key == "validation_playbook":
                    experiments = final_state[key].get("experiments", [])
                    print(f"   ✅ {name} ({len(experiments)} experiments)", flush=True)
                elif key == "financial_model":
                    projections = final_state[key].get("monthly_projections_year_1", [])
                    print(f"   ✅ {name} ({len(projections)} monthly projections)", flush=True)
                else:
                    print(f"   ✅ {name}", flush=True)
            else:
                missing.append(name)
                print(f"   ❌ {name}", flush=True)

        # Quality assessment
        print(f"\n🎯 Quality Assessment:", flush=True)
        qa = final_state.get("quality_assessment", {})
        if qa:
            print(f"   Overall Score: {qa.get('overall_score', 0):.1%}", flush=True)
            dims = qa.get("dimensions", {})
            if dims:
                for dim, score in dims.items():
                    print(f"   • {dim}: {score}/10", flush=True)
        else:
            print("   No quality assessment found", flush=True)

        # Errors
        errors = final_state.get("errors", [])
        if errors:
            print(f"\n⚠️ Errors ({len(errors)}):", flush=True)
            for err in errors[:5]:
                print(f"   • {err[:100]}...", flush=True)

        # Save state to file
        output_dir = Path(__file__).parent.parent / "test_outputs" / "single_pack"
        output_dir.mkdir(parents=True, exist_ok=True)

        state_file = output_dir / f"{session_id}.json"
        with open(state_file, "w") as f:
            # Make state JSON serializable
            serializable = {}
            for k, v in final_state.items():
                try:
                    json.dumps(v)
                    serializable[k] = v
                except (TypeError, ValueError):
                    serializable[k] = str(v)
            json.dump(serializable, f, indent=2, default=str)

        print(f"\n💾 State saved to: {state_file}", flush=True)

        # Generate HTML view
        from utils.pack_to_html import generate_pack_html
        html_file = generate_pack_html(serializable, output_dir / f"{session_id}.html")
        print(f"🌐 HTML Pack: {html_file}", flush=True)
        print(f"   Open: file://{html_file.absolute()}", flush=True)

        # Final verdict
        print(f"\n{'=' * 70}", flush=True)
        if status == "completed" and len(present) >= 10:
            print("✅ TEST PASSED - Workflow completed with required sections", flush=True)
        elif status == "completed":
            print(f"⚠️ TEST PARTIAL - Completed but missing {len(missing)} sections", flush=True)
        else:
            print("❌ TEST FAILED - Workflow did not complete", flush=True)
        print(f"{'=' * 70}", flush=True)

        return final_state

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n❌ TEST FAILED", flush=True)
        print(f"Duration: {duration:.1f} seconds", flush=True)
        print(f"Error: {str(e)}", flush=True)

        import traceback
        traceback.print_exc()

        return None


if __name__ == "__main__":
    print("\n🔧 Initializing...", flush=True)
    result = asyncio.run(run_test())
    print("\nDone.", flush=True)
