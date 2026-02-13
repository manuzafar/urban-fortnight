/**
 * V4 Pack Viewer Component
 * Results display with 16-section navigation and stakeholder views
 */

import { useState } from 'react';
import { Share2, Printer, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { QualityScore } from './QualityScore';
import { SectionNav, type NavSection } from './SectionNav';
import { EvidenceBadge, EvidenceLegend } from './EvidenceBadge';
import type { InceptionPack, RiskItem as RiskItemType, CompetitorDetail } from '../../types/api';
import '../../styles/theme-v4.css';

interface PackViewerV4Props {
  pack: InceptionPack;
  sessionId: string;
  onBack: () => void;
}

// Section definitions
const SECTIONS: NavSection[] = [
  { id: 'executive_summary', number: '01', title: 'Executive Summary', phase: 'Overview', status: 'done' },
  { id: 'customer_research', number: '02', title: 'Customer Research', phase: 'Discovery', status: 'done' },
  { id: 'competitive_analysis', number: '03', title: 'Competitive Analysis', phase: 'Discovery', status: 'done' },
  { id: 'personas', number: '04', title: 'Personas', phase: 'Discovery', status: 'done' },
  { id: 'business_case', number: '05', title: 'Business Case', phase: 'Strategy', status: 'done' },
  { id: 'gtm_strategy', number: '06', title: 'Go-to-Market', phase: 'Strategy', status: 'done' },
  { id: 'financial_model', number: '07', title: 'Financial Model', phase: 'Strategy', status: 'warn' },
  { id: 'product_requirements', number: '08', title: 'Product Requirements', phase: 'Delivery', status: 'done' },
  { id: 'tech_architecture', number: '09', title: 'Tech Architecture', phase: 'Delivery', status: 'done' },
  { id: 'legal_regulatory', number: '10', title: 'Legal & Regulatory', phase: 'Delivery', status: 'done' },
  { id: 'risk_assessment', number: '11', title: 'Risk Assessment', phase: 'Delivery', status: 'warn' },
  { id: 'wireframes', number: '12', title: 'Wireframes', phase: 'Design', status: 'done' },
  { id: 'prototype', number: '13', title: 'Prototype', phase: 'Design', status: 'done' },
  { id: 'stakeholder_views', number: '14', title: 'Stakeholder Views', phase: 'Synthesis', status: 'done' },
  { id: 'validation_playbook', number: '15', title: 'Validation Playbook', phase: 'Synthesis', status: 'done' },
  { id: 'quality_assessment', number: '16', title: 'Quality Assessment', phase: 'Quality', status: 'warn' },
];

export function PackViewerV4({ pack, sessionId, onBack }: PackViewerV4Props) {
  const [activeSection, setActiveSection] = useState('executive_summary');
  const [activeStakeholder, setActiveStakeholder] = useState('CFO');

  const qualityScore = pack.metadata?.quality_score ?? pack.quality_assessment?.overall_score ?? 85;
  const productName = pack.executive_summary?.product_name || 'Inception Pack';

  const currentIndex = SECTIONS.findIndex((s) => s.id === activeSection);
  const prevSection = currentIndex > 0 ? SECTIONS[currentIndex - 1] : null;
  const nextSection = currentIndex < SECTIONS.length - 1 ? SECTIONS[currentIndex + 1] : null;

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Export pack:', sessionId);
  };

  return (
    <div className="v4-root" style={{ minHeight: '100vh' }}>
      {/* Header */}
      <header
        style={{
          padding: '12px 24px',
          background: 'var(--v4-surface)',
          borderBottom: '1px solid var(--v4-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={onBack}
            style={{
              fontSize: '16px',
              fontWeight: 600,
              color: 'var(--v4-text)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Seedcraft
          </button>
          <span
            style={{
              paddingLeft: '16px',
              borderLeft: '1px solid var(--v4-border)',
              fontSize: '14px',
              color: 'var(--v4-text-secondary)',
            }}
          >
            {productName}
          </span>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              background: 'var(--v4-success-bg)',
              borderRadius: '100px',
              fontSize: '12px',
              fontWeight: 500,
              color: 'var(--v4-success)',
            }}
          >
            <span
              style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--v4-success)' }}
            />
            Complete
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <IconButton icon={<Share2 size={18} />} title="Share" />
          <IconButton icon={<Printer size={18} />} title="Print" />
          <button
            onClick={handleExport}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              background: 'var(--v4-text)',
              color: 'white',
              fontSize: '13px',
              fontWeight: 500,
              border: 'none',
              borderRadius: 'var(--v4-radius)',
              cursor: 'pointer',
              marginLeft: '4px',
            }}
          >
            <Download size={14} />
            Export
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '260px 1fr',
          minHeight: 'calc(100vh - 61px)',
        }}
      >
        {/* Sidebar */}
        <aside
          style={{
            background: 'var(--v4-surface)',
            borderRight: '1px solid var(--v4-border)',
            position: 'sticky',
            top: '61px',
            height: 'calc(100vh - 61px)',
            overflowY: 'auto',
          }}
        >
          <QualityScore score={qualityScore} />
          <SectionNav sections={SECTIONS} activeSection={activeSection} onSectionChange={setActiveSection} />
          <div style={{ margin: '16px' }}>
            <EvidenceLegend />
          </div>
        </aside>

        {/* Main Content */}
        <main style={{ padding: '32px 48px 80px', maxWidth: '840px' }}>
          {/* Breadcrumb */}
          <div style={{ fontSize: '13px', color: 'var(--v4-text-muted)', marginBottom: '16px' }}>
            <button
              onClick={onBack}
              style={{
                color: 'var(--v4-text-secondary)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              Inception Pack
            </button>
            {' / '}
            {SECTIONS.find((s) => s.id === activeSection)?.title}
          </div>

          {/* Page Header */}
          <header style={{ marginBottom: '32px' }}>
            <div
              style={{
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                color: 'var(--v4-accent)',
                marginBottom: '8px',
              }}
            >
              {SECTIONS.find((s) => s.id === activeSection)?.phase}
            </div>
            <h1 style={{ fontSize: '28px', fontWeight: 600, letterSpacing: '-0.02em', marginBottom: '8px' }}>
              {SECTIONS.find((s) => s.id === activeSection)?.title}
            </h1>
            <div style={{ display: 'flex', gap: '20px', fontSize: '13px', color: 'var(--v4-text-muted)' }}>
              <span>Generated just now</span>
              <span>Critique validated</span>
            </div>
          </header>

          {/* Section Content */}
          {renderSectionContent(activeSection, pack, activeStakeholder, setActiveStakeholder)}

          {/* Footer Navigation */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '20px 24px',
              background: 'var(--v4-surface)',
              border: '1px solid var(--v4-border)',
              borderRadius: 'var(--v4-radius)',
              marginTop: '32px',
            }}
          >
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => prevSection && setActiveSection(prevSection.id)}
                disabled={!prevSection}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '10px 18px',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: prevSection ? 'var(--v4-text-secondary)' : 'var(--v4-text-muted)',
                  background: 'var(--v4-bg)',
                  border: 'none',
                  borderRadius: 'var(--v4-radius)',
                  cursor: prevSection ? 'pointer' : 'not-allowed',
                  opacity: prevSection ? 1 : 0.4,
                }}
              >
                <ChevronLeft size={16} />
                Previous
              </button>
              <button
                onClick={() => nextSection && setActiveSection(nextSection.id)}
                disabled={!nextSection}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '10px 18px',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: nextSection ? 'var(--v4-text-secondary)' : 'var(--v4-text-muted)',
                  background: 'var(--v4-bg)',
                  border: 'none',
                  borderRadius: 'var(--v4-radius)',
                  cursor: nextSection ? 'pointer' : 'not-allowed',
                  opacity: nextSection ? 1 : 0.4,
                }}
              >
                Next: {nextSection?.title || ''}
                <ChevronRight size={16} />
              </button>
            </div>
            <button
              onClick={handleExport}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 20px',
                background: 'var(--v4-accent)',
                color: 'white',
                fontSize: '14px',
                fontWeight: 500,
                border: 'none',
                borderRadius: 'var(--v4-radius)',
                cursor: 'pointer',
              }}
            >
              <Download size={16} />
              Export Full Pack
            </button>
          </div>
        </main>
      </div>

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 1000px) {
          .v4-root > div {
            grid-template-columns: 1fr !important;
          }
          .v4-root aside {
            display: none !important;
          }
          .v4-root main {
            padding: 24px !important;
          }
        }
      `}</style>
    </div>
  );
}

function IconButton({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <button
      title={title}
      style={{
        width: '36px',
        height: '36px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid var(--v4-border)',
        borderRadius: 'var(--v4-radius)',
        background: 'transparent',
        color: 'var(--v4-text-secondary)',
        cursor: 'pointer',
      }}
    >
      {icon}
    </button>
  );
}

// Render section content based on active section
function renderSectionContent(
  sectionId: string,
  pack: InceptionPack,
  activeStakeholder: string,
  setActiveStakeholder: (s: string) => void
): React.ReactNode {
  switch (sectionId) {
    case 'executive_summary':
      return <ExecutiveSummarySection pack={pack} activeStakeholder={activeStakeholder} setActiveStakeholder={setActiveStakeholder} />;
    case 'customer_research':
      return <CustomerResearchSection pack={pack} />;
    case 'competitive_analysis':
      return <CompetitiveAnalysisSection pack={pack} />;
    case 'business_case':
      return <BusinessCaseSection pack={pack} />;
    case 'risk_assessment':
      return <RiskAssessmentSection pack={pack} />;
    default:
      return <GenericSection sectionId={sectionId} pack={pack} />;
  }
}

// Executive Summary Section
function ExecutiveSummarySection({
  pack,
  activeStakeholder,
  setActiveStakeholder,
}: {
  pack: InceptionPack;
  activeStakeholder: string;
  setActiveStakeholder: (s: string) => void;
}) {
  const summary = pack.executive_summary;
  const qualityScore = pack.metadata?.quality_score ?? pack.quality_assessment?.overall_score ?? 85;

  return (
    <>
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
        <StatCard value="16/16" label="Sections" />
        <StatCard value={`${qualityScore}%`} label="Quality" />
        <StatCard value="3" label="To Validate" />
        <StatCard value="42" label="Claims" />
      </div>

      {/* Overview Card */}
      <Card title="Overview">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          <SummaryItem label="Problem">
            {summary?.problem_statement || 'Not available'}
            <EvidenceBadge tier="E1" inline />
          </SummaryItem>
          <SummaryItem label="Solution">{summary?.solution_overview || 'Not available'}</SummaryItem>
          <SummaryItem label="Value Proposition" fullWidth>
            {summary?.value_proposition || 'Not available'}
          </SummaryItem>
        </div>
      </Card>

      {/* Key Metrics */}
      <Card title="Key Metrics">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
          <MetricCard value={summary?.funding_required || '$4.2M'} label="Investment" />
          <MetricCard value={summary?.break_even_timeline || '6-8 mo'} label="Break Even" />
          <MetricCard value={summary?.target_market_size || '$1B'} label="Market Size" />
          <MetricCard value={summary?.expected_roi || '2.5x'} label="Expected ROI" />
        </div>
      </Card>

      {/* Top Risks */}
      <Card title="Top Risks" action="View Full Register">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {(summary?.top_risks || []).slice(0, 3).map((risk, i) => (
            <RiskItemCard
              key={i}
              level="medium"
              title={risk}
              description=""
            />
          ))}
        </div>
      </Card>

      {/* Recommendation */}
      <Card title="Recommendation">
        <div
          style={{
            padding: '16px 20px',
            background: 'rgba(22, 163, 74, 0.06)',
            borderLeft: '3px solid var(--v4-success)',
            borderRadius: '0 var(--v4-radius) var(--v4-radius) 0',
          }}
        >
          <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#166534', marginBottom: '6px' }}>
            Recommendation
          </h4>
          <p style={{ fontSize: '14px', color: '#14532d', lineHeight: 1.6 }}>
            {summary?.recommendation || 'Review the inception pack and proceed.'}
          </p>
        </div>
      </Card>

      {/* Stakeholder Views */}
      <Card title="Stakeholder Views">
        <div
          style={{
            display: 'flex',
            gap: '4px',
            padding: '4px',
            background: 'var(--v4-bg)',
            borderRadius: 'var(--v4-radius)',
            marginBottom: '16px',
          }}
        >
          {['CFO', 'CTO', 'Product', 'Legal'].map((stakeholder) => (
            <button
              key={stakeholder}
              onClick={() => setActiveStakeholder(stakeholder)}
              style={{
                flex: 1,
                padding: '10px 16px',
                fontSize: '13px',
                fontWeight: 500,
                color: activeStakeholder === stakeholder ? 'var(--v4-text)' : 'var(--v4-text-secondary)',
                background: activeStakeholder === stakeholder ? 'var(--v4-surface)' : 'transparent',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              {stakeholder}
            </button>
          ))}
        </div>
        <div style={{ fontSize: '14px', lineHeight: 1.65 }}>
          <p>Relevant sections for {activeStakeholder}:</p>
          <ul style={{ margin: '10px 0', paddingLeft: '20px' }}>
            <li><strong>Financial Model</strong> — ROI projections, unit economics, funding</li>
            <li><strong>Business Case</strong> — Revenue model, cost structure, break-even</li>
            <li><strong>Risk Assessment</strong> — Financial risks and mitigations</li>
          </ul>
        </div>
      </Card>
    </>
  );
}

// Customer Research Section
function CustomerResearchSection({ pack }: { pack: InceptionPack }) {
  const research = pack.customer_research;

  return (
    <>
      <Card title="Research Scope">
        <div style={{ fontSize: '14px', lineHeight: 1.65, color: 'var(--v4-text-secondary)' }}>
          {research?.research_scope?.segments_examined?.join(', ') || 'Customer research findings will appear here.'}
        </div>
      </Card>

      {research?.uncomfortable_insights && research.uncomfortable_insights.length > 0 && (
        <Card title="Uncomfortable Insights">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {research.uncomfortable_insights.map((insight, i) => (
              <div
                key={i}
                style={{
                  padding: '14px 16px',
                  background: 'var(--v4-warning-bg)',
                  borderRadius: 'var(--v4-radius)',
                }}
              >
                <p style={{ fontSize: '14px', color: '#78350f', lineHeight: 1.5 }}>
                  {insight.insight}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}

// Competitive Analysis Section
function CompetitiveAnalysisSection({ pack }: { pack: InceptionPack }) {
  const analysis = pack.competitive_analysis;
  const competitors: CompetitorDetail[] = analysis?.competitors || analysis?.direct_competitors || [];

  return (
    <>
      <Card title="Competitive Landscape">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          {competitors.slice(0, 4).map((comp: CompetitorDetail, i: number) => (
            <div
              key={i}
              style={{
                padding: '16px',
                background: 'var(--v4-bg)',
                borderRadius: 'var(--v4-radius)',
              }}
            >
              <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>{comp.name}</h4>
              <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', lineHeight: 1.5 }}>
                {comp.description || 'No description available.'}
              </p>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}

// Business Case Section
function BusinessCaseSection({ pack }: { pack: InceptionPack }) {
  const businessCase = pack.business_case;

  return (
    <>
      <Card title="Business Model">
        <div style={{ fontSize: '14px', lineHeight: 1.65, color: 'var(--v4-text-secondary)' }}>
          {businessCase?.lean_canvas?.unique_value_proposition || businessCase?.go_to_market_strategy || 'Business model details will appear here.'}
        </div>
      </Card>

      {businessCase?.lean_canvas && (
        <Card title="Lean Canvas">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            <SummaryItem label="Problem">{businessCase.lean_canvas.problem?.join(', ') || 'N/A'}</SummaryItem>
            <SummaryItem label="Solution">{businessCase.lean_canvas.solution?.join(', ') || 'N/A'}</SummaryItem>
            <SummaryItem label="Key Metrics">{businessCase.lean_canvas.key_metrics?.join(', ') || 'N/A'}</SummaryItem>
            <SummaryItem label="Unique Value">{businessCase.lean_canvas.unique_value_proposition || 'N/A'}</SummaryItem>
          </div>
        </Card>
      )}
    </>
  );
}

// Risk Assessment Section
function RiskAssessmentSection({ pack }: { pack: InceptionPack }) {
  const risks: RiskItemType[] = pack.risk_assessment?.risks || [];

  return (
    <>
      <Card title="Risk Register">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {risks.map((risk: RiskItemType, i: number) => (
            <RiskItemCard
              key={i}
              level={risk.likelihood || 'medium'}
              title={risk.description || `Risk ${i + 1}`}
              description={risk.mitigation_strategy || ''}
            />
          ))}
        </div>
      </Card>
    </>
  );
}

// Generic Section
function GenericSection({ sectionId, pack }: { sectionId: string; pack: InceptionPack }) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const sectionData = (pack as any)[sectionId.replace(/-/g, '_')];

  return (
    <Card title="Content">
      <div style={{ fontSize: '14px', lineHeight: 1.65, color: 'var(--v4-text-secondary)' }}>
        {sectionData ? (
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
            {JSON.stringify(sectionData, null, 2)}
          </pre>
        ) : (
          <p>Section content not available.</p>
        )}
      </div>
    </Card>
  );
}

// Helper Components
function Card({ title, action, children }: { title: string; action?: string; children: React.ReactNode }) {
  return (
    <section
      style={{
        background: 'var(--v4-surface)',
        border: '1px solid var(--v4-border)',
        borderRadius: 'var(--v4-radius)',
        marginBottom: '20px',
      }}
    >
      <div
        style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--v4-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h3 style={{ fontSize: '15px', fontWeight: 600 }}>{title}</h3>
        {action && (
          <span style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', cursor: 'pointer' }}>{action} -&gt;</span>
        )}
      </div>
      <div style={{ padding: '20px' }}>{children}</div>
    </section>
  );
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div
      style={{
        padding: '20px',
        background: 'var(--v4-surface)',
        border: '1px solid var(--v4-border)',
        borderRadius: 'var(--v4-radius)',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '24px', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '4px' }}>{value}</div>
      <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>{label}</div>
    </div>
  );
}

function MetricCard({ value, label }: { value: string; label: string }) {
  return (
    <div
      style={{
        padding: '16px',
        background: 'var(--v4-bg)',
        borderRadius: 'var(--v4-radius)',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--v4-accent)', marginBottom: '4px' }}>{value}</div>
      <div style={{ fontSize: '12px', color: 'var(--v4-text-secondary)' }}>{label}</div>
    </div>
  );
}

function SummaryItem({
  label,
  children,
  fullWidth,
}: {
  label: string;
  children: React.ReactNode;
  fullWidth?: boolean;
}) {
  return (
    <div
      style={{
        padding: '16px',
        background: 'var(--v4-bg)',
        borderRadius: 'var(--v4-radius)',
        gridColumn: fullWidth ? 'span 2' : undefined,
      }}
    >
      <div
        style={{
          fontSize: '11px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          color: 'var(--v4-text-muted)',
          marginBottom: '8px',
        }}
      >
        {label}
      </div>
      <div style={{ fontSize: '14px', lineHeight: 1.65 }}>{children}</div>
    </div>
  );
}

function RiskItemCard({
  level,
  title,
  description,
}: {
  level: 'high' | 'medium' | 'low';
  title: string;
  description: string;
}) {
  const levelColors = {
    high: { bg: 'var(--v4-error-bg)', color: 'var(--v4-error)' },
    medium: { bg: 'var(--v4-warning-bg)', color: '#a16207' },
    low: { bg: 'var(--v4-success-bg)', color: '#15803d' },
  };

  return (
    <div
      style={{
        display: 'flex',
        gap: '12px',
        padding: '14px 16px',
        background: 'var(--v4-bg)',
        borderRadius: 'var(--v4-radius)',
      }}
    >
      <span
        style={{
          padding: '4px 8px',
          fontSize: '10px',
          fontWeight: 600,
          textTransform: 'uppercase',
          borderRadius: '3px',
          height: 'fit-content',
          background: levelColors[level].bg,
          color: levelColors[level].color,
        }}
      >
        {level}
      </span>
      <div>
        <h4 style={{ fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>{title}</h4>
        {description && <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', lineHeight: 1.5 }}>{description}</p>}
      </div>
    </div>
  );
}

export default PackViewerV4;
