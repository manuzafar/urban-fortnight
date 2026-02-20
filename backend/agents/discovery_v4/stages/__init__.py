"""
Discovery V4 Stage Implementations.

Each stage is based on proven product discovery methodologies:
- Problem Love: Uri Levine's "Fall in Love with the Problem"
- Customer Truth: Teresa Torres's Continuous Discovery
- Opportunity Mapping: Teresa Torres's Opportunity Solution Tree
- Solution Design: DHM (Delight, Hard-to-copy, Margin) framework
- Validation Plan: Validation ladder methodology
"""

from agents.discovery_v4.stages.problem_love import ProblemLoveStage
from agents.discovery_v4.stages.customer_truth import CustomerTruthStage
from agents.discovery_v4.stages.opportunity_mapping import OpportunityMappingStage
from agents.discovery_v4.stages.solution_design import SolutionDesignStage
from agents.discovery_v4.stages.validation_plan import ValidationPlanStage

__all__ = [
    "ProblemLoveStage",
    "CustomerTruthStage",
    "OpportunityMappingStage",
    "SolutionDesignStage",
    "ValidationPlanStage",
]
