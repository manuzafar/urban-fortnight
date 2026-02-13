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


if __name__ == "__main__":
    cli()
