"""
Discovery V4 Engine.

Orchestrates stage-by-stage discovery execution.
Supports three modes with different execution patterns.
"""

from datetime import datetime
from typing import Any

import structlog

from models.discovery_v4_schemas import (
    DiscoveryMode,
    DiscoverySessionV4,
    EvidenceQuality,
    FourForcesModel,
    OpportunitySolutionTree,
    PatternSynthesis,
    StageStatus,
    TarpitAnalysis,
)
from utils.db import SupabaseSessionStore

logger = structlog.get_logger(__name__)

# Session store
session_store = SupabaseSessionStore()


class DiscoveryEngineV4:
    """
    Orchestrates stage-by-stage discovery execution.
    Supports three modes with different execution patterns.
    """

    MODE_CONFIG = {
        "quick": {
            "auto_run_stages": [
                "problem_love",
                "customer_truth",
                "opportunity_mapping",
                "solution_design",
                "validation_plan",
            ],
            "checkpoints_enabled": False,
            "interviews_required": 0,
            "quality_threshold": 0.65,
            "evidence_target": "E4",
        },
        "guided": {
            "auto_run_stages": ["problem_love"],  # Others wait for checkpoint
            "checkpoints_enabled": True,
            "interviews_required": 0,  # Optional
            "quality_threshold": 0.75,
            "evidence_target": "E3",
        },
        "deep": {
            "auto_run_stages": [],  # All manual
            "checkpoints_enabled": True,
            "interviews_required": 5,
            "quality_threshold": 0.85,
            "evidence_target": "E1",
        },
    }

    def __init__(self):
        """Initialize the discovery engine."""
        # Import stages lazily to avoid circular imports
        self._stage_runners = None

    @property
    def stage_runners(self):
        """Lazy load stage runners."""
        if self._stage_runners is None:
            from agents.discovery_v4.stages import (
                ProblemLoveStage,
                CustomerTruthStage,
                OpportunityMappingStage,
                SolutionDesignStage,
                ValidationPlanStage,
            )

            self._stage_runners = {
                "problem_love": ProblemLoveStage(),
                "customer_truth": CustomerTruthStage(),
                "opportunity_mapping": OpportunityMappingStage(),
                "solution_design": SolutionDesignStage(),
                "validation_plan": ValidationPlanStage(),
            }
        return self._stage_runners

    async def run_session(
        self, session: DiscoverySessionV4
    ) -> DiscoverySessionV4:
        """
        Run discovery based on mode.

        For Quick mode: runs all stages automatically.
        For Guided mode: runs first stage, waits for approval.
        For Deep mode: waits for interviews before running.
        """
        # Handle both enum and string mode values
        mode_value = session.mode.value if hasattr(session.mode, 'value') else str(session.mode)
        config = self.MODE_CONFIG[mode_value]

        logger.info(
            "discovery_engine_run_session",
            session_id=session.session_id,
            mode=mode_value,
            auto_stages=config["auto_run_stages"],
        )

        for stage in config["auto_run_stages"]:
            session = await self.run_stage(session, stage)

            if config["checkpoints_enabled"]:
                # Save checkpoint, wait for user approval
                await self._save_checkpoint(session, stage)
                break  # Stop and wait for approval

        # Update overall progress
        session = self._update_session_progress(session)

        return session

    async def run_stage(
        self,
        session: DiscoverySessionV4,
        stage: str,
    ) -> DiscoverySessionV4:
        """Run a single stage."""
        logger.info(
            "discovery_engine_run_stage",
            session_id=session.session_id,
            stage=stage,
        )

        runner = self.stage_runners.get(stage)
        if not runner:
            raise ValueError(f"Unknown stage: {stage}")

        # Mark stage as in progress
        session.stages[stage].status = StageStatus.IN_PROGRESS
        session.stages[stage].started_at = datetime.utcnow().isoformat()

        # Build context from previous stages
        context = self._build_stage_context(session, stage)

        try:
            # Run stage
            output = await runner.run(session, context)

            # Update session with output
            session.stages[stage].output = output.model_dump() if hasattr(output, "model_dump") else output
            session.stages[stage].status = StageStatus.COMPLETED
            session.stages[stage].completed_at = datetime.utcnow().isoformat()

            # Extract score if available
            if hasattr(output, "overall_score"):
                session.stages[stage].score = output.overall_score
            elif hasattr(output, "readiness_score"):
                session.stages[stage].score = output.readiness_score

            # Check quality gate (Step 4)
            quality_passed, blocked_reason, quality_feedback = self._check_quality_gate(
                session, stage
            )
            session.stages[stage].quality_passed = quality_passed
            session.stages[stage].blocked_reason = blocked_reason
            session.stages[stage].quality_feedback = quality_feedback
            session.stages[stage].quality_score = float(session.stages[stage].score or 0)

            # Calculate evidence tier (Step 3)
            session.stages[stage].evidence_tier = self._calculate_evidence_tier(
                session, stage
            )

            # Update cross-stage data
            session = self._update_cross_stage_data(session, stage, output)

            # Persist to database (optional - may fail if tables don't exist)
            try:
                session_store.save_draft_state(
                    session_id=session.session_id,
                    stage_name=stage,
                    stage_output=session.stages[stage].output,
                    stage_status="completed",
                    score=session.stages[stage].score,
                )
            except Exception as db_error:
                logger.warning(
                    "discovery_engine_db_save_failed",
                    session_id=session.session_id,
                    stage=stage,
                    error=str(db_error),
                )
                # Continue without database persistence (for testing)

            logger.info(
                "discovery_engine_stage_complete",
                session_id=session.session_id,
                stage=stage,
                score=session.stages[stage].score,
                quality_passed=quality_passed,
                evidence_tier=session.stages[stage].evidence_tier,
            )

        except Exception as e:
            logger.error(
                "discovery_engine_stage_error",
                session_id=session.session_id,
                stage=stage,
                error=str(e),
                exc_info=True,
            )

            session.stages[stage].status = StageStatus.NOT_STARTED
            session.stages[stage].error_message = str(e)
            session.stages[stage].last_error_at = datetime.utcnow().isoformat()
            session.stages[stage].coaching_messages.append(f"Error: {str(e)}")

            raise

        session.updated_at = datetime.utcnow().isoformat()
        return session

    def _build_stage_context(
        self, session: DiscoverySessionV4, stage: str
    ) -> dict[str, Any]:
        """Build context from previous stages for current stage."""
        # Handle both enum and string mode values
        mode_value = session.mode.value if hasattr(session.mode, 'value') else str(session.mode)
        context = {
            "product_idea": session.product_idea,
            "industry": session.industry,
            "target_market": session.target_market,
            "mode": mode_value,
        }

        # Add outputs from completed stages
        if session.stages["problem_love"].output:
            problem_output = session.stages["problem_love"].output
            context["problem_statement"] = (
                problem_output.get("problem_statement_refined")
                or problem_output.get("problem_statement")
            )
            context["problem_love_output"] = problem_output

        if session.interviews:
            context["interviews"] = [i.model_dump() for i in session.interviews]
            context["interview_count"] = len(session.interviews)

        if session.patterns:
            context["patterns"] = session.patterns.model_dump()

        if session.four_forces:
            context["four_forces"] = session.four_forces.model_dump()

        if session.opportunity_tree:
            context["opportunity_tree"] = session.opportunity_tree.model_dump()
            context["primary_opportunity"] = (
                session.opportunity_tree.opportunities[0].description
                if session.opportunity_tree.opportunities
                else None
            )

        if session.stages["solution_design"].output:
            context["solution_design_output"] = session.stages["solution_design"].output
            context["solution"] = session.stages["solution_design"].output.get(
                "solution_concept"
            )
            context["dhm_score"] = session.stages["solution_design"].output.get(
                "dhm_score"
            )

        return context

    def _update_cross_stage_data(
        self,
        session: DiscoverySessionV4,
        stage: str,
        output: Any,
    ) -> DiscoverySessionV4:
        """Update cross-stage data based on stage output."""
        if stage == "customer_truth":
            if hasattr(output, "patterns") and output.patterns:
                session.patterns = output.patterns
            if hasattr(output, "interviews") and output.interviews:
                session.interviews = output.interviews

        elif stage == "opportunity_mapping":
            if hasattr(output, "four_forces"):
                session.four_forces = output.four_forces
            if hasattr(output, "opportunity_tree"):
                session.opportunity_tree = output.opportunity_tree

        return session

    def _update_session_progress(
        self, session: DiscoverySessionV4
    ) -> DiscoverySessionV4:
        """Update overall session progress and quality."""
        # Calculate progress
        stages_complete = sum(
            1
            for s in session.stages.values()
            if s.status in (StageStatus.COMPLETED, StageStatus.APPROVED, StageStatus.SKIPPED)
        )
        total_stages = len(session.stages)

        # Calculate quality score
        scores = [
            s.score for s in session.stages.values() if s.score is not None
        ]
        if scores:
            session.quality_score = int(sum(scores) / len(scores) * 10)

        # Update evidence quality based on interviews
        interview_count = len(session.interviews)
        if interview_count >= 5:
            session.overall_evidence_quality = EvidenceQuality.E1
        elif interview_count >= 3:
            session.overall_evidence_quality = EvidenceQuality.E2
        elif interview_count >= 1:
            session.overall_evidence_quality = EvidenceQuality.E3
        else:
            session.overall_evidence_quality = EvidenceQuality.E4

        # Update database
        session_store.update_status(
            session.session_id,
            {
                "progress_percentage": int((stages_complete / total_stages) * 100),
                "status": (
                    "completed"
                    if stages_complete == total_stages
                    else "in_progress"
                ),
            },
        )

        return session

    async def _save_checkpoint(
        self, session: DiscoverySessionV4, stage: str
    ) -> None:
        """Save checkpoint for guided/deep mode."""
        logger.info(
            "discovery_engine_checkpoint_saved",
            session_id=session.session_id,
            stage=stage,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # QUALITY GATE & EVIDENCE TIER METHODS (Step 3 & 4)
    # ═══════════════════════════════════════════════════════════════════════════

    # Quality requirements by stage
    STAGE_QUALITY_REQUIREMENTS = {
        "problem_love": {
            "min_score": 6.0,
            "required_fields": ["problem_statement", "frequency", "overall_score"],
            "blocking_message": "Problem statement needs more specificity before proceeding.",
        },
        "customer_truth": {
            "min_score": 5.0,
            "required_fields": ["readiness_score"],
            "blocking_message": "Need more customer insights to proceed.",
        },
        "opportunity_mapping": {
            "min_score": 5.0,
            "required_fields": ["primary_opportunity"],
            "blocking_message": "Opportunity mapping needs refinement.",
        },
        "solution_design": {
            "min_score": 5.0,
            "required_fields": ["solution_concept"],
            "blocking_message": "Solution design needs more detail.",
        },
        "validation_plan": {
            "min_score": 5.0,
            "required_fields": ["experiments"],
            "blocking_message": "Validation plan needs more experiments.",
        },
    }

    def _check_quality_gate(
        self, session: DiscoverySessionV4, stage: str
    ) -> tuple[bool, str | None, list[str]]:
        """
        Check if stage passes quality gate.

        Returns:
            tuple of (passed, blocked_reason, feedback_list)
        """
        requirements = self.STAGE_QUALITY_REQUIREMENTS.get(stage, {})
        stage_state = session.stages[stage]
        output = stage_state.output

        feedback = []

        if not output:
            return False, "No output generated", ["Stage failed to generate output"]

        # Check score threshold
        score = stage_state.score or 0
        min_score = requirements.get("min_score", 5.0)

        if score < min_score:
            feedback.append(f"Quality score {score} is below threshold {min_score}")

        # Check required fields
        for field in requirements.get("required_fields", []):
            if not output.get(field):
                feedback.append(f"Missing required field: {field}")

        # Mode-specific checks
        mode_value = session.mode.value if hasattr(session.mode, 'value') else str(session.mode)

        if mode_value == "deep" and stage == "customer_truth":
            if len(session.interviews) < 3:
                feedback.append("Deep mode requires at least 3 interviews")

        # Determine pass/fail
        passed = len(feedback) == 0 or score >= min_score
        blocked_reason = requirements.get("blocking_message") if not passed else None

        logger.info(
            "quality_gate_check",
            session_id=session.session_id,
            stage=stage,
            score=score,
            min_score=min_score,
            passed=passed,
            feedback_count=len(feedback),
        )

        return passed, blocked_reason, feedback

    def _calculate_evidence_tier(
        self, session: DiscoverySessionV4, stage: str
    ) -> EvidenceQuality:
        """
        Calculate evidence tier for a stage based on interview backing.

        Evidence Tiers:
        - E1: Direct customer quotes (5+ interviews)
        - E2: Verified patterns (3+ interviews)
        - E3: Partial evidence (1-2 interviews)
        - E4: AI-generated hypothesis (0 interviews)
        - E5: Unvalidated assumption
        """
        interview_count = len(session.interviews)

        # Customer truth stage gets tier based on actual interviews
        if stage == "customer_truth":
            if interview_count >= 5:
                return EvidenceQuality.E1
            elif interview_count >= 3:
                return EvidenceQuality.E2
            elif interview_count >= 1:
                return EvidenceQuality.E3
            else:
                return EvidenceQuality.E4

        # Other stages inherit from customer truth or default to E4
        if session.stages["customer_truth"].output:
            ct_output = session.stages["customer_truth"].output
            patterns = ct_output.get("patterns", {})
            evidence_quality = patterns.get("evidence_quality", "E4")
            return EvidenceQuality(evidence_quality)

        # Default: AI-generated
        return EvidenceQuality.E4

    # ═══════════════════════════════════════════════════════════════════════════
    # AI ASSISTANCE METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_coaching(
        self,
        session: DiscoverySessionV4,
        stage: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Get AI coaching for a stage."""
        from agents.discovery_v4.prompts import GENERAL_COACHING_PROMPT
        from agents.base_agent import call_llm

        prompt = GENERAL_COACHING_PROMPT.format(
            stage=stage,
            current_output=session.stages[stage].output or "No output yet",
            user_request=context.get("question", "Help me improve this stage"),
        )

        result = await call_llm(prompt, f"discovery_v4_coaching_{stage}")

        if result.get("success"):
            return result["data"]
        else:
            return {
                "acknowledgment": "Let me help you with this stage.",
                "improvements": [],
                "next_steps": ["Continue working on the current output"],
                "encouragement": "You're making good progress!",
            }

    async def synthesize_data(
        self,
        session: DiscoverySessionV4,
        stage: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Synthesize data for a stage."""
        if stage == "customer_truth":
            from agents.discovery_v4.stages.customer_truth import CustomerTruthStage

            runner = CustomerTruthStage()
            return await runner.synthesize_patterns(session.interviews)

        return {"message": "Synthesis not available for this stage"}

    async def get_suggestions(
        self,
        session: DiscoverySessionV4,
        stage: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Get AI suggestions for a stage."""
        runner = self.stage_runners.get(stage)
        if not runner:
            return {"suggestions": []}

        stage_context = self._build_stage_context(session, stage)
        stage_context.update(context)

        # Generate suggestions based on current state
        if hasattr(runner, "get_suggestions"):
            return await runner.get_suggestions(stage_context)

        return {
            "suggestions": [
                "Review the current output for completeness",
                "Consider edge cases and alternatives",
                "Validate assumptions with real data if possible",
            ]
        }

    async def check_tarpit(
        self,
        problem: str,
        solution: str | None = None,
    ) -> TarpitAnalysis:
        """Check if idea is a tarpit."""
        from agents.discovery_v4.stages.problem_love import ProblemLoveStage

        runner = ProblemLoveStage()
        return await runner.check_tarpit(problem, solution)
