#!/usr/bin/env python3
"""
E2E Showcase Test for Seedcraft v3.0

Tests the complete discovery workflow with 3 showcase product ideas:
1. AI cash flow forecasting for SME banking
2. AI clinical trial matching platform
3. Automated insurance claims with fraud detection

Run with: python -m tests.e2e_showcase_test
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Showcase product ideas
SHOWCASE_PACKS = [
    {
        "id": "banking",
        "name": "AI Cash Flow Forecasting for SME Banking",
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
        "validations": {
            "has_regulatory": True,
            "has_financial_model": True,
            "regulatory_bodies": ["APRA", "ASIC", "CDR"],
            "stakeholder_roles": ["CFO", "CISO"],
        },
    },
    {
        "id": "healthcare",
        "name": "AI Clinical Trial Matching Platform",
        "product_idea": """
AI platform that matches cancer patients with eligible clinical trials. The system:
- Analyzes patient medical records (EHRs) using NLP
- Matches against trial eligibility criteria from ClinicalTrials.gov
- Provides matching confidence scores with explanation
- Generates pre-screening packages for trial coordinators
- Supports both patient-initiated and physician-initiated workflows

Target users: Oncologists, clinical trial coordinators, cancer patients
Market: Initially Australia, expanding to US and EU
Key challenge: Accurate extraction of eligibility criteria from unstructured trial protocols
        """,
        "industry": "Healthcare / Clinical Research",
        "target_market": "Oncology clinical trials in Australia and US",
        "constraints": [
            "HIPAA compliance required for US market",
            "TGA compliance for Australian market",
            "Must handle sensitive patient health information",
            "Clinical validation required before deployment",
        ],
        "validations": {
            "has_regulatory": True,
            "has_personas": True,
            "regulatory_bodies": ["HIPAA", "TGA", "FDA"],
            "persona_types": ["patient", "physician", "researcher"],
        },
    },
    {
        "id": "insurance",
        "name": "Automated Insurance Claims with Fraud Detection",
        "product_idea": """
AI-powered insurance claims automation platform with integrated fraud detection:
- Automated claims intake via mobile app (photo/video of damage)
- AI damage assessment for auto and property claims
- Real-time fraud scoring using behavioral and claim pattern analysis
- Straight-through processing for low-risk claims
- Human-in-the-loop escalation for complex/suspicious claims
- Integration with repair networks for auto claims

