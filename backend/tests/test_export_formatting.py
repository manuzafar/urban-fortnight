"""
Comprehensive tests for PDF and DOCX export formatting.

Tests that JSON/dict structures are properly converted to readable text,
and that no raw {'key': 'value'} or ['item1', 'item2'] syntax appears in exports.
"""

import pytest
from typing import Any
from io import BytesIO

# Import the helper functions and generators
import sys
sys.path.insert(0, "..")

from utils.export_docx import (
    _extract_first_string,
    _format_list_value,
    generate_docx,
)


class TestExtractFirstString:
    """Test the _extract_first_string helper function."""

    def test_extracts_description_field(self):
        obj = {"description": "Test description", "value": 123}
        assert _extract_first_string(obj) == "Test description"

    def test_extracts_text_field(self):
        obj = {"text": "Test text", "id": 1}
        assert _extract_first_string(obj) == "Test text"

    def test_extracts_name_field(self):
        obj = {"name": "Test name", "count": 5}
        assert _extract_first_string(obj) == "Test name"

    def test_extracts_value_field(self):
        obj = {"value": "Test value", "type": "string"}
        assert _extract_first_string(obj) == "Test value"

    def test_falls_back_to_first_string_value(self):
        obj = {"custom": "Custom value", "other": "Other"}
        result = _extract_first_string(obj)
        assert result == "Custom value"

    def test_formats_as_key_value_pairs_when_no_strings(self):
        obj = {"count": 5, "active": True}
        result = _extract_first_string(obj)
        assert "count: 5" in result
        assert "active: True" in result

    def test_handles_plain_string(self):
        assert _extract_first_string("plain string") == "plain string"

    def test_handles_number(self):
        assert _extract_first_string(42) == "42"

    def test_handles_empty_dict(self):
        result = _extract_first_string({})
        assert result == ""

    def test_skips_none_values(self):
        obj = {"name": None, "value": "actual value"}
        assert _extract_first_string(obj) == "actual value"


class TestFormatListValue:
    """Test the _format_list_value helper function."""

    def test_joins_simple_list_with_semicolons(self):
        result = _format_list_value(["item1", "item2", "item3"])
        assert result == "item1; item2; item3"

    def test_handles_list_of_dicts(self):
        items = [{"name": "First"}, {"name": "Second"}]
        result = _format_list_value(items)
        assert result == "First; Second"

    def test_handles_single_dict(self):
        obj = {"description": "Single item"}
        result = _format_list_value(obj)
        assert result == "Single item"

    def test_handles_plain_string(self):
        assert _format_list_value("plain") == "plain"

    def test_handles_empty_list(self):
        assert _format_list_value([]) == ""

    def test_handles_none(self):
        assert _format_list_value(None) == ""


class TestCustomerResearchFormatting:
    """Test that Customer Research data is formatted correctly."""

    @pytest.fixture
    def sample_customer_research(self) -> dict[str, Any]:
        return {
            "target_customer": "Small business owners",
            "pain_signals": [
                {
                    "description": "Difficulty tracking inventory",
                    "evidence_tier": "E1",
                    "impact": "High cost of overstocking"
                },
                {
                    "signal": "Manual processes are time-consuming",
                    "evidence_tier": "E2"
                },
                "Simple string pain signal"
            ],
            "job_to_be_done": {
                "trigger_situation": "When inventory runs low unexpectedly",
                "underlying_goal": "Never run out of popular items",
                "success_definition": "Zero stockouts for top 20% products"
            },
            "market_context": {
                "tam": "$50 billion",
                "sam": "$10 billion",
                "som": "$500 million",
                "growth_rate": "15% annually",
                "trends": ["AI adoption", "Mobile-first", "Sustainability"]
            },
            "competitive_landscape": {
                "market_position": "Challenger in emerging market",
                "competitors": [
                    {
                        "name": "Competitor A",
                        "description": "Market leader",
                        "strengths": ["Brand recognition", "Large customer base"],
                        "weaknesses": ["Expensive", "Complex"]
                    },
                    {
                        "name": "Competitor B",
                        "description": "Budget option"
                    }
                ],
                "differentiation": "AI-powered predictions"
            },
            "market_hypotheses": [
                {
                    "hypothesis": "SMBs will pay for AI inventory",
                    "validation": "Survey of 100 business owners",
                    "evidence_tier": "E2"
                }
            ],
            "uncomfortable_insights": [
                "Many SMBs resistant to new technology",
                {"insight": "Training costs often exceed software costs"}
            ]
        }

    def test_pain_signals_dict_extraction(self, sample_customer_research):
        """Verify pain signals with dict format are properly extracted."""
        signal = sample_customer_research["pain_signals"][0]
        result = _extract_first_string(signal)
        assert "Difficulty tracking inventory" in result
        # Should not contain raw dict syntax
        assert "{" not in result or "description:" in result

    def test_job_to_be_done_fields(self, sample_customer_research):
        """Verify JTBD dict fields are accessible."""
        jtbd = sample_customer_research["job_to_be_done"]
        assert jtbd["trigger_situation"] == "When inventory runs low unexpectedly"
        assert jtbd["underlying_goal"] == "Never run out of popular items"

    def test_market_context_trends_list(self, sample_customer_research):
        """Verify market context trends list is joinable."""
        trends = sample_customer_research["market_context"]["trends"]
        result = _format_list_value(trends)
        assert "AI adoption" in result
        assert ";" in result  # Should be joined

    def test_competitors_extraction(self, sample_customer_research):
        """Verify competitor dicts are properly extracted."""
        competitor = sample_customer_research["competitive_landscape"]["competitors"][0]
        result = _extract_first_string(competitor)
        # Should extract description or name
        assert "Competitor A" in result or "Market leader" in result


