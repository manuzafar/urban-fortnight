"""
Snapshot (Golden File) tests for export regression testing.

These tests compare generated output against known-good snapshots.
When output changes intentionally, update snapshots with:
    pytest tests/integration/test_export_snapshots.py --update-snapshots

Or manually by deleting the snapshot file and running tests.
"""

import pytest
import hashlib
import json
from pathlib import Path
from io import BytesIO
import zipfile
from xml.etree import ElementTree
from typing import Any


# Snapshot configuration
SNAPSHOTS_DIR = Path(__file__).parent.parent / "snapshots"


def extract_docx_structure(docx_bytes: bytes) -> dict[str, Any]:
    """
    Extract a normalized structure from a DOCX file for comparison.

    Returns a dict with:
    - text_content: All text extracted from the document
    - paragraph_count: Number of paragraphs
    - table_count: Number of tables
    - heading_texts: List of heading texts
    """
    with zipfile.ZipFile(BytesIO(docx_bytes)) as zf:
        xml_content = zf.read("word/document.xml")
        tree = ElementTree.fromstring(xml_content)

        namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        # Extract all text
        text_nodes = tree.findall(".//w:t", namespaces)
        text_content = " ".join(node.text or "" for node in text_nodes)

        # Count paragraphs
        paragraphs = tree.findall(".//w:p", namespaces)

        # Count tables
        tables = tree.findall(".//w:tbl", namespaces)

        # Extract headings (paragraphs with heading styles)
        headings = []
        for p in paragraphs:
            style = p.find(".//w:pStyle", namespaces)
            if style is not None:
                style_val = style.get(f"{{{namespaces['w']}}}val", "")
                if "Heading" in style_val:
                    p_text = "".join(t.text or "" for t in p.findall(".//w:t", namespaces))
                    if p_text.strip():
                        headings.append(p_text.strip())

        return {
            "text_content": text_content,
            "paragraph_count": len(paragraphs),
            "table_count": len(tables),
            "heading_texts": headings,
        }


def normalize_text(text: str) -> str:
    """Normalize text for comparison (handle whitespace differences)."""
    import re
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


