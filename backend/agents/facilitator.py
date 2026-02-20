"""
Facilitator Agent for Swarm Orchestration — v3.0

The Facilitator is the central intelligence that:
- Coordinates all swarms in 7 phases
- Detects contradictions between agent outputs
- Resolves conflicts by re-running specific agents
- Runs design and synthesis phases
- Synthesizes final outputs with evidence grading

v3.0 Pipeline:
1. Planning
2. Discovery (parallel: MI + CL + CP)
3. Strategy (parallel: BC + GTM, then sequential: FM)
4. Delivery (parallel: PRD + TA + RC, then sequential: Risk)
5. Design (sequential: Wireframes → Prototype)
6. Quality Check (Critique with revision loop)
7. Synthesis (parallel: Stakeholder + Validation, then sequential: Exec Summary)
"""

import asyncio
from typing import Any, Optional, TYPE_CHECKING

import structlog

from agents.planner import run_planner_agent
from agents.critique import run_critique_agent
from agents.state import DiscoveryState
from agents.swarms import DiscoverySwarm, StrategySwarm, DeliverySwarm
from agents.constraint_broadcaster import (
    generate_phase_constraints,
    format_constraints_for_prompt,
)
from agents.output_validator import validate_agent_output, ValidationResult
from agents.eval_feedback_bridge import (
    process_eval_output_to_feedback,
    get_agents_needing_revision,
)
from models.schemas import SessionStatus

if TYPE_CHECKING:
    from utils.sse import SessionEventEmitter

logger = structlog.get_logger(__name__)


def get_current_emitter() -> Optional["SessionEventEmitter"]:
    """Get the current event emitter from the orchestrator."""
    from agents.orchestrator import _current_emitter
    return _current_emitter