Target: General insurers in Australian market (auto, home, contents)
Key metrics: Claims processing time reduction, fraud detection rate, customer NPS
        """,
        "industry": "Insurance / InsurTech",
        "target_market": "Australian general insurance market",
        "constraints": [
            "APRA prudential standards compliance",
            "ASIC responsible lending requirements",
            "Insurance Contracts Act compliance",
            "Fair claims handling requirements",
        ],
        "validations": {
            "has_regulatory": True,
            "has_financial_model": True,
            "has_risk_assessment": True,
            "regulatory_bodies": ["APRA", "ASIC"],
        },
    },
]


def validate_cross_reference_index(state: dict) -> dict[str, Any]:
    """Validate the cross-reference index structure and content."""
    index = state.get("cross_reference_index")

    if not index:
        return {"valid": False, "error": "No cross_reference_index in state"}

    claims = index.get("claims", [])

    results = {
        "valid": True,
        "total_claims": len(claims),
        "tier_distribution": index.get("tier_distribution", {}),
        "evidence_score": index.get("evidence_score", 0),
        "prefixes_found": set(),
        "grounded_claims": 0,  # E1, E2, E3
        "hypothesis_claims": 0,  # E4, E5
        "claims_with_sources": 0,
        "claims_with_validation": 0,
    }

    for claim in claims:
        # Extract prefix
        claim_id = claim.get("claim_id", "")
        if "-" in claim_id:
            prefix = claim_id.split("-")[0]
            results["prefixes_found"].add(prefix)

        # Count by tier
        tier = claim.get("evidence_tier", "E5")
        if tier in ["E1", "E2", "E3"]:
            results["grounded_claims"] += 1
        else:
            results["hypothesis_claims"] += 1

        # Check for source
        if claim.get("source"):
            results["claims_with_sources"] += 1

        # Check for validation method
        if claim.get("validation_method"):
            results["claims_with_validation"] += 1

    results["prefixes_found"] = list(results["prefixes_found"])

    # Validation checks
    if results["total_claims"] < 20:
        results["warning"] = f"Low claim count: {results['total_claims']} (expected 80+)"

    grounded_pct = results["grounded_claims"] / max(results["total_claims"], 1) * 100
    if grounded_pct < 30:
        results["warning"] = f"Low grounded claim percentage: {grounded_pct:.1f}% (expected 30%+)"

    return results


def validate_sections(state: dict, pack_config: dict) -> dict[str, Any]:
    """Validate that all required sections are present and populated."""
    results = {
        "sections": {},
        "missing": [],
        "warnings": [],
    }

    # Required v3.0 sections
    required_sections = [
        ("customer_research", "Market Intelligence"),
        ("competitive_analysis", "Competitive Landscape"),
        ("detailed_personas", "Customer Personas"),
        ("business_case", "Business Case"),
        ("gtm_plan", "Go-to-Market"),
        ("financial_model", "Financial Model"),
        ("product_requirements", "Product Requirements"),
        ("technical_architecture", "Technical Architecture"),
        ("legal_regulatory_review", "Regulatory & Compliance"),
        ("risk_assessment", "Risk Assessment"),
        ("wireframes", "Wireframes"),
        ("prototype", "Prototype"),
        ("stakeholder_views", "Stakeholder Views"),
        ("validation_playbook", "Validation Playbook"),
        ("executive_summary", "Executive Summary"),
    ]

    for key, name in required_sections:
        section = state.get(key)
        if section:
            results["sections"][key] = {
                "present": True,
                "has_content": bool(section),
                "type": type(section).__name__,
            }

            # Additional checks for specific sections
            if key == "wireframes" and section.get("screens"):
                results["sections"][key]["screen_count"] = len(section["screens"])

            if key == "financial_model" and section.get("monthly_projections_year_1"):
                results["sections"][key]["monthly_projections"] = len(
                    section["monthly_projections_year_1"]
                )

            if key == "stakeholder_views" and section.get("views"):
                results["sections"][key]["view_roles"] = [
                    v.get("stakeholder_role") for v in section["views"]
                ]

            if key == "validation_playbook" and section.get("experiments"):
                results["sections"][key]["experiment_count"] = len(section["experiments"])
        else:
            results["missing"].append(key)

    return results


def validate_quality_assessment(state: dict) -> dict[str, Any]:
    """Validate the quality assessment from critique agent."""
    qa = state.get("quality_assessment")

    if not qa:
        return {"valid": False, "error": "No quality_assessment in state"}

    results = {
        "valid": True,
        "overall_score": qa.get("overall_score"),
        "dimensions": qa.get("dimensions", {}),
        "sections_needing_revision": qa.get("sections_needing_revision", []),
        "quality_passed": state.get("quality_passed", False),
    }

    return results


async def run_showcase_pack(pack_config: dict, output_dir: Path) -> dict[str, Any]:
    """Run a single showcase pack through the discovery workflow."""
    from agents.orchestrator import run_discovery_workflow
    from utils.helpers import generate_session_id

    pack_id = pack_config["id"]
    session_id = generate_session_id()

    logger.info(
        "showcase_pack_start",
        pack_id=pack_id,
        pack_name=pack_config["name"],
        session_id=session_id,
    )

    start_time = datetime.now()

    try:
        # Run the discovery workflow
        final_state = await run_discovery_workflow(
            session_id=session_id,
            product_idea=pack_config["product_idea"],
            industry=pack_config.get("industry"),
            target_market=pack_config.get("target_market"),
            constraints=pack_config.get("constraints"),
            additional_context=None,
            event_emitter=None,  # No SSE for test
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Validate results
        results = {
            "pack_id": pack_id,
            "pack_name": pack_config["name"],
            "session_id": session_id,
            "status": final_state.get("status"),
            "duration_seconds": duration,
            "iterations": final_state.get("iteration", 1),
            "total_tokens": final_state.get("total_tokens_used", 0),
            "cross_reference": validate_cross_reference_index(final_state),
            "sections": validate_sections(final_state, pack_config),
            "quality": validate_quality_assessment(final_state),
            "errors": final_state.get("errors", []),
        }

        # Save full state to file
        state_file = output_dir / f"{pack_id}_state.json"
        with open(state_file, "w") as f:
            # Convert state to serializable format
            serializable_state = {}
            for key, value in final_state.items():
                try:
                    json.dumps(value)
                    serializable_state[key] = value
                except (TypeError, ValueError):
                    serializable_state[key] = str(value)
            json.dump(serializable_state, f, indent=2, default=str)

        results["state_file"] = str(state_file)

        # Generate HTML view
        from utils.pack_to_html import generate_pack_html
        html_file = generate_pack_html(serializable_state, output_dir / f"{pack_id}_pack.html")
        results["html_file"] = str(html_file)

        logger.info(
            "showcase_pack_complete",
            pack_id=pack_id,
            status=results["status"],
            duration=f"{duration:.1f}s",
            claims=results["cross_reference"].get("total_claims", 0),
            evidence_score=results["cross_reference"].get("evidence_score", 0),
        )

        return results

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.error(
            "showcase_pack_failed",
            pack_id=pack_id,
            error=str(e),
            duration=f"{duration:.1f}s",
            exc_info=True,
        )

        return {
            "pack_id": pack_id,
            "pack_name": pack_config["name"],
            "session_id": session_id,
            "status": "failed",
            "duration_seconds": duration,
            "error": str(e),
        }


def generate_html_report(results: list[dict], output_dir: Path) -> Path:
    """Generate an HTML report of the test results."""
    html_file = output_dir / "report.html"

    # Calculate overall stats
    completed = sum(1 for r in results if r.get("status") == "completed")
    total = len(results)
    total_duration = sum(r.get("duration_seconds", 0) for r in results)
    avg_claims = sum(
        r.get("cross_reference", {}).get("total_claims", 0)
        for r in results if r.get("status") == "completed"
    ) / max(completed, 1)
    avg_score = sum(
        r.get("cross_reference", {}).get("evidence_score", 0)
        for r in results if r.get("status") == "completed"
    ) / max(completed, 1)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seedcraft v3.0 E2E Test Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .tier-E1 {{ background-color: #dcfce7; color: #166534; }}
        .tier-E2 {{ background-color: #dbeafe; color: #1e40af; }}
        .tier-E3 {{ background-color: #fef9c3; color: #854d0e; }}
        .tier-E4 {{ background-color: #fed7aa; color: #9a3412; }}
        .tier-E5 {{ background-color: #fecaca; color: #991b1b; }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Header -->
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-slate-800">Seedcraft v3.0 E2E Test Report</h1>
            <p class="text-slate-600 mt-2">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>

        <!-- Overall Summary -->
        <section class="bg-white rounded-xl shadow-sm p-6 mb-8">
            <h2 class="text-xl font-semibold text-slate-800 mb-4">Overall Summary</h2>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-{"green" if completed == total else "amber"}-600">{completed}/{total}</div>
                    <div class="text-sm text-slate-600">Packs Completed</div>
                </div>
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-slate-800">{total_duration:.0f}s</div>
                    <div class="text-sm text-slate-600">Total Duration</div>
                </div>
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-indigo-600">{avg_claims:.0f}</div>
                    <div class="text-sm text-slate-600">Avg Claims</div>
                </div>
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-teal-600">{avg_score:.1%}</div>
                    <div class="text-sm text-slate-600">Avg Evidence Score</div>
                </div>
                <div class="bg-slate-50 rounded-lg p-4 text-center">
                    <div class="text-3xl font-bold text-purple-600">14</div>
                    <div class="text-sm text-slate-600">Sections</div>
                </div>
            </div>
        </section>
"""

    # Add each pack result
    for result in results:
        pack_name = result.get("pack_name", "Unknown Pack")
        pack_id = result.get("pack_id", "unknown")
        status = result.get("status", "unknown")
        duration = result.get("duration_seconds", 0)
        session_id = result.get("session_id", "N/A")

        status_color = "green" if status == "completed" else "red"
        status_icon = "✅" if status == "completed" else "❌"

        cr = result.get("cross_reference", {})
        total_claims = cr.get("total_claims", 0)
        evidence_score = cr.get("evidence_score", 0)
        tier_dist = cr.get("tier_distribution", {})
        prefixes = cr.get("prefixes_found", [])

        sections = result.get("sections", {})
        section_data = sections.get("sections", {})
        missing = sections.get("missing", [])

        qa = result.get("quality", {})
        overall_score = qa.get("overall_score", 0)
        dimensions = qa.get("dimensions", {})

        html_content += f"""
        <!-- Pack: {pack_name} -->
        <section class="bg-white rounded-xl shadow-sm p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-semibold text-slate-800">{status_icon} {pack_name}</h2>
                <span class="px-3 py-1 rounded-full text-sm font-medium bg-{status_color}-100 text-{status_color}-800">
                    {status.upper()}
                </span>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div class="text-center">
                    <div class="text-2xl font-bold text-slate-800">{duration:.0f}s</div>
                    <div class="text-xs text-slate-500">Duration</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-indigo-600">{total_claims}</div>
                    <div class="text-xs text-slate-500">Total Claims</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-teal-600">{evidence_score:.1%}</div>
                    <div class="text-xs text-slate-500">Evidence Score</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">{overall_score:.1%}</div>
                    <div class="text-xs text-slate-500">Quality Score</div>
                </div>
            </div>

            <!-- Evidence Tier Distribution -->
            <div class="mb-6">
                <h3 class="text-sm font-medium text-slate-700 mb-2">Evidence Tier Distribution</h3>
                <div class="flex gap-2 flex-wrap">
                    <span class="tier-E1 px-3 py-1 rounded-full text-sm font-medium">E1: {tier_dist.get("E1", 0)}</span>
                    <span class="tier-E2 px-3 py-1 rounded-full text-sm font-medium">E2: {tier_dist.get("E2", 0)}</span>
                    <span class="tier-E3 px-3 py-1 rounded-full text-sm font-medium">E3: {tier_dist.get("E3", 0)}</span>
                    <span class="tier-E4 px-3 py-1 rounded-full text-sm font-medium">E4: {tier_dist.get("E4", 0)}</span>
                    <span class="tier-E5 px-3 py-1 rounded-full text-sm font-medium">E5: {tier_dist.get("E5", 0)}</span>
                </div>
                <div class="mt-2 text-xs text-slate-500">
                    Section Prefixes: {", ".join(sorted(prefixes)) if prefixes else "N/A"}
                </div>
            </div>

            <!-- Sections Grid -->
            <div class="mb-6">
                <h3 class="text-sm font-medium text-slate-700 mb-2">Sections</h3>
                <div class="grid grid-cols-3 md:grid-cols-5 gap-2">
"""

        # Add section badges
        section_names = [
            ("customer_research", "Market Intel"),
            ("competitive_analysis", "Competitive"),
            ("detailed_personas", "Personas"),
            ("business_case", "Business Case"),
            ("gtm_plan", "GTM"),
            ("financial_model", "Financial"),
            ("product_requirements", "PRD"),
            ("technical_architecture", "Tech Arch"),
            ("legal_regulatory_review", "Legal"),
            ("risk_assessment", "Risk"),
            ("wireframes", "Wireframes"),
            ("prototype", "Prototype"),
            ("stakeholder_views", "Stakeholders"),
            ("validation_playbook", "Validation"),
            ("executive_summary", "Exec Summary"),
        ]

        for key, display_name in section_names:
            is_present = key in section_data and section_data[key].get("present")
            color = "green" if is_present else "red"
            icon = "✓" if is_present else "✗"

            extra_info = ""
            if is_present and key in section_data:
                sec = section_data[key]
                if key == "wireframes" and "screen_count" in sec:
                    extra_info = f" ({sec['screen_count']})"
                elif key == "financial_model" and "monthly_projections" in sec:
                    extra_info = f" ({sec['monthly_projections']}mo)"
                elif key == "validation_playbook" and "experiment_count" in sec:
                    extra_info = f" ({sec['experiment_count']})"

            html_content += f"""
                    <div class="flex items-center gap-1 px-2 py-1 bg-{color}-50 rounded text-xs">
                        <span class="text-{color}-600">{icon}</span>
                        <span class="text-slate-700">{display_name}{extra_info}</span>
                    </div>
"""

        html_content += """
                </div>
            </div>
"""

        # Quality dimensions if available
        if dimensions:
            html_content += """
            <!-- Quality Dimensions -->
            <div class="mb-4">
                <h3 class="text-sm font-medium text-slate-700 mb-2">Quality Dimensions</h3>
                <div class="grid grid-cols-5 gap-2">
"""
            for dim, score in dimensions.items():
                color = "green" if score >= 7 else ("amber" if score >= 5 else "red")
                html_content += f"""
                    <div class="text-center bg-slate-50 rounded p-2">
                        <div class="text-lg font-bold text-{color}-600">{score}/10</div>
                        <div class="text-xs text-slate-500 truncate">{dim.replace("_", " ").title()}</div>
                    </div>
"""
            html_content += """
                </div>
            </div>
"""

        html_content += f"""
            <div class="text-xs text-slate-400">
                Session ID: {session_id}
            </div>
        </section>
"""

    # Footer
    html_content += """
        <!-- Footer -->
        <footer class="text-center text-slate-500 text-sm py-4">
            <p>Seedcraft v3.0 — Cross-Reference Evidence Grading System</p>
        </footer>
    </div>
</body>
</html>
"""

    with open(html_file, "w") as f:
        f.write(html_content)

    return html_file


