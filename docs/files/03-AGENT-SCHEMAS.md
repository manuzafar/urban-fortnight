# Phase 3: Revamp All Agent Schemas

**Goal:** Replace every Pydantic model with richer structures required by the new prompts.

**Why before prompts:** Schemas define the contract. Prompts demand output matching these schemas. Agents validate against them. Get the schemas right first.

**Dependencies:** Phases 1-2

---

## 3.1 Market Intelligence (replaces CustomerResearch)

**File:** `backend/models/schemas.py` (MODIFY — replace existing customer research schemas)

```python
# ═══════════════════════════════════════════════════════════
# MARKET INTELLIGENCE (Section 1)
# ═══════════════════════════════════════════════════════════

class MarketSize(BaseModel):
    tam: str = Field(description="Total addressable market with number")
    tam_evidence_tier: str
    tam_source: Optional[str] = None
    tam_methodology: str = Field(description="Step-by-step derivation")
    sam: str
    sam_evidence_tier: str
    sam_methodology: str = Field(description="Filters that narrow TAM → SAM")
    som: str
    som_evidence_tier: str
    som_methodology: str = Field(description="Penetration assumptions")

class PainSignal(BaseModel):
    pain: str
    severity: str = Field(description="critical|high|moderate|low")
    frequency: str = Field(description="daily|weekly|monthly|quarterly|annual")
    who_feels_it: str = Field(description="Specific role/persona")
    current_workaround: str
    workaround_cost: str
    evidence_tier: str
    evidence_source: Optional[str] = None

class DemandIndicator(BaseModel):
    signal: str
    signal_type: str = Field(description="search_volume|funding_activity|competitor_traction|customer_statement|regulatory_driver|job_posting_trend")
    strength: str = Field(description="strong|moderate|weak")
    detail: str
    evidence_tier: str
    evidence_source: Optional[str] = None

class WhyNowFactor(BaseModel):
    factor: str
    category: str = Field(description="technology|regulation|market_shift|behaviour_change|cost_change")
    explanation: str = Field(description="Why NOW, not 3 years ago or 2 years from now")
    evidence_tier: str
    evidence_source: Optional[str] = None

class MarketDriver(BaseModel):
    driver: str
    explanation: str
    evidence_tier: str
    evidence_source: Optional[str] = None

class MarketIntelligence(BaseModel):
    market_definition: str
    market_size: MarketSize
    market_growth_rate: str
    market_growth_evidence_tier: str
    market_growth_source: Optional[str] = None
    market_drivers: list[MarketDriver]
    market_headwinds: list[MarketDriver]
    inflection_points: list[str]
    pain_signals: list[PainSignal]
    demand_indicators: list[DemandIndicator]
    why_now: list[WhyNowFactor]
    adoption_barriers: list[str]
    adoption_accelerators: list[str]
```

---

## 3.2 Competitive Landscape

```python
# ═══════════════════════════════════════════════════════════
# COMPETITIVE LANDSCAPE (Section 2)
# ═══════════════════════════════════════════════════════════

class CompetitorPricing(BaseModel):
    tiers: str = Field(description="Specific tiers with prices")
    evidence_tier: str
    source: Optional[str] = None

class CompetitorProfile(BaseModel):
    name: str
    website: Optional[str] = None
    one_liner: str
    founded: Optional[str] = None
    funding: Optional[str] = None
    funding_evidence_tier: Optional[str] = None
    funding_source: Optional[str] = None
    target_customer: str
    pricing: CompetitorPricing
    key_features: list[str]
    strengths: list[str]
    weaknesses: list[str]
    key_differentiator: str
    threat_level: str = Field(description="existential|significant|moderate|low")
    threat_rationale: str

class PotentialEntrant(BaseModel):
    name: str
    current_business: str
    entry_likelihood: str = Field(description="high|moderate|low")
    entry_rationale: str
    competitive_advantage_if_enters: str
    evidence_tier: str

class PositionMapEntry(BaseModel):
    name: str
    x_score: float
    y_score: float
    is_target_product: bool = False
    rationale: str

class PositioningMap(BaseModel):
    x_axis: str = Field(description="Meaningful axis — NOT generic 'features'")
    y_axis: str = Field(description="Meaningful axis — NOT generic 'price'")
    positions: list[PositionMapEntry]
    white_space: str

class CompetitiveGap(BaseModel):
    gap: str
    why_unserved: str
    our_advantage: str
    gap_size: str
    evidence_tier: str

class MoatAnalysis(BaseModel):
    defensible: list[str]
    not_defensible: list[str]
    moat_building_strategy: str

class CompetitiveLandscape(BaseModel):
    direct_competitors: list[CompetitorProfile]
    indirect_competitors: list[CompetitorProfile]
    potential_entrants: list[PotentialEntrant]
    positioning_map: PositioningMap
    competitive_gaps: list[CompetitiveGap]
    differentiation_thesis: str
    moat_analysis: MoatAnalysis
```

