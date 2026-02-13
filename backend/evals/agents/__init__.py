"""Agent-specific evaluations — tailored criteria for each agent type."""

from evals.agents.customer_research_eval import CustomerResearchEval
from evals.agents.competitive_analysis_eval import CompetitiveAnalysisEval
from evals.agents.persona_eval import PersonaEval
from evals.agents.business_case_eval import BusinessCaseEval
from evals.agents.gtm_strategy_eval import GTMStrategyEval
from evals.agents.financial_model_eval import FinancialModelEval
from evals.agents.prd_eval import PRDEval
from evals.agents.technical_architecture_eval import TechnicalArchitectureEval
from evals.agents.legal_regulatory_eval import LegalRegulatoryEval
from evals.agents.risk_assessment_eval import RiskAssessmentEval
from evals.agents.executive_summary_eval import ExecutiveSummaryEval
from evals.agents.stakeholder_views_eval import StakeholderViewsEval
from evals.agents.validation_playbook_eval import ValidationPlaybookEval
from evals.agents.wireframes_eval import WireframesEval
from evals.agents.prototype_eval import PrototypeEval
from evals.agents.planner_eval import PlannerEval

__all__ = [
    "CustomerResearchEval",
    "CompetitiveAnalysisEval",
    "PersonaEval",
    "BusinessCaseEval",
    "GTMStrategyEval",
    "FinancialModelEval",
    "PRDEval",
    "TechnicalArchitectureEval",
    "LegalRegulatoryEval",
    "RiskAssessmentEval",
    "ExecutiveSummaryEval",
    "StakeholderViewsEval",
    "ValidationPlaybookEval",
    "WireframesEval",
    "PrototypeEval",
    "PlannerEval",
]