def print_results_summary(results: list[dict]) -> None:
    """Print a formatted summary of all test results."""
    print("\n" + "=" * 80)
    print("SEEDCRAFT v3.0 E2E SHOWCASE TEST RESULTS")
    print("=" * 80)

    for result in results:
        print(f"\n{'─' * 80}")
        print(f"📦 {result['pack_name']}")
        print(f"{'─' * 80}")

        status_emoji = "✅" if result["status"] == "completed" else "❌"
        print(f"Status: {status_emoji} {result['status']}")
        print(f"Duration: {result.get('duration_seconds', 0):.1f}s")
        print(f"Session ID: {result['session_id']}")

        if result.get("error"):
            print(f"Error: {result['error']}")
            continue

        # Cross-reference results
        cr = result.get("cross_reference", {})
        print(f"\n📊 Cross-Reference Index:")
        print(f"   Total Claims: {cr.get('total_claims', 0)}")
        print(f"   Evidence Score: {cr.get('evidence_score', 0):.1%}")
        print(f"   Grounded (E1-E3): {cr.get('grounded_claims', 0)}")
        print(f"   Hypothesis (E4-E5): {cr.get('hypothesis_claims', 0)}")
        print(f"   Section Prefixes: {', '.join(cr.get('prefixes_found', []))}")

        if cr.get("warning"):
            print(f"   ⚠️  {cr['warning']}")

        # Section results
        sections = result.get("sections", {})
        missing = sections.get("missing", [])
        present = [k for k, v in sections.get("sections", {}).items() if v.get("present")]

        print(f"\n📄 Sections:")
        print(f"   Present: {len(present)}/{len(present) + len(missing)}")
        if missing:
            print(f"   Missing: {', '.join(missing)}")

        # Highlight key sections
        for key in ["wireframes", "prototype", "stakeholder_views", "validation_playbook"]:
            if key in sections.get("sections", {}):
                sec = sections["sections"][key]
                if key == "wireframes" and "screen_count" in sec:
                    print(f"   • Wireframes: {sec['screen_count']} screens")
                if key == "stakeholder_views" and "view_roles" in sec:
                    print(f"   • Stakeholder Views: {', '.join(sec['view_roles'])}")
                if key == "validation_playbook" and "experiment_count" in sec:
                    print(f"   • Validation Playbook: {sec['experiment_count']} experiments")

        # Quality results
        qa = result.get("quality", {})
        if qa.get("valid"):
            print(f"\n🎯 Quality Assessment:")
            print(f"   Overall Score: {qa.get('overall_score', 0):.1%}")
            if qa.get("dimensions"):
                for dim, score in qa["dimensions"].items():
                    print(f"   • {dim}: {score}/10")

        if result.get("state_file"):
            print(f"\n💾 State saved to: {result['state_file']}")

    # Overall summary
    print(f"\n{'=' * 80}")
    print("OVERALL SUMMARY")
    print("=" * 80)

    completed = sum(1 for r in results if r["status"] == "completed")
    total = len(results)
    print(f"Completed: {completed}/{total}")

    total_duration = sum(r.get("duration_seconds", 0) for r in results)
    print(f"Total Duration: {total_duration:.1f}s")

    avg_claims = sum(
        r.get("cross_reference", {}).get("total_claims", 0)
        for r in results if r["status"] == "completed"
    ) / max(completed, 1)
    print(f"Average Claims: {avg_claims:.0f}")

    avg_score = sum(
        r.get("cross_reference", {}).get("evidence_score", 0)
        for r in results if r["status"] == "completed"
    ) / max(completed, 1)
    print(f"Average Evidence Score: {avg_score:.1%}")


async def main():
    """Main entry point for E2E showcase tests."""
    print("=" * 80)
    print("SEEDCRAFT v3.0 E2E SHOWCASE TEST")
    print("=" * 80)
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Test Packs: {len(SHOWCASE_PACKS)}")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent / "test_outputs" / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output Directory: {output_dir}")
    print()

    # Check for required environment variables
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = [v for v in required_vars if not os.getenv(v)]
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        sys.exit(1)

    results = []

    for i, pack_config in enumerate(SHOWCASE_PACKS):
        print(f"\n{'─' * 80}")
        print(f"Running Pack {i + 1}/{len(SHOWCASE_PACKS)}: {pack_config['name']}")
        print(f"{'─' * 80}")

        result = await run_showcase_pack(pack_config, output_dir)
        results.append(result)

        # Save intermediate results
        results_file = output_dir / "results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

    # Print summary
    print_results_summary(results)

    # Generate HTML report
    html_file = generate_html_report(results, output_dir)
    print(f"\n📁 Full results saved to: {output_dir}/results.json")
    print(f"📊 HTML Report: {html_file}")
    print(f"\n🌐 Open in browser: file://{html_file}")


if __name__ == "__main__":
    asyncio.run(main())