---

## 3.3 Customer Personas

```python
# ═══════════════════════════════════════════════════════════
# CUSTOMER PERSONAS (Section 3)
# ═══════════════════════════════════════════════════════════

class JobToBeDone(BaseModel):
    situation: str = Field(description="When [trigger]...")
    motivation: str = Field(description="I want to [action]...")
    outcome: str = Field(description="So that I can [result]...")
    frequency: str
    current_time_spent: str
    pain_level: str = Field(description="critical|high|moderate|low")

class BuyingBehaviour(BaseModel):
    discovery_channels: list[str]
    evaluation_criteria: list[str] = Field(description="Ranked by importance")
    evaluation_process: str
    decision_authority: str = Field(description="sole_decision_maker|influencer|recommender|budget_approver")
    procurement_blockers: list[str]
    typical_procurement_timeline: str

class InternalPolitics(BaseModel):
    champions_what: str
    resists_what: str
    allies: list[str]
    blockers: list[str]
    political_currency: str

class ProductRelationship(BaseModel):
    current_tools: list[str]
    satisfaction_with_current: str
    switching_triggers: list[str]
    adoption_risk: str
    success_moment: str

class PersonaContext(BaseModel):
    organisation_type: str
    team_size: str
    reporting_line: str
    tenure: str

class Persona(BaseModel):
    name: str
    role: str
    archetype: str
    context: PersonaContext
    goals: list[str]
    frustrations: list[str]
    jobs_to_be_done: list[JobToBeDone]
    buying_behaviour: BuyingBehaviour
    internal_politics: InternalPolitics
    product_relationship: ProductRelationship
    evidence_tier: str
    evidence_note: Optional[str] = None

class PersonaPrioritisation(BaseModel):
    primary_buyer: str
    primary_user: str
    primary_champion: str
    note: str

class CustomerPersonas(BaseModel):
    personas: list[Persona]
    persona_prioritisation: PersonaPrioritisation
```

---

## 3.4 Business Case

```python
# ═══════════════════════════════════════════════════════════
# BUSINESS CASE (Section 4)
# ═══════════════════════════════════════════════════════════

class ProblemCost(BaseModel):
    description: str
    annual_cost_per_customer: str
    cost_components: list[str]
    total_market_cost: str
    evidence_tier: str
    source: Optional[str] = None

class SolutionValue(BaseModel):
    description: str
    time_saved: str
    cost_saved: str
    revenue_generated: Optional[str] = None
    value_to_cost_ratio: str
    evidence_tier: str

class PricingTier(BaseModel):
    tier_name: str
    price: str
    target_customer: str
    key_features: list[str]
    pricing_rationale: str

class RevenueModel(BaseModel):
    model_type: str
    rationale: str
    pricing_tiers: list[PricingTier]
    pricing_evidence_tier: str
    pricing_source: Optional[str] = None

class UnitEconomicComponent(BaseModel):
    value: str
    derivation: str
    assumptions: list[str] = Field(default_factory=list)
    evidence_tier: str

class UnitEconomics(BaseModel):
    cac: UnitEconomicComponent
    arpu: UnitEconomicComponent
    ltv: UnitEconomicComponent
    ltv_cac_ratio: str
    payback_period: str
    gross_margin: str

class BeachheadMarket(BaseModel):
    segment: str
    why_this_segment: str
    segment_size: str
    win_conditions: str

class ExpansionStage(BaseModel):
    stage: str
    segment: str
    timing: str
    prerequisite: str

class ScenarioCase(BaseModel):
    assumptions: list[str] = Field(default_factory=list)
    assumptions_changed: list[str] = Field(default_factory=list)
    revenue_year_1: str
    revenue_year_3: str
    break_even: Optional[str] = None

class SensitivityAnalysis(BaseModel):
    base_case: ScenarioCase
    optimistic_case: ScenarioCase
    pessimistic_case: ScenarioCase
    kill_conditions: str

class LeanCanvas(BaseModel):
    problem: list[str]
    customer_segments: list[str]
    unique_value_proposition: str
    solution: list[str]
    channels: list[str]
    revenue_streams: list[str]
    cost_structure: list[str]
    key_metrics: list[str]
    unfair_advantage: str

class BusinessCase(BaseModel):
    value_proposition: str
    problem_cost: ProblemCost
    solution_value: SolutionValue
    revenue_model: RevenueModel
    unit_economics: UnitEconomics
    beachhead_market: BeachheadMarket
    expansion_path: list[ExpansionStage]
    lean_canvas: LeanCanvas
    sensitivity_analysis: SensitivityAnalysis
```

