"""
Pytest configuration and shared fixtures for all tests.

This file is automatically loaded by pytest and provides:
- Common fixtures for sample inception packs
- Helper functions for test assertions
- Configuration for test paths
"""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add backend to path for imports
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Test directories
TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
SNAPSHOTS_DIR = TESTS_DIR / "snapshots"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture file by name."""
    fixture_path = FIXTURES_DIR / f"{name}.json"
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
    with open(fixture_path) as f:
        return json.load(f)


def save_snapshot(name: str, content: bytes | str, extension: str = "txt") -> Path:
    """Save a snapshot file."""
    snapshot_path = SNAPSHOTS_DIR / f"{name}.{extension}"
    if isinstance(content, str):
        snapshot_path.write_text(content)
    else:
        snapshot_path.write_bytes(content)
    return snapshot_path


def load_snapshot(name: str, extension: str = "txt") -> bytes | str | None:
    """Load a snapshot file if it exists."""
    snapshot_path = SNAPSHOTS_DIR / f"{name}.{extension}"
    if not snapshot_path.exists():
        return None
    if extension in ("txt", "json", "html"):
        return snapshot_path.read_text()
    return snapshot_path.read_bytes()


# ============================================================================
# Fixtures: Sample Inception Packs
# ============================================================================

@pytest.fixture
def minimal_pack() -> dict[str, Any]:
    """Minimal inception pack with only required fields."""
    return load_fixture("sample_pack_minimal")


@pytest.fixture
def full_pack() -> dict[str, Any]:
    """Complete inception pack with all sections populated."""
    return load_fixture("sample_pack_full")


@pytest.fixture
def edge_cases_pack() -> dict[str, Any]:
    """Pack with edge cases: empty arrays, None values, unicode, etc."""
    return load_fixture("sample_pack_edge_cases")


@pytest.fixture
def nested_dicts_pack() -> dict[str, Any]:
    """Pack with deeply nested dict/list structures."""
    return load_fixture("sample_pack_nested")


# ============================================================================
# Fixtures: Export Utilities
# ============================================================================

@pytest.fixture
def docx_generator():
    """Import and return the DOCX generator function."""
    from utils.export_docx import generate_docx
    return generate_docx


@pytest.fixture
def extract_first_string():
    """Import and return the string extraction helper."""
    from utils.export_docx import _extract_first_string
    return _extract_first_string


@pytest.fixture
def format_list_value():
    """Import and return the list formatting helper."""
    from utils.export_docx import _format_list_value
    return _format_list_value


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def snapshot_dir() -> Path:
    """Return the snapshots directory path."""
    return SNAPSHOTS_DIR


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the fixtures directory path."""
    return FIXTURES_DIR


# ============================================================================
# Assertion Helpers
# ============================================================================

def assert_no_raw_json(text: str) -> None:
    """Assert that text contains no raw JSON/dict syntax."""
    # Check for raw dict syntax like {'key': 'value'} or {"key": "value"}
    import re

    # Pattern for dict-like syntax (but allow URLs and other valid uses of {})
    raw_dict_pattern = r"\{['\"][\w_]+['\"]:\s*['\"]"
    matches = re.findall(raw_dict_pattern, text)

    assert not matches, f"Found raw dict syntax in text: {matches[:3]}..."

    # Check for raw list syntax like ['item'] but not markdown [links](url)
    raw_list_pattern = r"\[['\"][\w\s]+['\"](?:,\s*['\"][\w\s]+['\"])*\]"
    matches = re.findall(raw_list_pattern, text)

    assert not matches, f"Found raw list syntax in text: {matches[:3]}..."


def assert_readable_text(text: str) -> None:
    """Assert that text is human-readable (no obvious JSON artifacts)."""
    assert_no_raw_json(text)

    # Should not have excessive punctuation from JSON
    assert text.count("{}") == 0, "Found empty dict '{}' in text"
    assert text.count("[]") == 0, "Found empty list '[]' in text"


# Export assertion helpers for use in tests
pytest.assert_no_raw_json = assert_no_raw_json
pytest.assert_readable_text = assert_readable_text


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================

def pytest_addoption(parser):
    """Add custom command line options for tests."""
    try:
        parser.addoption(
            "--update-snapshots",
            action="store_true",
            default=False,
            help="Update snapshot files with current output",
        )
    except ValueError:
        # Option already added by another conftest
        pass
