"""
Multi-Dimension Judge — Evaluates outputs across 6 quality dimensions.

Dimensions scored (0.0-1.0 each):
1. Accuracy - Facts and claims well-sourced
2. Relevance - Content relevant to product idea
3. Actionability - Product team can act on info
4. Evidence Quality - Appropriate evidence tiers
5. Completeness - All expected aspects covered
6. Coherence - Internally consistent and logical
"""

import json
from typing import Any

from evals.base import EvalRegistry
from evals.llm_judge.base_judge import BaseLLMJudge


MULTI_DIMENSION_PROMPT = """You are an expert evaluator assessing the quality of a product discovery document.

Evaluate the following {agent_name} output across 6 dimensions. For each dimension, provide:
- A score from 0.0 to 1.0 (1.0 = excellent)
- A brief explanation (1-2 sentences)

## PRODUCT IDEA CONTEXT
{product_idea}

## OUTPUT TO EVALUATE
{output_json}

## EVALUATION DIMENSIONS

1. **ACCURACY** (0.0-1.0)
   - Are facts and claims well-sourced or clearly marked as assumptions?
   - Are numbers and statistics plausible?
   - Are there obvious errors or hallucinations?

2. **RELEVANCE** (0.0-1.0)
   - Is the content directly relevant to this specific product idea?
   - Does it address the target market and use case?
   - Is it tailored rather than generic?

3. **ACTIONABILITY** (0.0-1.0)
   - Can a product team act on this information?
   - Are recommendations specific and implementable?
   - Are next steps clear?

4. **EVIDENCE_QUALITY** (0.0-1.0)
   - Are claims properly tiered (E1-E5) where applicable?
   - Is there appropriate skepticism about unverified claims?
   - Are sources cited where available?

5. **COMPLETENESS** (0.0-1.0)
   - Are all expected aspects of this section covered?
   - Are there obvious gaps in the analysis?
   - Is the depth appropriate?

6. **COHERENCE** (0.0-1.0)
   - Is the content internally consistent?
   - Does it logically flow?
   - Are there contradictions?

## OUTPUT FORMAT
Respond with valid JSON only:
{{
  "accuracy": {{
    "score": 0.0,
    "explanation": "..."
  }},
  "relevance": {{
    "score": 0.0,
    "explanation": "..."
  }},
  "actionability": {{
    "score": 0.0,
    "explanation": "..."
  }},
  "evidence_quality": {{
    "score": 0.0,
    "explanation": "..."
  }},
  "completeness": {{
    "score": 0.0,
    "explanation": "..."
  }},
  "coherence": {{
    "score": 0.0,
    "explanation": "..."
  }},
  "overall_assessment": "Brief 2-3 sentence overall assessment",
  "key_strengths": ["strength 1", "strength 2"],
  "key_weaknesses": ["weakness 1", "weakness 2"],
  "improvement_suggestions": ["suggestion 1", "suggestion 2"]
}}

Be critical but fair. This is for quality improvement, not punishment.
"""


class MultiDimensionJudge(BaseLLMJudge):
    """
    Evaluates agent outputs across 6 quality dimensions using LLM.

    This provides a comprehensive quality assessment that considers
    accuracy, relevance, actionability, evidence, completeness, and coherence.
    """

    name = "multi_dimension_quality"
    description = "LLM-based 6-dimension quality assessment"
    pass_threshold = 0.7

    # Dimension weights for overall score
    DIMENSION_WEIGHTS = {
        "accuracy": 0.20,
        "relevance": 0.20,
        "actionability": 0.15,
        "evidence_quality": 0.15,
        "completeness": 0.15,
        "coherence": 0.15,
    }

    def build_prompt(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None,
    ) -> str:
        """Build the multi-dimension evaluation prompt."""
        # Get product idea from context if available
        product_idea = "Not provided"
        if context and "full_state" in context:
            product_idea = context["full_state"].get("product_idea", product_idea)

        # Truncate output if too long
        output_str = json.dumps(agent_output, indent=2, default=str)
        if len(output_str) > 8000:
            output_str = output_str[:8000] + "\n... (truncated)"

        return MULTI_DIMENSION_PROMPT.format(
            agent_name=agent_name,
            product_idea=product_idea,
            output_json=output_str,
        )

    def parse_response(
        self,
        response_data: dict[str, Any],
    ) -> tuple[float, str, dict[str, Any]]:
        """Parse the multi-dimension response."""
        # Extract dimension scores
        dimension_scores = {}
        explanations = {}

        for dim in self.DIMENSION_WEIGHTS.keys():
            dim_data = response_data.get(dim, {})
            if isinstance(dim_data, dict):
                score = dim_data.get("score", 0.5)
                explanation = dim_data.get("explanation", "")
            else:
                score = 0.5
                explanation = ""

            # Normalize score to 0-1
            score = max(0.0, min(1.0, float(score)))
            dimension_scores[dim] = score
            explanations[dim] = explanation

        # Calculate weighted overall score
        overall_score = sum(
            dimension_scores.get(dim, 0.5) * weight
            for dim, weight in self.DIMENSION_WEIGHTS.items()
        )

        # Build message
        assessment = response_data.get("overall_assessment", "")
        if overall_score >= 0.8:
            quality_label = "High quality"
        elif overall_score >= 0.6:
            quality_label = "Acceptable quality"
        else:
            quality_label = "Needs improvement"

        message = f"{quality_label} ({overall_score:.1%}): {assessment[:100]}"

        # Build details
        details = {
            "dimension_scores": dimension_scores,
            "explanations": explanations,
            "overall_assessment": assessment,
            "key_strengths": response_data.get("key_strengths", []),
            "key_weaknesses": response_data.get("key_weaknesses", []),
            "improvement_suggestions": response_data.get("improvement_suggestions", []),
        }

        return overall_score, message, details


# Register the eval
EvalRegistry.register(MultiDimensionJudge())