---

## 3.5 Go-to-Market Strategy (NEW)

```python
# ═══════════════════════════════════════════════════════════
# GO-TO-MARKET STRATEGY (Section 5 — NEW)
# ═══════════════════════════════════════════════════════════

class PersonaMessaging(BaseModel):
    persona_name: str
    headline: str
    value_prop: str
    proof_point: str
    objection_preempt: str

class LaunchTactic(BaseModel):
    tactic: str
    channel: str
    budget: str
    expected_result: str
    measurement: str
    timeline: str
    evidence_tier: str

class LaunchPhase(BaseModel):
    phase_name: str
    objective: str
    tactics: list[LaunchTactic]
    total_phase_budget: str
    phase_success_criteria: str

class ChannelStrategy(BaseModel):
    channel: str
    why_this_channel: str
    expected_cac: str
    cac_derivation: str
    scale_ceiling: str
    evidence_tier: str

class MetricTarget(BaseModel):
    metric: str
    target_month_1: str
    target_month_3: str
    target_month_6: str
    measurement_tool: str

class GoToMarket(BaseModel):
    positioning_statement: str
    messaging_by_persona: list[PersonaMessaging]
    launch_phases: list[LaunchPhase]
    channel_strategy: list[ChannelStrategy]
    partnerships_and_distribution: Optional[dict] = None
    metrics_dashboard: list[MetricTarget]
```

---

## 3.6 Financial Model (NEW)

```python
# ═══════════════════════════════════════════════════════════
# FINANCIAL MODEL (Section 6 — NEW)
# ═══════════════════════════════════════════════════════════

class InputAssumption(BaseModel):
    assumption: str
    evidence_tier: str
    source: Optional[str] = None
    sensitivity: str = Field(description="high|medium|low")

class MonthlyProjection(BaseModel):
    month: int
    new_customers: int
    churned_customers: int
    total_customers: int
    mrr: float
    revenue: float
    cogs: float
    gross_profit: float
    marketing_spend: float
    total_opex: float
    net_income: float
    cash_balance: float
    key_drivers: str

class QuarterlyProjection(BaseModel):
    quarter: str
    total_customers: int
    arr: float
    revenue: float
    gross_margin_pct: float
    net_income: float
    cash_balance: float

class FinancialScenario(BaseModel):
    description: str
    key_assumptions: list[str] = Field(default_factory=list)
    assumptions_changed: list[str] = Field(default_factory=list)
    revenue_year_1: str
    revenue_year_3: str
    break_even_month: int
    total_funding_required: Optional[str] = None

class FixedCost(BaseModel):
    item: str
    cost: float
    notes: str

class VariableCost(BaseModel):
    item: str
    cost_per_customer_monthly: float
    notes: str

class CostStructure(BaseModel):
    fixed_costs_monthly: list[FixedCost]
    variable_costs_per_customer: list[VariableCost]
    scaling_thresholds: list[str]

class FundingRequirements(BaseModel):
    pre_revenue_burn: str
    runway_needed: str
    total_funding_required: str
    funding_strategy: str

class FinancialModel(BaseModel):
    input_assumptions: list[InputAssumption]
    revenue_model: dict
    monthly_projections_year_1: list[MonthlyProjection]
    quarterly_projections_year_2_3: list[QuarterlyProjection]
    key_metrics_over_time: dict
    scenario_analysis: dict
    cost_structure: CostStructure
    funding_requirements: FundingRequirements
```

---

## 3.7 Product Requirements (replaces existing PRD)

```python
# ═══════════════════════════════════════════════════════════
# PRODUCT REQUIREMENTS (Section 7)
# ═══════════════════════════════════════════════════════════

class UserStory(BaseModel):
    story_id: str = Field(description="US-1.1, US-1.2, etc.")
    persona: str = Field(description="Persona name — not 'user'")
    story: str
    acceptance_criteria: list[str]
    edge_cases: list[str]
    screen_references: list[str] = Field(description="S1, S2, etc.")
    priority: str = Field(description="must-have|should-have|nice-to-have")
    complexity_estimate: str
    evidence_tier: str

class Epic(BaseModel):
    epic_id: str = Field(description="E1, E2, etc.")
    title: str
    description: str
    priority: str
    persona: str
    user_stories: list[UserStory]

class NonFunctionalRequirement(BaseModel):
    category: str = Field(description="performance|security|scalability|accessibility|reliability|compliance")
    requirement: str
    rationale: str
    priority: str
    evidence_tier: str

class SuccessMetric(BaseModel):
    metric: str
    target: str
    measurement_method: str
    leading_indicator: str
    evidence_tier: str

class ScreenMapEntry(BaseModel):
    screen_id: str
    screen_name: str
    purpose: str
    primary_epic: str
    user_stories: list[str]

class Scope(BaseModel):
    in_scope: list[str]
    out_of_scope: list[str]
    mvp_definition: str

class ProductRequirements(BaseModel):
    product_name: str
    one_liner: str
    product_principles: list[str]
    scope: Scope
    epics: list[Epic]
    non_functional_requirements: list[NonFunctionalRequirement]
    success_metrics: list[SuccessMetric]
    screen_map: list[ScreenMapEntry]
```