class FacilitatorAgent:
    """
    Central intelligence coordinating all swarms.

    The Facilitator:
    1. Creates a research plan
    2. Dispatches swarms in dependency order
    3. Detects contradictions between outputs
    4. Resolves conflicts through targeted re-runs
    5. Synthesizes final outputs
    """

    def __init__(self):
        self.logger = structlog.get_logger("facilitator")
        self.discovery_swarm = DiscoverySwarm()
        self.strategy_swarm = StrategySwarm()
        self.delivery_swarm = DeliverySwarm()

    async def _emit_agent_start(self, agent: str, message: str = "Processing..."):
        """Emit agent start event."""
        emitter = get_current_emitter()
        if emitter:
            await emitter.emit_agent_start(agent, message)

    async def _emit_insight(self, agent: str, key: str, value: str):
        """Emit an insight from an agent."""
        emitter = get_current_emitter()
        if emitter:
            await emitter.emit_insight(agent, key, value)

    async def _emit_agent_complete(self, agent: str, summary: str, insights_count: int = 1):
        """Emit agent completion event."""
        emitter = get_current_emitter()
        if emitter:
            try:
                await emitter.emit_agent_complete(agent, summary, insights_count=insights_count)
                self.logger.debug("emit_agent_complete_success", agent=agent, summary=summary)
            except Exception as e:
                self.logger.error("emit_agent_complete_error", agent=agent, error=str(e))
        else:
            self.logger.warning("emit_agent_complete_no_emitter", agent=agent)

    async def _emit_progress(self, percentage: int, agent: str):
        """Emit progress update."""
        emitter = get_current_emitter()
        if emitter:
            await emitter.emit_progress(percentage, agent)

    def _validate_agent_output(
        self, agent_name: str, output: dict, state: DiscoveryState
    ) -> ValidationResult:
        """
        Validate agent output and log results.

        Args:
            agent_name: Name of the agent
            output: The agent's output dictionary
            state: Current discovery state

        Returns:
            ValidationResult with validation status
        """
        result = validate_agent_output(agent_name, output)

        if not result.valid:
            self.logger.warning(
                "agent_output_validation_failed",
                agent=agent_name,
                session_id=state.get("session_id"),
                error_count=len(result.errors),
                errors=result.errors[:5],  # Log first 5 errors
            )

            # Store validation failures for potential retry
            if "validation_failures" not in state:
                state["validation_failures"] = {}
            state["validation_failures"][agent_name] = result.errors
        else:
            self.logger.info(
                "agent_output_validated",
                agent=agent_name,
                session_id=state.get("session_id"),
                warning_count=len(result.warnings),
            )

        return result

    async def run(self, state: DiscoveryState) -> DiscoveryState:
        """
        Execute the complete v3.0 swarm-based workflow.

        7-Phase Pipeline:
        1. Planning
        2. Discovery (parallel: MI + CL + CP)
        3. Strategy (parallel: BC + GTM → sequential: FM)
        4. Delivery (parallel: PRD + TA + RC → sequential: Risk)
        5. Design (sequential: Wireframes → Prototype)
        6. Quality Check (Critique with revision loop)
        7. Synthesis (parallel: Stakeholder + Validation → sequential: Exec Summary)

        Args:
            state: Initial discovery state.

        Returns:
            DiscoveryState: Final state with all outputs.
        """
        self.logger.info(
            "facilitator_start",
            session_id=state["session_id"],
            version="3.1",  # Updated version to verify deployment
        )

        # Verify emitter is available at start
        emitter = get_current_emitter()
        self.logger.info(
            "facilitator_emitter_check",
            session_id=state["session_id"],
            has_emitter=emitter is not None,
        )

        try:
            # ═══════════════════════════════════════════════════════════════
            # PHASE 1: PLANNING
            # ═══════════════════════════════════════════════════════════════
            state = await self._run_planning_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # ═══════════════════════════════════════════════════════════════
            # PHASE 2: DISCOVERY (Parallel: MI + CL + CP)
            # ═══════════════════════════════════════════════════════════════
            state = await self._run_discovery_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # Check for contradictions in discovery outputs
            contradictions = self.detect_contradictions(state, phase="discovery")
            if contradictions:
                state = await self._resolve_contradictions(state, contradictions)

            # ═══════════════════════════════════════════════════════════════
            # PHASE 3: STRATEGY (Parallel: BC + GTM → Sequential: FM)
            # ═══════════════════════════════════════════════════════════════
            state = await self._run_strategy_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # Run Financial Model AFTER BC + GTM complete
            state = await self._run_financial_model(state)

            # Check for contradictions between discovery and strategy
            contradictions = self.detect_contradictions(state, phase="strategy")
            if contradictions:
                state = await self._resolve_contradictions(state, contradictions)

            # ═══════════════════════════════════════════════════════════════
            # PHASE 4: DELIVERY (Parallel: PRD + TA + RC → Sequential: Risk)
            # ═══════════════════════════════════════════════════════════════
            try:
                state = await self._run_delivery_phase(state)
                if state.get("status") == SessionStatus.FAILED:
                    return state
            except Exception as e:
                self.logger.error("delivery_phase_exception", error=str(e), exc_info=True)
                raise Exception(f"Delivery phase failed: {str(e)}")

            # ═══════════════════════════════════════════════════════════════
            # PHASE 5: DESIGN (Sequential: Wireframes → Prototype)
            # ═══════════════════════════════════════════════════════════════
            try:
                state = await self._run_design_phase(state)
            except Exception as e:
                self.logger.error("design_phase_exception", error=str(e), exc_info=True)
                raise Exception(f"Design phase failed: {str(e)}")

            # ═══════════════════════════════════════════════════════════════
            # PHASE 6: QUALITY CHECK (Critique with revision loop)
            # ═══════════════════════════════════════════════════════════════
            try:
                state = await self._run_quality_check(state)

                # Handle revision loop if needed (max 2 iterations)
                revision_count = 0
                while state.get("requires_revision") and revision_count < 2:
                    self.logger.info(
                        "revision_loop",
                        session_id=state["session_id"],
                        iteration=revision_count + 1,
                    )
                    # Re-run weak sections based on critique
                    state = await self._rerun_weak_sections(state)
                    state = await self._run_quality_check(state)
                    revision_count += 1
            except Exception as e:
                self.logger.error("quality_phase_exception", error=str(e), exc_info=True)
                raise Exception(f"Quality phase failed: {str(e)}")

            # ═══════════════════════════════════════════════════════════════
            # PHASE 7: SYNTHESIS (Parallel: Stakeholder + Validation → Exec Summary)
            # ═══════════════════════════════════════════════════════════════
            try:
                state = await self._run_synthesis_phase(state)
            except Exception as e:
                self.logger.error("synthesis_phase_exception", error=str(e), exc_info=True)
                raise Exception(f"Synthesis phase failed: {str(e)}")

            cross_ref = state.get("cross_reference_index") or {}
            self.logger.info(
                "facilitator_complete",
                session_id=state["session_id"],
                status=state.get("status"),
                claims_count=cross_ref.get("total_claims", 0),
            )

            return state

        except Exception as e:
            self.logger.error(
                "facilitator_error",
                session_id=state["session_id"],
                error=str(e),
                exc_info=True,
            )
            state["status"] = SessionStatus.FAILED
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Facilitator error: {str(e)}")

            # Emit error via SSE so frontend knows what happened
            emitter = get_current_emitter()
            if emitter:
                try:
                    await emitter.emit_error(f"Workflow failed: {str(e)}")
                except Exception:
                    pass  # Don't fail on emit error
            return state

    async def _run_planning_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the planning agent."""
        self.logger.info("phase_start", phase="planning", session_id=state["session_id"])

        await self._emit_agent_start("planner", "Creating research plan...")
        state = await run_planner_agent(state)

        # Emit insights from research plan
        plan = state.get("research_plan", {})
        if plan.get("domain_type"):
            await self._emit_insight("planner", "domain_type", f"Domain: {plan['domain_type']}")
        if plan.get("competitors_to_analyze"):
            names = [c.get("name", "Unknown") for c in plan["competitors_to_analyze"][:3]]
            await self._emit_insight("planner", "competitors", f"Competitors: {', '.join(names)}")

        await self._emit_agent_complete("planner", "Research plan created", insights_count=2)
        await self._emit_progress(5, "planner")

        return state

    async def _run_discovery_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the discovery swarm."""
        self.logger.info("phase_start", phase="discovery", session_id=state["session_id"])

        # Emit start for discovery agents
        await self._emit_agent_start("customer_research", "Analyzing market...")
        await self._emit_agent_start("competitive_intelligence", "Researching competitors...")
        await self._emit_agent_start("persona_development", "Building personas...")

        state = await self.discovery_swarm.run(state)

        # Emit insights from discovery (always emit complete, even if data missing)
        cr = state.get("customer_research") or {}
        market_ctx = cr.get("market_context") or {}
        tam = market_ctx.get("total_addressable_market")
        if tam:
            await self._emit_insight("customer_research", "tam", f"TAM: {tam}")
        await self._emit_agent_complete("customer_research", "Market research complete", insights_count=1)

        ca = state.get("competitive_analysis") or {}
        competitors = ca.get("direct_competitors") or []
        if competitors:
            names = [c.get("name", "Unknown") for c in competitors[:3] if isinstance(c, dict)]
            await self._emit_insight("competitive_intelligence", "competitors", f"Found: {', '.join(names)}")
        await self._emit_agent_complete("competitive_intelligence", f"Analyzed {len(competitors)} competitors", insights_count=1)

        dp = state.get("detailed_personas") or {}
        primary = dp.get("primary_persona") or {}
        if primary.get("name"):
            await self._emit_insight("persona_development", "primary_persona", f"Primary: {primary['name']} - {primary.get('archetype', '')}")
        await self._emit_agent_complete("persona_development", "Personas created", insights_count=1)

        await self._emit_progress(25, "discovery")

        # Validate discovery outputs
        if state.get("customer_research"):
            self._validate_agent_output(
                "Customer Research Agent",
                state["customer_research"],
                state
            )
        if state.get("competitive_analysis"):
            self._validate_agent_output(
                "competitive_analysis",
                state["competitive_analysis"],
                state
            )

        return state

    async def _run_strategy_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the strategy swarm."""
        self.logger.info("phase_start", phase="strategy", session_id=state["session_id"])

        # Generate and inject constraints from Discovery phase
        constraints = await generate_phase_constraints(state, "strategy")
        state["active_constraints"] = [c.to_dict() for c in constraints]
        state["constraints_prompt"] = format_constraints_for_prompt(constraints)

        self.logger.info(
            "strategy_constraints_generated",
            session_id=state["session_id"],
            constraint_count=len(constraints),
        )

        await self._emit_agent_start("business_strategy", "Developing business case...")
        await self._emit_agent_start("gtm_strategy", "Creating go-to-market strategy...")

        state = await self.strategy_swarm.run(state)

        # Emit insights from strategy (always emit complete)
        bc = state.get("business_case") or {}
        lean_canvas = bc.get("lean_canvas") or {}
        problems = lean_canvas.get("problem") or []
        if problems and len(problems) > 0:
            problem_text = str(problems[0])[:80] if problems[0] else "Unknown"
            await self._emit_insight("business_strategy", "problem", f"Problem: {problem_text}...")
        await self._emit_agent_complete("business_strategy", "Business case complete", insights_count=1)

        gtm = state.get("gtm_plan") or {}
        market_entry = gtm.get("market_entry_strategy") or {}
        initial_segment = market_entry.get("initial_segment")
        if initial_segment:
            await self._emit_insight("gtm_strategy", "segment", f"Target: {initial_segment}")
        await self._emit_agent_complete("gtm_strategy", "GTM strategy complete", insights_count=1)

        await self._emit_progress(40, "strategy")

        # Validate strategy outputs
        if state.get("business_case"):
            self._validate_agent_output(
                "Business Strategy Agent",
                state["business_case"],
                state
            )
        if state.get("gtm_plan"):
            self._validate_agent_output(
                "Go-to-Market",
                state["gtm_plan"],
                state
            )

        return state

    async def _run_delivery_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the delivery swarm."""
        self.logger.info("phase_start", phase="delivery", session_id=state["session_id"])

        # Generate and inject constraints from Discovery + Strategy phases
        constraints = await generate_phase_constraints(state, "delivery")
        state["active_constraints"] = [c.to_dict() for c in constraints]
        state["constraints_prompt"] = format_constraints_for_prompt(constraints)

        self.logger.info(
            "delivery_constraints_generated",
            session_id=state["session_id"],
            constraint_count=len(constraints),
        )

        await self._emit_agent_start("product_requirements", "Writing requirements...")
        await self._emit_agent_start("technical_architect", "Designing architecture...")
        await self._emit_agent_start("legal_regulatory", "Reviewing compliance...")
        await self._emit_agent_start("risk_assessment", "Assessing risks...")

        state = await self.delivery_swarm.run(state)

        self.logger.info(
            "delivery_swarm_complete",
            session_id=state["session_id"],
            has_prd=state.get("product_requirements") is not None,
            has_ta=state.get("technical_architecture") is not None,
            has_legal=state.get("legal_regulatory_review") is not None,
            has_risk=state.get("risk_assessment") is not None,
        )

        # Emit insights from delivery (try to extract, but always complete)
        self.logger.info("emitting_delivery_completes", session_id=state["session_id"])

        # Safely extract PRD features (functional_requirements is a LIST, not a dict)
        prd = state.get("product_requirements") or {}
        features = prd.get("functional_requirements") or []  # This is the list of FRs
        if features and isinstance(features, list):
            await self._emit_insight("product_requirements", "features", f"Functional requirements: {len(features)}")
        await self._emit_agent_complete("product_requirements", "PRD complete", insights_count=1)
        self.logger.info("emitted_prd_complete", session_id=state["session_id"])

        # Safely extract tech stack
        ta = state.get("technical_architecture") or {}
        stack = ta.get("recommended_stack") or {}
        if stack.get("frontend"):
            await self._emit_insight("technical_architect", "stack", f"Stack: {stack.get('frontend', '')} + {stack.get('backend', '')}")
        await self._emit_agent_complete("technical_architect", "Architecture complete", insights_count=1)
        self.logger.info("emitted_ta_complete", session_id=state["session_id"])

        # Safely extract regulations
        lr = state.get("legal_regulatory_review") or {}
        regs = lr.get("applicable_regulations") or []
        if regs:
            await self._emit_insight("legal_regulatory", "regulations", f"Regulations: {len(regs)} applicable")
        await self._emit_agent_complete("legal_regulatory", "Legal review complete", insights_count=1)
        self.logger.info("emitted_legal_complete", session_id=state["session_id"])

        # Safely extract risks (backend uses risk_matrix, not risks)
        ra = state.get("risk_assessment") or {}
        risks = ra.get("risk_matrix") or ra.get("risks") or []
        if risks:
            # Risk uses likelihood/impact scores, not severity
            high_risks = [r for r in risks if isinstance(r, dict) and r.get("risk_score", 0) >= 12]
            await self._emit_insight("risk_assessment", "risks", f"Risks: {len(high_risks)} high, {len(risks)} total")
        await self._emit_agent_complete("risk_assessment", "Risk assessment complete", insights_count=1)
        self.logger.info("emitted_risk_complete", session_id=state["session_id"])

        await self._emit_progress(60, "delivery")
        self.logger.info("delivery_phase_complete", session_id=state["session_id"])

        # Validate delivery outputs
        if state.get("product_requirements"):
            self._validate_agent_output(
                "Product Requirements Agent",
                state["product_requirements"],
                state
            )
        if state.get("technical_architecture"):
            self._validate_agent_output(
                "Technical Architect Agent",
                state["technical_architecture"],
                state
            )
        if state.get("legal_regulatory_review"):
            self._validate_agent_output(
                "Legal & Regulatory Review",
                state["legal_regulatory_review"],
                state
            )

        return state

    async def _run_quality_check(self, state: DiscoveryState) -> DiscoveryState:
        """Run the critique agent with retry support for quality assessment."""
        from config import settings

        self.logger.info("phase_start", phase="quality_check", session_id=state["session_id"])

        # Integrate any validation failures into revision priority
        state = _integrate_validation_failures_into_revision(state)

        await self._emit_agent_start("critique", "Checking quality...")

        max_retries = settings.max_critique_retries

        for attempt in range(1, max_retries + 1):
            state["critique_attempt"] = attempt
            state = await run_critique_agent(state)

            # Check if retry is needed
            if not state.get("_retry_critique"):
                break

            # Clear retry flag
            state["_retry_critique"] = False

            self.logger.info(
                "critique_retry",
                session_id=state["session_id"],
                attempt=attempt,
                max_retries=max_retries,
            )

        # Emit quality insights
        qa = state.get("quality_assessment", {})
        if qa.get("overall_score"):
            await self._emit_insight("critique", "score", f"Quality score: {int(qa['overall_score'] * 100)}%")
        if qa.get("quality_passed") is not None:
            status = "PASSED" if qa["quality_passed"] else "NEEDS REVISION"
            await self._emit_insight("critique", "status", f"Status: {status}")

        # Log if quality gate was bypassed
        if state.get("quality_passed_reason") == "max_critique_retries_exceeded":
            self.logger.warning(
                "quality_gate_bypassed",
                session_id=state["session_id"],
                reason="max_critique_retries_exceeded",
            )

        await self._emit_agent_complete("critique", f"Quality: {int(qa.get('overall_score', 0) * 100)}%", insights_count=2)
        await self._emit_progress(80, "critique")

        return state

    async def _run_financial_model(self, state: DiscoveryState) -> DiscoveryState:
        """Run financial model agent after BC + GTM complete."""
        from agents.financial_model_agent import run_financial_model_agent

        self.logger.info("phase_start", phase="financial_model", session_id=state["session_id"])

        await self._emit_agent_start("financial_modeling", "Building financial model...")

        state = await run_financial_model_agent(state)

        # Emit financial insights (safely handle None values)
        fm = state.get("financial_model") or {}
        five_year = fm.get("five_year_projection") or {}
        if five_year:
            y5 = five_year.get("year_5") or {}
            if y5.get("revenue"):
                await self._emit_insight("financial_modeling", "revenue", f"Y5 Revenue: {y5['revenue']}")
        unit_econ = fm.get("unit_economics") or {}
        if unit_econ.get("ltv_cac_ratio"):
            await self._emit_insight("financial_modeling", "ltv_cac", f"LTV:CAC = {unit_econ['ltv_cac_ratio']}")

        await self._emit_agent_complete("financial_modeling", "Financial model complete", insights_count=2)
        await self._emit_progress(50, "financial_modeling")

        # Validate financial model output
        if state.get("financial_model"):
            self._validate_agent_output(
                "Financial Model",
                state["financial_model"],
                state
            )

        return state

    async def _run_design_phase(self, state: DiscoveryState) -> DiscoveryState:
        """
        Run the design phase: Wireframes → Prototype.

        This phase runs sequentially: wireframes must complete before prototype.
        """
        from agents.wireframe_agent import run_wireframe_agent
        from agents.prototype_agent import run_prototype_agent

        self.logger.info("phase_start", phase="design", session_id=state["session_id"])

        # Generate and inject constraints from Delivery phase
        constraints = await generate_phase_constraints(state, "design")
        state["active_constraints"] = [c.to_dict() for c in constraints]
        state["constraints_prompt"] = format_constraints_for_prompt(constraints)

        self.logger.info(
            "design_constraints_generated",
            session_id=state["session_id"],
            constraint_count=len(constraints),
        )

        # First: Wireframes
        await self._emit_agent_start("wireframe_agent", "Designing wireframes...")
        state = await run_wireframe_agent(state)

        wf = state.get("wireframes", {})
        screens = wf.get("screens", [])
        if screens:
            await self._emit_insight("wireframe_agent", "screens", f"Designed {len(screens)} screens")
        await self._emit_agent_complete("wireframe_agent", f"{len(screens)} wireframes created", insights_count=1)
        await self._emit_progress(70, "wireframe_agent")

        # Second: Prototype (depends on wireframes)
        await self._emit_agent_start("prototype_agent", "Generating prototype code...")
        state = await run_prototype_agent(state)

        proto = state.get("prototype", {})
        if proto.get("react_code"):
            await self._emit_insight("prototype_agent", "code", "React prototype generated")
        await self._emit_agent_complete("prototype_agent", "Interactive prototype ready", insights_count=1)
        await self._emit_progress(75, "prototype_agent")

        return state

    async def _run_synthesis_phase(self, state: DiscoveryState) -> DiscoveryState:
        """
        Run the synthesis phase: Stakeholder + Validation (parallel) → Exec Summary.

        This produces the final outputs that synthesize all prior work.
        """
        from agents.stakeholder_agent import run_stakeholder_agent
        from agents.validation_agent import run_validation_agent
        from agents.executive_summary_agent import run_executive_summary_agent
        from agents.orchestrator import finalize_node

        self.logger.info("phase_start", phase="synthesis", session_id=state["session_id"])

        # Generate and inject constraints from all prior phases
        constraints = await generate_phase_constraints(state, "synthesis")
        state["active_constraints"] = [c.to_dict() for c in constraints]
        state["constraints_prompt"] = format_constraints_for_prompt(constraints)

        self.logger.info(
            "synthesis_constraints_generated",
            session_id=state["session_id"],
            constraint_count=len(constraints),
        )

        # Parallel: Stakeholder Views + Validation Playbook
        await self._emit_agent_start("stakeholder_agent", "Creating stakeholder views...")
        await self._emit_agent_start("validation_agent", "Building validation playbook...")

        stakeholder_state, validation_state = await asyncio.gather(
            run_stakeholder_agent(state.copy()),
            run_validation_agent(state.copy()),
        )

        # Merge parallel results
        state["stakeholder_views"] = stakeholder_state.get("stakeholder_views")
        state["validation_playbook"] = validation_state.get("validation_playbook")

        # Emit stakeholder insights
        sv = state.get("stakeholder_views", {})
        if sv.get("views"):
            await self._emit_insight("stakeholder_agent", "views", f"Created {len(sv['views'])} stakeholder views")
        await self._emit_agent_complete("stakeholder_agent", "Stakeholder views ready", insights_count=1)

        # Emit validation insights
        vp = state.get("validation_playbook", {})
        if vp.get("experiments"):
            await self._emit_insight("validation_agent", "experiments", f"Designed {len(vp['experiments'])} experiments")
        await self._emit_agent_complete("validation_agent", "Validation playbook ready", insights_count=1)

        await self._emit_progress(90, "synthesis")

        # Merge any errors
        for s in [stakeholder_state, validation_state]:
            if s.get("errors"):
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].extend(s["errors"])

        # Merge cross-reference indices
        from agents.state import merge_cross_references
        state["cross_reference_index"] = merge_cross_references(
            state.get("cross_reference_index"),
            stakeholder_state.get("cross_reference_index")
        )
        state["cross_reference_index"] = merge_cross_references(
            state.get("cross_reference_index"),
            validation_state.get("cross_reference_index")
        )

        # Sequential: Executive Summary (depends on Stakeholder + Validation)
        await self._emit_agent_start("executive_summary_agent", "Writing executive summary...")
        state = await run_executive_summary_agent(state)

        es = state.get("executive_summary", {})
        if es.get("product_name"):
            await self._emit_insight("executive_summary_agent", "product", f"Product: {es['product_name']}")
        await self._emit_agent_complete("executive_summary_agent", "Executive summary complete", insights_count=1)

        await self._emit_progress(95, "executive_summary_agent")

        # Finalize
        state = await finalize_node(state)

        await self._emit_progress(100, "complete")

        return state

    async def _rerun_weak_sections(self, state: DiscoveryState) -> DiscoveryState:
        """
        Re-run sections that were flagged as weak by the critique.

        Enhanced with revision history tracking (Quality Improvement System):
        - Tracks what was tried before
        - Provides context to agents about previous attempts
        - Records score changes for analysis
        - INJECTS FEEDBACK INTO critique_feedback so agents can read it

        Uses the revision_priority from quality_assessment to determine
        which agents to re-run.
        """
        from datetime import datetime

        quality = state.get("quality_assessment", {})
        revision_priority = quality.get("revision_priority", [])

        if not revision_priority:
            return state

        self.logger.info(
            "rerunning_weak_sections",
            session_id=state["session_id"],
            sections=[r.get("section") for r in revision_priority[:3]],
            iteration=state.get("iteration", 1),
        )

        # Map section names to agent runners
        section_to_agent = {
            "customer_research": "discovery",
            "market_intelligence": "discovery",
            "competitive_analysis": "discovery",
            "business_case": "strategy",
            "gtm_plan": "strategy",
            "financial_model": "financial",
            "product_requirements": "delivery",
            "technical_architecture": "delivery",
            "legal_regulatory_review": "delivery",
        }

        # Map section names to critique_feedback keys (what agents look for)
        section_to_feedback_key = {
            "customer_research": "customer_research_feedback",
            "market_intelligence": "customer_research_feedback",
            "competitive_analysis": "competitive_analysis_feedback",
            "business_case": "business_case_feedback",
            "gtm_plan": "gtm_plan_feedback",
            "financial_model": "financial_model_feedback",
            "product_requirements": "product_requirements_feedback",
            "technical_architecture": "technical_architecture_feedback",
            "legal_regulatory_review": "legal_regulatory_feedback",
        }

        # Re-run specific agents based on priority
        for item in revision_priority[:2]:  # Limit to top 2
            section = item.get("section", "").lower().replace(" ", "_")
            score_before = item.get("score", 0)
            feedback = item.get("feedback", [])
            agent_phase = section_to_agent.get(section)

            if not agent_phase:
                continue

            # Build revision context for the agent
            revision_context = _format_revision_context(
                previous_output=state.get(section, {}),
                feedback=feedback,
                revision_history=state.get("revision_history", []),
                section_name=section,
            )

            # CRITICAL: Inject feedback into critique_feedback so agents can read it
            # Agents use extract_feedback_for_agent() which reads from state["critique_feedback"]
            feedback_key = section_to_feedback_key.get(section)
            if feedback_key:
                if "critique_feedback" not in state or state["critique_feedback"] is None:
                    state["critique_feedback"] = {}
                # Convert to dict if it's a CritiqueFeedback TypedDict
                if hasattr(state["critique_feedback"], "__dict__"):
                    state["critique_feedback"] = dict(state["critique_feedback"])
                elif not isinstance(state["critique_feedback"], dict):
                    state["critique_feedback"] = {}

                # Set the feedback with revision context prepended
                state["critique_feedback"][feedback_key] = [
                    f"[REVISION {state.get('iteration', 1)}] {fb}" for fb in feedback
                ]

                self.logger.info(
                    "feedback_injected_for_revision",
                    session_id=state["session_id"],
                    section=section,
                    feedback_key=feedback_key,
                    feedback_count=len(feedback),
                )

            # Also store the formatted revision context
            state["_revision_context"] = revision_context

            self.logger.info(
                "rerunning_section",
                session_id=state["session_id"],
                section=section,
                score_before=score_before,
                feedback_count=len(feedback),
            )

            if agent_phase == "discovery":
                state = await self.discovery_swarm.run(state)
            elif agent_phase == "strategy":
                state = await self.strategy_swarm.run(state)
            elif agent_phase == "delivery":
                state = await self.delivery_swarm.run(state)
            elif agent_phase == "financial":
                state = await self._run_financial_model(state)

            # Record revision attempt in history
            revision_attempt = {
                "iteration": state.get("iteration", 1),
                "agent": section,
                "issues_addressed": feedback[:5],  # Top 5 issues
                "score_before": score_before,
                "score_after": 0,  # Will be updated after next critique
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Ensure revision_history exists as a list
            if "revision_history" not in state or state["revision_history"] is None:
                state["revision_history"] = []
            state["revision_history"].append(revision_attempt)

        # Clear revision context after use
        if "_revision_context" in state:
            del state["_revision_context"]

        return state

    def detect_contradictions(
        self, state: DiscoveryState, phase: str = "all"
    ) -> list[dict[str, Any]]:
        """
        Detect contradictions between agent outputs.

        Checks for inconsistencies in:
        - Market size estimates
        - Pricing assumptions
        - Target customer definitions
        - Technical feasibility vs business requirements

        Args:
            state: Current workflow state.
            phase: Which phase to check ("discovery", "strategy", or "all").

        Returns:
            list[dict]: List of detected contradictions.
        """
        contradictions = []

        # Get relevant outputs (use or {} to handle None values)
        customer_research = state.get("customer_research") or {}
        business_case = state.get("business_case") or {}
        financial_model = state.get("financial_model") or {}
        gtm_plan = state.get("gtm_plan") or {}

        # Check 1: Market size consistency
        if customer_research and business_case:
            cr_market = customer_research.get("market_context") or {}
            cr_tam = cr_market.get("total_addressable_market", "")
            bc_market = business_case.get("market_size") or {}
            bc_tam = bc_market.get("tam", "")

            if cr_tam and bc_tam and self._values_differ_significantly(cr_tam, bc_tam):
                contradictions.append({
                    "type": "market_size",
                    "agents": ["customer_research", "business_strategy"],
                    "field": "TAM",
                    "values": {"customer_research": cr_tam, "business_case": bc_tam},
                    "severity": "medium",
                })

        # Check 2: Pricing consistency
        if business_case and financial_model:
            bc_pricing = business_case.get("revenue_streams") or []
            fm_revenue = financial_model.get("revenue_model") or {}
            fm_pricing = fm_revenue.get("primary_revenue_stream") or {}

            if bc_pricing and fm_pricing:
                bc_price = self._extract_price(bc_pricing)
                pricing_tiers = fm_pricing.get("pricing_tiers") or [{}]
                fm_price = (pricing_tiers[0] if pricing_tiers else {}).get("price_monthly", 0)

                if bc_price and fm_price and abs(bc_price - fm_price) / max(bc_price, fm_price) > 0.5:
                    contradictions.append({
                        "type": "pricing",
                        "agents": ["business_strategy", "financial_modeling"],
                        "field": "pricing",
                        "values": {"business_case": bc_price, "financial_model": fm_price},
                        "severity": "high",
                    })

        # Check 3: Target customer consistency
        if customer_research and gtm_plan:
            cr_market = customer_research.get("market_context") or {}
            cr_segments = cr_market.get("customer_segments") or []
            gtm_entry = gtm_plan.get("market_entry_strategy") or {}
            gtm_segment = gtm_entry.get("initial_segment", "")

            if cr_segments and gtm_segment:
                if not any(gtm_segment.lower() in str(seg).lower() for seg in cr_segments):
                    contradictions.append({
                        "type": "target_customer",
                        "agents": ["customer_research", "gtm_strategy"],
                        "field": "initial_segment",
                        "values": {"customer_research": cr_segments, "gtm_plan": gtm_segment},
                        "severity": "medium",
                    })

        if contradictions:
            self.logger.warning(
                "contradictions_detected",
                session_id=state["session_id"],
                phase=phase,
                count=len(contradictions),
                types=[c["type"] for c in contradictions],
            )

        return contradictions

    async def _resolve_contradictions(
        self,
        state: DiscoveryState,
        contradictions: list[dict[str, Any]],
    ) -> DiscoveryState:
        """
        Resolve contradictions by re-running specific agents with context.

        Args:
            state: Current workflow state.
            contradictions: List of detected contradictions.

        Returns:
            DiscoveryState: Updated state after resolution.
        """
        self.logger.info(
            "resolving_contradictions",
            session_id=state["session_id"],
            count=len(contradictions),
        )

        # For high-severity contradictions, re-run the affected agents
        high_severity = [c for c in contradictions if c.get("severity") == "high"]

        if not high_severity:
            # Just log medium severity and continue
            return state

        # Add contradiction context to state for agents to consider
        state["contradiction_context"] = {
            "contradictions": contradictions,
            "resolution_instruction": (
                "Previous outputs contained inconsistencies. "
                "Please review and ensure your output is consistent with other agents' findings. "
                "Contradictions detected: " + str([c["type"] for c in contradictions])
            ),
        }

        # Re-run the second agent in each contradiction (typically the one that should adjust)
        agents_to_rerun = set()
        for c in high_severity:
            agents_to_rerun.add(c["agents"][1])  # Re-run the second agent

        for agent in agents_to_rerun:
            self.logger.info(
                "rerunning_agent_for_resolution",
                session_id=state["session_id"],
                agent=agent,
            )

            if agent == "business_strategy":
                from agents.business_strategy import run_business_strategy_agent
                state = await run_business_strategy_agent(state)
            elif agent == "financial_modeling":
                from agents.swarms.strategy_swarm import run_financial_modeling
                state = await run_financial_modeling(state)
            elif agent == "gtm_strategy":
                from agents.swarms.strategy_swarm import run_gtm_strategy
                state = await run_gtm_strategy(state)

        # Clear contradiction context after resolution
        if "contradiction_context" in state:
            del state["contradiction_context"]

        return state

    def _values_differ_significantly(self, val1: str, val2: str) -> bool:
        """Check if two string values representing numbers differ significantly."""
        import re

        def extract_number(s: str) -> float | None:
            # Extract numeric value from strings like "$5B", "5 billion", etc.
            s = s.lower().replace(",", "").replace("$", "")
            multipliers = {"k": 1e3, "m": 1e6, "b": 1e9, "t": 1e12}

            match = re.search(r"(\d+(?:\.\d+)?)\s*(k|m|b|t|billion|million|thousand|trillion)?", s)
            if match:
                num = float(match.group(1))
                mult = match.group(2) or ""
                if mult.startswith("b"):
                    num *= 1e9
                elif mult.startswith("m"):
                    num *= 1e6
                elif mult.startswith("t"):
                    if "thousand" in mult:
                        num *= 1e3
                    else:
                        num *= 1e12
                elif mult.startswith("k"):
                    num *= 1e3
                elif mult in multipliers:
                    num *= multipliers[mult]
                return num
            return None

        n1 = extract_number(val1)
        n2 = extract_number(val2)

        if n1 is None or n2 is None:
            return False

        # Differ by more than 100%
        return abs(n1 - n2) / max(n1, n2) > 1.0

    def _extract_price(self, revenue_streams: list) -> float | None:
        """Extract a price from revenue streams list."""
        if not revenue_streams:
            return None

        for stream in revenue_streams:
            if isinstance(stream, dict):
                price = stream.get("price") or stream.get("pricing") or stream.get("monthly_price")
                if price:
                    if isinstance(price, (int, float)):
                        return float(price)
                    import re
                    match = re.search(r"(\d+(?:\.\d+)?)", str(price))
                    if match:
                        return float(match.group(1))
        return None

    # ═══════════════════════════════════════════════════════════════════════════════
    # DISCOVERY V4 INTEGRATION
    # ═══════════════════════════════════════════════════════════════════════════════

    async def run_with_v4_discovery(
        self,
        v4_session: Any,  # DiscoverySessionV4 from models.discovery_v4_schemas
    ) -> DiscoveryState:
        """
        Run full lifecycle using V4 discovery outputs as foundation.

        Injects discovery findings as high-confidence constraints so downstream
        agents (Strategy, Delivery, Design) build on validated research.

        Args:
            v4_session: The V4 discovery session with completed stages.

        Returns:
            DiscoveryState: Final state after running Strategy, Delivery, and Design phases.
        """
        from models.discovery_v4_schemas import EvidenceQuality

        self.logger.info(
            "v4_integration_start",
            session_id=v4_session.session_id,
            mode=v4_session.mode,
            evidence_quality=v4_session.overall_evidence_quality,
        )

        # Initialize state from V4 session
        state: DiscoveryState = {
            "session_id": v4_session.session_id,
            "product_idea": v4_session.product_idea,
            "industry": v4_session.industry,
            "target_market": v4_session.target_market,
            "status": SessionStatus.IN_PROGRESS,
            "iteration": 1,
            "errors": [],
        }

        # Convert V4 discovery outputs to V3 state fields
        state = self._convert_v4_to_v3_state(state, v4_session)

        # Mark evidence tier for downstream agents
        if v4_session.overall_evidence_quality in (EvidenceQuality.E1, EvidenceQuality.E2):
            state["_discovery_evidence_tier"] = v4_session.overall_evidence_quality
            state["_high_confidence_discovery"] = True
            self.logger.info(
                "v4_high_confidence_discovery",
                session_id=v4_session.session_id,
                evidence_tier=v4_session.overall_evidence_quality,
            )

        # Skip discovery phase since V4 already completed it
        # Go straight to strategy
        await self._emit_phase_start("strategy")
        state = await self._run_strategy_phase(state)

        # Run delivery phase
        await self._emit_phase_start("delivery")
        state = await self._run_delivery_phase(state)

        # Run design phase
        await self._emit_phase_start("design")
        state = await self._run_design_phase(state)

        # Run quality check
        await self._emit_phase_start("quality")
        state = await self._run_quality_check(state)

        # Run synthesis phase
        await self._emit_phase_start("synthesis")
        state = await self._run_synthesis_phase(state)

        state["status"] = SessionStatus.COMPLETED

        self.logger.info(
            "v4_integration_complete",
            session_id=v4_session.session_id,
            quality_score=(state.get("quality_assessment") or {}).get("overall_score"),
        )

        return state

    def _convert_v4_to_v3_state(
        self,
        state: DiscoveryState,
        v4_session: Any,
    ) -> DiscoveryState:
        """
        Convert V4 discovery outputs to V3 state format.

        This allows downstream agents to use V4 insights as constraints.
        """
        # Problem Love -> Problem statement and validation
        if v4_session.stages.get("problem_love", {}).get("output"):
            problem_love = v4_session.stages["problem_love"]["output"]
            state["_v4_problem_statement"] = (
                problem_love.get("problem_statement_refined")
                or problem_love.get("problem_statement")
            )
            state["_v4_problem_score"] = problem_love.get("overall_score")

        # Customer Truth -> Customer research and personas
        if v4_session.stages.get("customer_truth", {}).get("output"):
            customer_truth = v4_session.stages["customer_truth"]["output"]

            # Convert patterns to persona format
            patterns = customer_truth.get("patterns") or {}
            if patterns:
                state["_v4_pain_patterns"] = patterns.get("pain_patterns", [])
                state["_v4_trigger_patterns"] = patterns.get("trigger_patterns", [])
                state["_v4_outcome_patterns"] = patterns.get("outcome_patterns", [])

            # Convert interviews to customer research format
            if v4_session.interviews:
                state["_v4_interview_count"] = len(v4_session.interviews)
                state["_v4_key_quotes"] = [
                    i.key_quote for i in v4_session.interviews if i.key_quote
                ][:5]

        # Opportunity Mapping -> Competitive analysis and strategy
        if v4_session.stages.get("opportunity_mapping", {}).get("output"):
            opp_mapping = v4_session.stages["opportunity_mapping"]["output"]

            if opp_mapping.get("four_forces"):
                state["_v4_four_forces"] = opp_mapping["four_forces"]

            if opp_mapping.get("opportunity_tree"):
                state["_v4_opportunity_tree"] = opp_mapping["opportunity_tree"]

            state["_v4_primary_opportunity"] = opp_mapping.get("primary_opportunity")

        # Solution Design -> Solution constraints
        if v4_session.stages.get("solution_design", {}).get("output"):
            solution = v4_session.stages["solution_design"]["output"]

            state["_v4_solution_concept"] = solution.get("solution_concept")
            state["_v4_dhm_score"] = solution.get("dhm_score")
            state["_v4_pre_mortem"] = solution.get("pre_mortem")

        # Validation Plan -> Validation experiments
        if v4_session.stages.get("validation_plan", {}).get("output"):
            validation = v4_session.stages["validation_plan"]["output"]
            state["_v4_validation_experiments"] = validation.get("experiments", [])

        # Build constraints prompt from V4 data
        state["_injected_constraints"] = self._build_v4_constraints_prompt(state)

        return state

    def _build_v4_constraints_prompt(self, state: DiscoveryState) -> str:
        """Build a constraints prompt from V4 discovery data."""
        constraints = []

        if state.get("_v4_problem_statement"):
            constraints.append(f"VALIDATED PROBLEM: {state['_v4_problem_statement']}")

        if state.get("_v4_pain_patterns"):
            pains = [p.get("description", str(p)) for p in state["_v4_pain_patterns"][:3]]
            constraints.append(f"KEY PAIN POINTS: {'; '.join(pains)}")

        if state.get("_v4_key_quotes"):
            constraints.append(f"CUSTOMER EVIDENCE ({state.get('_v4_interview_count', 0)} interviews): "
                             f"{' | '.join(state['_v4_key_quotes'][:3])}")

        if state.get("_v4_primary_opportunity"):
            constraints.append(f"PRIMARY OPPORTUNITY: {state['_v4_primary_opportunity']}")

        if state.get("_v4_solution_concept"):
            constraints.append(f"SOLUTION DIRECTION: {state['_v4_solution_concept']}")

        if state.get("_v4_dhm_score"):
            dhm = state["_v4_dhm_score"]
            constraints.append(
                f"DHM SCORE: Delight={dhm.get('delight', 'N/A')}, "
                f"Hard-to-copy={dhm.get('hard_to_copy', 'N/A')}, "
                f"Margin={dhm.get('margin', 'N/A')}"
            )

        if not constraints:
            return ""

        return (
            "## V4 DISCOVERY CONSTRAINTS (HIGH CONFIDENCE)\n"
            "The following insights come from validated discovery research. "
            "Build on these constraints rather than generating conflicting data.\n\n"
            + "\n".join(f"- {c}" for c in constraints)
        )

    async def _emit_phase_start(self, phase: str) -> None:
        """Emit a phase start event."""
        emitter = get_current_emitter()
        if emitter:
            try:
                await emitter.emit_phase_start(phase)
            except Exception as e:
                self.logger.warning("emit_phase_start_error", phase=phase, error=str(e))


def _integrate_validation_failures_into_revision(
    state: DiscoveryState,
) -> DiscoveryState:
    """
    Integrate validation failures into the revision priority list.

    This ensures that agents with validation failures are prioritized
    for revision alongside critique feedback.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation failures integrated
    """
    try:
        validation_failures = state.get("validation_failures") or {}
        if not validation_failures:
            return state

        # Get existing revision priority (handle None values)
        quality = state.get("quality_assessment")
        if quality is None:
            quality = {}
            state["quality_assessment"] = quality

        revision_priority = quality.get("revision_priority") or []

        # Map validation failures to revision priority format
        for agent_name, errors in validation_failures.items():
            if not errors:
                continue
            # Check if agent already in revision priority
            existing = next(
                (r for r in revision_priority if r.get("section", "").lower() == agent_name.lower()),
                None
            )

            if existing:
                # Add validation errors to existing feedback
                existing_feedback = existing.get("feedback") or []
                existing["feedback"] = existing_feedback + [f"[VALIDATION] {e}" for e in errors[:5]]
            else:
                # Add new revision priority entry
                revision_priority.append({
                    "section": agent_name,
                    "score": 0.4,  # Low score = needs revision
                    "feedback": [f"[VALIDATION] {e}" for e in errors[:5]],
                })

        # Sort by score (lowest first = most urgent)
        revision_priority.sort(key=lambda x: x.get("score", 1.0))

        # Update state safely
        if isinstance(state.get("quality_assessment"), dict):
            state["quality_assessment"]["revision_priority"] = revision_priority

    except Exception as e:
        # Log but don't fail the workflow for validation integration errors
        import structlog
        logger = structlog.get_logger(__name__)
        logger.warning(
            "validation_integration_error",
            error=str(e),
            session_id=state.get("session_id"),
        )

    return state


def _format_revision_context(
    previous_output: dict,
    feedback: list[str],
    revision_history: list[dict],
    section_name: str,
) -> str:
    """
    Format revision context for agent prompt.

    Provides agents with:
    - Previous attempt history (to avoid repeating mistakes)
    - Current feedback to address
    - Score trajectory

    Args:
        previous_output: The previous output being revised
        feedback: List of feedback items to address
        revision_history: History of revision attempts
        section_name: Name of the section being revised

    Returns:
        Formatted string for prompt injection
    """
    lines = [
        "## REVISION CONTEXT",
        "",
        f"This is a revision of the {section_name.replace('_', ' ').title()} section.",
        "Review the feedback carefully and address ALL issues.",
        "",
    ]

    # Previous attempts for this section
    section_history = [
        h for h in revision_history
        if h.get("agent") == section_name
    ]

    if section_history:
        lines.append("### Previous Revision Attempts:")
        for attempt in section_history[-3:]:  # Last 3 attempts
            lines.append(f"- **Iteration {attempt.get('iteration', '?')}**")
            lines.append(f"  Score: {attempt.get('score_before', 0):.2f}")
            issues = attempt.get("issues_addressed", [])
            if issues:
                lines.append(f"  Issues addressed: {', '.join(issues[:3])}")
        lines.append("")
        lines.append("**DO NOT repeat mistakes from previous attempts.**")
        lines.append("")

    # Current feedback to address
    if feedback:
        lines.append("### Issues to Address NOW:")
        for i, fb in enumerate(feedback[:10], 1):  # Top 10 issues
            lines.append(f"{i}. {fb}")
        lines.append("")

    # Summary of previous output (for context)
    if previous_output:
        # Include a brief summary of what was in the previous output
        output_keys = list(previous_output.keys())[:10]
        lines.append(f"### Previous Output Sections: {', '.join(output_keys)}")
        lines.append("")

    lines.append("**Address ALL issues listed above. Be specific and data-driven.**")

    return "\n".join(lines)


async def run_facilitator(state: DiscoveryState) -> DiscoveryState:
    """
    Run the Facilitator agent.

    This is the main entry point for swarm-based workflow execution.

    Args:
        state: Initial discovery state.

    Returns:
        DiscoveryState: Final state with all outputs.
    """
    facilitator = FacilitatorAgent()
    return await facilitator.run(state)