class TestDocxSnapshots:
    """Snapshot tests for DOCX generation."""

    def _get_snapshot_path(self, name: str) -> Path:
        return SNAPSHOTS_DIR / f"{name}.json"

    def _save_snapshot(self, name: str, data: dict[str, Any]) -> None:
        """Save snapshot data to file."""
        snapshot_path = self._get_snapshot_path(name)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with open(snapshot_path, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def _load_snapshot(self, name: str) -> dict[str, Any] | None:
        """Load snapshot data from file, or None if it doesn't exist."""
        snapshot_path = self._get_snapshot_path(name)
        if not snapshot_path.exists():
            return None
        with open(snapshot_path) as f:
            return json.load(f)

    def _compare_structure(
        self, actual: dict[str, Any], expected: dict[str, Any], name: str
    ) -> None:
        """Compare document structures with helpful error messages."""
        # Compare paragraph count (allow some variance)
        actual_p = actual["paragraph_count"]
        expected_p = expected["paragraph_count"]
        variance = abs(actual_p - expected_p) / max(expected_p, 1)
        assert variance < 0.2, (
            f"Paragraph count changed significantly: {expected_p} -> {actual_p} "
            f"({variance:.0%} change) in {name}"
        )

        # Compare table count
        assert actual["table_count"] == expected["table_count"], (
            f"Table count changed: {expected['table_count']} -> {actual['table_count']} "
            f"in {name}"
        )

        # Compare headings (order matters)
        actual_headings = actual["heading_texts"]
        expected_headings = expected["heading_texts"]

        # Check that expected headings are present (allow new headings)
        for heading in expected_headings:
            assert any(
                normalize_text(heading) in normalize_text(h) for h in actual_headings
            ), f"Expected heading '{heading}' not found in {name}"

        # Compare text content similarity
        actual_text = normalize_text(actual["text_content"])
        expected_text = normalize_text(expected["text_content"])

        # Check for key content preservation
        expected_words = set(expected_text.split())
        actual_words = set(actual_text.split())

        # At least 90% of expected words should be present
        common_words = expected_words & actual_words
        if len(expected_words) > 0:
            similarity = len(common_words) / len(expected_words)
            assert similarity > 0.9, (
                f"Text content changed significantly in {name}: "
                f"only {similarity:.0%} of expected words found"
            )

    def test_full_pack_snapshot(self, full_pack, docx_generator, request):
        """Test full pack export matches snapshot."""
        snapshot_name = "docx_full_pack"

        result = docx_generator(full_pack)
        actual_structure = extract_docx_structure(result)

        expected = self._load_snapshot(snapshot_name)

        if expected is None:
            # First run - create snapshot
            self._save_snapshot(snapshot_name, actual_structure)
            pytest.skip(
                f"Snapshot created: {self._get_snapshot_path(snapshot_name)}. "
                "Review and commit the snapshot file."
            )

        # Check for --update-snapshots flag
        if request.config.getoption("--update-snapshots", default=False):
            self._save_snapshot(snapshot_name, actual_structure)
            pytest.skip(f"Snapshot updated: {snapshot_name}")

        self._compare_structure(actual_structure, expected, snapshot_name)

    def test_minimal_pack_snapshot(self, minimal_pack, docx_generator, request):
        """Test minimal pack export matches snapshot."""
        snapshot_name = "docx_minimal_pack"

        result = docx_generator(minimal_pack)
        actual_structure = extract_docx_structure(result)

        expected = self._load_snapshot(snapshot_name)

        if expected is None:
            self._save_snapshot(snapshot_name, actual_structure)
            pytest.skip(f"Snapshot created: {snapshot_name}")

        if request.config.getoption("--update-snapshots", default=False):
            self._save_snapshot(snapshot_name, actual_structure)
            pytest.skip(f"Snapshot updated: {snapshot_name}")

        self._compare_structure(actual_structure, expected, snapshot_name)

    def test_section_snapshots(self, full_pack, docx_generator, request):
        """Test individual section exports match snapshots."""
        sections = [
            "executive_summary",
            "customer_research",
            "business_case",
        ]

        for section in sections:
            snapshot_name = f"docx_section_{section}"

            result = docx_generator(full_pack, section=section)
            actual_structure = extract_docx_structure(result)

            expected = self._load_snapshot(snapshot_name)

            if expected is None:
                self._save_snapshot(snapshot_name, actual_structure)
                continue  # Create all snapshots on first run

            if request.config.getoption("--update-snapshots", default=False):
                self._save_snapshot(snapshot_name, actual_structure)
                continue

            self._compare_structure(actual_structure, expected, snapshot_name)


class TestTextContentSnapshots:
    """Test that specific text content is preserved across versions."""

    def test_no_raw_json_regression(self, full_pack, docx_generator):
        """Regression test: ensure raw JSON never appears in output."""
        result = docx_generator(full_pack)

        with zipfile.ZipFile(BytesIO(result)) as zf:
            xml_content = zf.read("word/document.xml")
            tree = ElementTree.fromstring(xml_content)

            namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            text_nodes = tree.findall(".//w:t", namespaces)
            text = " ".join(node.text or "" for node in text_nodes)

        # These patterns should NEVER appear
        forbidden_patterns = [
            "{'",  # Python dict start
            "'}",  # Python dict end
            '{"',  # JSON dict start
            '"}',  # JSON dict end
            "['",  # Python list start
            "']",  # Python list end
        ]

        for pattern in forbidden_patterns:
            assert pattern not in text, f"Found forbidden pattern '{pattern}' in DOCX"

    def test_key_content_preserved(self, full_pack, docx_generator):
        """Test that key content from the pack appears in output."""
        result = docx_generator(full_pack)

        with zipfile.ZipFile(BytesIO(result)) as zf:
            xml_content = zf.read("word/document.xml")
            tree = ElementTree.fromstring(xml_content)

            namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            text_nodes = tree.findall(".//w:t", namespaces)
            text = " ".join(node.text or "" for node in text_nodes).lower()

        # Key content that must appear
        required_content = [
            "inventoryai pro",  # Product name
            "smart inventory",  # Tagline
            "executive summary",  # Section heading
            "customer research",  # Section heading
            "business case",  # Section heading
            "tam",  # Market sizing
            "sam",  # Market sizing
        ]

        for content in required_content:
            assert content in text, f"Required content '{content}' not found in DOCX"


class TestExportStability:
    """Test that exports are stable across multiple runs."""

    def test_deterministic_output(self, full_pack, docx_generator):
        """Test that the same input produces structurally identical output."""
        result1 = docx_generator(full_pack)
        result2 = docx_generator(full_pack)

        structure1 = extract_docx_structure(result1)
        structure2 = extract_docx_structure(result2)

        # Structure should be identical
        assert structure1["paragraph_count"] == structure2["paragraph_count"]
        assert structure1["table_count"] == structure2["table_count"]
        assert structure1["heading_texts"] == structure2["heading_texts"]

        # Text content should be identical
        assert normalize_text(structure1["text_content"]) == normalize_text(
            structure2["text_content"]
        )


# Note: pytest_addoption is defined in conftest.py