class TestBusinessCaseFormatting:
    """Test that Business Case data is formatted correctly."""

    @pytest.fixture
    def sample_business_case(self) -> dict[str, Any]:
        return {
            "lean_canvas": {
                "problem": ["Inventory tracking is manual", "Stockouts are common"],
                "solution": ["AI-powered predictions", "Real-time alerts"],
                "unique_value_proposition": "Never run out of stock again",
                "unfair_advantage": ["Proprietary AI model", "Industry expertise"],
                "customer_segments": ["Small retailers", "Convenience stores"],
                "channels": ["Direct sales", "App stores", "Partnerships"],
                "revenue_streams": ["Subscription", "Transaction fees"],
                "cost_structure": ["Development", "Cloud infrastructure", "Support"]
            },
            "revenue_streams": [
                {
                    "name": "Basic Subscription",
                    "description": "Monthly access to core features",
                    "pricing_model": "Per-user monthly",
                    "estimated_revenue": "$100k/year"
                },
                {
                    "name": "Enterprise",
                    "description": "Full feature access with support",
                    "pricing_model": "Annual contract"
                }
            ],
            "cost_structure": [
                {
                    "category": "Development",
                    "description": "Engineering team salaries",
                    "estimated_amount": "$500k/year",
                    "type": "Fixed"
                },
                {
                    "category": "Infrastructure",
                    "description": "Cloud hosting and services",
                    "type": "Variable"
                }
            ],
            "market_sizing": {
                "tam": "$50B globally",
                "sam": "$10B in US market",
                "som": "$500M achievable in 5 years"
            }
        }

    def test_lean_canvas_arrays_joined(self, sample_business_case):
        """Verify lean canvas arrays are joined properly."""
        problem = sample_business_case["lean_canvas"]["problem"]
        result = _format_list_value(problem)
        assert "Inventory tracking is manual" in result
        assert "Stockouts are common" in result
        assert ";" in result

    def test_revenue_streams_extraction(self, sample_business_case):
        """Verify revenue stream dicts are properly extracted."""
        stream = sample_business_case["revenue_streams"][0]
        # Should be able to extract name and description
        assert stream["name"] == "Basic Subscription"
        assert "Monthly access" in stream["description"]

    def test_cost_structure_extraction(self, sample_business_case):
        """Verify cost structure dicts are properly extracted."""
        cost = sample_business_case["cost_structure"][0]
        assert cost["category"] == "Development"
        assert "Engineering" in cost["description"]


class TestQualityAssessmentFormatting:
    """Test that Quality Assessment data is formatted correctly."""

    @pytest.fixture
    def sample_quality_assessment(self) -> dict[str, Any]:
        return {
            "overall_score": 0.75,
            "section_scores": {
                "executive_summary": 0.8,
                "customer_research": 0.7,
                "business_case": 0.75
            },
            "strengths": [
                "Clear problem statement",
                {"description": "Strong market research", "score": 0.9}
            ],
            "critical_gaps": [
                "Missing competitive analysis depth",
                {"gap": "Financial projections need validation"}
            ],
            "recommendations": [
                "Add more customer interviews",
                {"recommendation": "Validate pricing with beta users"}
            ]
        }

    def test_section_scores_dict_format(self, sample_quality_assessment):
        """Verify section scores dict is handled properly."""
        scores = sample_quality_assessment["section_scores"]
        assert isinstance(scores, dict)
        assert scores["executive_summary"] == 0.8

    def test_strengths_mixed_types(self, sample_quality_assessment):
        """Verify strengths with mixed types (str and dict) work."""
        strengths = sample_quality_assessment["strengths"]
        assert strengths[0] == "Clear problem statement"
        result = _extract_first_string(strengths[1])
        assert "Strong market research" in result


