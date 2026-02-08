/**
 * PackViewer Component
 *
 * Enhanced pack viewer with:
 * - Metrics hero banner at top
 * - Horizontal section tabs
 * - Evidence tier badges
 * - Modern card-based layout
 */

import { useState, useCallback } from 'react';
import {
  ArrowLeft,
  Download,
  FileText,
  FileJson,
  TrendingUp,
  Target,
  Clock,
  Award,
  ChevronDown,
  AlertTriangle,
} from 'lucide-react';
import { exportPdf, exportDocx } from '../api/client';
import type { InceptionPack, EvidenceTier } from '../types/api';
import { MermaidDiagram } from './MermaidDiagram';
import {
  CompetitivePositionChart,
  FinancialProjectionChart,
  RiskMatrixChart,
  LeanCanvasVisual,
} from './charts';
import { WireframeViewer } from './PackViewer/WireframeViewer';
import { PrototypeViewer } from './PackViewer/PrototypeViewer';
import { StakeholderViewSelector } from './PackViewer/StakeholderViewSelector';
import { ValidationPlaybook } from './PackViewer/ValidationPlaybook';
import './PackViewer.css';
import './charts/charts.css';

export interface PackViewerProps {
  pack: InceptionPack;
  sessionId: string;
  onBack: () => void;
}

// Section configuration (V3.0 - 16 tabs)
const SECTIONS = [
  { key: 'summary', label: 'Summary', category: 'Overview' },
  { key: 'research', label: 'Research', category: 'Discovery' },
  { key: 'competitive', label: 'Competitive', category: 'Discovery' },
  { key: 'personas', label: 'Personas', category: 'Discovery' },
  { key: 'business', label: 'Business', category: 'Strategy' },
  { key: 'gtm', label: 'Go-to-Market', category: 'Strategy' },
  { key: 'financial', label: 'Financial', category: 'Strategy' },
  { key: 'product', label: 'Product', category: 'Delivery' },
  { key: 'tech', label: 'Tech', category: 'Delivery' },
  { key: 'legal', label: 'Legal', category: 'Delivery' },
  { key: 'risks', label: 'Risks', category: 'Delivery' },
  { key: 'wireframes', label: 'Wireframes', category: 'Design' },
  { key: 'prototype', label: 'Prototype', category: 'Design' },
  { key: 'stakeholders', label: 'Stakeholders', category: 'Synthesis' },
  { key: 'validation', label: 'Validation', category: 'Synthesis' },
  { key: 'quality', label: 'QA', category: 'Quality' },
] as const;

type SectionKey = (typeof SECTIONS)[number]['key'];

// Helper to check if a section has content
function checkSectionHasContent(pack: InceptionPack, sectionKey: SectionKey): boolean {
  switch (sectionKey) {
    case 'summary':
      return !!pack.executive_summary;
    case 'research':
      return !!pack.customer_research;
    case 'competitive':
      // Backend may use direct_competitors or competitors
      return !!(pack.competitive_analysis?.competitors?.length || pack.competitive_analysis?.direct_competitors?.length);
    case 'personas':
      return !!(pack.detailed_personas?.personas?.length || pack.customer_research?.user_personas?.length);
    case 'business':
      return !!pack.business_case;
    case 'gtm':
      return !!pack.gtm_strategy;
    case 'financial':
      return !!pack.financial_model;
    case 'product':
      return !!pack.product_requirements_document;
    case 'tech':
      return !!pack.technical_architecture;
    case 'legal':
      return !!pack.legal_regulatory_review;
    case 'risks':
      // Backend uses risk_matrix, not risks
      return !!(pack.risk_assessment?.risk_matrix?.length || pack.risk_assessment?.risks?.length);
    case 'wireframes':
      return !!pack.wireframes?.screens?.length;
    case 'prototype':
      // Check for react_component_code or react_code
      return !!(pack.prototype?.react_component_code || pack.prototype?.react_code);
    case 'stakeholders':
      return !!pack.stakeholder_views?.views?.length;
    case 'validation':
      // Check for experiments or validation_experiments
      return !!(pack.validation_playbook?.experiments?.length || pack.validation_playbook?.validation_experiments?.length);
    case 'quality':
      return !!pack.quality_assessment;
    default:
      return false;
  }
}

// Evidence tier configuration
const EVIDENCE_TIERS: Record<
  EvidenceTier,
  { label: string; color: string; bgColor: string; description: string }
> = {
  E1: {
    label: 'Validated',
    color: '#22c55e',
    bgColor: 'rgba(34, 197, 94, 0.15)',
    description: 'Confirmed by research',
  },
  E2: {
    label: 'Supported',
    color: '#3b82f6',
    bgColor: 'rgba(59, 130, 246, 0.15)',
    description: 'Strong indicators',
  },
  E3: {
    label: 'Hypothesis',
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.15)',
    description: 'Needs validation',
  },
  E4: {
    label: 'Assumption',
    color: '#ef4444',
    bgColor: 'rgba(239, 68, 68, 0.15)',
    description: 'Requires testing',
  },
};

// Evidence Badge Component
function EvidenceBadge({ tier }: { tier: EvidenceTier }) {
  const config = EVIDENCE_TIERS[tier] || EVIDENCE_TIERS.E4;
  return (
    <span
      className="evidence-badge"
      style={{ backgroundColor: config.bgColor, color: config.color }}
      title={config.description}
    >
      {tier}
    </span>
  );
}

