"""
Integration tests for the export pipeline.

Tests the full flow from inception pack data to generated documents,
ensuring all components work together correctly.
"""

import pytest
from pathlib import Path
from io import BytesIO
from typing import Any
import zipfile
import re

# For extracting DOCX content
from xml.etree import ElementTree


def extract_docx_text(docx_bytes: bytes) -> str:
    """Extract plain text content from a DOCX file."""
    with zipfile.ZipFile(BytesIO(docx_bytes)) as zf:
        # DOCX files are ZIP archives with XML content
        xml_content = zf.read("word/document.xml")
        tree = ElementTree.fromstring(xml_content)

        # Extract all text nodes
        namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        text_nodes = tree.findall(".//w:t", namespaces)
        return " ".join(node.text or "" for node in text_nodes)


class TestDocxExportPipeline:
    """Test the complete DOCX export pipeline."""

    def test_full_pack_generates_valid_docx(self, full_pack, docx_generator):
        """Test that a full pack generates a valid DOCX file."""
        result = docx_generator(full_pack)

        # Should be valid bytes
        assert isinstance(result, bytes)
        assert len(result) > 0

        # Should be a valid ZIP (DOCX is a ZIP format)
        with zipfile.ZipFile(BytesIO(result)) as zf:
            # DOCX must contain these files
            assert "word/document.xml" in zf.namelist()
            assert "[Content_Types].xml" in zf.namelist()

    def test_full_pack_contains_expected_content(self, full_pack, docx_generator):
        """Test that generated DOCX contains expected text content."""
        result = docx_generator(full_pack)
        text = extract_docx_text(result)

        # Should contain product name
        assert "InventoryAI Pro" in text

        # Should contain section headings
        assert "Executive Summary" in text
        assert "Customer Research" in text
        assert "Business Case" in text

        # Should contain specific content
        assert "Target Customer" in text
        assert "Pain Signals" in text
        assert "Lean Canvas" in text

    def test_full_pack_no_raw_json_in_docx(self, full_pack, docx_generator):
        """Test that DOCX contains no raw JSON/dict syntax."""
        result = docx_generator(full_pack)
        text = extract_docx_text(result)

        # Should not contain Python dict/list repr syntax
        assert "{'key':" not in text.lower()
        assert '{"key":' not in text.lower()

        # Check for list patterns (but allow markdown-style links)
        raw_list_pattern = r"\[['\"]\w+['\"]"
        matches = re.findall(raw_list_pattern, text)
        assert len(matches) == 0, f"Found raw list syntax: {matches}"

    def test_minimal_pack_generates_docx(self, minimal_pack, docx_generator):
        """Test that a minimal pack still generates valid DOCX."""
        result = docx_generator(minimal_pack)

        assert isinstance(result, bytes)
        assert len(result) > 0

        text = extract_docx_text(result)
        assert "TestProduct" in text
        assert "Executive Summary" in text

    def test_edge_cases_pack_no_crash(self, edge_cases_pack, docx_generator):
        """Test that edge cases don't crash the generator."""
        # Should not raise any exceptions
        result = docx_generator(edge_cases_pack)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_edge_cases_pack_handles_unicode(self, edge_cases_pack, docx_generator):
        """Test that unicode and special characters are preserved."""
        result = docx_generator(edge_cases_pack)
        text = extract_docx_text(result)

        # Unicode should be preserved
        assert "日本語" in text
        # Emoji might be stripped but shouldn't crash

    def test_nested_pack_extracts_readable_text(self, nested_dicts_pack, docx_generator):
        """Test that deeply nested structures are converted to readable text."""
        result = docx_generator(nested_dicts_pack)
        text = extract_docx_text(result)

        # Should contain extracted text, not raw dict
        assert "NestedStructures" in text

        # Should not contain nested dict patterns
        nested_dict_pattern = r"\{['\"]?\w+['\"]?:\s*\{['\"]?\w+"
        matches = re.findall(nested_dict_pattern, text)
        assert len(matches) == 0, f"Found nested dict pattern: {matches}"

    def test_single_section_export(self, full_pack, docx_generator):
        """Test exporting a single section."""
        result = docx_generator(full_pack, section="executive_summary")

        text = extract_docx_text(result)

        # Should contain executive summary content
        assert "InventoryAI Pro" in text
        assert "problem" in text.lower()

        # Should NOT contain other section headings (as section titles)
        # Note: some content may reference other areas, but not as section headers
        assert "2. Customer Research" not in text

    def test_all_sections_exportable(self, full_pack, docx_generator):
        """Test that all individual sections can be exported."""
        sections = [
            "executive_summary",
            "customer_research",
            "business_case",
            "product_requirements_document",
            "technical_architecture",
            "legal_regulatory_review",
            "quality_assessment",
        ]

        for section in sections:
            result = docx_generator(full_pack, section=section)
            assert isinstance(result, bytes), f"Failed for section: {section}"
            assert len(result) > 0, f"Empty output for section: {section}"


