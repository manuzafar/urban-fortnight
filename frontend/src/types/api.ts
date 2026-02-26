/**
 * API Types for Product Discovery Multi-Agent System
 */

// Session status enum
export type SessionStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

// Priority levels
export type Priority = 'critical' | 'high' | 'medium' | 'low';

// T-shirt sizing
export type StorySize = 'XS' | 'S' | 'M' | 'L' | 'XL';

// Risk levels
export type RiskLevel = 'high' | 'medium' | 'low';

// ═══════════════════════════════════════════════════════════════════════════════
// Session List Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface SessionSummary {
  id: string;
  status: SessionStatus;
  product_idea: string;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface SessionListResponse {
  count: number;
  sessions: SessionSummary[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// API Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface DiscoveryRequest {
  product_idea: string;
  industry?: string;
  target_market?: string;
  constraints?: string[];
  additional_context?: string;
}

export interface DiscoveryResponse {
  session_id: string;
  status: SessionStatus;
  message: string;
  created_at: string;
}

export interface SessionStatusResponse {
  session_id: string;
  status: SessionStatus;
  current_agent: string | null;
  iteration: number;
  progress_percentage: number;
  inception_pack: InceptionPack | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Inception Pack Types
// ═══════════════════════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════════════════════
// V4 Discovery Journey Types
// ═══════════════════════════════════════════════════════════════════════════════

export interface DiscoveryJourney {
  // Problem Love Stage
  problem_love: {
    problem_statement: string;
    problem_score?: number | null;
    evidence_quality?: string;
  };
  // Customer Truth Stage
  customer_truth: {
    interview_count: number;
    key_quotes: string[];
    pain_patterns: Array<{ description?: string; severity?: string; frequency?: string } | string>;
    trigger_patterns: string[];
    outcome_patterns: string[];
  };
  // Opportunity Mapping Stage
  opportunity_mapping: {
    four_forces: {
      push_factors?: string[];
      pull_factors?: string[];
      anxiety_factors?: string[];
      habit_factors?: string[];
    };
    opportunity_tree?: Record<string, unknown>;
    primary_opportunity?: string;
  };
  // Solution Design Stage
  solution_design: {
    solution_concept?: string;
    dhm_score?: {
      delight?: number | string;
      hard_to_copy?: number | string;
      margin?: number | string;
    };
    pre_mortem?: {
      failure_scenarios?: string[];
      mitigations?: string[];
    };
  };
  // Validation Plan Stage
  validation_plan: {
    experiments: Array<{
      name?: string;
      hypothesis?: string;
      method?: string;
      success_criteria?: string;
      effort_level?: string;
    }>;
  };
  // Metadata
  mode: 'quick' | 'guided' | 'deep' | 'unknown';
  high_confidence: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// V3.0 New Section Types
// ═══════════════════════════════════════════════════════════════════════════════

// Go-To-Market Strategy
export interface LaunchPhase {
  phase_name: string;
  duration: string;
  objectives: string[];
  key_activities: string[];
  success_metrics: string[];
}

export interface ChannelStrategy {
  channel: string;
  purpose: string;
  tactics: string[];
  budget_allocation: string;
  expected_roi: string;
}

export interface GoToMarket {
  positioning_statement: string;
  target_segments: string[];
  launch_phases: LaunchPhase[];
  channel_strategy: ChannelStrategy[];
  messaging_framework: {
    headline: string;
    subheadline: string;
    key_benefits: string[];
    proof_points: string[];
  };
  pricing_strategy: string;
  partnership_approach: string;
}

// Financial Model
export interface FinancialProjection {
  period: string;
  revenue: number;
  costs: number;
  profit: number;
  cumulative_profit: number;
}

export interface UnitEconomics {
  metric: string;
  value: string;
  benchmark: string;
  assessment: string;
}

export interface FinancialModel {
  summary: string;
  projections: FinancialProjection[];
  unit_economics: UnitEconomics[];
  assumptions: string[];
  sensitivity_analysis: {
    optimistic: string;
    base_case: string;
    pessimistic: string;
  };
  funding_requirements: string;
  break_even_analysis: string;
}

// Stakeholder Views
export interface StakeholderView {
  stakeholder_role: string;
  tailored_summary: string;
  key_questions_answered?: string[];
  key_question_answered?: string;
  anticipated_objections: Array<{
    objection: string;
    response: string;
    supporting_claim_ids: string[];
  }>;
  evidence_confidence: string;
  key_metrics?: string[];
  key_metrics_for_role?: string[];
  decision_criteria?: string[];
  decision_recommendation?: string;
}

export interface StakeholderViews {
  views: StakeholderView[];
  common_concerns: string[];
  cross_stakeholder_alignment: string;
}

// Validation Playbook
export interface ValidationExperiment {
  experiment_id: string;
  hypothesis_claim_id: string;
  experiment_name: string;
  target_profile: string;
  specific_instructions: string;
  success_criteria: string;
  failure_criteria: string;
  upgrade_path: string[];
  effort_level: 'quick' | 'moderate' | 'significant';
  priority: 'critical' | 'high' | 'medium' | 'low';
  sample_size?: string;
  timeline?: string;
}

export interface ValidationPlaybook {
  experiments?: ValidationExperiment[];
  validation_experiments?: ValidationExperiment[]; // Alternative field name from backend
  prioritization_rationale?: string;
  quick_wins?: string[];
  critical_path?: string[];
}

// Wireframes
export interface WireframeScreen {
  screen_id: string;
  screen_name: string;
  purpose: string;
  user_stories_covered: string[];
  key_components: string[];
  navigation_to: string[];
  react_code: string;
}

export interface Wireframes {
  screens: WireframeScreen[];
  user_flows: Array<{
    flow_name: string;
    description: string;
    screens: string[];
  }>;
  user_flow_description?: string;
  user_flow_mermaid?: string;
  design_system_notes: string[];
}

// Prototype
export interface Prototype {
  prototype_name?: string;
  primary_persona?: string;
  key_user_story?: string;
  react_component_code?: string;
  react_code?: string; // Alternative field name from backend
  css_code?: string;
  color_palette?: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
  };
  interactivity_notes?: string[];
  demo_scenario?: string;
}

// Competitive Analysis
export interface CompetitorDetail {
  name: string;
  description?: string;
  strengths?: string[];
  weaknesses?: string[];
  market_share?: string;
  pricing?: string;
  threat_level?: 'high' | 'medium' | 'low';
  differentiation_opportunity?: string;
}

export interface CompetitiveAnalysis {
  summary?: string;
  // Frontend format
  competitors?: CompetitorDetail[];
  // Backend format (V3.0)
  direct_competitors?: CompetitorDetail[];
  indirect_competitors?: CompetitorDetail[];
  potential_future_competitors?: CompetitorDetail[];
  positioning_map?: {
    x_axis: string;
    y_axis: string;
    our_position: { x: number; y: number };
    competitor_positions: Array<{ name: string; x: number; y: number }>;
  };
  competitive_moat?: string[];
  competitive_moats?: string[];
  market_gaps?: string[];
  market_dynamics?: string;
  strategic_recommendations?: string[];
}

// Detailed Personas
export interface DetailedPersona {
  persona_id: string;
  name: string;
  role: string;
  demographics: {
    age_range: string;
    location: string;
    income_level: string;
    education: string;
  };
  jobs_to_be_done: Array<{
    job: string;
    importance: 'critical' | 'high' | 'medium' | 'low';
    current_solution: string;
  }>;
  pain_points: string[];
  goals: string[];
  behaviors: string[];
  quote: string;
  day_in_life: string;
  decision_factors: string[];
  channels: string[];
}

export interface DetailedPersonas {
  personas: DetailedPersona[];
  key_insights: string[];
  prioritization: string;
}

// Risk Assessment
export interface RiskItem {
  risk_id: string;
  category: string;
  description: string;
  likelihood: 'high' | 'medium' | 'low';
  impact: 'high' | 'medium' | 'low';
  risk_score: number;
  mitigation_strategy: string;
  contingency_plan: string;
  owner: string;
  status: 'identified' | 'mitigating' | 'accepted' | 'resolved';
}

// Risk item from backend's risk_matrix array
export interface RiskMatrixItem {
  id?: string;
  name?: string;
  description?: string;
  category?: string;
  likelihood?: number;
  impact?: number;
  risk_score?: number;
  triggers?: string[];
  early_warning_signs?: string[];
  mitigation_strategy?: string;
  contingency_plan?: string;
  owner?: string;
  review_frequency?: string;
}

export interface RiskSummary {
  total_risks?: number;
  critical_risks?: number;
  high_risks?: number;
  medium_risks?: number;
  low_risks?: number;
  overall_risk_level?: 'low' | 'medium' | 'high' | 'critical';
}

export interface TopRiskItem {
  risk_id?: string;
  name?: string;
  why_critical?: string;
  immediate_action?: string;
}

export interface RiskAssessment {
  summary?: string;
  risks?: RiskItem[];
  // Backend uses risk_matrix as array of risk objects
  risk_matrix?: RiskMatrixItem[];
  risk_summary?: RiskSummary;
  top_risks?: string[];
  top_3_risks?: TopRiskItem[];
  overall_risk_level?: 'high' | 'medium' | 'low' | 'critical';
  risk_appetite_recommendation?: {
    risk_tolerance_level?: string;
    rationale?: string;
    go_no_go_recommendation?: string;
    conditions_for_go?: string[];
  };
  monitoring_plan?: {
    key_risk_indicators?: Array<{
      indicator?: string;
      threshold?: string;
      action_if_exceeded?: string;
    }>;
    review_cadence?: string;
    escalation_process?: string;
  };
}

// Cross-Reference Index
export interface CrossReferenceClaim {
  claim_id: string;
  claim_text: string;
  evidence_tier: EvidenceTier;
  source_section: string;
  supporting_data: string[];
  confidence_score: number;
  validation_status: 'validated' | 'pending' | 'disputed';
}

export interface CrossReferenceIndex {
  claims: CrossReferenceClaim[];
  evidence_score: number;
  validation_summary: string;
  key_validated_claims: string[];
  claims_needing_validation: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Inception Pack (Updated for V3.0)
// ═══════════════════════════════════════════════════════════════════════════════

export interface InceptionPack {
  // V4 Discovery Journey (optional - only present for V4 sessions)
  discovery_journey?: DiscoveryJourney | null;

  // Core sections (existing)
  executive_summary: ExecutiveSummary;
  customer_research: CustomerResearch;
  business_case: BusinessCase;
  product_requirements_document: ProductRequirementsDocument | null;
  technical_architecture: TechnicalArchitecture;
  legal_regulatory_review: LegalRegulatoryReview;
  quality_assessment: QualityAssessment;

  // V3.0 additions (optional for backward compatibility)
  competitive_analysis?: CompetitiveAnalysis | null;
  detailed_personas?: DetailedPersonas | null;
  gtm_strategy?: GoToMarket | null;
  financial_model?: FinancialModel | null;
  risk_assessment?: RiskAssessment | null;
  wireframes?: Wireframes | null;
  prototype?: Prototype | null;
  stakeholder_views?: StakeholderViews | null;
  validation_playbook?: ValidationPlaybook | null;
  cross_reference_index?: CrossReferenceIndex | null;

  metadata: InceptionPackMetadata;
}

export interface InceptionPackMetadata {
  session_id: string;
  generated_at: string;
  version: string;
  generator: string;
  iterations: number;
  total_tokens_used: number;
  total_duration_seconds: number;
  quality_score: number | null;
  quality_passed: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Executive Summary
// ═══════════════════════════════════════════════════════════════════════════════

export interface ExecutiveSummary {
  // Product Identity
  product_name: string;
  tagline: string;

  // Problem & Solution
  problem_statement: string;
  solution_overview: string;
  value_proposition: string;

  // Target Market
  target_users: string[];
  target_market_size: string;

  // Competitive Position
  key_differentiators: string[];
  competitive_landscape: string;

  // Financial Summary
  funding_required: string;
  revenue_model: string;
  financial_projections: string;
  break_even_timeline: string;
  expected_roi: string;

  // Risk & Compliance
  top_risks: string[];
  regulatory_summary: string;

  // Go-to-Market
  gtm_strategy: string;
  key_milestones: string[];

  // Success Metrics
  success_metrics: string[];

  // Recommendation
  recommendation: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Customer Research (Evidence-Based Reality Investigation)
// ═══════════════════════════════════════════════════════════════════════════════

// Evidence tiers for research insights
export type EvidenceTier = 'E1' | 'E2' | 'E3' | 'E4';

export interface ResearchScope {
  segments_examined: string[];
  observation_context: string;
  known_gaps: string[];
  confidence_level: 'high' | 'medium' | 'low';
}

export interface JobToBeDone {
  trigger_situation: string;
  underlying_goal: string;
  success_definition: string;
}

export interface CurrentBehaviour {
  existing_solutions: string[];
  tools_and_workarounds: string[];
  friction_points: string[];
  why_problem_persists: string;
}

export interface PainSignal {
  description: string;
  evidence_tier: EvidenceTier;
  evidence_detail: string;
  impact: string;
  severity: Priority;
  challenges_solution: boolean;
}

export interface UncomfortableInsight {
  insight: string;
  evidence_tier: EvidenceTier;
  implication: string;
}

export interface CustomerIndifference {
  assumed_need: string;
  reality: string;
  evidence_tier: EvidenceTier;
}

export interface OpenQuestion {
  question: string;
  why_it_matters: string;
  validation_needed: string;
}

export interface CompetitorReality {
  name: string;
  how_they_solve_it: string;
  why_they_havent_won: string;
  switching_barriers: string;
}

export interface CompetitiveLandscape {
  competitors: CompetitorReality[];
  market_position: string;
}

export interface MarketTrend {
  trend: string;
  helps_or_hurts: 'helps' | 'hurts' | 'neutral';
  evidence_tier: EvidenceTier;
}

export interface MarketContext {
  total_addressable_market: string;
  serviceable_addressable_market: string;
  serviceable_obtainable_market: string;
  uncertainty_factors: string[];
  market_trends: MarketTrend[];
}

export interface ResearchQualityCheck {
  could_kill_idea: boolean;
  skeptic_would_trust: boolean;
  assumptions_separated: boolean;
  self_critique: string;
}

export interface CustomerResearch {
  // New evidence-based format
  research_scope?: ResearchScope;
  job_to_be_done?: JobToBeDone;
  current_behaviour?: CurrentBehaviour;
  pain_signals?: PainSignal[];
  uncomfortable_insights?: UncomfortableInsight[];
  what_customers_dont_care_about?: CustomerIndifference[];
  open_questions?: OpenQuestion[];
  competitive_landscape?: CompetitiveLandscape;
  market_context?: MarketContext;
  research_quality_check?: ResearchQualityCheck;
  validation_reminder?: string;

  // Legacy format (backward compatibility)
  user_personas?: UserPersona[];
  pain_points?: PainPoint[];
  market_segments?: MarketSegment[];
  total_addressable_market?: string;
  serviceable_addressable_market?: string;
  serviceable_obtainable_market?: string;
  competitors?: Competitor[];
  market_trends?: string[];
  validation_assumptions?: string[];
}

// Legacy types for backward compatibility
export interface UserPersona {
  name: string;
  role: string;
  demographics: string;
  goals: string[];
  frustrations: string[];
  behaviors: string[];
  tech_savviness: string;
  quote: string;
}

export interface PainPoint {
  description: string;
  severity: Priority;
  current_workaround: string | null;
}

export interface MarketSegment {
  name: string;
  size_estimate: string;
  characteristics: string[];
  willingness_to_pay: string;
}

export interface Competitor {
  name: string;
  strengths: string[];
  weaknesses: string[];
  market_position: string;
  pricing_model: string | null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Business Case
// ═══════════════════════════════════════════════════════════════════════════════

export interface LeanCanvas {
  problem: string[];
  solution: string[];
  unique_value_proposition: string;
  unfair_advantage: string;
  customer_segments: string[];
  key_metrics: string[];
  channels: string[];
  cost_structure: string[];
  revenue_streams: string[];
}

export interface RevenueStream {
  name: string;
  description: string;
  pricing_model: string;
  estimated_contribution: string;
}

export interface CostStructure {
  category: string;
  description: string;
  estimated_amount: string;
  frequency: string;
}

export interface BusinessCase {
  lean_canvas: LeanCanvas;
  revenue_streams: RevenueStream[];
  cost_structure: CostStructure[];
  break_even_analysis: string;
  year_1_projection: string;
  year_3_projection: string;
  funding_requirement: string;
  roi_analysis: string;
  go_to_market_strategy: string;
  key_partnerships: string[];
  risks_and_mitigations: Array<{ risk: string; mitigation: string }>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Product Requirements Document
// ═══════════════════════════════════════════════════════════════════════════════

export interface AcceptanceCriteria {
  given: string;
  when: string;
  then: string;
}

export interface UserStory {
  id: string;
  epic_id?: string;
  title: string;
  description: string;
  // New format fields
  acceptance_criteria: string[] | AcceptanceCriteria[];
  priority: Priority;
  story_points?: number;
  // Old format fields (optional for backwards compatibility)
  as_a?: string;
  i_want?: string;
  so_that?: string;
  size?: StorySize;
  dependencies?: string[];
  notes?: string | null;
}

export interface Epic {
  id: string;
  title: string;
  description: string;
  priority?: Priority;
  business_value?: string;
  stories: UserStory[];
}

export interface FunctionalRequirement {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  rationale: string;
  acceptance_criteria: string[];
}

export interface NonFunctionalRequirement {
  id: string;
  category: string;
  title: string;
  description: string;
  metric: string;
  target: string;
  priority: Priority;
}

export interface DataEntity {
  name: string;
  description: string;
  attributes: Array<{ name: string; type: string; description: string }>;
  relationships: string[];
}

export interface DataModel {
  entities: DataEntity[];
  description: string;
}

export interface ReleasePhase {
  phase: string;
  description: string;
  features: string[];
  success_criteria: string[];
}

export interface Risk {
  id: string;
  description: string;
  likelihood: RiskLevel;
  impact: RiskLevel;
  mitigation: string;
}

export interface ProductOverview {
  name: string;
  vision: string;
  problem_statement?: string;
  objectives: string[];
  success_metrics?: string[];
}

export interface PRDScope {
  in_scope: string[];
  out_of_scope: string[];
  assumptions?: string[];
}

export interface PRDStatistics {
  total_epics: number;
  total_stories: number;
  total_story_points: number;
  total_functional_requirements: number;
  total_non_functional_requirements: number;
  priority_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

export interface ProductRequirementsDocument {
  version?: string;
  formatted_at?: string;
  quality_score?: number;
  iterations_required?: number;
  // New format
  product_overview?: ProductOverview;
  scope?: PRDScope;
  statistics?: PRDStatistics;
  // Old format (backwards compatibility)
  last_updated?: string;
  overview?: string;
  objectives?: string[];
  scope_in?: string[];
  scope_out?: string[];
  user_personas?: string[];
  // Common fields
  epics: Epic[];
  functional_requirements: FunctionalRequirement[];
  non_functional_requirements: NonFunctionalRequirement[];
  data_model?: DataModel;
  integration_requirements?: string[] | Array<{ name: string; description: string; type: string }>;
  constraints?: string[];
  assumptions?: string[];
  release_plan?: ReleasePhase[] | { phases: Array<{ name: string; description: string; features: string[]; success_criteria: string[] }> };
  risks?: Risk[];
  risks_and_mitigations?: Risk[];
  open_questions?: string[];
  glossary?: Record<string, string>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Technical Architecture
// ═══════════════════════════════════════════════════════════════════════════════

export interface TechnologyChoice {
  category: string;
  technology: string;
  rationale: string;
  alternatives_considered: string[];
}

export interface SystemComponent {
  name: string;
  description: string;
  responsibilities: string[];
  technologies: string[];
  interfaces: string[];
}

export interface IntegrationPoint {
  name: string;
  type: string;
  description: string;
  authentication: string;
  data_flow: string;
}

export interface TechnicalArchitecture {
  architecture_style: string;
  architecture_diagram_description: string;
  architecture_diagram_mermaid?: string;
  sequence_diagram_mermaid?: string;
  technology_stack: TechnologyChoice[];
  system_components: SystemComponent[];
  integration_points: IntegrationPoint[];
  data_storage: string;
  security_architecture: string;
  scalability_approach: string;
  deployment_strategy: string;
  infrastructure_requirements: string[];
  development_approach: string;
  technical_risks: Array<{ risk: string; mitigation: string }>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Legal & Regulatory Review
// ═══════════════════════════════════════════════════════════════════════════════

export interface Regulation {
  name: string;
  description: string;
  applicability: string;
  compliance_requirements: string[];
  impact_level: RiskLevel;
  estimated_compliance_timeline: string;
  estimated_compliance_cost: string;
}

export interface LicenseRequirement {
  license_type: string;
  issuing_authority: string;
  requirements: string[];
  timeline: string;
  cost: string;
  renewal_requirements: string;
}

export interface DataProtectionRequirement {
  regulation: string;
  data_types_covered: string[];
  key_obligations: string[];
  user_rights: string[];
  penalties_for_non_compliance: string;
  implementation_requirements: string[];
}

export interface LegalRisk {
  risk_category: string;
  description: string;
  severity: RiskLevel;
  likelihood: string;
  mitigation_strategies: string[];
  legal_counsel_recommended: boolean;
}

export interface IntellectualPropertyConsideration {
  ip_type: string;
  description: string;
  action_required: string;
  priority: Priority;
  estimated_cost: string;
}

export interface OverallRiskAssessment {
  risk_level: RiskLevel;
  key_concerns: string[];
  blocking_issues: string[];
  recommended_timeline_buffer: string;
  recommended_budget_allocation: string;
}

export interface LegalRegulatoryReview {
  executive_summary: string;
  applicable_regulations: Regulation[];
  licensing_requirements: LicenseRequirement[];
  data_protection_requirements: DataProtectionRequirement[];
  legal_risks: LegalRisk[];
  intellectual_property: IntellectualPropertyConsideration[];
  industry_specific_considerations: string[];
  international_considerations: string[];
  recommended_legal_structure: string;
  ongoing_compliance_requirements: string[];
  overall_risk_assessment: OverallRiskAssessment;
  next_steps: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Quality Assessment
// ═══════════════════════════════════════════════════════════════════════════════

export interface SectionScore {
  section: string;
  score: number;
  feedback: string;
  suggestions: string[];
}

export interface QualityAssessment {
  overall_score: number;
  passed: boolean;
  iteration: number;
  section_scores: SectionScore[];
  strengths: string[];
  weaknesses: string[];
  critical_gaps: string[];
  recommendations: string[];
  ready_for_delivery: boolean;
}
