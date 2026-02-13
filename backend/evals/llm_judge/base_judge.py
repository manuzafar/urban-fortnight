"""
Base LLM Judge — Foundation for LLM-based evaluations.

Provides common functionality for LLM-as-judge evaluations including
retry logic, structured output parsing, and scoring normalization.
"""

import json
from abc import abstractmethod
from typing import Any

import structlog

from agents.base_agent import call_llm
from evals.base import BaseEval, EvalResult, EvalSeverity, EvalType

logger = structlog.get_logger(__name__)


class BaseLLMJudge(BaseEval):
    """
    Base class for LLM-as-judge evaluations.

    Subclasses should implement:
    - build_prompt(): Generate the evaluation prompt
    - parse_response(): Extract scores and feedback from LLM response
    """

    eval_type = EvalType.LLM_JUDGE
    severity = EvalSeverity.WARNING

    # Model to use for judging
    judge_model: str = "gemini-2.0-flash"

    # Score threshold for passing
    pass_threshold: float = 0.7

    @abstractmethod
    def build_prompt(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None,
    ) -> str:
        """Build the evaluation prompt for the LLM judge."""
        pass

    @abstractmethod
    def parse_response(
        self,
        response_data: dict[str, Any],
    ) -> tuple[float, str, dict[str, Any]]:
        """
        Parse the LLM response into score, message, and details.

        Returns:
            Tuple of (score, message, details)
        """
        pass

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Run the LLM-based evaluation.

        Args:
            agent_output: The agent's output to evaluate
            agent_name: Name of the agent
            context: Optional additional context

        Returns:
            EvalResult with LLM assessment
        """
        # Build the prompt
        prompt = self.build_prompt(agent_output, agent_name, context)

        # Call LLM
        try:
            result = await call_llm(
                prompt=prompt,
                agent_name=f"{self.name}_judge",
                model_override=self.judge_model,
            )

            if not result.get("success"):
                logger.warning(
                    "llm_judge_call_failed",
                    eval_name=self.name,
                    agent_name=agent_name,
                    error=result.get("error"),
                )
                return EvalResult(
                    eval_name=self.name,
                    eval_type=self.eval_type,
                    passed=True,  # Don't fail on LLM errors
                    score=None,
                    severity=EvalSeverity.INFO,
                    message=f"LLM judge unavailable: {result.get('error', 'unknown error')}",
                    agent_name=agent_name,
                )

            # Parse response
            response_data = result.get("data", {})
            score, message, details = self.parse_response(response_data)

            # Determine pass/fail
            passed = score >= self.pass_threshold

            logger.info(
                "llm_judge_complete",
                eval_name=self.name,
                agent_name=agent_name,
                score=score,
                passed=passed,
            )

            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=passed,
                score=round(score, 3),
                severity=self.severity if not passed else EvalSeverity.INFO,
                message=message,
                agent_name=agent_name,
                details=details,
            )

        except Exception as e:
            logger.error(
                "llm_judge_exception",
                eval_name=self.name,
                agent_name=agent_name,
                error=str(e),
            )
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,  # Don't fail on exceptions
                score=None,
                severity=EvalSeverity.INFO,
                message=f"LLM judge error: {str(e)}",
                agent_name=agent_name,
            )
