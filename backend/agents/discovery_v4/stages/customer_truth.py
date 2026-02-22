"""
Stage 2: Customer Truth

Based on Teresa Torres's Continuous Discovery methodology.
This stage captures and synthesizes customer interview insights.

Includes reflection loop: Generate -> Critique -> Refine (max 2 iterations)
"""

import json
from datetime import date, datetime
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.discovery_v4.prompts import (
    CUSTOMER_TRUTH_HYPOTHETICAL_PROMPT,
    CUSTOMER_TRUTH_REFINE_PROMPT,
    INTERVIEW_GUIDE_PROMPT,
    INTERVIEW_SYNTHESIS_PROMPT,
)
from agents.discovery_v4.stages.mini_critique import critique_stage_output
from models.discovery_v4_schemas import (
    Contradiction,
    CustomerTruthOutput,
    DiscoverySessionV4,
    Evidence,
    EvidenceQuality,
    Interview,
    OutcomePattern,
    PainPattern,
    PatternSynthesis,
    Severity,
    TriggerPattern,
)

logger = structlog.get_logger(__name__)

# Reflection loop configuration
MAX_REFLECTION_ITERATIONS = 2
MIN_QUALITY_THRESHOLD = 7.0


class CustomerTruthStage:
    """
    Stage 2: Customer Truth

    Based on Teresa Torres's Continuous Discovery methodology:
    - "Tell me about the last time..."
    - Look for patterns across interviews
    - Find contradictions and gaps
    - Build evidence-based understanding
    """

    async def run(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> CustomerTruthOutput:
        """Run customer truth stage based on mode."""
        logger.info(
            "customer_truth_stage_run",
            session_id=session.session_id,
            mode=context.get("mode"),
            interview_count=len(session.interviews),
        )

        mode = context.get("mode", "guided")

        if mode == "deep":
            # Deep mode: Require real interviews
            if len(session.interviews) > 0:
                return await self._synthesize_available(session, context)
            else:
                # Return empty state with guidance for Deep mode
                return CustomerTruthOutput(
                    interviews=[],
                    patterns=None,
                    interview_goal=5,
                    interviews_completed=0,
                    readiness_score=1,
                )
        elif len(session.interviews) > 0:
            # Quick/Guided mode with interviews: Synthesize real data
            return await self._synthesize_available(session, context)
        else:
            # Quick/Guided mode without interviews: Generate hypothetical insights
            return await self._generate_hypothetical(context)

    async def _generate_hypothetical(
        self, context: dict[str, Any]
    ) -> CustomerTruthOutput:
        """Generate hypothetical customer insights for Quick mode with reflection loop."""
        return await self._generate_with_reflection(context)

    async def _generate_with_reflection(
        self, context: dict[str, Any]
    ) -> CustomerTruthOutput:
        """Generate with reflection loop: Generate -> Critique -> Refine."""
        iteration = 0
        critique_feedback = None
        output = None

        while iteration < MAX_REFLECTION_ITERATIONS:
            logger.info(
                "customer_truth_reflection_iteration",
                iteration=iteration + 1,
                max_iterations=MAX_REFLECTION_ITERATIONS,
                has_feedback=critique_feedback is not None,
            )

            # Generate (or refine based on feedback)
            if critique_feedback:
                output = await self._generate_with_feedback(context, critique_feedback)
            else:
                output = await self._generate_initial(context)

            # Critique the output
            critique = await critique_stage_output(
                "customer_truth",
                output.model_dump(),
                evidence_tier="E4",  # Quick mode is E4
            )

            logger.info(
                "customer_truth_critique_result",
                iteration=iteration + 1,
                overall_score=critique.get("overall_score"),
                passes_threshold=critique.get("passes_threshold"),
            )

            # Check quality gate
            if critique.get("overall_score", 0) >= MIN_QUALITY_THRESHOLD:
                output.readiness_score = int(critique.get("overall_score", 7))
                logger.info(
                    "customer_truth_quality_threshold_met",
                    score=output.readiness_score,
                    iteration=iteration + 1,
                )
                break

            # Prepare feedback for next iteration
            critique_feedback = {
                "feedback": critique.get("feedback", []),
                "suggested_improvements": critique.get("suggested_improvements", {}),
                "previous_output": output.model_dump(),
                "dimension_scores": critique.get("dimension_scores", {}),
            }
            iteration += 1

        # If max iterations reached, allow progression with lower threshold
        if iteration >= MAX_REFLECTION_ITERATIONS:
            output.readiness_score = max(5, int(critique.get("overall_score", 5)))
            logger.info(
                "customer_truth_max_iterations_reached",
                final_score=critique.get("overall_score"),
            )

        return output

    async def _generate_initial(
        self, context: dict[str, Any]
    ) -> CustomerTruthOutput:
        """Generate initial hypothetical customer insights."""
        prompt = CUSTOMER_TRUTH_HYPOTHETICAL_PROMPT.format(
            product_idea=context.get("product_idea", ""),
            industry=context.get("industry", "Not specified"),
            target_market=context.get("target_market", "Not specified"),
            problem_statement=context.get("problem_statement", context.get("product_idea", "")),
        )

        result = await call_llm(prompt, "customer_truth_hypothetical")

        if result.get("success"):
            data = result["data"]
            return self._parse_output(data)
        else:
            logger.error(
                "customer_truth_hypothetical_failed",
                error=result.get("error"),
            )
            return CustomerTruthOutput(
                interviews=[],
                patterns=None,
                interview_goal=5,
                interviews_completed=0,
                readiness_score=2,
            )

    async def _generate_with_feedback(
        self, context: dict[str, Any], feedback: dict[str, Any]
    ) -> CustomerTruthOutput:
        """Generate refined output incorporating critique feedback."""
        prompt = CUSTOMER_TRUTH_REFINE_PROMPT.format(
            original_output=json.dumps(feedback["previous_output"], indent=2, default=str),
            feedback="\n".join(f"- {f}" for f in feedback.get("feedback", [])),
        )

        logger.info("customer_truth_refine_generation_start")

        result = await call_llm(prompt, "customer_truth_refine")

        if result.get("success"):
            data = result["data"]
            output = self._parse_output(data)
            logger.info(
                "customer_truth_refine_generation_complete",
                readiness_score=output.readiness_score,
            )
            return output
        else:
            logger.warning(
                "customer_truth_refine_failed",
                error=result.get("error"),
            )
            # Return the previous output if refinement fails
            return self._parse_output(feedback["previous_output"])

    async def _synthesize_available(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> CustomerTruthOutput:
        """Synthesize patterns from available interviews."""
        patterns = await self.synthesize_patterns(session.interviews)

        # Determine readiness based on interview count and pattern quality
        interview_count = len(session.interviews)
        readiness_score = min(10, interview_count * 2)

        return CustomerTruthOutput(
            interviews=session.interviews,
            patterns=patterns,
            interview_goal=5,
            interviews_completed=interview_count,
            readiness_score=readiness_score,
        )

    async def synthesize_patterns(
        self, interviews: list[Interview]
    ) -> PatternSynthesis:
        """Synthesize patterns from real interviews."""
        if not interviews:
            return PatternSynthesis(
                pain_patterns=[],
                trigger_patterns=[],
                outcome_patterns=[],
                contradictions=[],
                interview_gaps=["No interviews to synthesize"],
                total_interviews=0,
                evidence_quality=EvidenceQuality.E4,
            )

        # Serialize interviews for prompt
        interviews_json = json.dumps(
            [self._interview_to_dict(i) for i in interviews],
            default=str,
        )

        prompt = INTERVIEW_SYNTHESIS_PROMPT.format(
            interviews_json=interviews_json
        )

        result = await call_llm(prompt, "interview_synthesis")

        if result.get("success"):
            data = result["data"]
            return self._parse_patterns(data, len(interviews))
        else:
            logger.error(
                "interview_synthesis_failed",
                error=result.get("error"),
            )
            # Return basic patterns
            return self._basic_patterns_from_interviews(interviews)

    async def generate_interview_guide(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate Teresa Torres-style interview guide."""
        prompt = INTERVIEW_GUIDE_PROMPT.format(
            problem_statement=context.get("problem_statement", ""),
            target_user=context.get("target_market", "target users"),
            previous_findings=json.dumps(context.get("previous_findings", {}), default=str),
        )

        result = await call_llm(prompt, "interview_guide")

        if result.get("success"):
            return result["data"]
        else:
            # Return default interview guide
            return {
                "interview_goal": "Understand the user's experience with this problem",
                "opening_script": "Thank you for taking the time to speak with me today. I'm researching how people experience [problem area]. There are no right or wrong answers - I'm just trying to understand your experience.",
                "story_prompt": "Tell me about the last time you experienced [the problem]...",
                "follow_up_questions": [
                    "What happened next?",
                    "How did that make you feel?",
                    "What did you do about it?",
                    "How often does this happen?",
                ],
                "deep_dive_areas": [
                    {
                        "area": "Pain points",
                        "questions": [
                            "What was most frustrating about that experience?",
                            "What would you change if you could?",
                        ],
                    },
                    {
                        "area": "Current solutions",
                        "questions": [
                            "What do you do today to handle this?",
                            "Have you tried any tools or solutions?",
                        ],
                    },
                    {
                        "area": "Desired outcomes",
                        "questions": [
                            "What would success look like for you?",
                            "If this problem was solved, what would change?",
                        ],
                    },
                ],
                "things_to_listen_for": [
                    "Emotional language (frustrated, overwhelmed, anxious)",
                    "Workarounds they've built",
                    "Frequency signals (daily, weekly)",
                    "Quotes that capture the pain",
                ],
                "closing_script": "Thank you so much for sharing your experience. This is really helpful.",
                "referral_ask": "Do you know anyone else who might have similar experiences that I could talk to?",
            }

    def _parse_output(self, data: dict[str, Any]) -> CustomerTruthOutput:
        """Parse LLM output into CustomerTruthOutput model."""
        # Parse interviews
        interviews = []
        for i in data.get("interviews", []):
            try:
                interview_date = i.get("interview_date", date.today().isoformat())
                if isinstance(interview_date, str):
                    interview_date = date.fromisoformat(interview_date)

                interviews.append(
                    Interview(
                        id=i.get("id"),
                        interviewee_name=i.get("interviewee_name", "Hypothetical"),
                        interviewee_role=i.get("interviewee_role", ""),
                        company_type=i.get("company_type", ""),
                        company_size=i.get("company_size", ""),
                        interview_date=interview_date,
                        story_raw=i.get("story_raw", ""),
                        key_quote=i.get("key_quote", ""),
                        struggling_moment=i.get("struggling_moment", ""),
                        emotions=i.get("emotions", []),
                        current_workaround=i.get("current_workaround", ""),
                        desired_outcome=i.get("desired_outcome", ""),
                        ai_pain_points=i.get("ai_pain_points", []),
                        ai_triggers=i.get("ai_triggers", []),
                        ai_goals=i.get("ai_goals", []),
                    )
                )
            except Exception as e:
                logger.warning("interview_parse_error", error=str(e))

        # Parse patterns
        patterns = None
        if data.get("patterns"):
            patterns = self._parse_patterns(data["patterns"], len(interviews))

        return CustomerTruthOutput(
            interviews=interviews,
            patterns=patterns,
            interview_goal=data.get("interview_goal", 5),
            interviews_completed=data.get("interviews_completed", len(interviews)),
            readiness_score=data.get("readiness_score", 4),
        )

    def _parse_patterns(
        self, data: dict[str, Any], interview_count: int
    ) -> PatternSynthesis:
        """Parse pattern synthesis data."""
        # Parse pain patterns
        pain_patterns = []
        for p in data.get("pain_patterns", []):
            evidence = [
                Evidence(
                    interview_id=e.get("interview_id", ""),
                    quote=e.get("quote", ""),
                )
                for e in p.get("evidence", [])
            ]
            pain_patterns.append(
                PainPattern(
                    description=p.get("description", ""),
                    frequency=p.get("frequency", 1),
                    evidence=evidence,
                    severity=Severity(p.get("severity", "medium")),
                )
            )

        # Parse trigger patterns
        trigger_patterns = []
        for t in data.get("trigger_patterns", []):
            evidence = [
                Evidence(
                    interview_id=e.get("interview_id", ""),
                    quote=e.get("quote", ""),
                )
                for e in t.get("evidence", [])
            ]
            trigger_patterns.append(
                TriggerPattern(
                    description=t.get("description", ""),
                    frequency=t.get("frequency", 1),
                    evidence=evidence,
                )
            )

        # Parse outcome patterns
        outcome_patterns = []
        for o in data.get("outcome_patterns", []):
            evidence = [
                Evidence(
                    interview_id=e.get("interview_id", ""),
                    quote=e.get("quote", ""),
                )
                for e in o.get("evidence", [])
            ]
            outcome_patterns.append(
                OutcomePattern(
                    description=o.get("description", ""),
                    frequency=o.get("frequency", 1),
                    evidence=evidence,
                )
            )

        # Parse contradictions
        contradictions = []
        for c in data.get("contradictions", []):
            contradictions.append(
                Contradiction(
                    description=c.get("description", ""),
                    interview_a=c.get("interview_a", ""),
                    interview_b=c.get("interview_b", ""),
                    resolution_suggestion=c.get("resolution_suggestion"),
                )
            )

        # Determine evidence quality
        evidence_quality = EvidenceQuality.E4
        if interview_count >= 5:
            evidence_quality = EvidenceQuality.E1
        elif interview_count >= 3:
            evidence_quality = EvidenceQuality.E2
        elif interview_count >= 1:
            evidence_quality = EvidenceQuality.E3

        return PatternSynthesis(
            pain_patterns=pain_patterns,
            trigger_patterns=trigger_patterns,
            outcome_patterns=outcome_patterns,
            contradictions=contradictions,
            interview_gaps=data.get("interview_gaps", []),
            total_interviews=interview_count,
            evidence_quality=evidence_quality,
        )

    def _basic_patterns_from_interviews(
        self, interviews: list[Interview]
    ) -> PatternSynthesis:
        """Create basic patterns from interview data without LLM."""
        pain_patterns = []
        seen_pains = {}

        for interview in interviews:
            # Extract pains from AI-extracted or manual
            pains = interview.ai_pain_points or [interview.struggling_moment]
            for pain in pains:
                if pain:
                    if pain not in seen_pains:
                        seen_pains[pain] = {
                            "description": pain,
                            "frequency": 0,
                            "evidence": [],
                        }
                    seen_pains[pain]["frequency"] += 1
                    seen_pains[pain]["evidence"].append(
                        Evidence(
                            interview_id=interview.id or "",
                            quote=interview.key_quote,
                        )
                    )

        for pain_data in seen_pains.values():
            pain_patterns.append(
                PainPattern(
                    description=pain_data["description"],
                    frequency=pain_data["frequency"],
                    evidence=pain_data["evidence"],
                    severity=Severity.MEDIUM,
                )
            )

        return PatternSynthesis(
            pain_patterns=pain_patterns,
            trigger_patterns=[],
            outcome_patterns=[],
            contradictions=[],
            interview_gaps=["Need more interviews for comprehensive synthesis"],
            total_interviews=len(interviews),
            evidence_quality=(
                EvidenceQuality.E1
                if len(interviews) >= 5
                else EvidenceQuality.E2
                if len(interviews) >= 3
                else EvidenceQuality.E3
            ),
        )

    def _interview_to_dict(self, interview: Interview) -> dict[str, Any]:
        """Convert Interview to dict for serialization."""
        return {
            "id": interview.id,
            "interviewee_name": interview.interviewee_name,
            "interviewee_role": interview.interviewee_role,
            "company_type": interview.company_type,
            "company_size": interview.company_size,
            "interview_date": str(interview.interview_date),
            "story_raw": interview.story_raw,
            "key_quote": interview.key_quote,
            "struggling_moment": interview.struggling_moment,
            "emotions": interview.emotions,
            "current_workaround": interview.current_workaround,
            "desired_outcome": interview.desired_outcome,
            "ai_pain_points": interview.ai_pain_points,
            "ai_triggers": interview.ai_triggers,
            "ai_goals": interview.ai_goals,
        }

    async def get_suggestions(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Get suggestions for interview research."""
        interview_count = context.get("interview_count", 0)

        if interview_count == 0:
            return {
                "suggestions": [
                    "Start with 5 target interviews to validate patterns",
                    "Use the interview guide to structure conversations",
                    "Focus on 'the last time' stories, not hypotheticals",
                ]
            }
        elif interview_count < 3:
            return {
                "suggestions": [
                    f"Add {3 - interview_count} more interviews to find patterns",
                    "Look for common themes in existing interviews",
                    "Identify gaps in understanding",
                ]
            }
        else:
            return {
                "suggestions": [
                    "Run pattern synthesis to identify themes",
                    "Look for contradictions that need resolution",
                    "Identify segments with different needs",
                ]
            }