---

## 3.8 Technical Architecture (replaces existing)

```python
# ═══════════════════════════════════════════════════════════
# TECHNICAL ARCHITECTURE (Section 8)
# ═══════════════════════════════════════════════════════════

class ArchitecturePattern(BaseModel):
    pattern: str
    rationale: str
    evidence_tier: str

class SystemComponent(BaseModel):
    name: str
    type: str
    description: str
    technology: str
    technology_rationale: str
    communicates_with: list[str]
    evidence_tier: str

class DataField(BaseModel):
    name: str
    type: str
    description: str
    constraints: list[str] = Field(default_factory=list)

class DataEntity(BaseModel):
    name: str
    description: str
    fields: list[DataField]
    estimated_volume_year_1: str
    growth_rate: str

class DataRelationship(BaseModel):
    from_entity: str
    to_entity: str
    relationship: str
    description: str

class DataModel(BaseModel):
    entities: list[DataEntity]
    relationships: list[DataRelationship]
    erd_mermaid: str

class APIEndpoint(BaseModel):
    method: str
    path: str
    description: str
    request_body: Optional[str] = None
    response_body: str
    auth_required: bool = True
    related_user_stories: list[str]

class APIDesign(BaseModel):
    style: str
    style_rationale: str
    authentication: str
    versioning: str
    endpoints: list[APIEndpoint]

class InfrastructureCost(BaseModel):
    at_100_users: str
    at_1000_users: str
    at_10000_users: str
    cost_driver: str

class Deployment(BaseModel):
    environment: str
    architecture: str
    deployment_diagram_mermaid: str
    scaling_strategy: str
    estimated_infrastructure_cost: InfrastructureCost

class TechStackLayer(BaseModel):
    framework: str
    rationale: str
    key_libraries: list[str] = Field(default_factory=list)

class TechStack(BaseModel):
    frontend: TechStackLayer
    backend: TechStackLayer
    database: dict
    infrastructure: dict

class TechnicalArchitecture(BaseModel):
    architecture_summary: str
    architecture_pattern: ArchitecturePattern
    system_components: list[SystemComponent]
    data_model: DataModel
    api_design: APIDesign
    system_diagram_mermaid: str
    deployment: Deployment
    tech_stack_recommendation: TechStack
    technical_risks: list[dict]
    technical_debt_strategy: str
```

---

## 3.9 Remaining Schemas

For these sections, read the OUTPUT FORMAT in each prompt library file and create matching Pydantic models:

| Schema Name | Prompt File | State Field |
|-------------|-------------|-------------|
| `RegulatoryCompliance` | `seedcraft-v3-prompts/09-regulatory-compliance.md` | `legal_regulatory_review` |
| `RiskAssessment` | `seedcraft-v3-prompts/10-risk-assessment.md` | `risk_assessment` |
| `StakeholderViewSet` | `seedcraft-v3-prompts/11-stakeholder-views.md` | `stakeholder_views` |
| `ValidationPlaybook` | `seedcraft-v3-prompts/12-validation-playbook.md` | `validation_playbook` |
| `NarrativeExecutiveSummary` | `seedcraft-v3-prompts/13-narrative-executive-summary.md` | `executive_summary` |
| `WireframeSet` | `seedcraft-v3-prompts/14-wireframe-agent.md` | `wireframes` |
| `WorkingPrototype` | `seedcraft-v3-prompts/15-prototype-agent.md` | `prototype` |

**Pattern:** Open the prompt file → find the `## OUTPUT FORMAT` section → create nested Pydantic models matching each JSON key. Follow the same style as schemas above.

---

## Test Phase 3

1. Import every new model and verify no Pydantic errors
2. Create a test instance of each top-level model with realistic sample data
3. Verify `model.model_dump()` produces valid JSON
4. Verify existing tests still pass (no broken imports from renamed schemas)
