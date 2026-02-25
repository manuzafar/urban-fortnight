"""
Eval CLI — Command-line interface for running evaluations.

Usage:
    python -m evals.cli run test_outputs/state.json
    python -m evals.cli run test_outputs/state.json -t unit
    python -m evals.cli run test_outputs/state.json --golden-set banking_v1
    python -m evals.cli create-golden state.json banking_v1 --name "AI Banking"
    python -m evals.cli list-golden
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click

from evals.base import EvalType
from evals.runner import EvalRunner
from evals.reporter import EvalReporter
from evals.golden.golden_set_manager import GoldenSetManager


@click.group()
def cli():
    """Eval CLI for the Product Discovery Multi-Agent System."""
    pass


@cli.command()
@click.argument("state_path", type=click.Path(exists=True))
@click.option(
    "-t", "--type",
    "eval_types",
    multiple=True,
    type=click.Choice(["unit", "llm_judge", "golden", "consistency", "agent_specific"]),
    help="Types of evals to run (can specify multiple)"
)
@click.option(
    "-a", "--agent",
    "agents",
    multiple=True,
    help="Specific agents to evaluate (can specify multiple)"
)
@click.option(
    "--golden-set", "-g",
    help="Golden set ID for comparison"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path for results (JSON)"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["console", "json", "markdown"]),
    default="console",
    help="Output format"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Verbose output"
)
@click.option(
    "--sequential",
    is_flag=True,
    help="Run evals sequentially (not parallel)"
)
def run(
    state_path: str,
    eval_types: tuple[str, ...],
    agents: tuple[str, ...],
    golden_set: Optional[str],
    output: Optional[str],
    format: str,
    verbose: bool,
    sequential: bool,
):
    """Run evaluations on a state file."""
    # Convert type strings to EvalType enum
    type_list = None
    if eval_types:
        type_list = [EvalType(t) for t in eval_types]

    # Convert agents to list
    agent_list = list(agents) if agents else None

    # Create runner
    runner = EvalRunner(
        eval_types=type_list,
        agents=agent_list,
        golden_set_path=golden_set,
        parallel=not sequential,
    )

    # Run evals
    click.echo(f"Running evals on {state_path}...")
    result = asyncio.run(runner.run(state_path))

    # Create reporter
    reporter = EvalReporter(result)

    # Output results
    if format == "json":
        output_text = reporter.to_json()
    elif format == "markdown":
        output_text = reporter.to_markdown()
    else:
        output_text = reporter.to_console(verbose=verbose)

    if output:
        Path(output).write_text(output_text)
        click.echo(f"Results written to {output}")
    else:
        click.echo(output_text)

    # Exit with error code if critical failures
    if result.has_critical_failures:
        sys.exit(1)


@cli.command("create-golden")
@click.argument("state_path", type=click.Path(exists=True))
@click.argument("golden_set_id")
@click.option(
    "--name", "-n",
    help="Human-readable name for the golden set"
)
@click.option(
    "--version", "-v",
    default="1.0",
    help="Version string"
)
def create_golden(
    state_path: str,
    golden_set_id: str,
    name: Optional[str],
    version: str,
):
    """Create a golden set from a state file."""
    # Load state
    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception as e:
        click.echo(f"Error loading state: {e}", err=True)
        sys.exit(1)

    # Create golden set
    manager = GoldenSetManager()
    success = manager.save(
        golden_set_id=golden_set_id,
        state=state,
        name=name or golden_set_id,
        version=version,
    )

    if success:
        click.echo(f"Golden set '{golden_set_id}' created successfully")
    else:
        click.echo("Failed to create golden set", err=True)
        sys.exit(1)


@cli.command("list-golden")
def list_golden():
    """List available golden sets."""
    manager = GoldenSetManager()
    golden_sets = manager.list_golden_sets()

    if not golden_sets:
        click.echo("No golden sets found.")
        return

    click.echo("\nAvailable Golden Sets:")
    click.echo("-" * 60)

    for gs in golden_sets:
        click.echo(f"\n{gs['id']}:")
        click.echo(f"  Name: {gs['name']}")
        click.echo(f"  Version: {gs['version']}")
        click.echo(f"  Created: {gs['created_at']}")
        if gs.get('quality_score'):
            click.echo(f"  Quality Score: {gs['quality_score']:.1%}")
        if gs.get('product_idea'):
            click.echo(f"  Product: {gs['product_idea'][:60]}...")


@cli.command("delete-golden")
@click.argument("golden_set_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete_golden(golden_set_id: str, yes: bool):
    """Delete a golden set."""
    if not yes:
        if not click.confirm(f"Delete golden set '{golden_set_id}'?"):
            return

    manager = GoldenSetManager()
    if manager.delete(golden_set_id):
        click.echo(f"Golden set '{golden_set_id}' deleted")
    else:
        click.echo(f"Golden set '{golden_set_id}' not found", err=True)
        sys.exit(1)


@cli.command("compare")
@click.argument("state_path", type=click.Path(exists=True))
@click.argument("golden_set_id")
@click.option("--verbose", "-v", is_flag=True)
def compare(state_path: str, golden_set_id: str, verbose: bool):
    """Compare a state file against a golden set."""
    from evals.golden.similarity_scorer import SimilarityScorer

    # Load state
    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception as e:
        click.echo(f"Error loading state: {e}", err=True)
        sys.exit(1)

    # Load golden set
    manager = GoldenSetManager()
    golden_data = manager.load(golden_set_id)

    if not golden_data:
        click.echo(f"Golden set '{golden_set_id}' not found", err=True)
        sys.exit(1)

    golden_state = golden_data.get("state", {})

    # Compare
    scorer = SimilarityScorer()
    result = scorer.score_full_state(state, golden_state)

    click.echo(f"\nComparison: {state_path} vs {golden_set_id}")
    click.echo("=" * 60)
    click.echo(f"Overall Similarity: {result['overall']:.1%}")
    click.echo(f"Sections Compared: {result['sections_compared']}")

    if verbose:
        click.echo("\nPer-Section Scores:")
        click.echo("-" * 40)
        for section, scores in result.get("sections", {}).items():
            click.echo(f"\n{section}:")
            click.echo(f"  Overall: {scores['overall']:.1%}")
            click.echo(f"  Key Overlap: {scores['key_overlap']:.1%}")
            click.echo(f"  Content Similarity: {scores['content_similarity']:.1%}")
            click.echo(f"  Field Coverage: {scores['field_coverage']:.1%}")


@cli.command("summary")
@click.argument("state_path", type=click.Path(exists=True))
def summary(state_path: str):
    """Show a quick summary of a state file."""
    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception as e:
        click.echo(f"Error loading state: {e}", err=True)
        sys.exit(1)

    click.echo(f"\nState Summary: {state_path}")
    click.echo("=" * 60)

    # Product idea
    product_idea = state.get("product_idea", "")[:100]
    click.echo(f"Product: {product_idea}")

    # Sections present
    sections = [
        "executive_summary",
        "customer_research",
        "business_case",
        "product_requirements_document",
        "technical_architecture",
        "legal_regulatory_review",
        "gtm_strategy",
        "financial_model",
        "stakeholder_views",
        "validation_playbook",
        "wireframes",
        "prototype",
    ]

    click.echo("\nSections:")
    for section in sections:
        present = "✓" if state.get(section) else "✗"
        click.echo(f"  {present} {section}")

    # Quality info
    quality = state.get("quality_assessment", {})
    if quality:
        click.echo(f"\nQuality Score: {quality.get('overall_score', 'N/A')}")
        click.echo(f"Quality Passed: {quality.get('passed', 'N/A')}")


# ═══════════════════════════════════════════════════════════════════════════════
# GOLDEN SET SUBCOMMANDS
# ═══════════════════════════════════════════════════════════════════════════════


@cli.group("golden")
def golden():
    """Golden set management commands."""
    pass


@golden.command("create")
@click.argument("state_path", type=click.Path(exists=True))
@click.option("--id", "golden_id", help="ID for the golden set (defaults to filename)")
@click.option("--name", "-n", help="Human-readable name")
@click.option("--domain", "-d", help="Domain category (e.g., B2B_SaaS, Fintech, Healthcare)")
@click.option("--version", "-v", default="1.0", help="Version string")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing golden set")
def golden_create(
    state_path: str,
    golden_id: Optional[str],
    name: Optional[str],
    domain: Optional[str],
    version: str,
    force: bool,
):
    """Create a new golden set from a state file.

    Example:
        python -m evals.cli golden create output.json --name "B2B SaaS Example" --domain B2B_SaaS
    """
    # Load state
    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception as e:
        click.echo(f"Error loading state: {e}", err=True)
        sys.exit(1)

    # Generate ID if not provided
    if not golden_id:
        golden_id = Path(state_path).stem
        if golden_id.startswith("e2e_test_"):
            golden_id = golden_id.replace("e2e_test_", "golden_")

    # Check if exists
    manager = GoldenSetManager()
    existing = manager.load(golden_id)
    if existing and not force:
        click.echo(f"Golden set '{golden_id}' already exists. Use --force to overwrite.", err=True)
        sys.exit(1)

    # Add domain to state metadata if provided
    if domain:
        # Store domain in the state for later retrieval
        if "metadata" not in state:
            state["metadata"] = {}
        state["metadata"]["domain"] = domain

    # Save golden set with updated metadata
    # We need to extend the save method or add domain to metadata
    manager.golden_sets_dir.mkdir(parents=True, exist_ok=True)

    golden_data = {
        "metadata": {
            "name": name or golden_id,
            "version": version,
            "created_at": __import__("datetime").datetime.utcnow().isoformat(),
            "quality_score": None,
            "product_idea": state.get("product_idea", ""),
            "domain": domain or "",
        },
        "state": state,
    }

    path = manager.golden_sets_dir / f"{golden_id}.json"
    try:
        with open(path, "w") as f:
            json.dump(golden_data, f, indent=2, default=str)
        click.echo(f"Golden set '{golden_id}' created at {path}")
    except Exception as e:
        click.echo(f"Failed to create golden set: {e}", err=True)
        sys.exit(1)


@golden.command("compare")
@click.argument("state_path", type=click.Path(exists=True))
@click.option("--golden-id", "-g", help="Compare against specific golden set (default: all)")
@click.option("--output", "-o", type=click.Path(), help="Save results to JSON file")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed section scores")
@click.option("--threshold", "-t", type=float, default=0.5, help="Minimum similarity threshold")
def golden_compare(
    state_path: str,
    golden_id: Optional[str],
    output: Optional[str],
    verbose: bool,
    threshold: float,
):
    """Compare a state file against golden sets for regression detection.

    Example:
        python -m evals.cli golden compare output.json -v
        python -m evals.cli golden compare output.json -g b2b_saas_meeting_room_v1
    """
    from evals.golden.similarity_scorer import SimilarityScorer
    from evals.golden.golden_set_eval import GoldenSetRegression

    # Load state
    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception as e:
        click.echo(f"Error loading state: {e}", err=True)
        sys.exit(1)

    manager = GoldenSetManager()
    scorer = SimilarityScorer(manager)

    if golden_id:
        # Compare against specific golden set
        golden_data = manager.load(golden_id)
        if not golden_data:
            click.echo(f"Golden set '{golden_id}' not found", err=True)
            sys.exit(1)

        golden_state = golden_data.get("state", {})
        result = scorer.score_full_state(state, golden_state)

        click.echo(f"\nComparison: {state_path} vs {golden_id}")
        click.echo("=" * 70)
        click.echo(f"Overall Similarity: {result['overall']:.1%}")
        click.echo(f"Sections Compared: {result['sections_compared']}")

        if result['overall'] < threshold:
            click.echo(f"\n[WARNING] Similarity {result['overall']:.1%} below threshold {threshold:.1%}")

        if verbose:
            click.echo("\nPer-Section Scores:")
            click.echo("-" * 50)
            for section, scores in result.get("sections", {}).items():
                status = "OK" if scores['overall'] >= threshold else "LOW"
                click.echo(f"\n[{status}] {section}: {scores['overall']:.1%}")
                click.echo(f"      Key Overlap: {scores['key_overlap']:.1%}")
                click.echo(f"      Content Sim: {scores['content_similarity']:.1%}")
                click.echo(f"      Coverage:    {scores['field_coverage']:.1%}")

        if output:
            Path(output).write_text(json.dumps(result, indent=2))
            click.echo(f"\nResults saved to {output}")

    else:
        # Compare against all golden sets
        comparison = manager.compare_to_all(state, scorer)

        click.echo(f"\nComparison Against All Golden Sets")
        click.echo("=" * 70)
        click.echo(f"Best Match: {comparison['best_match']} ({comparison['best_score']:.1%})")
        click.echo(f"Golden Sets Compared: {len(comparison['all_comparisons'])}")

        click.echo("\nAll Comparisons:")
        click.echo("-" * 50)
        for gs_id, comp_data in sorted(
            comparison['all_comparisons'].items(),
            key=lambda x: x[1]['scores']['overall'],
            reverse=True
        ):
            score = comp_data['scores']['overall']
            name = comp_data.get('name', gs_id)
            domain = comp_data.get('domain', 'unknown')
            status = "PASS" if score >= threshold else "FAIL"
            click.echo(f"  [{status}] {gs_id}: {score:.1%}")
            click.echo(f"        Name: {name}, Domain: {domain}")

        if verbose:
            click.echo("\n\nDetailed Section Scores for Best Match:")
            click.echo("-" * 50)
            best_id = comparison['best_match']
            if best_id:
                best_data = comparison['all_comparisons'][best_id]
                for section, scores in best_data['scores'].get('sections', {}).items():
                    click.echo(f"  {section}: {scores['overall']:.1%}")

        if output:
            Path(output).write_text(json.dumps(comparison, indent=2))
            click.echo(f"\nResults saved to {output}")

        # Exit with error if below threshold
        if comparison['best_score'] < threshold:
            click.echo(f"\n[FAIL] Best similarity {comparison['best_score']:.1%} below threshold {threshold:.1%}")
            sys.exit(1)


@golden.command("list")
@click.option("--domain", "-d", help="Filter by domain")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table")
def golden_list(domain: Optional[str], format: str):
    """List all available golden sets.

    Example:
        python -m evals.cli golden list
        python -m evals.cli golden list --domain Fintech
    """
    manager = GoldenSetManager()

    if domain:
        golden_sets = manager.list_by_domain(domain)
    else:
        golden_sets = manager.list_golden_sets()

    if not golden_sets:
        click.echo("No golden sets found.")
        return

    if format == "json":
        click.echo(json.dumps(golden_sets, indent=2))
        return

    click.echo(f"\nGolden Sets ({len(golden_sets)} total)")
    click.echo("=" * 80)

    for gs in golden_sets:
        click.echo(f"\n  ID: {gs['id']}")
        click.echo(f"  Name: {gs['name']}")
        click.echo(f"  Domain: {gs.get('domain', 'N/A')}")
        click.echo(f"  Version: {gs['version']}")
        click.echo(f"  Created: {gs['created_at']}")
        if gs.get('quality_score'):
            click.echo(f"  Quality Score: {gs['quality_score']:.1%}")
        if gs.get('product_idea'):
            click.echo(f"  Product: {gs['product_idea'][:60]}...")
        click.echo("-" * 40)


@golden.command("delete")
@click.argument("golden_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def golden_delete(golden_id: str, yes: bool):
    """Delete a golden set.

    Example:
        python -m evals.cli golden delete old_golden_set_v1 -y
    """
    manager = GoldenSetManager()

    if not manager.load(golden_id):
        click.echo(f"Golden set '{golden_id}' not found", err=True)
        sys.exit(1)

    if not yes:
        if not click.confirm(f"Delete golden set '{golden_id}'?"):
            return

    if manager.delete(golden_id):
        click.echo(f"Golden set '{golden_id}' deleted")
    else:
        click.echo(f"Failed to delete golden set '{golden_id}'", err=True)
        sys.exit(1)


@golden.command("validate")
@click.argument("state_path", type=click.Path(exists=True))
def golden_validate(state_path: str):
    """Validate a state file is suitable for golden set creation.

    Checks completeness and structure.

    Example:
        python -m evals.cli golden validate output.json
    """
    from evals.golden.golden_set_eval import GoldenSetCoverage

    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception as e:
        click.echo(f"Error loading state: {e}", err=True)
        sys.exit(1)

    coverage_eval = GoldenSetCoverage()

    # Run coverage check
    import asyncio
    result = asyncio.run(coverage_eval.evaluate(
        agent_output={},
        agent_name="full_state",
        context={"full_state": state}
    ))

    click.echo(f"\nValidation Results: {state_path}")
    click.echo("=" * 60)
    click.echo(f"Status: {'PASS' if result.passed else 'FAIL'}")
    click.echo(f"Coverage Score: {result.score:.1%}")
    click.echo(f"Message: {result.message}")

    if result.details:
        missing = result.details.get("missing_required", [])
        optional = result.details.get("present_optional", [])

        if missing:
            click.echo(f"\nMissing Required Sections:")
            for section in missing:
                click.echo(f"  - {section}")

        if optional:
            click.echo(f"\nOptional Sections Present ({len(optional)}):")
            for section in optional:
                click.echo(f"  + {section}")

    if result.passed:
        click.echo("\n[OK] State file is suitable for golden set creation")
    else:
        click.echo("\n[FAIL] State file is not suitable for golden set creation")
        sys.exit(1)


if __name__ == "__main__":
    cli()