// Metric Card Component
function MetricCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}) {
  return (
    <div className="metric-card" style={{ borderColor: color }}>
      <div className="metric-icon" style={{ color }}>
        {icon}
      </div>
      <div className="metric-content">
        <span className="metric-value">{value}</span>
        <span className="metric-label">{label}</span>
      </div>
    </div>
  );
}

// Format duration
function formatDuration(seconds: number | undefined): string {
  if (!seconds) return 'N/A';
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Count hypotheses across the pack
function countHypotheses(pack: InceptionPack): number {
  let count = 0;

  // Count pain signals
  if (pack.customer_research?.pain_signals) {
    count += pack.customer_research.pain_signals.length;
  }

  // Count epics
  if (pack.product_requirements_document?.epics) {
    count += pack.product_requirements_document.epics.length;
  }

  // Count risks
  if (pack.business_case?.risks_and_mitigations) {
    count += pack.business_case.risks_and_mitigations.length;
  }

  return count;
}

export function PackViewer({ pack, sessionId, onBack }: PackViewerProps) {
  const [activeSection, setActiveSection] = useState<SectionKey>('summary');
  const [isExporting, setIsExporting] = useState(false);
  const [exportDropdownOpen, setExportDropdownOpen] = useState(false);

  const handleExport = useCallback(
    async (format: 'pdf' | 'docx') => {
      setIsExporting(true);
      setExportDropdownOpen(false);

      try {
        const blob = format === 'pdf' ? await exportPdf(sessionId) : await exportDocx(sessionId);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `inception-pack-${sessionId}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Export failed:', error);
      } finally {
        setIsExporting(false);
      }
    },
    [sessionId]
  );

  const handleExportJson = useCallback(() => {
    const blob = new Blob([JSON.stringify(pack, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inception-pack-${sessionId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportDropdownOpen(false);
  }, [pack, sessionId]);

  const qualityScore = pack.quality_assessment?.overall_score ?? pack.metadata?.quality_score;
  const scorePercent = qualityScore ? Math.round(qualityScore * 100) : null;

  // Extract TAM from customer research
  const tam = pack.customer_research?.market_context?.total_addressable_market;

  return (
    <div className="pack-viewer">
      {/* Header */}
      <header className="pack-header">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={18} />
          <span>Dashboard</span>
        </button>

        <div className="header-spacer" />

        <div className="export-dropdown">
          <button
            className="export-btn"
            onClick={() => setExportDropdownOpen(!exportDropdownOpen)}
            disabled={isExporting}
          >
            <Download size={16} />
            <span>{isExporting ? 'Exporting...' : 'Export'}</span>
            <ChevronDown size={14} />
          </button>

          {exportDropdownOpen && (
            <div className="export-menu">
              <button onClick={() => handleExport('pdf')}>
                <FileText size={16} />
                <span>Export PDF</span>
              </button>
              <button onClick={() => handleExport('docx')}>
                <FileText size={16} />
                <span>Export DOCX</span>
              </button>
              <button onClick={handleExportJson}>
                <FileJson size={16} />
                <span>Export JSON</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="pack-hero">
        <h1 className="hero-title">{pack.executive_summary?.product_name || 'Inception Pack'}</h1>
        {pack.executive_summary?.tagline && (
          <p className="hero-tagline">{pack.executive_summary.tagline}</p>
        )}

        <div className="metrics-grid">
          {scorePercent !== null && (
            <MetricCard
              label="Score"
              value={`${scorePercent}%`}
              icon={<Award size={20} />}
              color="#8b5cf6"
            />
          )}
          {tam && (
            <MetricCard
              label="TAM"
              value={tam}
              icon={<TrendingUp size={20} />}
              color="#3b82f6"
            />
          )}
          <MetricCard
            label="Hypotheses"
            value={countHypotheses(pack)}
            icon={<Target size={20} />}
            color="#22c55e"
          />
          <MetricCard
            label="Duration"
            value={formatDuration(pack.metadata?.total_duration_seconds)}
            icon={<Clock size={20} />}
            color="#6b7280"
          />
        </div>
      </section>

      {/* Section Navigation */}
      <nav className="section-nav">
        {SECTIONS.map((section) => {
          const hasContent = checkSectionHasContent(pack, section.key);
          return (
            <button
              key={section.key}
              className={`section-tab ${activeSection === section.key ? 'active' : ''} ${!hasContent ? 'disabled' : ''}`}
              onClick={() => hasContent && setActiveSection(section.key)}
              disabled={!hasContent}
              title={!hasContent ? 'No content available' : undefined}
            >
              {section.label}
            </button>
          );
        })}
      </nav>

      {/* Section Content */}
      <main className="section-content">
        {activeSection === 'summary' && (
          <SummarySection summary={pack.executive_summary} />
        )}
        {activeSection === 'research' && (
          <ResearchSection research={pack.customer_research} />
        )}
        {activeSection === 'competitive' && (
          <CompetitiveSection analysis={pack.competitive_analysis} />
        )}
        {activeSection === 'personas' && (
          <PersonasSection
            personas={pack.detailed_personas}
            legacyPersonas={pack.customer_research?.user_personas}
          />
        )}
        {activeSection === 'business' && (
          <BusinessSection business={pack.business_case} />
        )}
        {activeSection === 'gtm' && (
          <GTMSection gtm={pack.gtm_strategy} />
        )}
        {activeSection === 'financial' && (
          <FinancialSection financial={pack.financial_model} />
        )}
        {activeSection === 'product' && (
          <ProductSection prd={pack.product_requirements_document} />
        )}
        {activeSection === 'tech' && (
          <TechSection tech={pack.technical_architecture} />
        )}
        {activeSection === 'legal' && (
          <LegalSection legal={pack.legal_regulatory_review} />
        )}
        {activeSection === 'risks' && (
          <RisksSection risks={pack.risk_assessment} />
        )}
        {activeSection === 'wireframes' && (
          <WireframesSection wireframes={pack.wireframes} />
        )}
        {activeSection === 'prototype' && (
          <PrototypeSection prototype={pack.prototype} />
        )}
        {activeSection === 'stakeholders' && (
          <StakeholdersSection stakeholders={pack.stakeholder_views} />
        )}
        {activeSection === 'validation' && (
          <ValidationSection playbook={pack.validation_playbook} />
        )}
        {activeSection === 'quality' && (
          <QualitySection quality={pack.quality_assessment} />
        )}
      </main>
    </div>
  );
}

// Section Components

function SummarySection({ summary }: { summary: InceptionPack['executive_summary'] }) {
  if (!summary) return <EmptySection message="No executive summary available" />;

  return (
    <div className="section-grid">
      <div className="content-card full-width">
        <h3>Problem Statement</h3>
        <p>{summary.problem_statement}</p>
      </div>

      <div className="content-card full-width">
        <h3>Solution Overview</h3>
        <p>{summary.solution_overview}</p>
      </div>

      <div className="content-card">
        <h3>Value Proposition</h3>
        <p>{summary.value_proposition}</p>
      </div>

      <div className="content-card">
        <h3>Target Users</h3>
        <ul className="bullet-list">
          {summary.target_users?.map((user, i) => (
            <li key={i}>{user}</li>
          ))}
        </ul>
      </div>

      <div className="content-card">
        <h3>Key Differentiators</h3>
        <ul className="bullet-list">
          {summary.key_differentiators?.map((diff, i) => (
            <li key={i}>{diff}</li>
          ))}
        </ul>
      </div>

      <div className="content-card">
        <h3>Top Risks</h3>
        <ul className="bullet-list warning">
          {summary.top_risks?.map((risk, i) => (
            <li key={i}>{risk}</li>
          ))}
        </ul>
      </div>

      <div className="content-card full-width highlight">
        <h3>Recommendation</h3>
        <p className="recommendation">{summary.recommendation}</p>
      </div>
    </div>
  );
}

function ResearchSection({ research }: { research: InceptionPack['customer_research'] }) {
  if (!research) return <EmptySection message="No customer research available" />;

  // Type assertion for competitive_positioning since it may come from visual data
  const competitivePositioning = (research as Record<string, unknown>).competitive_positioning as
    | { competitors: unknown[]; x_axis_label: string; y_axis_label: string }
    | undefined;

  return (
    <div className="section-grid">
      {/* Competitive Positioning Chart */}
      {competitivePositioning && competitivePositioning.competitors && (
        <div className="content-card full-width">
          <h3>Competitive Positioning</h3>
          <CompetitivePositionChart data={competitivePositioning as Parameters<typeof CompetitivePositionChart>[0]['data']} />
        </div>
      )}

      {/* Pain Signals */}
      {research.pain_signals && research.pain_signals.length > 0 && (
        <div className="content-card full-width">
          <h3>Pain Signals</h3>
          <div className="evidence-table">
            <div className="table-header">
              <span>Description</span>
              <span>Severity</span>
              <span>Evidence</span>
            </div>
            {research.pain_signals.map((signal, i) => (
              <div key={i} className="table-row">
                <span className="pain-description">{signal.description}</span>
                <span className={`severity ${signal.severity}`}>{signal.severity}</span>
                <span>
                  <EvidenceBadge tier={signal.evidence_tier} />
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Job to be Done */}
      {research.job_to_be_done && (
        <div className="content-card">
          <h3>Job to be Done</h3>
          <div className="jtbd-card">
            <p>
              <strong>When</strong> {research.job_to_be_done.trigger_situation}
            </p>
            <p>
              <strong>I want to</strong> {research.job_to_be_done.underlying_goal}
            </p>
            <p>
              <strong>So that</strong> {research.job_to_be_done.success_definition}
            </p>
          </div>
        </div>
      )}

      {/* Market Context */}
      {research.market_context && (
        <div className="content-card">
          <h3>Market Context</h3>
          <div className="market-funnel">
            <div className="funnel-item">
              <span className="funnel-label">TAM</span>
              <span className="funnel-value">
                {research.market_context.total_addressable_market}
              </span>
            </div>
            <div className="funnel-arrow">→</div>
            <div className="funnel-item">
              <span className="funnel-label">SAM</span>
              <span className="funnel-value">
                {research.market_context.serviceable_addressable_market}
              </span>
            </div>
            <div className="funnel-arrow">→</div>
            <div className="funnel-item">
              <span className="funnel-label">SOM</span>
              <span className="funnel-value">
                {research.market_context.serviceable_obtainable_market}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Personas */}
      {research.user_personas && research.user_personas.length > 0 && (
        <div className="content-card full-width">
          <h3>Personas</h3>
          <div className="persona-grid">
            {research.user_personas.map((persona, i) => (
              <div key={i} className="persona-card">
                <h4>{persona.name}</h4>
                <p className="persona-role">{persona.role}</p>
                <div className="persona-details">
                  <p>
                    <strong>Goals:</strong> {persona.goals?.join(', ')}
                  </p>
                  <p>
                    <strong>Pain Points:</strong> {persona.frustrations?.join(', ')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function BusinessSection({ business }: { business: InceptionPack['business_case'] }) {
  if (!business) return <EmptySection message="No business case available" />;

  // Type assertion for financial_projection since it may come from visual data
  const financialProjection = (business as unknown as Record<string, unknown>).financial_projection as
    | { monthly_data: unknown[]; break_even_month: number | null }
    | undefined;

  return (
    <div className="section-grid">
      {/* Financial Projection Chart */}
      {financialProjection && financialProjection.monthly_data && (
        <div className="content-card full-width">
          <h3>Financial Projections</h3>
          <FinancialProjectionChart data={financialProjection as Parameters<typeof FinancialProjectionChart>[0]['data']} />
        </div>
      )}

      {/* Lean Canvas Visual */}
      {business.lean_canvas && (
        <div className="content-card full-width">
          <h3>Lean Canvas</h3>
          <LeanCanvasVisual data={business.lean_canvas as Parameters<typeof LeanCanvasVisual>[0]['data']} />
        </div>
      )}

      {/* Revenue Streams */}
      {business.revenue_streams && business.revenue_streams.length > 0 && (
        <div className="content-card">
          <h3>Revenue Streams</h3>
          <ul className="revenue-list">
            {business.revenue_streams.map((stream, i) => (
              <li key={i}>
                <span className="stream-name">{stream.name}</span>
                <span className="stream-model">{stream.pricing_model}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risks */}
      {business.risks_and_mitigations && business.risks_and_mitigations.length > 0 && (
        <div className="content-card">
          <h3>Risks & Mitigations</h3>
          <ul className="risk-list">
            {business.risks_and_mitigations.map((item, i) => (
              <li key={i}>
                <div className="risk-item">
                  <span className="risk-label">{item.risk}</span>
                  <span className="mitigation">{item.mitigation}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ProductSection({ prd }: { prd: InceptionPack['product_requirements_document'] }) {
  if (!prd) return <EmptySection message="No product requirements available" />;

  return (
    <div className="section-grid">
      {/* Epics */}
      {prd.epics && prd.epics.length > 0 && (
        <div className="content-card full-width">
          <h3>Epics & User Stories</h3>
          <div className="epic-list">
            {prd.epics.map((epic, i) => (
              <div key={i} className="epic-card">
                <h4>
                  <span className="epic-number">E{i + 1}</span>
                  {epic.title}
                </h4>
                <p className="epic-description">{epic.description}</p>
                {epic.stories && epic.stories.length > 0 && (
                  <div className="story-list">
                    {epic.stories.slice(0, 3).map((story, j) => (
                      <div key={j} className="story-item">
                        <span className="story-id">{story.id}</span>
                        <span className="story-text">{story.title}</span>
                        <span className={`story-priority ${story.priority}`}>
                          {story.priority}
                        </span>
                      </div>
                    ))}
                    {epic.stories.length > 3 && (
                      <span className="more-stories">
                        +{epic.stories.length - 3} more stories
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Functional Requirements */}
      {prd.functional_requirements && prd.functional_requirements.length > 0 && (
        <div className="content-card">
          <h3>Functional Requirements</h3>
          <ul className="requirement-list">
            {prd.functional_requirements.slice(0, 8).map((req, i) => (
              <li key={i}>
                <span className="req-id">{req.id}</span>
                <span className="req-text">{req.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Non-Functional Requirements */}
      {prd.non_functional_requirements && prd.non_functional_requirements.length > 0 && (
        <div className="content-card">
          <h3>Non-Functional Requirements</h3>
          <ul className="requirement-list">
            {prd.non_functional_requirements.slice(0, 6).map((req, i) => (
              <li key={i}>
                <span className="req-category">{req.category}</span>
                <span className="req-text">{req.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function TechSection({ tech }: { tech: InceptionPack['technical_architecture'] }) {
  if (!tech) return <EmptySection message="No technical architecture available" />;

  return (
    <div className="section-grid">
      {/* Architecture Diagram */}
      {tech.architecture_diagram_mermaid && (
        <div className="content-card full-width">
          <h3>System Architecture</h3>
          <div className="diagram-container">
            <MermaidDiagram chart={tech.architecture_diagram_mermaid} />
          </div>
        </div>
      )}

      {/* Tech Stack */}
      {tech.technology_stack && tech.technology_stack.length > 0 && (
        <div className="content-card">
          <h3>Tech Stack</h3>
          <div className="tech-stack-grid">
            {tech.technology_stack.map((item, i) => (
              <div key={i} className="stack-item">
                <span className="stack-label">{item.category}</span>
                <span className="stack-value">{item.technology}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Components */}
      {tech.system_components && tech.system_components.length > 0 && (
        <div className="content-card">
          <h3>System Components</h3>
          <ul className="component-list">
            {tech.system_components.map((comp, i) => (
              <li key={i}>
                <span className="comp-name">{comp.name}</span>
                <span className="comp-purpose">{comp.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function LegalSection({ legal }: { legal: InceptionPack['legal_regulatory_review'] }) {
  if (!legal) return <EmptySection message="No legal review available" />;

  // Type assertion for risk_matrix since it may come from visual data
  const riskMatrix = (legal as unknown as Record<string, unknown>).risk_matrix as
    | { risks: unknown[]; high_priority_count: number; overall_risk_level: string }
    | undefined;

  return (
    <div className="section-grid">
      {/* Risk Matrix Chart */}
      {riskMatrix && riskMatrix.risks && riskMatrix.risks.length > 0 && (
        <div className="content-card full-width">
          <h3>Risk Matrix</h3>
          <RiskMatrixChart data={riskMatrix as Parameters<typeof RiskMatrixChart>[0]['data']} />
        </div>
      )}

      {/* Risk Assessment */}
      {legal.overall_risk_assessment && (
        <div className="content-card highlight">
          <h3>Overall Risk Assessment</h3>
          <div className="risk-assessment">
            <span className={`risk-level ${legal.overall_risk_assessment.risk_level}`}>
              {legal.overall_risk_assessment.risk_level?.toUpperCase()} RISK
            </span>
            {legal.overall_risk_assessment.key_concerns && legal.overall_risk_assessment.key_concerns.length > 0 && (
              <ul className="bullet-list">
                {legal.overall_risk_assessment.key_concerns.slice(0, 3).map((concern, i) => (
                  <li key={i}>{concern}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* Applicable Regulations */}
      {legal.applicable_regulations && legal.applicable_regulations.length > 0 && (
        <div className="content-card full-width">
          <h3>Applicable Regulations</h3>
          <div className="regulation-grid">
            {legal.applicable_regulations.map((reg, i) => (
              <div key={i} className="regulation-card">
                <h4>{reg.name}</h4>
                <p>{reg.description}</p>
                {reg.compliance_requirements && (
                  <ul className="compliance-list">
                    {reg.compliance_requirements.slice(0, 3).map((req, j) => (
                      <li key={j}>{req}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Protection */}
      {legal.data_protection_requirements && legal.data_protection_requirements.length > 0 && (
        <div className="content-card">
          <h3>Data Protection</h3>
          <ul className="bullet-list">
            {legal.data_protection_requirements.map((req, i) => (
              <li key={i}>
                <strong>{req.regulation}:</strong> {req.key_obligations?.join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function QualitySection({ quality }: { quality: InceptionPack['quality_assessment'] }) {
  if (!quality) return <EmptySection message="No quality assessment available" />;

  const score = quality.overall_score ? Math.round(quality.overall_score * 100) : null;

  return (
    <div className="section-grid">
      {/* Overall Score */}
      <div className="content-card highlight center">
        <h3>Overall Quality Score</h3>
        <div className="quality-score">
          <span className="score-value">{score ?? 'N/A'}%</span>
          <span className="score-label">
            {score && score >= 80 ? 'Excellent' : score && score >= 60 ? 'Good' : 'Needs Work'}
          </span>
        </div>
      </div>

      {/* Strengths */}
      {quality.strengths && quality.strengths.length > 0 && (
        <div className="content-card">
          <h3>Strengths</h3>
          <ul className="bullet-list success">
            {quality.strengths.map((strength, i) => (
              <li key={i}>{strength}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Areas for Improvement (Weaknesses) */}
      {quality.weaknesses && quality.weaknesses.length > 0 && (
        <div className="content-card">
          <h3>Areas for Improvement</h3>
          <ul className="bullet-list warning">
            {quality.weaknesses.map((weakness, i) => (
              <li key={i}>{weakness}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Section Scores */}
      {quality.section_scores && quality.section_scores.length > 0 && (
        <div className="content-card full-width">
          <h3>Section Scores</h3>
          <div className="score-bars">
            {quality.section_scores.map((sectionScore, i) => {
              const percent = Math.round(sectionScore.score * 100);
              return (
                <div key={i} className="score-bar-item">
                  <span className="score-bar-label">
                    {sectionScore.section.replace(/_/g, ' ')}
                  </span>
                  <div className="score-bar-track">
                    <div
                      className="score-bar-fill"
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                  <span className="score-bar-value">{percent}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// New V3.0 Section Components

function CompetitiveSection({ analysis }: { analysis: InceptionPack['competitive_analysis'] }) {
  if (!analysis) return <EmptySection message="No competitive analysis available" />;

  // Handle both frontend format (competitors) and backend format (direct_competitors)
  const competitors = analysis.competitors || analysis.direct_competitors || [];

  return (
    <div className="section-grid">
      {/* Summary */}
      {analysis.summary && (
        <div className="content-card full-width">
          <h3>Competitive Landscape</h3>
          <p>{analysis.summary}</p>
        </div>
      )}

      {/* Competitors */}
      {competitors.length > 0 && (
        <div className="content-card full-width">
          <h3>Competitor Analysis</h3>
          <div className="competitor-grid">
            {competitors.map((competitor, i) => (
              <div key={i} className="competitor-card">
                <div className="competitor-header">
                  <h4>{competitor.name}</h4>
                  <span className={`threat-badge ${competitor.threat_level}`}>
                    {competitor.threat_level} threat
                  </span>
                </div>
                <p className="competitor-desc">{competitor.description}</p>
                <div className="competitor-details">
                  <div className="detail-group">
                    <span className="detail-label">Strengths</span>
                    <ul className="detail-list">
                      {competitor.strengths?.slice(0, 3).map((s, j) => (
                        <li key={j}>{s}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="detail-group">
                    <span className="detail-label">Weaknesses</span>
                    <ul className="detail-list warning">
                      {competitor.weaknesses?.slice(0, 3).map((w, j) => (
                        <li key={j}>{w}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                {competitor.differentiation_opportunity && (
                  <div className="differentiation-note">
                    <strong>Opportunity:</strong> {competitor.differentiation_opportunity}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Competitive Moat */}
      {analysis.competitive_moat && analysis.competitive_moat.length > 0 && (
        <div className="content-card">
          <h3>Our Competitive Moat</h3>
          <ul className="bullet-list success">
            {analysis.competitive_moat.map((moat, i) => (
              <li key={i}>{moat}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Market Gaps */}
      {analysis.market_gaps && analysis.market_gaps.length > 0 && (
        <div className="content-card">
          <h3>Market Gaps</h3>
          <ul className="bullet-list">
            {analysis.market_gaps.map((gap, i) => (
              <li key={i}>{gap}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function PersonasSection({
  personas,
  legacyPersonas,
}: {
  personas: InceptionPack['detailed_personas'];
  legacyPersonas?: InceptionPack['customer_research']['user_personas'];
}) {
  const personaList = personas?.personas || [];
  const hasDetailedPersonas = personaList.length > 0;

  if (!hasDetailedPersonas && !legacyPersonas?.length) {
    return <EmptySection message="No personas available" />;
  }

  return (
    <div className="section-grid">
      {/* Key Insights */}
      {personas?.key_insights && personas.key_insights.length > 0 && (
        <div className="content-card full-width highlight">
          <h3>Key Insights</h3>
          <ul className="bullet-list">
            {personas.key_insights.map((insight, i) => (
              <li key={i}>{insight}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Detailed Personas */}
      {hasDetailedPersonas ? (
        <div className="content-card full-width">
          <h3>Detailed Personas</h3>
          <div className="persona-grid detailed">
            {personaList.map((persona, i) => (
              <div key={i} className="persona-card detailed">
                <div className="persona-header">
                  <h4>{persona.name}</h4>
                  <span className="persona-role">{persona.role}</span>
                </div>
                {persona.quote && (
                  <blockquote className="persona-quote">"{persona.quote}"</blockquote>
                )}
                <div className="persona-details">
                  {persona.demographics && (
                    <div className="detail-group">
                      <span className="detail-label">Demographics</span>
                      <p>
                        {persona.demographics.age_range}, {persona.demographics.location}
                      </p>
                    </div>
                  )}
                  {persona.jobs_to_be_done && persona.jobs_to_be_done.length > 0 && (
                    <div className="detail-group">
                      <span className="detail-label">Jobs to be Done</span>
                      <ul className="jtbd-list">
                        {persona.jobs_to_be_done.map((jtbd, j) => (
                          <li key={j}>
                            <span className={`importance-badge ${jtbd.importance}`}>
                              {jtbd.importance}
                            </span>
                            {jtbd.job}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {persona.pain_points && persona.pain_points.length > 0 && (
                    <div className="detail-group">
                      <span className="detail-label">Pain Points</span>
                      <ul className="detail-list warning">
                        {persona.pain_points.slice(0, 3).map((pain, j) => (
                          <li key={j}>{pain}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {persona.goals && persona.goals.length > 0 && (
                    <div className="detail-group">
                      <span className="detail-label">Goals</span>
                      <ul className="detail-list success">
                        {persona.goals.slice(0, 3).map((goal, j) => (
                          <li key={j}>{goal}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        // Fallback to legacy personas
        legacyPersonas && legacyPersonas.length > 0 && (
          <div className="content-card full-width">
            <h3>Personas</h3>
            <div className="persona-grid">
              {legacyPersonas.map((persona, i) => (
                <div key={i} className="persona-card">
                  <h4>{persona.name}</h4>
                  <p className="persona-role">{persona.role}</p>
                  <div className="persona-details">
                    <p>
                      <strong>Goals:</strong> {persona.goals?.join(', ')}
                    </p>
                    <p>
                      <strong>Pain Points:</strong> {persona.frustrations?.join(', ')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      )}
    </div>
  );
}

function GTMSection({ gtm }: { gtm: InceptionPack['gtm_strategy'] }) {
  if (!gtm) return <EmptySection message="No go-to-market strategy available" />;

  return (
    <div className="section-grid">
      {/* Positioning */}
      {gtm.positioning_statement && (
        <div className="content-card full-width highlight">
          <h3>Positioning Statement</h3>
          <p className="positioning-statement">{gtm.positioning_statement}</p>
        </div>
      )}

      {/* Launch Phases */}
      {gtm.launch_phases && gtm.launch_phases.length > 0 && (
        <div className="content-card full-width">
          <h3>Launch Phases</h3>
          <div className="phase-timeline">
            {gtm.launch_phases.map((phase, i) => (
              <div key={i} className="phase-card">
                <div className="phase-header">
                  <span className="phase-number">{i + 1}</span>
                  <div className="phase-title">
                    <h4>{phase.phase_name}</h4>
                    <span className="phase-duration">{phase.duration}</span>
                  </div>
                </div>
                <div className="phase-content">
                  {phase.objectives && phase.objectives.length > 0 && (
                    <div className="phase-section">
                      <span className="section-label">Objectives</span>
                      <ul>
                        {phase.objectives.map((obj, j) => (
                          <li key={j}>{obj}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {phase.key_activities && phase.key_activities.length > 0 && (
                    <div className="phase-section">
                      <span className="section-label">Activities</span>
                      <ul>
                        {phase.key_activities.slice(0, 3).map((act, j) => (
                          <li key={j}>{act}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Channel Strategy */}
      {gtm.channel_strategy && gtm.channel_strategy.length > 0 && (
        <div className="content-card full-width">
          <h3>Channel Strategy</h3>
          <div className="channel-grid">
            {gtm.channel_strategy.map((channel, i) => (
              <div key={i} className="channel-card">
                <h4>{channel.channel}</h4>
                <p className="channel-purpose">{channel.purpose}</p>
                {channel.tactics && channel.tactics.length > 0 && (
                  <ul className="channel-tactics">
                    {channel.tactics.slice(0, 3).map((tactic, j) => (
                      <li key={j}>{tactic}</li>
                    ))}
                  </ul>
                )}
                {channel.expected_roi && (
                  <span className="channel-roi">Expected ROI: {channel.expected_roi}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messaging Framework */}
      {gtm.messaging_framework && (
        <div className="content-card">
          <h3>Messaging Framework</h3>
          <div className="messaging-framework">
            <h4 className="headline">{gtm.messaging_framework.headline}</h4>
            {gtm.messaging_framework.subheadline && (
              <p className="subheadline">{gtm.messaging_framework.subheadline}</p>
            )}
            {gtm.messaging_framework.key_benefits && (
              <ul className="benefits-list">
                {gtm.messaging_framework.key_benefits.map((benefit, i) => (
                  <li key={i}>{benefit}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* Target Segments */}
      {gtm.target_segments && gtm.target_segments.length > 0 && (
        <div className="content-card">
          <h3>Target Segments</h3>
          <ul className="bullet-list">
            {gtm.target_segments.map((segment, i) => (
              <li key={i}>{segment}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function FinancialSection({ financial }: { financial: InceptionPack['financial_model'] }) {
  if (!financial) return <EmptySection message="No financial model available" />;

  return (
    <div className="section-grid">
      {/* Summary */}
      {financial.summary && (
        <div className="content-card full-width">
          <h3>Financial Summary</h3>
          <p>{financial.summary}</p>
        </div>
      )}

      {/* Projections Table */}
      {financial.projections && financial.projections.length > 0 && (
        <div className="content-card full-width">
          <h3>Financial Projections</h3>
          <div className="projection-table">
            <table>
              <thead>
                <tr>
                  <th>Period</th>
                  <th>Revenue</th>
                  <th>Costs</th>
                  <th>Profit</th>
                  <th>Cumulative</th>
                </tr>
              </thead>
              <tbody>
                {financial.projections.map((proj, i) => (
                  <tr key={i}>
                    <td>{proj.period}</td>
                    <td className="currency">${proj.revenue?.toLocaleString()}</td>
                    <td className="currency">${proj.costs?.toLocaleString()}</td>
                    <td className={`currency ${proj.profit >= 0 ? 'positive' : 'negative'}`}>
                      ${proj.profit?.toLocaleString()}
                    </td>
                    <td className={`currency ${proj.cumulative_profit >= 0 ? 'positive' : 'negative'}`}>
                      ${proj.cumulative_profit?.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Unit Economics */}
      {financial.unit_economics && financial.unit_economics.length > 0 && (
        <div className="content-card">
          <h3>Unit Economics</h3>
          <div className="unit-economics">
            {financial.unit_economics.map((metric, i) => (
              <div key={i} className="unit-metric">
                <span className="metric-name">{metric.metric}</span>
                <span className="metric-value">{metric.value}</span>
                {metric.benchmark && (
                  <span className="metric-benchmark">Benchmark: {metric.benchmark}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assumptions */}
      {financial.assumptions && financial.assumptions.length > 0 && (
        <div className="content-card">
          <h3>Key Assumptions</h3>
          <ul className="assumptions-list">
            {financial.assumptions.map((assumption, i) => (
              <li key={i}>{assumption}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Break-even */}
      {financial.break_even_analysis && (
        <div className="content-card highlight">
          <h3>Break-Even Analysis</h3>
          <p>{financial.break_even_analysis}</p>
        </div>
      )}

      {/* Funding Requirements */}
      {financial.funding_requirements && (
        <div className="content-card">
          <h3>Funding Requirements</h3>
          <p>{financial.funding_requirements}</p>
        </div>
      )}
    </div>
  );
}

function RisksSection({ risks }: { risks: InceptionPack['risk_assessment'] }) {
  if (!risks) return <EmptySection message="No risk assessment available" />;

  // Backend uses risk_matrix, support both for compatibility
  const riskList = (risks as Record<string, unknown>).risk_matrix as Array<Record<string, unknown>> ||
                   (risks as Record<string, unknown>).risks as Array<Record<string, unknown>> || [];
  const riskSummary = (risks as Record<string, unknown>).risk_summary as Record<string, unknown> || {};
  const topRisks = (risks as Record<string, unknown>).top_3_risks as Array<Record<string, unknown>> ||
                   (risks as Record<string, unknown>).top_risks as string[] || [];

  return (
    <div className="section-grid">
      {/* Summary */}
      {(riskSummary.overall_risk_level || risks.summary) && (
        <div className="content-card full-width">
          <h3>Risk Overview</h3>
          <div className="risk-overview">
            {risks.summary && <p>{risks.summary}</p>}
            {riskSummary.overall_risk_level && (
              <span className={`overall-risk-badge ${riskSummary.overall_risk_level}`}>
                Overall: {String(riskSummary.overall_risk_level).toUpperCase()} RISK
              </span>
            )}
            {riskSummary.total_risks && (
              <p>Total risks identified: {String(riskSummary.total_risks)}
                {riskSummary.critical_risks ? ` (${riskSummary.critical_risks} critical, ${riskSummary.high_risks} high)` : ''}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Top Risks */}
      {topRisks && topRisks.length > 0 && (
        <div className="content-card full-width highlight">
          <h3>
            <AlertTriangle size={16} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            Top Risks
          </h3>
          <ul className="bullet-list warning">
            {topRisks.map((risk, i) => (
              <li key={i}>
                {typeof risk === 'string' ? risk : `${risk.name}: ${risk.why_critical || risk.immediate_action || ''}`}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risk Table */}
      {riskList && riskList.length > 0 && (
        <div className="content-card full-width">
          <h3>Risk Register</h3>
          <div className="risk-table">
            <table>
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Risk</th>
                  <th>Likelihood</th>
                  <th>Impact</th>
                  <th>Mitigation</th>
                </tr>
              </thead>
              <tbody>
                {riskList.map((risk, i) => (
                  <tr key={i}>
                    <td className="category">{String(risk.category || '')}</td>
                    <td className="description">{String(risk.name || risk.description || '')}</td>
                    <td>
                      <span className={`risk-level-badge level-${risk.likelihood}`}>
                        {String(risk.likelihood || '')}
                      </span>
                    </td>
                    <td>
                      <span className={`risk-level-badge level-${risk.impact}`}>
                        {String(risk.impact || '')}
                      </span>
                    </td>
                    <td className="mitigation">{String(risk.mitigation_strategy || '')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function WireframesSection({ wireframes }: { wireframes: InceptionPack['wireframes'] }) {
  if (!wireframes?.screens?.length) {
    return <EmptySection message="No wireframes available" />;
  }

  return (
    <div className="section-grid">
      <div className="content-card full-width wireframe-container">
        <h3>UI Wireframes</h3>
        <WireframeViewer wireframes={wireframes} />
      </div>

      {/* User Flows */}
      {wireframes.user_flows && wireframes.user_flows.length > 0 && (
        <div className="content-card full-width">
          <h3>User Flows</h3>
          <div className="user-flows">
            {wireframes.user_flows.map((flow, i) => (
              <div key={i} className="flow-item">
                <h4>{flow.flow_name}</h4>
                <p>{flow.description}</p>
                <div className="flow-screens">
                  {flow.screens.map((screen, j) => (
                    <span key={j} className="flow-screen">
                      {screen}
                      {j < flow.screens.length - 1 && ' → '}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Design Notes */}
      {wireframes.design_system_notes && wireframes.design_system_notes.length > 0 && (
        <div className="content-card">
          <h3>Design System Notes</h3>
          <ul className="bullet-list">
            {wireframes.design_system_notes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function PrototypeSection({ prototype }: { prototype: InceptionPack['prototype'] }) {
  if (!prototype?.react_component_code) {
    return <EmptySection message="No prototype available" />;
  }

  return (
    <div className="section-grid">
      <div className="content-card full-width prototype-container">
        <h3>Interactive Prototype</h3>
        <PrototypeViewer prototype={prototype} />
      </div>
    </div>
  );
}

function StakeholdersSection({ stakeholders }: { stakeholders: InceptionPack['stakeholder_views'] }) {
  if (!stakeholders?.views?.length) {
    return <EmptySection message="No stakeholder views available" />;
  }

  return (
    <div className="section-grid">
      <div className="content-card full-width stakeholder-container">
        <h3>Stakeholder Views</h3>
        <StakeholderViewSelector views={stakeholders.views} />
      </div>

      {/* Common Concerns */}
      {stakeholders.common_concerns && stakeholders.common_concerns.length > 0 && (
        <div className="content-card">
          <h3>Common Concerns</h3>
          <ul className="bullet-list warning">
            {stakeholders.common_concerns.map((concern, i) => (
              <li key={i}>{concern}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Cross-Stakeholder Alignment */}
      {stakeholders.cross_stakeholder_alignment && (
        <div className="content-card">
          <h3>Cross-Stakeholder Alignment</h3>
          <p>{stakeholders.cross_stakeholder_alignment}</p>
        </div>
      )}
    </div>
  );
}

function ValidationSection({ playbook }: { playbook: InceptionPack['validation_playbook'] }) {
  if (!playbook?.experiments?.length) {
    return <EmptySection message="No validation playbook available" />;
  }

  return (
    <div className="section-grid">
      <div className="content-card full-width validation-container">
        <h3>Validation Playbook</h3>
        <ValidationPlaybook playbook={playbook} />
      </div>
    </div>
  );
}

function EmptySection({ message }: { message: string }) {
  return (
    <div className="empty-section">
      <p>{message}</p>
    </div>
  );
}

export default PackViewer;