class TestExportDataTransformations:
    """Test specific data transformations in the export pipeline."""

    def test_lean_canvas_arrays_formatted(self, full_pack, docx_generator):
        """Test that Lean Canvas arrays are properly formatted."""
        result = docx_generator(full_pack, section="business_case")
        text = extract_docx_text(result)

        # Should contain lean canvas content
        assert "Lean Canvas" in text

        # Arrays should be joined, not raw
        # The problems list should appear as joined text
        assert "Manual inventory tracking" in text or "inventory" in text.lower()

    def test_pain_signals_with_evidence_tier(self, full_pack, docx_generator):
        """Test that pain signals show evidence tier prefix."""
        result = docx_generator(full_pack, section="customer_research")
        text = extract_docx_text(result)

        # Should contain evidence tier markers
        assert "E1" in text or "E2" in text

    def test_market_sizing_values(self, full_pack, docx_generator):
        """Test that market sizing TAM/SAM/SOM are displayed."""
        result = docx_generator(full_pack, section="business_case")
        text = extract_docx_text(result)

        # Should contain market sizing labels and values
        assert "TAM" in text
        assert "SAM" in text
        assert "SOM" in text
        assert "$50B" in text or "50B" in text or "50 billion" in text.lower()

    def test_quality_scores_as_percentages(self, full_pack, docx_generator):
        """Test that quality scores are displayed as percentages."""
        result = docx_generator(full_pack, section="quality_assessment")
        text = extract_docx_text(result)

        # Should contain percentage values
        assert "%" in text

        # The overall score of 0.78 should appear as 78%
        assert "78%" in text

    def test_competitors_extracted_properly(self, full_pack, docx_generator):
        """Test that competitor information is extracted and displayed."""
        result = docx_generator(full_pack, section="customer_research")
        text = extract_docx_text(result)

        # Should contain competitor names
        assert "Square" in text or "Lightspeed" in text or "Competitor" in text.lower()


class TestExportRobustness:
    """Test export robustness with various data conditions."""

    def test_handles_missing_sections(self, docx_generator):
        """Test handling of packs with missing sections."""
        partial_pack = {
            "metadata": {"session_id": "test", "generated_at": "2024-01-01"},
            "executive_summary": {"product_name": "Partial", "problem_statement": "Test"},
            # Missing all other sections
        }

        result = docx_generator(partial_pack)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_handles_none_values(self, docx_generator):
        """Test handling of None values throughout the pack."""
        pack_with_nones = {
            "metadata": {"session_id": "test", "generated_at": "2024-01-01"},
            "executive_summary": {
                "product_name": "Test",
                "problem_statement": "Problem",
                "tagline": None,
                "key_metrics": None,
                "key_risks": None,
            },
            "customer_research": None,
            "business_case": {
                "lean_canvas": None,
                "market_sizing": None,
            },
        }

        result = docx_generator(pack_with_nones)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_handles_empty_arrays(self, docx_generator):
        """Test handling of empty arrays."""
        pack_with_empty = {
            "metadata": {"session_id": "test", "generated_at": "2024-01-01"},
            "executive_summary": {
                "product_name": "Test",
                "problem_statement": "Problem",
                "key_metrics": [],
                "key_risks": [],
            },
            "customer_research": {
                "pain_signals": [],
                "market_hypotheses": [],
            },
        }

        result = docx_generator(pack_with_empty)
        assert isinstance(result, bytes)

    def test_handles_very_long_text(self, docx_generator):
        """Test handling of very long text fields."""
        long_text = "A" * 10000  # 10KB of text
        pack_with_long = {
            "metadata": {"session_id": "test", "generated_at": "2024-01-01"},
            "executive_summary": {
                "product_name": "Test",
                "problem_statement": long_text,
                "solution_overview": long_text,
            },
        }

        result = docx_generator(pack_with_long)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_handles_special_characters_in_text(self, docx_generator):
        """Test handling of special characters."""
        special_pack = {
            "metadata": {"session_id": "test", "generated_at": "2024-01-01"},
            "executive_summary": {
                "product_name": "Test & Co. <Ltd>",
                "problem_statement": 'Problem with "quotes" and \'apostrophes\'',
                "solution_overview": "Solution with <html> & XML entities &amp;",
            },
        }

        result = docx_generator(special_pack)
        assert isinstance(result, bytes)

        text = extract_docx_text(result)
        # Should preserve the text (XML entities may be decoded)
        assert "Test" in text