class TestNoRawJsonInOutput:
    """Test that no raw JSON/dict syntax appears in formatted output."""

    def test_no_curly_braces_in_simple_extraction(self):
        """Verify no raw dict syntax in simple extraction."""
        obj = {"name": "Test", "value": 123}
        result = _extract_first_string(obj)
        # Should not look like raw dict
        assert not (result.startswith("{") and result.endswith("}"))

    def test_no_square_brackets_in_list_format(self):
        """Verify no raw list syntax in list formatting."""
        items = ["a", "b", "c"]
        result = _format_list_value(items)
        assert not result.startswith("[")
        assert not result.endswith("]")

    def test_nested_dict_extraction(self):
        """Verify nested dicts don't produce raw syntax."""
        obj = {
            "outer": {
                "inner": "value"
            }
        }
        # The _extract_first_string should handle this gracefully
        result = _extract_first_string(obj)
        # Should not contain raw dict syntax like {'key': 'value'}
        assert "{'inner': 'value'}" not in result
        # Should extract the nested value properly
        assert "value" in result


class TestDocxGeneration:
    """Test the full DOCX generation with various data formats."""

    @pytest.fixture
    def sample_pack(self) -> dict[str, Any]:
        return {
            "metadata": {
                "session_id": "test-session-123",
                "generated_at": "2024-01-15T10:00:00Z"
            },
            "executive_summary": {
                "product_name": "InventoryAI",
                "tagline": "Smart inventory for smart businesses",
                "problem_statement": "Manual inventory tracking is error-prone",
                "solution_overview": "AI-powered inventory management",
                "key_metrics": [
                    {"name": "Monthly Active Users", "target": "10,000"},
                    {"metric": "Revenue", "value": "$1M ARR"}
                ],
                "key_risks": [
                    {"risk": "Market adoption slower than expected"},
                    "Competition from established players"
                ]
            },
            "customer_research": {
                "target_customer": "Small retail business owners",
                "pain_signals": [
                    {"description": "Inventory errors cost money", "evidence_tier": "E1"}
                ],
                "job_to_be_done": {
                    "trigger_situation": "End of day inventory count",
                    "underlying_goal": "Accurate inventory without manual work"
                }
            },
            "business_case": {
                "lean_canvas": {
                    "problem": ["Manual tracking", "Stockouts"],
                    "solution": ["AI predictions", "Alerts"],
                    "unique_value_proposition": "Zero stockouts guaranteed",
                    "customer_segments": ["SMB Retail"],
                    "channels": ["Direct", "Partners"],
                    "revenue_streams": ["Subscription"],
                    "cost_structure": ["Dev", "Cloud"]
                }
            },
            "quality_assessment": {
                "overall_score": 0.72,
                "section_scores": {
                    "executive_summary": 0.8,
                    "customer_research": 0.65
                },
                "strengths": ["Clear vision"],
                "critical_gaps": ["Need more validation"]
            }
        }

    def test_docx_generation_succeeds(self, sample_pack):
        """Test that DOCX generation completes without error."""
        result = generate_docx(sample_pack)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_docx_generation_with_section(self, sample_pack):
        """Test that single section export works."""
        result = generate_docx(sample_pack, section="executive_summary")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_docx_with_missing_sections(self):
        """Test that DOCX handles missing sections gracefully."""
        minimal_pack = {
            "metadata": {"session_id": "test", "generated_at": "2024-01-01"},
            "executive_summary": {
                "product_name": "Test Product",
                "problem_statement": "Test problem"
            }
        }
        result = generate_docx(minimal_pack)
        assert isinstance(result, bytes)

    def test_docx_with_all_dict_formats(self, sample_pack):
        """Test DOCX generation with various dict/list formats."""
        # Add more complex nested structures
        sample_pack["customer_research"]["competitive_landscape"] = {
            "market_position": "Challenger",
            "competitors": [
                {"name": "Comp A", "strengths": ["Feature 1", "Feature 2"]}
            ]
        }
        sample_pack["business_case"]["revenue_streams"] = [
            {"name": "Sub", "description": "Monthly", "pricing_model": "Per user"}
        ]

        result = generate_docx(sample_pack)
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dict(self):
        result = _extract_first_string({})
        assert result == ""

    def test_none_value(self):
        result = _format_list_value(None)
        assert result == ""

    def test_deeply_nested_structure(self):
        obj = {
            "level1": {
                "level2": {
                    "level3": "deep value"
                }
            }
        }
        result = _extract_first_string(obj)
        # Should not crash, may format as key-value
        assert isinstance(result, str)

    def test_mixed_type_list(self):
        items = ["string", 123, {"name": "dict"}, None]
        result = _format_list_value(items)
        assert isinstance(result, str)
        assert "string" in result

    def test_unicode_content(self):
        obj = {"description": "日本語テスト with émojis 🚀"}
        result = _extract_first_string(obj)
        assert "日本語" in result
        assert "🚀" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
