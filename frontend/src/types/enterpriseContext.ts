/**
 * Enterprise Context Types for Seedcraft
 *
 * These types define the data structures for organizational context
 * that guides AI agents with soft constraints.
 */

// ═══════════════════════════════════════════════════════════════════════════════
// ENUMS
// ═══════════════════════════════════════════════════════════════════════════════

export type ContextType = 'company' | 'division' | 'team';
export type ContextScope = 'private' | 'shared' | 'organization';
export type ValidationStatus = 'pending' | 'valid' | 'invalid';

// ═══════════════════════════════════════════════════════════════════════════════
// CONTEXT LIST & SUMMARY TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface EnterpriseContextListItem {
  id: string;
  name: string;
  context_type: ContextType;
  parent_id: string | null;
  validation_status: ValidationStatus;
  scope: ContextScope;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface EnterpriseContextListResponse {
  contexts: EnterpriseContextListItem[];
  count: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// FULL CONTEXT TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface EnterpriseContext {
  id: string;
  user_id: string;
  name: string;
  context_type: ContextType;
  parent_id: string | null;
  raw_content: string;
  parsed_content: ParsedEnterpriseContext;
  validation_status: ValidationStatus;
  validation_errors: string[];
  scope: ContextScope;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// PARSED CONTENT STRUCTURE (matches enterprise-context-spec)
// ═══════════════════════════════════════════════════════════════════════════════

export interface StrategyContext {
  time_horizon?: string;
  strategic_priorities?: string[];
  strategic_constraints?: string[];
  innovation_stance?: string;
  investment_thesis?: string;
}

export interface TechnologyContext {
  cloud?: string;
  primary_languages?: string[];
  databases?: string[];
  infrastructure?: string[];
  technical_constraints?: string[];
  approved_vendors?: string[];
  deprecated_technologies?: string[];
}

export interface RegulatoryContext {
  frameworks?: string[];
  jurisdictions?: string[];
  data_residency?: string;
  audit_requirements?: string[];
}

export interface OrganizationContext {
  delivery_model?: string;
  decision_authority?: string;
  budget_cycle?: string;
  approval_process?: string;
}

export interface RiskManagementContext {
  risk_appetite?: string;
  risk_categories?: string[];
  mitigation_requirements?: string[];
}

export interface ParsedEnterpriseContext {
  schema?: string;
  company?: string;
  division?: string;
  team?: string;
  industry?: string;

  strategy?: StrategyContext;
  technology?: TechnologyContext;
  regulatory?: RegulatoryContext;
  organization?: OrganizationContext;
  risk_management?: RiskManagementContext;

  // Merged context tracking
  _sources?: string[];

  // Allow additional fields
  [key: string]: unknown;
}

// ═══════════════════════════════════════════════════════════════════════════════
// REQUEST/RESPONSE TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface EnterpriseContextCreate {
  name: string;
  context_type: ContextType;
  raw_content: string;
  parent_id?: string;
  scope?: ContextScope;
  is_default?: boolean;
}

export interface EnterpriseContextUpdate {
  name?: string;
  raw_content?: string;
  parent_id?: string;
  scope?: ContextScope;
  is_default?: boolean;
}

export interface ContextUploadResponse {
  id: string;
  name: string;
  context_type: ContextType;
  validation_status: ValidationStatus;
  validation_errors: string[];
  parsed_content: ParsedEnterpriseContext;
}

export interface MergedContextPreview {
  merged_context: ParsedEnterpriseContext;
  sources: string[];
  constraints_preview: EnterpriseConstraint[];
}

export interface SessionContextAttach {
  context_ids: string[];
}

export interface SessionContextResponse {
  session_id: string;
  contexts: EnterpriseContextListItem[];
  merged_context: ParsedEnterpriseContext;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTRAINT TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface EnterpriseConstraint {
  field: string;
  value: unknown;
  source_section: string;
  source_claim_id: string;
  constraint_type: 'must_use' | 'must_align' | 'guidance' | 'must_not_use';
  evidence_tier: string;
  confidence: number;
  is_negotiable: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UI STATE TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface ContextSelectionState {
  company?: EnterpriseContextListItem;
  division?: EnterpriseContextListItem;
  team?: EnterpriseContextListItem;
}

export interface ContextLibraryState {
  contexts: EnterpriseContextListItem[];
  loading: boolean;
  error: string | null;
  selectedForSession: ContextSelectionState;
}
