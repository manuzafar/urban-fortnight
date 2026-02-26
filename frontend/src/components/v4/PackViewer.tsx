/**
 * V4 Pack Viewer Component
 * Results display with 16-section navigation and stakeholder views
 */

import { useState } from 'react';
import { Share2, Printer, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { QualityScore } from './QualityScore';
import { SectionNav, type NavSection } from './SectionNav';
import { EvidenceBadge, EvidenceLegend } from './EvidenceBadge';
import { MermaidDiagram } from '../MermaidDiagram';
import type { InceptionPack, RiskItem as RiskItemType, RiskMatrixItem, CompetitorDetail } from '../../types/api';
import '../../styles/theme-v4.css';

interface PackViewerV4Props {
  pack: InceptionPack;
  sessionId: string;
  onBack: () => void;
}

// Section definitions - IDs must match the switch cases in renderSectionContent
const SECTIONS: NavSection[] = [
  { id: 'executive_summary', number: '01', title: 'Executive Summary', phase: 'Overview', status: 'done' },
  { id: 'customer_research', number: '02', title: 'Customer Research', phase: 'Discovery', status: 'done' },
  { id: 'competitive_analysis', number: '03', title: 'Competitive Analysis', phase: 'Discovery', status: 'done' },
  { id: 'personas', number: '04', title: 'Personas', phase: 'Discovery', status: 'done' },
  { id: 'business_case', number: '05', title: 'Business Case', phase: 'Strategy', status: 'done' },
  { id: 'gtm_strategy', number: '06', title: 'Go-to-Market', phase: 'Strategy', status: 'done' },
  { id: 'financial_model', number: '07', title: 'Financial Model', phase: 'Strategy', status: 'warn' },
  { id: 'product_requirements', number: '08', title: 'Product Requirements', phase: 'Delivery', status: 'done' },
  { id: 'technical_architecture', number: '09', title: 'Tech Architecture', phase: 'Delivery', status: 'done' },
  { id: 'legal_regulatory', number: '10', title: 'Legal & Regulatory', phase: 'Delivery', status: 'done' },
  { id: 'risk_assessment', number: '11', title: 'Risk Assessment', phase: 'Delivery', status: 'warn' },
  { id: 'wireframes', number: '12', title: 'Wireframes', phase: 'Design', status: 'done' },
  { id: 'prototype', number: '13', title: 'Prototype', phase: 'Design', status: 'done' },
  { id: 'stakeholder_views', number: '14', title: 'Stakeholder Views', phase: 'Synthesis', status: 'done' },
  { id: 'validation_playbook', number: '15', title: 'Validation Playbook', phase: 'Synthesis', status: 'done' },
  { id: 'quality_assessment', number: '16', title: 'Quality Assessment', phase: 'Quality', status: 'warn' },
];

// Helper to normalize quality score to percentage (0-100)
function normalizeScore(score: number | undefined | null): number {
  if (score === undefined || score === null) return 85;
  // If score is between 0 and 1, it's a decimal - convert to percentage
  if (score > 0 && score <= 1) return Math.round(score * 100);
  // Otherwise assume it's already a percentage
  return Math.round(score);
}

export function PackViewerV4({ pack, sessionId, onBack }: PackViewerV4Props) {
  const [activeSection, setActiveSection] = useState('executive_summary');
  const [activeStakeholder, setActiveStakeholder] = useState('CFO');

  const qualityScore = normalizeScore(pack.metadata?.quality_score ?? pack.quality_assessment?.overall_score);
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
    case 'personas':
      return <PersonasSection pack={pack} />;
    case 'business_case':
      return <BusinessCaseSection pack={pack} />;
    case 'gtm_strategy':
      return <GTMSection pack={pack} />;
    case 'financial_model':
      return <FinancialModelSection pack={pack} />;
    case 'product_requirements':
      return <PRDSection pack={pack} />;
    case 'technical_architecture':
      return <TechArchitectureSection pack={pack} />;
    case 'legal_regulatory':
      return <LegalRegulatorySection pack={pack} />;
    case 'risk_assessment':
      return <RiskAssessmentSection pack={pack} />;
    case 'wireframes':
      return <WireframesSection pack={pack} />;
    case 'prototype':
      return <PrototypeSection pack={pack} />;
    case 'stakeholder_views':
      return <StakeholderViewsSection pack={pack} />;
    case 'validation_playbook':
      return <ValidationPlaybookSection pack={pack} />;
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
  const qualityScore = normalizeScore(pack.metadata?.quality_score ?? pack.quality_assessment?.overall_score);
  const claimsCount = pack.cross_reference_index?.claims?.length || 0;
  const toValidateCount = pack.validation_playbook?.experiments?.length || pack.validation_playbook?.validation_experiments?.length || 0;

  // Stakeholder-specific section recommendations
  const stakeholderSections: Record<string, Array<{ section: string; description: string }>> = {
    CFO: [
      { section: 'Financial Model', description: 'ROI projections, unit economics, funding requirements' },
      { section: 'Business Case', description: 'Revenue model, cost structure, break-even analysis' },
      { section: 'Risk Assessment', description: 'Financial risks and mitigation strategies' },
    ],
    CTO: [
      { section: 'Tech Architecture', description: 'System design, technology stack, scalability' },
      { section: 'Product Requirements', description: 'Technical requirements, integrations, APIs' },
      { section: 'Risk Assessment', description: 'Technical risks, security considerations' },
    ],
    Product: [
      { section: 'Product Requirements', description: 'User stories, epics, feature prioritization' },
      { section: 'Customer Research', description: 'User needs, pain points, validation findings' },
      { section: 'Personas', description: 'Target user profiles, jobs to be done' },
      { section: 'Wireframes', description: 'UI/UX concepts, user flows' },
    ],
    Legal: [
      { section: 'Legal & Regulatory', description: 'Compliance requirements, regulations, licensing' },
      { section: 'Risk Assessment', description: 'Legal risks, IP considerations' },
      { section: 'Tech Architecture', description: 'Data protection, security architecture' },
    ],
  };

  const currentSections = stakeholderSections[activeStakeholder] || stakeholderSections['CFO'];

  return (
    <>
      {/* Product Header */}
      {(summary?.product_name || summary?.tagline) && (
        <Card title="Product Identity">
          <div style={{ marginBottom: '12px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px', letterSpacing: '-0.02em' }}>
              {summary.product_name}
            </h2>
            {summary.tagline && (
              <p style={{ fontSize: '16px', color: 'var(--v4-text-secondary)', fontStyle: 'italic', margin: 0 }}>
                "{summary.tagline}"
              </p>
            )}
          </div>
        </Card>
      )}

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
        <StatCard value="16/16" label="Sections" />
        <StatCard value={`${qualityScore}%`} label="Quality" />
        <StatCard value={String(toValidateCount)} label="To Validate" />
        <StatCard value={String(claimsCount || 42)} label="Claims" />
      </div>

      {/* Overview Card */}
      <Card title="Problem & Solution">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          <SummaryItem label="Problem Statement">
            {summary?.problem_statement || 'Not available'}
            <EvidenceBadge tier="E1" inline />
          </SummaryItem>
          <SummaryItem label="Solution Overview">{summary?.solution_overview || 'Not available'}</SummaryItem>
          <SummaryItem label="Value Proposition" fullWidth>
            {summary?.value_proposition || 'Not available'}
          </SummaryItem>
        </div>
      </Card>

      {/* Target Market */}
      {(summary?.target_users || summary?.target_market_size) && (
        <Card title="Target Market">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {summary.target_users && summary.target_users.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '10px' }}>Target Users</h5>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {summary.target_users.map((user, i) => (
                    <span key={i} style={{ padding: '6px 12px', fontSize: '13px', background: 'var(--v4-bg)', borderRadius: '4px' }}>{user}</span>
                  ))}
                </div>
              </div>
            )}
            {summary.target_market_size && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '10px' }}>Market Size</h5>
                <p style={{ fontSize: '20px', fontWeight: 700, color: 'var(--v4-accent)', margin: 0 }}>{summary.target_market_size}</p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Competitive Position */}
      {(summary?.key_differentiators || summary?.competitive_landscape) && (
        <Card title="Competitive Position">
          {summary.competitive_landscape && (
            <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, marginBottom: '16px' }}>
              {summary.competitive_landscape}
            </p>
          )}
          {summary.key_differentiators && summary.key_differentiators.length > 0 && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '10px' }}>Key Differentiators</h5>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {summary.key_differentiators.map((diff, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', padding: '10px 12px', background: 'var(--v4-success-bg)', borderRadius: 'var(--v4-radius)' }}>
                    <span style={{ color: 'var(--v4-success)', fontSize: '16px' }}>✓</span>
                    <span style={{ fontSize: '14px', color: '#166534' }}>{diff}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Financial Summary */}
      <Card title="Financial Summary">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
          <MetricCard value={summary?.funding_required || 'N/A'} label="Investment Required" />
          <MetricCard value={summary?.break_even_timeline || 'N/A'} label="Break Even" />
          <MetricCard value={summary?.target_market_size || 'N/A'} label="Market Size" />
          <MetricCard value={summary?.expected_roi || 'N/A'} label="Expected ROI" />
        </div>
        {(summary?.revenue_model || summary?.financial_projections) && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {summary.revenue_model && (
              <div style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Revenue Model</h5>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{summary.revenue_model}</p>
              </div>
            )}
            {summary.financial_projections && (
              <div style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Financial Projections</h5>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{summary.financial_projections}</p>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Go-to-Market */}
      {(summary?.gtm_strategy || summary?.key_milestones) && (
        <Card title="Go-to-Market">
          {summary.gtm_strategy && (
            <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, marginBottom: '16px' }}>
              {summary.gtm_strategy}
            </p>
          )}
          {summary.key_milestones && summary.key_milestones.length > 0 && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '10px' }}>Key Milestones</h5>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {summary.key_milestones.map((milestone, i) => (
                  <span key={i} style={{ padding: '6px 12px', fontSize: '12px', background: 'var(--v4-accent)', color: 'white', borderRadius: '4px' }}>{milestone}</span>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Success Metrics */}
      {summary?.success_metrics && summary.success_metrics.length > 0 && (
        <Card title="Success Metrics">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
            {summary.success_metrics.map((metric, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--v4-accent)' }}></span>
                <span style={{ fontSize: '13px', color: 'var(--v4-text-secondary)' }}>{metric}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Top Risks */}
      <Card title="Top Risks">
        {(summary?.top_risks && summary.top_risks.length > 0) ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {summary.top_risks.slice(0, 3).map((risk, i) => (
              <RiskItemCard
                key={i}
                level={i === 0 ? 'high' : 'medium'}
                title={risk}
                description=""
              />
            ))}
          </div>
        ) : (
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No risks identified.</p>
        )}
      </Card>

      {/* Regulatory Summary */}
      {summary?.regulatory_summary && (
        <Card title="Regulatory Summary">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, margin: 0 }}>
            {summary.regulatory_summary}
          </p>
        </Card>
      )}

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
            Strategic Recommendation
          </h4>
          <p style={{ fontSize: '14px', color: '#14532d', lineHeight: 1.6, margin: 0 }}>
            {summary?.recommendation || 'Review the inception pack and proceed with validation.'}
          </p>
        </div>
      </Card>

      {/* Stakeholder Quick Links */}
      <Card title="Stakeholder Quick Links">
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
                color: activeStakeholder === stakeholder ? 'white' : 'var(--v4-text-secondary)',
                background: activeStakeholder === stakeholder ? 'var(--v4-accent)' : 'transparent',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {stakeholder}
            </button>
          ))}
        </div>
        <div style={{ fontSize: '14px', lineHeight: 1.65 }}>
          <p style={{ marginBottom: '12px', color: 'var(--v4-text-muted)' }}>
            Recommended sections for <strong style={{ color: 'var(--v4-text)' }}>{activeStakeholder}</strong>:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {currentSections.map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', padding: '10px 12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--v4-accent)', marginTop: '6px', flexShrink: 0 }}></span>
                <div>
                  <strong style={{ fontSize: '14px' }}>{item.section}</strong>
                  <span style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}> — {item.description}</span>
                </div>
              </div>
            ))}
          </div>
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

  // Helper to get competitor description from available fields
  const getCompetitorInfo = (comp: CompetitorDetail): string => {
    if (comp.description) return comp.description;
    if (comp.strengths && comp.strengths.length > 0) {
      return `Strengths: ${comp.strengths.slice(0, 2).join(', ')}`;
    }
    if (comp.market_share) return `Market share: ${comp.market_share}`;
    if (comp.differentiation_opportunity) return comp.differentiation_opportunity;
    return 'Competitor identified';
  };

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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600 }}>{comp.name}</h4>
                {comp.threat_level && (
                  <span
                    style={{
                      fontSize: '10px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      padding: '2px 6px',
                      borderRadius: '3px',
                      background: comp.threat_level === 'high' ? 'var(--v4-error-bg)' : comp.threat_level === 'medium' ? 'var(--v4-warning-bg)' : 'var(--v4-success-bg)',
                      color: comp.threat_level === 'high' ? 'var(--v4-error)' : comp.threat_level === 'medium' ? '#a16207' : 'var(--v4-success)',
                    }}
                  >
                    {comp.threat_level}
                  </span>
                )}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', lineHeight: 1.5, marginBottom: comp.weaknesses?.length ? '8px' : 0 }}>
                {getCompetitorInfo(comp)}
              </p>
              {comp.weaknesses && comp.weaknesses.length > 0 && (
                <p style={{ fontSize: '12px', color: 'var(--v4-text-muted)', lineHeight: 1.4 }}>
                  Weaknesses: {comp.weaknesses.slice(0, 2).join(', ')}
                </p>
              )}
            </div>
          ))}
        </div>
      </Card>

      {analysis?.market_gaps && analysis.market_gaps.length > 0 && (
        <Card title="Market Gaps">
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {analysis.market_gaps.map((gap, i) => (
              <li key={i} style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.6, marginBottom: '8px' }}>
                {gap}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {(analysis?.competitive_moat || analysis?.competitive_moats) && (
        <Card title="Competitive Moats">
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {(analysis.competitive_moat || analysis.competitive_moats || []).map((moat, i) => (
              <li key={i} style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.6, marginBottom: '8px' }}>
                {moat}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}

// Personas Section
function PersonasSection({ pack }: { pack: InceptionPack }) {
  const personas = pack.detailed_personas?.personas || [];
  const keyInsights = pack.detailed_personas?.key_insights || [];

  if (personas.length === 0) {
    return (
      <Card title="Personas">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No persona data available.</p>
      </Card>
    );
  }

  return (
    <>
      {personas.map((persona, i) => (
        <Card key={i} title={persona.name}>
          <div style={{ marginBottom: '16px' }}>
            <span
              style={{
                display: 'inline-block',
                padding: '4px 10px',
                fontSize: '12px',
                fontWeight: 500,
                background: 'var(--v4-accent)',
                color: 'white',
                borderRadius: '100px',
                marginRight: '8px',
              }}
            >
              {persona.role}
            </span>
            {persona.demographics && (
              <span style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}>
                {persona.demographics.age_range} · {persona.demographics.location}
              </span>
            )}
          </div>

          {persona.quote && (
            <blockquote
              style={{
                margin: '0 0 16px 0',
                padding: '12px 16px',
                background: 'var(--v4-bg)',
                borderLeft: '3px solid var(--v4-accent)',
                borderRadius: '0 var(--v4-radius) var(--v4-radius) 0',
                fontStyle: 'italic',
                fontSize: '14px',
                color: 'var(--v4-text-secondary)',
              }}
            >
              "{persona.quote}"
            </blockquote>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {persona.goals && persona.goals.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Goals</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {persona.goals.slice(0, 3).map((goal, j) => (
                    <li key={j} style={{ marginBottom: '4px' }}>{goal}</li>
                  ))}
                </ul>
              </div>
            )}
            {persona.pain_points && persona.pain_points.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Pain Points</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {persona.pain_points.slice(0, 3).map((pain, j) => (
                    <li key={j} style={{ marginBottom: '4px' }}>{pain}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {persona.jobs_to_be_done && persona.jobs_to_be_done.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Jobs to Be Done</h5>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {persona.jobs_to_be_done.slice(0, 3).map((job, j) => (
                  <div key={j} style={{ padding: '10px 12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', fontSize: '13px' }}>
                    <span style={{ fontWeight: 500 }}>{job.job}</span>
                    {job.importance && (
                      <span style={{ marginLeft: '8px', fontSize: '11px', color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>
                        {job.importance}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      ))}

      {keyInsights.length > 0 && (
        <Card title="Key Insights">
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {keyInsights.map((insight, i) => (
              <li key={i} style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.6, marginBottom: '8px' }}>
                {insight}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}

// Business Case Section
function BusinessCaseSection({ pack }: { pack: InceptionPack }) {
  const businessCase = pack.business_case;
  const canvas = businessCase?.lean_canvas;

  return (
    <>
      {/* Lean Canvas - Full Grid */}
      {canvas && (
        <Card title="Lean Canvas">
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(5, 1fr)',
              gap: '1px',
              background: 'var(--v4-border)',
              border: '1px solid var(--v4-border)',
              borderRadius: 'var(--v4-radius)',
              overflow: 'hidden',
            }}
          >
            {/* Row 1 */}
            <CanvasCell label="Problem" items={canvas.problem} rowSpan={2} />
            <CanvasCell label="Solution" items={canvas.solution} />
            <CanvasCell label="Unique Value Proposition" text={canvas.unique_value_proposition} rowSpan={2} />
            <CanvasCell label="Unfair Advantage" text={canvas.unfair_advantage} />
            <CanvasCell label="Customer Segments" items={canvas.customer_segments} rowSpan={2} />

            {/* Row 2 */}
            <CanvasCell label="Key Metrics" items={canvas.key_metrics} />
            <CanvasCell label="Channels" items={canvas.channels} />

            {/* Row 3 - Full width */}
            <div style={{ gridColumn: 'span 2', background: 'var(--v4-surface)', padding: '12px' }}>
              <div style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Cost Structure</div>
              <div style={{ fontSize: '13px', color: 'var(--v4-text-secondary)' }}>{canvas.cost_structure?.join(', ') || 'N/A'}</div>
            </div>
            <div style={{ gridColumn: 'span 3', background: 'var(--v4-surface)', padding: '12px' }}>
              <div style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Revenue Streams</div>
              <div style={{ fontSize: '13px', color: 'var(--v4-text-secondary)' }}>{canvas.revenue_streams?.join(', ') || 'N/A'}</div>
            </div>
          </div>
        </Card>
      )}

      {/* Financial Projections */}
      <Card title="Financial Projections">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          <SummaryItem label="Year 1 Projection">{businessCase?.year_1_projection || 'N/A'}</SummaryItem>
          <SummaryItem label="Year 3 Projection">{businessCase?.year_3_projection || 'N/A'}</SummaryItem>
          <SummaryItem label="Break-Even Analysis">{businessCase?.break_even_analysis || 'N/A'}</SummaryItem>
          <SummaryItem label="Funding Requirement">{businessCase?.funding_requirement || 'N/A'}</SummaryItem>
          <SummaryItem label="ROI Analysis" fullWidth>{businessCase?.roi_analysis || 'N/A'}</SummaryItem>
        </div>
      </Card>

      {/* Revenue Streams Detail */}
      {businessCase?.revenue_streams && businessCase.revenue_streams.length > 0 && (
        <Card title="Revenue Streams">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {businessCase.revenue_streams.map((stream, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 600 }}>{stream.name}</h4>
                  {stream.estimated_contribution && (
                    <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--v4-accent)' }}>{stream.estimated_contribution}</span>
                  )}
                </div>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginBottom: '4px' }}>{stream.description}</p>
                {stream.pricing_model && (
                  <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>Pricing: {stream.pricing_model}</span>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Go-to-Market Strategy */}
      {businessCase?.go_to_market_strategy && (
        <Card title="Go-to-Market Strategy">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>
            {businessCase.go_to_market_strategy}
          </p>
        </Card>
      )}

      {/* Key Partnerships */}
      {businessCase?.key_partnerships && businessCase.key_partnerships.length > 0 && (
        <Card title="Key Partnerships">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {businessCase.key_partnerships.map((partner, i) => (
              <span
                key={i}
                style={{
                  padding: '6px 12px',
                  fontSize: '13px',
                  background: 'var(--v4-bg)',
                  borderRadius: '100px',
                  color: 'var(--v4-text-secondary)',
                }}
              >
                {partner}
              </span>
            ))}
          </div>
        </Card>
      )}

      {/* Risks and Mitigations */}
      {businessCase?.risks_and_mitigations && businessCase.risks_and_mitigations.length > 0 && (
        <Card title="Risks & Mitigations">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {businessCase.risks_and_mitigations.map((item, i) => (
              <div key={i} style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--v4-text)', marginBottom: '4px' }}>
                  {item.risk}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
                  Mitigation: {item.mitigation}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}

// Helper component for Lean Canvas cells
function CanvasCell({ label, items, text, rowSpan }: { label: string; items?: string[]; text?: string; rowSpan?: number }) {
  return (
    <div
      style={{
        background: 'var(--v4-surface)',
        padding: '12px',
        gridRow: rowSpan ? `span ${rowSpan}` : undefined,
      }}
    >
      <div style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>
        {label}
      </div>
      {text ? (
        <div style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', lineHeight: 1.5 }}>{text}</div>
      ) : items && items.length > 0 ? (
        <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
          {items.slice(0, 4).map((item, i) => (
            <li key={i} style={{ marginBottom: '2px' }}>{item}</li>
          ))}
        </ul>
      ) : (
        <div style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}>N/A</div>
      )}
    </div>
  );
}

// Go-to-Market Section
function GTMSection({ pack }: { pack: InceptionPack }) {
  const gtm = pack.gtm_strategy;

  if (!gtm) {
    return (
      <Card title="Go-to-Market Strategy">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No GTM strategy data available.</p>
      </Card>
    );
  }

  return (
    <>
      {/* Positioning Statement */}
      {gtm.positioning_statement && (
        <Card title="Positioning Statement">
          <p style={{ fontSize: '15px', color: 'var(--v4-text)', lineHeight: 1.7, fontStyle: 'italic' }}>
            "{gtm.positioning_statement}"
          </p>
        </Card>
      )}

      {/* Target Segments */}
      {gtm.target_segments && gtm.target_segments.length > 0 && (
        <Card title="Target Segments">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {gtm.target_segments.map((segment, i) => (
              <span
                key={i}
                style={{
                  padding: '8px 14px',
                  fontSize: '13px',
                  background: 'var(--v4-bg)',
                  borderRadius: '100px',
                  color: 'var(--v4-text-secondary)',
                }}
              >
                {segment}
              </span>
            ))}
          </div>
        </Card>
      )}

      {/* Messaging Framework */}
      {gtm.messaging_framework && (
        <Card title="Messaging Framework">
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px' }}>{gtm.messaging_framework.headline}</h3>
            <p style={{ fontSize: '15px', color: 'var(--v4-text-secondary)' }}>{gtm.messaging_framework.subheadline}</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {gtm.messaging_framework.key_benefits && gtm.messaging_framework.key_benefits.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Key Benefits</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {gtm.messaging_framework.key_benefits.map((benefit, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{benefit}</li>
                  ))}
                </ul>
              </div>
            )}
            {gtm.messaging_framework.proof_points && gtm.messaging_framework.proof_points.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Proof Points</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {gtm.messaging_framework.proof_points.map((point, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Launch Phases */}
      {gtm.launch_phases && gtm.launch_phases.length > 0 && (
        <Card title="Launch Phases">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {gtm.launch_phases.map((phase, i) => (
              <div
                key={i}
                style={{
                  padding: '16px',
                  background: 'var(--v4-bg)',
                  borderRadius: 'var(--v4-radius)',
                  borderLeft: '3px solid var(--v4-accent)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 600 }}>{phase.phase_name}</h4>
                  <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)', background: 'var(--v4-surface)', padding: '4px 10px', borderRadius: '100px' }}>
                    {phase.duration}
                  </span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                  <div>
                    <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Objectives</h5>
                    <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                      {phase.objectives?.slice(0, 3).map((obj, j) => (
                        <li key={j} style={{ marginBottom: '2px' }}>{obj}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Key Activities</h5>
                    <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                      {phase.key_activities?.slice(0, 3).map((act, j) => (
                        <li key={j} style={{ marginBottom: '2px' }}>{act}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Success Metrics</h5>
                    <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                      {phase.success_metrics?.slice(0, 3).map((metric, j) => (
                        <li key={j} style={{ marginBottom: '2px' }}>{metric}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Channel Strategy */}
      {gtm.channel_strategy && gtm.channel_strategy.length > 0 && (
        <Card title="Channel Strategy">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {gtm.channel_strategy.map((channel, i) => (
              <div key={i} style={{ padding: '14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 600 }}>{channel.channel}</h4>
                  {channel.expected_roi && (
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--v4-success)' }}>{channel.expected_roi}</span>
                  )}
                </div>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginBottom: '8px' }}>{channel.purpose}</p>
                {channel.budget_allocation && (
                  <span style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>Budget: {channel.budget_allocation}</span>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Pricing Strategy */}
      {gtm.pricing_strategy && (
        <Card title="Pricing Strategy">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>
            {gtm.pricing_strategy}
          </p>
        </Card>
      )}

      {/* Partnership Approach */}
      {gtm.partnership_approach && (
        <Card title="Partnership Approach">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>
            {gtm.partnership_approach}
          </p>
        </Card>
      )}
    </>
  );
}

// Financial Model Section
function FinancialModelSection({ pack }: { pack: InceptionPack }) {
  const fm = pack.financial_model;

  if (!fm) {
    return (
      <Card title="Financial Model">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No financial model data available.</p>
      </Card>
    );
  }

  // Format currency
  const formatCurrency = (value: number) => {
    if (Math.abs(value) >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (Math.abs(value) >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  return (
    <>
      {/* Summary */}
      {fm.summary && (
        <Card title="Summary">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>
            {fm.summary}
          </p>
        </Card>
      )}

      {/* Financial Projections Table */}
      {fm.projections && fm.projections.length > 0 && (
        <Card title="Financial Projections">
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--v4-border)' }}>
                  <th style={{ textAlign: 'left', padding: '10px 12px', fontWeight: 600, color: 'var(--v4-text-muted)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Period</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', fontWeight: 600, color: 'var(--v4-text-muted)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Revenue</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', fontWeight: 600, color: 'var(--v4-text-muted)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Costs</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', fontWeight: 600, color: 'var(--v4-text-muted)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Profit</th>
                  <th style={{ textAlign: 'right', padding: '10px 12px', fontWeight: 600, color: 'var(--v4-text-muted)', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Cumulative</th>
                </tr>
              </thead>
              <tbody>
                {fm.projections.map((proj, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--v4-border)' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 500 }}>{proj.period}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', color: 'var(--v4-success)' }}>{formatCurrency(proj.revenue)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', color: 'var(--v4-text-secondary)' }}>{formatCurrency(proj.costs)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', color: proj.profit >= 0 ? 'var(--v4-success)' : 'var(--v4-error)', fontWeight: 500 }}>{formatCurrency(proj.profit)}</td>
                    <td style={{ padding: '10px 12px', textAlign: 'right', color: proj.cumulative_profit >= 0 ? 'var(--v4-success)' : 'var(--v4-error)' }}>{formatCurrency(proj.cumulative_profit)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Unit Economics */}
      {fm.unit_economics && fm.unit_economics.length > 0 && (
        <Card title="Unit Economics">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {fm.unit_economics.map((ue, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', marginBottom: '4px' }}>{ue.metric}</div>
                <div style={{ fontSize: '20px', fontWeight: 600, color: 'var(--v4-text)', marginBottom: '6px' }}>{ue.value}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                  <span style={{ color: 'var(--v4-text-muted)' }}>Benchmark: {ue.benchmark}</span>
                  <span style={{
                    color: ue.assessment?.toLowerCase().includes('good') || ue.assessment?.toLowerCase().includes('strong')
                      ? 'var(--v4-success)'
                      : ue.assessment?.toLowerCase().includes('poor') || ue.assessment?.toLowerCase().includes('weak')
                        ? 'var(--v4-error)'
                        : 'var(--v4-text-secondary)'
                  }}>{ue.assessment}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Sensitivity Analysis */}
      {fm.sensitivity_analysis && (
        <Card title="Sensitivity Analysis">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'rgba(22, 163, 74, 0.08)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-success)', marginBottom: '8px' }}>Optimistic</div>
              <div style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.5 }}>{fm.sensitivity_analysis.optimistic}</div>
            </div>
            <div style={{ padding: '16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Base Case</div>
              <div style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.5 }}>{fm.sensitivity_analysis.base_case}</div>
            </div>
            <div style={{ padding: '16px', background: 'rgba(220, 38, 38, 0.08)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-error)', marginBottom: '8px' }}>Pessimistic</div>
              <div style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.5 }}>{fm.sensitivity_analysis.pessimistic}</div>
            </div>
          </div>
        </Card>
      )}

      {/* Funding & Break-Even */}
      <Card title="Funding & Break-Even">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          <SummaryItem label="Funding Requirements">{fm.funding_requirements || 'N/A'}</SummaryItem>
          <SummaryItem label="Break-Even Analysis">{fm.break_even_analysis || 'N/A'}</SummaryItem>
        </div>
      </Card>

      {/* Assumptions */}
      {fm.assumptions && fm.assumptions.length > 0 && (
        <Card title="Key Assumptions">
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {fm.assumptions.map((assumption, i) => (
              <li key={i} style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.6, marginBottom: '8px' }}>
                {assumption}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}

// Product Requirements Section
function PRDSection({ pack }: { pack: InceptionPack }) {
  const prd = pack.product_requirements_document;

  if (!prd) {
    return (
      <Card title="Product Requirements">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No PRD data available.</p>
      </Card>
    );
  }

  const priorityColors: Record<string, { bg: string; color: string }> = {
    critical: { bg: 'var(--v4-error-bg)', color: 'var(--v4-error)' },
    high: { bg: 'rgba(234, 88, 12, 0.1)', color: '#c2410c' },
    medium: { bg: 'var(--v4-warning-bg)', color: '#a16207' },
    low: { bg: 'var(--v4-success-bg)', color: 'var(--v4-success)' },
  };

  return (
    <>
      {/* Product Overview */}
      {(prd.product_overview || prd.overview) && (
        <Card title="Product Overview">
          {prd.product_overview ? (
            <>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>{prd.product_overview.name}</h3>
              <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, marginBottom: '16px' }}>
                {prd.product_overview.vision}
              </p>
              {prd.product_overview.objectives && prd.product_overview.objectives.length > 0 && (
                <div>
                  <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Objectives</h5>
                  <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                    {prd.product_overview.objectives.map((obj, i) => (
                      <li key={i} style={{ marginBottom: '4px' }}>{obj}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>{prd.overview}</p>
          )}
        </Card>
      )}

      {/* Scope */}
      {(prd.scope || prd.scope_in || prd.scope_out) && (
        <Card title="Scope">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-success)', marginBottom: '8px' }}>In Scope</h5>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                {(prd.scope?.in_scope || prd.scope_in || []).map((item, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-error)', marginBottom: '8px' }}>Out of Scope</h5>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                {(prd.scope?.out_of_scope || prd.scope_out || []).map((item, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      )}

      {/* Statistics */}
      {prd.statistics && (
        <Card title="PRD Statistics">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
            <div style={{ padding: '12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--v4-accent)' }}>{prd.statistics.total_epics}</div>
              <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>Epics</div>
            </div>
            <div style={{ padding: '12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--v4-accent)' }}>{prd.statistics.total_stories}</div>
              <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>Stories</div>
            </div>
            <div style={{ padding: '12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--v4-accent)' }}>{prd.statistics.total_story_points}</div>
              <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>Story Points</div>
            </div>
            <div style={{ padding: '12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--v4-accent)' }}>{prd.statistics.total_functional_requirements}</div>
              <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>Requirements</div>
            </div>
          </div>
        </Card>
      )}

      {/* Epics & Stories */}
      {prd.epics && prd.epics.length > 0 && (
        <Card title="Epics & User Stories">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {prd.epics.map((epic, i) => (
              <div key={i} style={{ border: '1px solid var(--v4-border)', borderRadius: 'var(--v4-radius)', overflow: 'hidden' }}>
                <div style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderBottom: '1px solid var(--v4-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: 600 }}>{epic.title}</h4>
                    {epic.priority && (
                      <span style={{
                        padding: '2px 8px',
                        fontSize: '10px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        borderRadius: '3px',
                        background: priorityColors[epic.priority]?.bg || 'var(--v4-bg)',
                        color: priorityColors[epic.priority]?.color || 'var(--v4-text-muted)',
                      }}>
                        {epic.priority}
                      </span>
                    )}
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginTop: '6px' }}>{epic.description}</p>
                </div>
                {epic.stories && epic.stories.length > 0 && (
                  <div style={{ padding: '12px 16px' }}>
                    <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>
                      User Stories ({epic.stories.length})
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {epic.stories.slice(0, 5).map((story, j) => (
                        <div key={j} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', padding: '8px 10px', background: 'var(--v4-bg)', borderRadius: '4px' }}>
                          <div style={{ flex: 1 }}>
                            <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)', marginRight: '8px' }}>{story.id}</span>
                            <span style={{ fontSize: '13px' }}>{story.title}</span>
                          </div>
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                            {story.story_points && (
                              <span style={{ fontSize: '11px', padding: '2px 6px', background: 'var(--v4-surface)', borderRadius: '3px', color: 'var(--v4-text-muted)' }}>
                                {story.story_points} pts
                              </span>
                            )}
                            <span style={{
                              padding: '2px 6px',
                              fontSize: '9px',
                              fontWeight: 600,
                              textTransform: 'uppercase',
                              borderRadius: '3px',
                              background: priorityColors[story.priority]?.bg || 'var(--v4-bg)',
                              color: priorityColors[story.priority]?.color || 'var(--v4-text-muted)',
                            }}>
                              {story.priority}
                            </span>
                          </div>
                        </div>
                      ))}
                      {epic.stories.length > 5 && (
                        <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', textAlign: 'center', padding: '4px' }}>
                          +{epic.stories.length - 5} more stories
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Functional Requirements */}
      {prd.functional_requirements && prd.functional_requirements.length > 0 && (
        <Card title="Functional Requirements">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {prd.functional_requirements.slice(0, 8).map((req, i) => (
              <div key={i} style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                  <div>
                    <span style={{ fontSize: '11px', color: 'var(--v4-text-muted)', marginRight: '8px' }}>{req.id}</span>
                    <span style={{ fontSize: '14px', fontWeight: 500 }}>{req.title}</span>
                  </div>
                  <span style={{
                    padding: '2px 6px',
                    fontSize: '9px',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    borderRadius: '3px',
                    background: priorityColors[req.priority]?.bg || 'var(--v4-bg)',
                    color: priorityColors[req.priority]?.color || 'var(--v4-text-muted)',
                  }}>
                    {req.priority}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{req.description}</p>
              </div>
            ))}
            {prd.functional_requirements.length > 8 && (
              <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', textAlign: 'center', padding: '8px' }}>
                +{prd.functional_requirements.length - 8} more requirements
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Non-Functional Requirements */}
      {prd.non_functional_requirements && prd.non_functional_requirements.length > 0 && (
        <Card title="Non-Functional Requirements">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
            {prd.non_functional_requirements.slice(0, 6).map((req, i) => (
              <div key={i} style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-accent)', marginBottom: '4px' }}>{req.category}</div>
                <div style={{ fontSize: '13px', fontWeight: 500, marginBottom: '4px' }}>{req.title}</div>
                <div style={{ fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                  Target: <span style={{ fontWeight: 500 }}>{req.target}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}

// Tech Architecture Section
function TechArchitectureSection({ pack }: { pack: InceptionPack }) {
  const arch = pack.technical_architecture;

  if (!arch) {
    return (
      <Card title="Technical Architecture">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No technical architecture data available.</p>
      </Card>
    );
  }

  return (
    <>
      {/* Architecture Overview */}
      <Card title="Architecture Overview">
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <span style={{
              padding: '4px 12px',
              fontSize: '12px',
              fontWeight: 600,
              background: 'var(--v4-accent)',
              color: 'white',
              borderRadius: '4px',
            }}>
              {arch.architecture_style}
            </span>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>
            {arch.architecture_diagram_description}
          </p>
        </div>
        {arch.development_approach && (
          <div style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>
              Development Approach
            </h5>
            <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{arch.development_approach}</p>
          </div>
        )}
      </Card>

      {/* Technology Stack */}
      {arch.technology_stack && arch.technology_stack.length > 0 && (
        <Card title="Technology Stack">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {arch.technology_stack.map((tech, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-accent)' }}>
                    {tech.category}
                  </span>
                </div>
                <div style={{ fontSize: '15px', fontWeight: 600, marginBottom: '6px' }}>{tech.technology}</div>
                <p style={{ fontSize: '12px', color: 'var(--v4-text-secondary)', lineHeight: 1.5, margin: 0 }}>{tech.rationale}</p>
                {tech.alternatives_considered && tech.alternatives_considered.length > 0 && (
                  <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--v4-text-muted)' }}>
                    Alternatives: {tech.alternatives_considered.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* System Components */}
      {arch.system_components && arch.system_components.length > 0 && (
        <Card title="System Components">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {arch.system_components.map((component, i) => (
              <div key={i} style={{ border: '1px solid var(--v4-border)', borderRadius: 'var(--v4-radius)', overflow: 'hidden' }}>
                <div style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderBottom: '1px solid var(--v4-border)' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>{component.name}</h4>
                  <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{component.description}</p>
                </div>
                <div style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                    <div>
                      <h5 style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Responsibilities</h5>
                      <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                        {component.responsibilities.slice(0, 3).map((r, j) => <li key={j} style={{ marginBottom: '2px' }}>{r}</li>)}
                      </ul>
                    </div>
                    <div>
                      <h5 style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Technologies</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {component.technologies.map((t, j) => (
                          <span key={j} style={{ padding: '2px 8px', fontSize: '11px', background: 'var(--v4-bg)', borderRadius: '3px' }}>{t}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h5 style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Interfaces</h5>
                      <div style={{ fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                        {component.interfaces.slice(0, 3).join(', ')}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Integration Points */}
      {arch.integration_points && arch.integration_points.length > 0 && (
        <Card title="Integration Points">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {arch.integration_points.map((integration, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 600, margin: 0 }}>{integration.name}</h4>
                  <span style={{ padding: '2px 8px', fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', background: 'var(--v4-surface)', borderRadius: '3px', color: 'var(--v4-text-muted)' }}>
                    {integration.type}
                  </span>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--v4-text-secondary)', marginBottom: '8px' }}>{integration.description}</p>
                <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>
                  <strong>Auth:</strong> {integration.authentication} | <strong>Flow:</strong> {integration.data_flow}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Infrastructure & Deployment */}
      <Card title="Infrastructure & Deployment">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          <div>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Data Storage</h5>
            <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{arch.data_storage}</p>
          </div>
          <div>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Deployment Strategy</h5>
            <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{arch.deployment_strategy}</p>
          </div>
          <div>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Scalability Approach</h5>
            <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{arch.scalability_approach}</p>
          </div>
          <div>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Security Architecture</h5>
            <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{arch.security_architecture}</p>
          </div>
        </div>
        {arch.infrastructure_requirements && arch.infrastructure_requirements.length > 0 && (
          <div style={{ marginTop: '16px', padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Infrastructure Requirements</h5>
            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
              {arch.infrastructure_requirements.map((req, i) => <li key={i} style={{ marginBottom: '4px' }}>{req}</li>)}
            </ul>
          </div>
        )}
      </Card>

      {/* Technical Risks */}
      {arch.technical_risks && arch.technical_risks.length > 0 && (
        <Card title="Technical Risks">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {arch.technical_risks.map((risk, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', borderLeft: '3px solid var(--v4-warning)' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>{risk.risk}</h4>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>
                  <strong>Mitigation:</strong> {risk.mitigation}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Architecture Diagrams (Mermaid) */}
      {(arch.architecture_diagram_mermaid || arch.sequence_diagram_mermaid) && (
        <Card title="Architecture Diagrams">
          {arch.architecture_diagram_mermaid && (
            <div style={{ marginBottom: arch.sequence_diagram_mermaid ? '16px' : 0 }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>System Architecture</h5>
              <div style={{
                padding: '14px',
                background: 'var(--v4-bg)',
                borderRadius: 'var(--v4-radius)',
                overflow: 'auto',
              }}>
                <MermaidDiagram chart={arch.architecture_diagram_mermaid} />
              </div>
            </div>
          )}
          {arch.sequence_diagram_mermaid && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Sequence Diagram</h5>
              <div style={{
                padding: '14px',
                background: 'var(--v4-bg)',
                borderRadius: 'var(--v4-radius)',
                overflow: 'auto',
              }}>
                <MermaidDiagram chart={arch.sequence_diagram_mermaid} />
              </div>
            </div>
          )}
        </Card>
      )}
    </>
  );
}

// Legal & Regulatory Section
function LegalRegulatorySection({ pack }: { pack: InceptionPack }) {
  const legal = pack.legal_regulatory_review;

  if (!legal) {
    return (
      <Card title="Legal & Regulatory">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No legal & regulatory data available.</p>
      </Card>
    );
  }

  const riskLevelColors: Record<string, { bg: string; color: string }> = {
    critical: { bg: 'var(--v4-error-bg)', color: 'var(--v4-error)' },
    high: { bg: 'rgba(234, 88, 12, 0.1)', color: '#c2410c' },
    medium: { bg: 'var(--v4-warning-bg)', color: '#a16207' },
    low: { bg: 'var(--v4-success-bg)', color: 'var(--v4-success)' },
  };

  return (
    <>
      {/* Executive Summary */}
      {legal.executive_summary && (
        <Card title="Executive Summary">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>{legal.executive_summary}</p>
        </Card>
      )}

      {/* Overall Risk Assessment */}
      {legal.overall_risk_assessment && (
        <Card title="Overall Risk Assessment">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <span style={{
              padding: '6px 14px',
              fontSize: '13px',
              fontWeight: 600,
              textTransform: 'uppercase',
              borderRadius: '4px',
              background: riskLevelColors[legal.overall_risk_assessment.risk_level]?.bg || 'var(--v4-bg)',
              color: riskLevelColors[legal.overall_risk_assessment.risk_level]?.color || 'var(--v4-text)',
            }}>
              {legal.overall_risk_assessment.risk_level} Risk
            </span>
          </div>
          {legal.overall_risk_assessment.key_concerns && legal.overall_risk_assessment.key_concerns.length > 0 && (
            <div style={{ marginBottom: '12px' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Key Concerns</h5>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                {legal.overall_risk_assessment.key_concerns.map((concern, i) => <li key={i} style={{ marginBottom: '4px' }}>{concern}</li>)}
              </ul>
            </div>
          )}
          {legal.overall_risk_assessment.blocking_issues && legal.overall_risk_assessment.blocking_issues.length > 0 && (
            <div style={{ padding: '12px 14px', background: 'var(--v4-error-bg)', borderRadius: 'var(--v4-radius)', marginBottom: '12px' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-error)', marginBottom: '8px' }}>Blocking Issues</h5>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: '#b91c1c' }}>
                {legal.overall_risk_assessment.blocking_issues.map((issue, i) => <li key={i} style={{ marginBottom: '4px' }}>{issue}</li>)}
              </ul>
            </div>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            <div style={{ padding: '10px 12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
              <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', marginBottom: '4px' }}>Timeline Buffer</div>
              <div style={{ fontSize: '14px', fontWeight: 500 }}>{legal.overall_risk_assessment.recommended_timeline_buffer}</div>
            </div>
            <div style={{ padding: '10px 12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
              <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', marginBottom: '4px' }}>Budget Allocation</div>
              <div style={{ fontSize: '14px', fontWeight: 500 }}>{legal.overall_risk_assessment.recommended_budget_allocation}</div>
            </div>
          </div>
        </Card>
      )}

      {/* Applicable Regulations */}
      {legal.applicable_regulations && legal.applicable_regulations.length > 0 && (
        <Card title="Applicable Regulations">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {legal.applicable_regulations.map((reg, i) => (
              <div key={i} style={{ border: '1px solid var(--v4-border)', borderRadius: 'var(--v4-radius)', overflow: 'hidden' }}>
                <div style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderBottom: '1px solid var(--v4-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>{reg.name}</h4>
                    <span style={{
                      padding: '2px 8px',
                      fontSize: '10px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      borderRadius: '3px',
                      background: riskLevelColors[reg.impact_level]?.bg || 'var(--v4-bg)',
                      color: riskLevelColors[reg.impact_level]?.color || 'var(--v4-text-muted)',
                    }}>
                      {reg.impact_level} Impact
                    </span>
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{reg.description}</p>
                </div>
                <div style={{ padding: '12px 16px' }}>
                  <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>
                    <strong>Applicability:</strong> {reg.applicability}
                  </div>
                  {reg.compliance_requirements && reg.compliance_requirements.length > 0 && (
                    <div>
                      <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Compliance Requirements</h5>
                      <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                        {reg.compliance_requirements.slice(0, 4).map((req, j) => <li key={j} style={{ marginBottom: '2px' }}>{req}</li>)}
                      </ul>
                    </div>
                  )}
                  <div style={{ display: 'flex', gap: '16px', marginTop: '10px', fontSize: '11px', color: 'var(--v4-text-muted)' }}>
                    <span><strong>Timeline:</strong> {reg.estimated_compliance_timeline}</span>
                    <span><strong>Cost:</strong> {reg.estimated_compliance_cost}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Data Protection Requirements */}
      {legal.data_protection_requirements && legal.data_protection_requirements.length > 0 && (
        <Card title="Data Protection Requirements">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {legal.data_protection_requirements.map((dp, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '10px', color: 'var(--v4-accent)' }}>{dp.regulation}</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '10px' }}>
                  <div>
                    <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Data Types Covered</h5>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {dp.data_types_covered.map((dt, j) => (
                        <span key={j} style={{ padding: '2px 8px', fontSize: '11px', background: 'var(--v4-surface)', borderRadius: '3px' }}>{dt}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>User Rights</h5>
                    <div style={{ fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                      {dp.user_rights.slice(0, 4).join(', ')}
                    </div>
                  </div>
                </div>
                {dp.key_obligations && dp.key_obligations.length > 0 && (
                  <div>
                    <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Key Obligations</h5>
                    <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                      {dp.key_obligations.slice(0, 4).map((ob, j) => <li key={j} style={{ marginBottom: '2px' }}>{ob}</li>)}
                    </ul>
                  </div>
                )}
                <div style={{ marginTop: '10px', padding: '8px 10px', background: 'var(--v4-error-bg)', borderRadius: '4px', fontSize: '12px', color: '#b91c1c' }}>
                  <strong>Penalties:</strong> {dp.penalties_for_non_compliance}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Legal Risks */}
      {legal.legal_risks && legal.legal_risks.length > 0 && (
        <Card title="Legal Risks">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {legal.legal_risks.map((risk, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', borderLeft: `3px solid ${riskLevelColors[risk.severity]?.color || 'var(--v4-border)'}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div>
                    <span style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-accent)', marginRight: '8px' }}>{risk.risk_category}</span>
                    <span style={{
                      padding: '2px 6px',
                      fontSize: '9px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      borderRadius: '3px',
                      background: riskLevelColors[risk.severity]?.bg || 'var(--v4-bg)',
                      color: riskLevelColors[risk.severity]?.color || 'var(--v4-text-muted)',
                    }}>
                      {risk.severity}
                    </span>
                  </div>
                  {risk.legal_counsel_recommended && (
                    <span style={{ padding: '2px 6px', fontSize: '9px', fontWeight: 600, background: 'var(--v4-warning-bg)', color: '#a16207', borderRadius: '3px' }}>
                      Counsel Recommended
                    </span>
                  )}
                </div>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginBottom: '8px' }}>{risk.description}</p>
                {risk.mitigation_strategies && risk.mitigation_strategies.length > 0 && (
                  <div>
                    <h5 style={{ fontSize: '11px', fontWeight: 600, color: 'var(--v4-text-muted)', marginBottom: '4px' }}>Mitigation</h5>
                    <ul style={{ margin: 0, paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                      {risk.mitigation_strategies.slice(0, 3).map((m, j) => <li key={j}>{m}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Intellectual Property */}
      {legal.intellectual_property && legal.intellectual_property.length > 0 && (
        <Card title="Intellectual Property Considerations">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {legal.intellectual_property.map((ip, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-accent)' }}>{ip.ip_type}</span>
                  <span style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>{ip.priority}</span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginBottom: '8px' }}>{ip.description}</p>
                <div style={{ fontSize: '12px' }}>
                  <strong>Action:</strong> {ip.action_required}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', marginTop: '4px' }}>
                  Est. Cost: {ip.estimated_cost}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Licensing Requirements */}
      {legal.licensing_requirements && legal.licensing_requirements.length > 0 && (
        <Card title="Licensing Requirements">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {legal.licensing_requirements.map((lic, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>{lic.license_type}</h4>
                <div style={{ fontSize: '12px', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>
                  Issuing Authority: {lic.issuing_authority}
                </div>
                {lic.requirements && lic.requirements.length > 0 && (
                  <ul style={{ margin: '0 0 8px 0', paddingLeft: '14px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                    {lic.requirements.slice(0, 3).map((req, j) => <li key={j}>{req}</li>)}
                  </ul>
                )}
                <div style={{ display: 'flex', gap: '16px', fontSize: '11px', color: 'var(--v4-text-muted)' }}>
                  <span><strong>Timeline:</strong> {lic.timeline}</span>
                  <span><strong>Cost:</strong> {lic.cost}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Recommended Legal Structure & Next Steps */}
      <Card title="Recommendations">
        {legal.recommended_legal_structure && (
          <div style={{ marginBottom: '16px' }}>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Recommended Legal Structure</h5>
            <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', margin: 0 }}>{legal.recommended_legal_structure}</p>
          </div>
        )}
        {legal.next_steps && legal.next_steps.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Next Steps</h5>
            <ol style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
              {legal.next_steps.map((step, i) => <li key={i} style={{ marginBottom: '4px' }}>{step}</li>)}
            </ol>
          </div>
        )}
        {legal.ongoing_compliance_requirements && legal.ongoing_compliance_requirements.length > 0 && (
          <div>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Ongoing Compliance Requirements</h5>
            <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
              {legal.ongoing_compliance_requirements.map((req, i) => <li key={i} style={{ marginBottom: '4px' }}>{req}</li>)}
            </ul>
          </div>
        )}
      </Card>

      {/* Industry & International Considerations */}
      {((legal.industry_specific_considerations && legal.industry_specific_considerations.length > 0) ||
        (legal.international_considerations && legal.international_considerations.length > 0)) && (
        <Card title="Additional Considerations">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {legal.industry_specific_considerations && legal.industry_specific_considerations.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Industry-Specific</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {legal.industry_specific_considerations.map((item, i) => <li key={i} style={{ marginBottom: '4px' }}>{item}</li>)}
                </ul>
              </div>
            )}
            {legal.international_considerations && legal.international_considerations.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>International</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {legal.international_considerations.map((item, i) => <li key={i} style={{ marginBottom: '4px' }}>{item}</li>)}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}
    </>
  );
}

// Risk Assessment Section
function RiskAssessmentSection({ pack }: { pack: InceptionPack }) {
  const riskData = pack.risk_assessment;

  if (!riskData) {
    return (
      <Card title="Risk Assessment">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No risk assessment data available.</p>
      </Card>
    );
  }

  const risks: RiskItemType[] = riskData.risks || [];
  const riskMatrix: RiskMatrixItem[] = riskData.risk_matrix || [];
  const hasRisks = risks.length > 0 || riskMatrix.length > 0;

  const riskLevelColors: Record<string, { bg: string; color: string }> = {
    critical: { bg: 'var(--v4-error-bg)', color: 'var(--v4-error)' },
    high: { bg: 'rgba(234, 88, 12, 0.1)', color: '#c2410c' },
    medium: { bg: 'var(--v4-warning-bg)', color: '#a16207' },
    low: { bg: 'var(--v4-success-bg)', color: 'var(--v4-success)' },
  };

  // Convert numeric likelihood/impact to levels
  const getLevelFromScore = (score: number | undefined): string => {
    if (!score) return 'medium';
    if (score >= 4) return 'high';
    if (score >= 2) return 'medium';
    return 'low';
  };

  return (
    <>
      {/* Summary & Overall Risk */}
      {(riskData.summary || riskData.overall_risk_level || riskData.risk_summary) && (
        <Card title="Risk Overview">
          {riskData.overall_risk_level && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <span style={{
                padding: '6px 14px',
                fontSize: '13px',
                fontWeight: 600,
                textTransform: 'uppercase',
                borderRadius: '4px',
                background: riskLevelColors[riskData.overall_risk_level]?.bg || 'var(--v4-bg)',
                color: riskLevelColors[riskData.overall_risk_level]?.color || 'var(--v4-text)',
              }}>
                {riskData.overall_risk_level} Overall Risk
              </span>
            </div>
          )}
          {riskData.summary && (
            <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, marginBottom: '16px' }}>
              {riskData.summary}
            </p>
          )}
          {riskData.risk_summary && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
              <div style={{ padding: '12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700 }}>{riskData.risk_summary.total_risks || 0}</div>
                <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', textTransform: 'uppercase' }}>Total</div>
              </div>
              <div style={{ padding: '12px', background: 'var(--v4-error-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--v4-error)' }}>{riskData.risk_summary.critical_risks || 0}</div>
                <div style={{ fontSize: '11px', color: 'var(--v4-error)', textTransform: 'uppercase' }}>Critical</div>
              </div>
              <div style={{ padding: '12px', background: 'rgba(234, 88, 12, 0.1)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#c2410c' }}>{riskData.risk_summary.high_risks || 0}</div>
                <div style={{ fontSize: '11px', color: '#c2410c', textTransform: 'uppercase' }}>High</div>
              </div>
              <div style={{ padding: '12px', background: 'var(--v4-warning-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: '#a16207' }}>{riskData.risk_summary.medium_risks || 0}</div>
                <div style={{ fontSize: '11px', color: '#a16207', textTransform: 'uppercase' }}>Medium</div>
              </div>
              <div style={{ padding: '12px', background: 'var(--v4-success-bg)', borderRadius: 'var(--v4-radius)', textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--v4-success)' }}>{riskData.risk_summary.low_risks || 0}</div>
                <div style={{ fontSize: '11px', color: 'var(--v4-success)', textTransform: 'uppercase' }}>Low</div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Top Risks */}
      {riskData.top_3_risks && riskData.top_3_risks.length > 0 && (
        <Card title="Top Critical Risks">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {riskData.top_3_risks.map((risk, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-error-bg)', borderRadius: 'var(--v4-radius)', borderLeft: '3px solid var(--v4-error)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#b91c1c' }}>{risk.name || `Critical Risk ${i + 1}`}</h4>
                  {risk.risk_id && <span style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>{risk.risk_id}</span>}
                </div>
                {risk.why_critical && (
                  <p style={{ fontSize: '13px', color: '#b91c1c', marginBottom: '8px' }}>
                    <strong>Why Critical:</strong> {risk.why_critical}
                  </p>
                )}
                {risk.immediate_action && (
                  <div style={{ fontSize: '13px', color: '#991b1b' }}>
                    <strong>Immediate Action:</strong> {risk.immediate_action}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Simple top_risks string array fallback */}
      {!riskData.top_3_risks && riskData.top_risks && riskData.top_risks.length > 0 && (
        <Card title="Top Risks">
          <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '14px', color: 'var(--v4-text-secondary)' }}>
            {riskData.top_risks.map((risk, i) => <li key={i} style={{ marginBottom: '6px' }}>{risk}</li>)}
          </ul>
        </Card>
      )}

      {/* Risk Register from risks array */}
      {risks.length > 0 && (
        <Card title="Risk Register">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {risks.map((risk: RiskItemType, i: number) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', borderLeft: `3px solid ${riskLevelColors[risk.likelihood]?.color || 'var(--v4-border)'}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div>
                    <span style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-accent)', marginRight: '8px' }}>{risk.category}</span>
                    <span style={{
                      padding: '2px 6px',
                      fontSize: '9px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      borderRadius: '3px',
                      background: riskLevelColors[risk.likelihood]?.bg || 'var(--v4-bg)',
                      color: riskLevelColors[risk.likelihood]?.color || 'var(--v4-text-muted)',
                    }}>
                      {risk.likelihood}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    {risk.risk_score && (
                      <span style={{ fontSize: '11px', padding: '2px 6px', background: 'var(--v4-surface)', borderRadius: '3px', color: 'var(--v4-text-muted)' }}>
                        Score: {risk.risk_score}
                      </span>
                    )}
                    <span style={{
                      padding: '2px 6px',
                      fontSize: '9px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      borderRadius: '3px',
                      background: risk.status === 'resolved' ? 'var(--v4-success-bg)' : 'var(--v4-bg)',
                      color: risk.status === 'resolved' ? 'var(--v4-success)' : 'var(--v4-text-muted)',
                    }}>
                      {risk.status}
                    </span>
                  </div>
                </div>
                <p style={{ fontSize: '14px', color: 'var(--v4-text)', marginBottom: '10px' }}>{risk.description}</p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', fontSize: '12px' }}>
                  <div>
                    <strong style={{ color: 'var(--v4-text-muted)' }}>Mitigation:</strong>
                    <p style={{ margin: '4px 0 0 0', color: 'var(--v4-text-secondary)' }}>{risk.mitigation_strategy}</p>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--v4-text-muted)' }}>Contingency:</strong>
                    <p style={{ margin: '4px 0 0 0', color: 'var(--v4-text-secondary)' }}>{risk.contingency_plan}</p>
                  </div>
                </div>
                {risk.owner && (
                  <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--v4-text-muted)' }}>
                    <strong>Owner:</strong> {risk.owner}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Risk Matrix fallback */}
      {risks.length === 0 && riskMatrix.length > 0 && (
        <Card title="Risk Register">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {riskMatrix.map((risk: RiskMatrixItem, i: number) => {
              const likelihoodLevel = getLevelFromScore(risk.likelihood);
              return (
                <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', borderLeft: `3px solid ${riskLevelColors[likelihoodLevel]?.color || 'var(--v4-border)'}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div>
                      {risk.category && <span style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-accent)', marginRight: '8px' }}>{risk.category}</span>}
                      <span style={{
                        padding: '2px 6px',
                        fontSize: '9px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        borderRadius: '3px',
                        background: riskLevelColors[likelihoodLevel]?.bg || 'var(--v4-bg)',
                        color: riskLevelColors[likelihoodLevel]?.color || 'var(--v4-text-muted)',
                      }}>
                        L:{risk.likelihood || 'N/A'} I:{risk.impact || 'N/A'}
                      </span>
                    </div>
                    {risk.risk_score && (
                      <span style={{ fontSize: '11px', padding: '2px 6px', background: 'var(--v4-surface)', borderRadius: '3px', color: 'var(--v4-text-muted)' }}>
                        Score: {risk.risk_score}
                      </span>
                    )}
                  </div>
                  <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>{risk.name || `Risk ${i + 1}`}</h4>
                  <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginBottom: '10px' }}>{risk.description}</p>
                  {risk.triggers && risk.triggers.length > 0 && (
                    <div style={{ marginBottom: '8px' }}>
                      <strong style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>Triggers:</strong>
                      <span style={{ fontSize: '12px', color: 'var(--v4-text-secondary)', marginLeft: '6px' }}>{risk.triggers.join(', ')}</span>
                    </div>
                  )}
                  {risk.mitigation_strategy && (
                    <div style={{ fontSize: '12px' }}>
                      <strong style={{ color: 'var(--v4-text-muted)' }}>Mitigation:</strong>
                      <p style={{ margin: '4px 0 0 0', color: 'var(--v4-text-secondary)' }}>{risk.mitigation_strategy}</p>
                    </div>
                  )}
                  {risk.owner && (
                    <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--v4-text-muted)' }}>
                      <strong>Owner:</strong> {risk.owner} {risk.review_frequency && `| Review: ${risk.review_frequency}`}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Risk Appetite Recommendation */}
      {riskData.risk_appetite_recommendation && (
        <Card title="Risk Appetite & Recommendation">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '16px' }}>
            {riskData.risk_appetite_recommendation.risk_tolerance_level && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Risk Tolerance Level</h5>
                <p style={{ fontSize: '14px', color: 'var(--v4-text)', margin: 0 }}>{riskData.risk_appetite_recommendation.risk_tolerance_level}</p>
              </div>
            )}
            {riskData.risk_appetite_recommendation.go_no_go_recommendation && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Go/No-Go Recommendation</h5>
                <span style={{
                  padding: '4px 10px',
                  fontSize: '13px',
                  fontWeight: 600,
                  borderRadius: '4px',
                  background: riskData.risk_appetite_recommendation.go_no_go_recommendation.toLowerCase().includes('go') ? 'var(--v4-success-bg)' : 'var(--v4-error-bg)',
                  color: riskData.risk_appetite_recommendation.go_no_go_recommendation.toLowerCase().includes('go') ? 'var(--v4-success)' : 'var(--v4-error)',
                }}>
                  {riskData.risk_appetite_recommendation.go_no_go_recommendation}
                </span>
              </div>
            )}
          </div>
          {riskData.risk_appetite_recommendation.rationale && (
            <div style={{ marginBottom: '16px' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Rationale</h5>
              <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', margin: 0 }}>{riskData.risk_appetite_recommendation.rationale}</p>
            </div>
          )}
          {riskData.risk_appetite_recommendation.conditions_for_go && riskData.risk_appetite_recommendation.conditions_for_go.length > 0 && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Conditions for Go</h5>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                {riskData.risk_appetite_recommendation.conditions_for_go.map((cond, i) => <li key={i} style={{ marginBottom: '4px' }}>{cond}</li>)}
              </ul>
            </div>
          )}
        </Card>
      )}

      {/* Monitoring Plan */}
      {riskData.monitoring_plan && (
        <Card title="Risk Monitoring Plan">
          {riskData.monitoring_plan.review_cadence && (
            <div style={{ marginBottom: '16px' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Review Cadence</h5>
              <p style={{ fontSize: '14px', color: 'var(--v4-text)', margin: 0 }}>{riskData.monitoring_plan.review_cadence}</p>
            </div>
          )}
          {riskData.monitoring_plan.escalation_process && (
            <div style={{ marginBottom: '16px' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Escalation Process</h5>
              <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', margin: 0 }}>{riskData.monitoring_plan.escalation_process}</p>
            </div>
          )}
          {riskData.monitoring_plan.key_risk_indicators && riskData.monitoring_plan.key_risk_indicators.length > 0 && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '10px' }}>Key Risk Indicators</h5>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {riskData.monitoring_plan.key_risk_indicators.map((kri, i) => (
                  <div key={i} style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                    <div style={{ fontSize: '14px', fontWeight: 500, marginBottom: '6px' }}>{kri.indicator}</div>
                    <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--v4-text-secondary)' }}>
                      <span><strong>Threshold:</strong> {kri.threshold}</span>
                      <span><strong>Action:</strong> {kri.action_if_exceeded}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Fallback if no risks found */}
      {!hasRisks && !riskData.top_risks && !riskData.top_3_risks && (
        <Card title="Risk Register">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No individual risks documented.</p>
        </Card>
      )}
    </>
  );
}

// Wireframes Section
function WireframesSection({ pack }: { pack: InceptionPack }) {
  const wireframes = pack.wireframes;
  const [activeScreen, setActiveScreen] = useState(0);

  if (!wireframes || !wireframes.screens || wireframes.screens.length === 0) {
    return (
      <Card title="Wireframes">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No wireframes available.</p>
      </Card>
    );
  }

  const currentScreen = wireframes.screens[activeScreen];

  // Generate iframe content with the React code
  const generateIframeContent = (reactCode: string) => {
    // Clean up the react_code - handle potential malformed code
    let cleanCode = reactCode;

    // If code starts with a common pattern, try to extract just the component
    if (cleanCode.includes('export default function')) {
      return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://unpkg.com/lucide-react@latest" rel="stylesheet">
  <style>
    body { margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; background: #f5f5f4; }
    .wireframe-container { min-height: 100vh; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    // Mock lucide-react icons
    const Search = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>;
    const Bell = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>;
    const Settings = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>;
    const FileText = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>;
    const AlertTriangle = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>;
    const Check = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>;
    const ChevronRight = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>;
    const Plus = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>;
    const Upload = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>;
    const User = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
    const Home = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>;
    const Menu = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>;
    const X = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>;
    const ArrowRight = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>;
    const ArrowLeft = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>;

    try {
      ${cleanCode.replace(/import\s*{[^}]*}\s*from\s*['"][^'"]*['"];?\s*/g, '').replace(/export default /g, 'const WireframeComponent = ')}

      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(<WireframeComponent />);
    } catch (e) {
      document.getElementById('root').innerHTML = '<div style="padding: 20px; color: #b91c1c;">Error rendering wireframe: ' + e.message + '</div>';
    }
  </script>
</body>
</html>`;
    }

    // Fallback for other code formats
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { margin: 0; padding: 20px; font-family: system-ui, -apple-system, sans-serif; background: #f5f5f4; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    try {
      ${cleanCode}

      // Try to find and render the component
      if (typeof WireframeComponent !== 'undefined') {
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<WireframeComponent />);
      }
    } catch (e) {
      document.getElementById('root').innerHTML = '<div style="padding: 20px; color: #b91c1c;">Error rendering wireframe: ' + e.message + '</div>';
    }
  </script>
</body>
</html>`;
  };

  return (
    <>
      {/* Screen Navigation */}
      <Card title="Wireframe Screens">
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
          {wireframes.screens.map((screen, i) => (
            <button
              key={i}
              onClick={() => setActiveScreen(i)}
              style={{
                padding: '8px 14px',
                fontSize: '13px',
                fontWeight: activeScreen === i ? 600 : 400,
                color: activeScreen === i ? 'white' : 'var(--v4-text-secondary)',
                background: activeScreen === i ? 'var(--v4-accent)' : 'var(--v4-bg)',
                border: `1px solid ${activeScreen === i ? 'var(--v4-accent)' : 'var(--v4-border)'}`,
                borderRadius: 'var(--v4-radius)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {screen.screen_name || screen.screen_id || `Screen ${i + 1}`}
            </button>
          ))}
        </div>

        {/* Current Screen Info */}
        <div style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)', marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
            <h4 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }}>
              {currentScreen.screen_name || currentScreen.screen_id || `Screen ${activeScreen + 1}`}
            </h4>
            <span style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>{currentScreen.screen_id}</span>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', margin: 0 }}>{currentScreen.purpose}</p>
        </div>

        {/* Wireframe Preview */}
        {currentScreen.react_code && (
          <div style={{ border: '1px solid var(--v4-border)', borderRadius: 'var(--v4-radius)', overflow: 'hidden' }}>
            <div style={{ padding: '8px 12px', background: 'var(--v4-bg)', borderBottom: '1px solid var(--v4-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--v4-text-muted)' }}>Preview</span>
              <div style={{ display: 'flex', gap: '4px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }}></span>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#eab308' }}></span>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#22c55e' }}></span>
              </div>
            </div>
            <iframe
              srcDoc={generateIframeContent(currentScreen.react_code)}
              style={{
                width: '100%',
                height: '500px',
                border: 'none',
                background: '#f5f5f4',
              }}
              sandbox="allow-scripts"
              title={`Wireframe: ${currentScreen.screen_name || currentScreen.screen_id}`}
            />
          </div>
        )}
      </Card>

      {/* Screen Details */}
      <Card title="Screen Details">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          {currentScreen.key_components && currentScreen.key_components.length > 0 && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Key Components</h5>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                {currentScreen.key_components.map((comp, i) => <li key={i} style={{ marginBottom: '4px' }}>{comp}</li>)}
              </ul>
            </div>
          )}
          {currentScreen.user_stories_covered && currentScreen.user_stories_covered.length > 0 && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>User Stories Covered</h5>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {currentScreen.user_stories_covered.map((story, i) => (
                  <span key={i} style={{ padding: '2px 8px', fontSize: '11px', background: 'var(--v4-bg)', borderRadius: '3px' }}>{story}</span>
                ))}
              </div>
            </div>
          )}
          {currentScreen.navigation_to && currentScreen.navigation_to.length > 0 && (
            <div style={{ gridColumn: 'span 2' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Navigation To</h5>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {currentScreen.navigation_to.map((nav, i) => (
                  <span key={i} style={{ padding: '4px 10px', fontSize: '12px', background: 'var(--v4-accent)', color: 'white', borderRadius: '4px' }}>{nav}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* User Flows */}
      {wireframes.user_flows && wireframes.user_flows.length > 0 && (
        <Card title="User Flows">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {wireframes.user_flows.map((flow, i) => (
              <div key={i} style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '6px' }}>{flow.flow_name}</h4>
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginBottom: '10px' }}>{flow.description}</p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  {flow.screens.map((screen, j) => (
                    <span key={j} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ padding: '4px 10px', fontSize: '12px', background: 'var(--v4-surface)', border: '1px solid var(--v4-border)', borderRadius: '4px' }}>{screen}</span>
                      {j < flow.screens.length - 1 && <span style={{ color: 'var(--v4-text-muted)' }}>→</span>}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Design System Notes */}
      {wireframes.design_system_notes && wireframes.design_system_notes.length > 0 && (
        <Card title="Design System Notes">
          <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '14px', color: 'var(--v4-text-secondary)' }}>
            {wireframes.design_system_notes.map((note, i) => <li key={i} style={{ marginBottom: '6px' }}>{note}</li>)}
          </ul>
        </Card>
      )}
    </>
  );
}

// Prototype Section
function PrototypeSection({ pack }: { pack: InceptionPack }) {
  const prototype = pack.prototype;

  if (!prototype) {
    return (
      <Card title="Prototype">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No prototype available.</p>
      </Card>
    );
  }

  const reactCode = prototype.react_component_code || prototype.react_code;

  // Generate iframe content with the React code and CSS
  const generateIframeContent = (code: string, css?: string) => {
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; background: #f5f5f4; }
    .prototype-container { min-height: 100vh; }
    ${css || ''}
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    // Mock lucide-react icons
    const Search = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>;
    const Bell = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>;
    const Settings = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>;
    const FileText = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>;
    const AlertTriangle = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>;
    const Check = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>;
    const CheckCircle = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>;
    const ChevronRight = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>;
    const ChevronDown = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>;
    const Plus = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>;
    const Upload = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>;
    const User = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
    const Home = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>;
    const Menu = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>;
    const X = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>;
    const ArrowRight = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>;
    const ArrowLeft = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>;
    const Star = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>;
    const Heart = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>;
    const Image = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>;
    const Calendar = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg>;
    const Clock = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>;
    const Mail = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>;
    const Phone = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>;
    const MapPin = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>;
    const Trash2 = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>;
    const Edit = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>;
    const Eye = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>;
    const Download = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>;
    const Filter = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>;
    const MoreVertical = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>;
    const ShoppingCart = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>;
    const CreditCard = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>;
    const Lock = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>;
    const Zap = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>;

    try {
      ${code.replace(/import\s*{[^}]*}\s*from\s*['"][^'"]*['"];?\s*/g, '').replace(/export default /g, 'const PrototypeComponent = ')}

      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(<PrototypeComponent />);
    } catch (e) {
      document.getElementById('root').innerHTML = '<div style="padding: 20px; color: #b91c1c;">Error rendering prototype: ' + e.message + '</div>';
    }
  </script>
</body>
</html>`;
  };

  return (
    <>
      {/* Prototype Overview */}
      <Card title="Prototype Overview">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '16px' }}>
          {prototype.prototype_name && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Prototype Name</h5>
              <p style={{ fontSize: '16px', fontWeight: 600, color: 'var(--v4-text)', margin: 0 }}>{prototype.prototype_name}</p>
            </div>
          )}
          {prototype.primary_persona && (
            <div>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Primary Persona</h5>
              <p style={{ fontSize: '14px', color: 'var(--v4-text)', margin: 0 }}>{prototype.primary_persona}</p>
            </div>
          )}
        </div>
        {prototype.key_user_story && (
          <div style={{ padding: '12px 14px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
            <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Key User Story</h5>
            <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', margin: 0, fontStyle: 'italic' }}>"{prototype.key_user_story}"</p>
          </div>
        )}
      </Card>

      {/* Live Prototype Preview */}
      {reactCode && (
        <Card title="Live Prototype">
          <div style={{ border: '1px solid var(--v4-border)', borderRadius: 'var(--v4-radius)', overflow: 'hidden' }}>
            <div style={{ padding: '8px 12px', background: 'var(--v4-bg)', borderBottom: '1px solid var(--v4-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--v4-text-muted)' }}>Interactive Preview</span>
              <div style={{ display: 'flex', gap: '4px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }}></span>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#eab308' }}></span>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#22c55e' }}></span>
              </div>
            </div>
            <iframe
              srcDoc={generateIframeContent(reactCode, prototype.css_code)}
              style={{
                width: '100%',
                height: '600px',
                border: 'none',
                background: '#f5f5f4',
              }}
              sandbox="allow-scripts"
              title={`Prototype: ${prototype.prototype_name || 'Interactive Prototype'}`}
            />
          </div>
        </Card>
      )}

      {/* Color Palette */}
      {prototype.color_palette && (
        <Card title="Color Palette">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
            {Object.entries(prototype.color_palette).map(([name, color]) => (
              <div key={name} style={{ textAlign: 'center' }}>
                <div style={{
                  width: '100%',
                  height: '60px',
                  background: color,
                  borderRadius: 'var(--v4-radius)',
                  border: '1px solid var(--v4-border)',
                  marginBottom: '8px',
                }}></div>
                <div style={{ fontSize: '12px', fontWeight: 500, textTransform: 'capitalize' }}>{name}</div>
                <div style={{ fontSize: '11px', color: 'var(--v4-text-muted)', fontFamily: 'monospace' }}>{color}</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Demo Scenario */}
      {prototype.demo_scenario && (
        <Card title="Demo Scenario">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, margin: 0 }}>{prototype.demo_scenario}</p>
        </Card>
      )}

      {/* Interactivity Notes */}
      {prototype.interactivity_notes && prototype.interactivity_notes.length > 0 && (
        <Card title="Interactivity Notes">
          <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '14px', color: 'var(--v4-text-secondary)' }}>
            {prototype.interactivity_notes.map((note, i) => <li key={i} style={{ marginBottom: '6px' }}>{note}</li>)}
          </ul>
        </Card>
      )}
    </>
  );
}

// Stakeholder Views Section
function StakeholderViewsSection({ pack }: { pack: InceptionPack }) {
  const stakeholderData = pack.stakeholder_views;
  const [activeView, setActiveView] = useState(0);

  if (!stakeholderData || !stakeholderData.views || stakeholderData.views.length === 0) {
    return (
      <Card title="Stakeholder Views">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No stakeholder views available.</p>
      </Card>
    );
  }

  const currentView = stakeholderData.views[activeView];

  // Map common stakeholder roles to colors
  const roleColors: Record<string, { bg: string; color: string }> = {
    cfo: { bg: 'rgba(37, 99, 235, 0.1)', color: '#1d4ed8' },
    cto: { bg: 'rgba(124, 58, 237, 0.1)', color: '#6d28d9' },
    ceo: { bg: 'rgba(194, 65, 12, 0.1)', color: '#c2410c' },
    cmo: { bg: 'rgba(234, 88, 12, 0.1)', color: '#ea580c' },
    legal: { bg: 'rgba(220, 38, 38, 0.1)', color: '#dc2626' },
    product: { bg: 'rgba(22, 163, 74, 0.1)', color: '#16a34a' },
    engineering: { bg: 'rgba(124, 58, 237, 0.1)', color: '#7c3aed' },
    operations: { bg: 'rgba(202, 138, 4, 0.1)', color: '#ca8a04' },
  };

  const getRoleColor = (role: string) => {
    const lowerRole = role.toLowerCase();
    for (const key of Object.keys(roleColors)) {
      if (lowerRole.includes(key)) {
        return roleColors[key];
      }
    }
    return { bg: 'var(--v4-bg)', color: 'var(--v4-text)' };
  };

  return (
    <>
      {/* Stakeholder Tabs */}
      <Card title="Stakeholder Perspectives">
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
          {stakeholderData.views.map((view, i) => {
            const colors = getRoleColor(view.stakeholder_role);
            return (
              <button
                key={i}
                onClick={() => setActiveView(i)}
                style={{
                  padding: '10px 16px',
                  fontSize: '13px',
                  fontWeight: activeView === i ? 600 : 500,
                  color: activeView === i ? colors.color : 'var(--v4-text-secondary)',
                  background: activeView === i ? colors.bg : 'var(--v4-bg)',
                  border: `1px solid ${activeView === i ? colors.color : 'var(--v4-border)'}`,
                  borderRadius: 'var(--v4-radius)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {view.stakeholder_role}
              </button>
            );
          })}
        </div>

        {/* Current Stakeholder View */}
        <div style={{ padding: '20px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <span style={{
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 600,
              borderRadius: '4px',
              background: getRoleColor(currentView.stakeholder_role).bg,
              color: getRoleColor(currentView.stakeholder_role).color,
            }}>
              {currentView.stakeholder_role}
            </span>
            {currentView.evidence_confidence && (
              <span style={{ fontSize: '12px', color: 'var(--v4-text-muted)' }}>
                Evidence Confidence: <strong>{currentView.evidence_confidence}</strong>
              </span>
            )}
          </div>

          {/* Tailored Summary */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>Executive Summary</h4>
            <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, margin: 0 }}>
              {currentView.tailored_summary}
            </p>
          </div>

          {/* Decision Recommendation */}
          {currentView.decision_recommendation && (
            <div style={{ padding: '12px 14px', background: 'var(--v4-success-bg)', borderRadius: 'var(--v4-radius)', marginBottom: '20px' }}>
              <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-success)', marginBottom: '6px' }}>Recommendation</h5>
              <p style={{ fontSize: '14px', color: '#166534', margin: 0 }}>{currentView.decision_recommendation}</p>
            </div>
          )}

          {/* Key Questions Answered */}
          {(currentView.key_questions_answered || currentView.key_question_answered) && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '10px' }}>Key Questions Answered</h4>
              {currentView.key_questions_answered ? (
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {currentView.key_questions_answered.map((q, i) => <li key={i} style={{ marginBottom: '6px' }}>{q}</li>)}
                </ul>
              ) : (
                <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{currentView.key_question_answered}</p>
              )}
            </div>
          )}

          {/* Key Metrics */}
          {(currentView.key_metrics || currentView.key_metrics_for_role) && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '10px' }}>Key Metrics</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {(currentView.key_metrics || currentView.key_metrics_for_role || []).map((metric, i) => (
                  <span key={i} style={{
                    padding: '6px 12px',
                    fontSize: '12px',
                    background: 'var(--v4-surface)',
                    border: '1px solid var(--v4-border)',
                    borderRadius: '4px',
                  }}>
                    {metric}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Decision Criteria */}
          {currentView.decision_criteria && currentView.decision_criteria.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '10px' }}>Decision Criteria</h4>
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                {currentView.decision_criteria.map((criteria, i) => <li key={i} style={{ marginBottom: '6px' }}>{criteria}</li>)}
              </ul>
            </div>
          )}
        </div>
      </Card>

      {/* Anticipated Objections */}
      {currentView.anticipated_objections && currentView.anticipated_objections.length > 0 && (
        <Card title={`Anticipated Objections - ${currentView.stakeholder_role}`}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {currentView.anticipated_objections.map((obj, i) => (
              <div key={i} style={{ border: '1px solid var(--v4-border)', borderRadius: 'var(--v4-radius)', overflow: 'hidden' }}>
                <div style={{ padding: '14px 16px', background: 'var(--v4-error-bg)', borderBottom: '1px solid var(--v4-border)' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#b91c1c', margin: 0 }}>
                    Objection: {obj.objection}
                  </h4>
                </div>
                <div style={{ padding: '14px 16px' }}>
                  <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', marginBottom: '10px' }}>
                    <strong style={{ color: 'var(--v4-success)' }}>Response:</strong> {obj.response}
                  </p>
                  {obj.supporting_claim_ids && obj.supporting_claim_ids.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--v4-text-muted)' }}>Supporting Claims:</span>
                      {obj.supporting_claim_ids.map((id, j) => (
                        <span key={j} style={{ padding: '2px 6px', fontSize: '10px', background: 'var(--v4-bg)', borderRadius: '3px', fontFamily: 'monospace' }}>{id}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Cross-Stakeholder Alignment */}
      {stakeholderData.cross_stakeholder_alignment && (
        <Card title="Cross-Stakeholder Alignment">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, margin: 0 }}>
            {stakeholderData.cross_stakeholder_alignment}
          </p>
        </Card>
      )}

      {/* Common Concerns */}
      {stakeholderData.common_concerns && stakeholderData.common_concerns.length > 0 && (
        <Card title="Common Concerns Across Stakeholders">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {stakeholderData.common_concerns.map((concern, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', padding: '10px 12px', background: 'var(--v4-bg)', borderRadius: 'var(--v4-radius)' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--v4-warning)', marginTop: '6px', flexShrink: 0 }}></span>
                <span style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>{concern}</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}

// Validation Playbook Section
function ValidationPlaybookSection({ pack }: { pack: InceptionPack }) {
  const playbook = pack.validation_playbook;

  if (!playbook) {
    return (
      <Card title="Validation Playbook">
        <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No validation playbook available.</p>
      </Card>
    );
  }

  const experiments = playbook.experiments || playbook.validation_experiments || [];

  const priorityColors: Record<string, { bg: string; color: string }> = {
    critical: { bg: 'var(--v4-error-bg)', color: 'var(--v4-error)' },
    high: { bg: 'rgba(234, 88, 12, 0.1)', color: '#c2410c' },
    medium: { bg: 'var(--v4-warning-bg)', color: '#a16207' },
    low: { bg: 'var(--v4-success-bg)', color: 'var(--v4-success)' },
  };

  const effortColors: Record<string, { bg: string; color: string }> = {
    quick: { bg: 'var(--v4-success-bg)', color: 'var(--v4-success)' },
    moderate: { bg: 'var(--v4-warning-bg)', color: '#a16207' },
    significant: { bg: 'rgba(234, 88, 12, 0.1)', color: '#c2410c' },
  };

  return (
    <>
      {/* Quick Wins & Critical Path */}
      {(playbook.quick_wins || playbook.critical_path) && (
        <Card title="Validation Strategy">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            {playbook.quick_wins && playbook.quick_wins.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-success)', marginBottom: '10px' }}>Quick Wins</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {playbook.quick_wins.map((win, i) => <li key={i} style={{ marginBottom: '6px' }}>{win}</li>)}
                </ul>
              </div>
            )}
            {playbook.critical_path && playbook.critical_path.length > 0 && (
              <div>
                <h5 style={{ fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-error)', marginBottom: '10px' }}>Critical Path</h5>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '13px', color: 'var(--v4-text-secondary)' }}>
                  {playbook.critical_path.map((item, i) => <li key={i} style={{ marginBottom: '6px' }}>{item}</li>)}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Prioritization Rationale */}
      {playbook.prioritization_rationale && (
        <Card title="Prioritization Rationale">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.65, margin: 0 }}>
            {playbook.prioritization_rationale}
          </p>
        </Card>
      )}

      {/* Experiments */}
      {experiments.length > 0 && (
        <Card title="Validation Experiments">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {experiments.map((exp, i) => (
              <div key={i} style={{ border: '1px solid var(--v4-border)', borderRadius: 'var(--v4-radius)', overflow: 'hidden' }}>
                {/* Experiment Header */}
                <div style={{ padding: '14px 16px', background: 'var(--v4-bg)', borderBottom: '1px solid var(--v4-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '11px', fontFamily: 'monospace', color: 'var(--v4-text-muted)' }}>{exp.experiment_id}</span>
                      <span style={{
                        padding: '2px 8px',
                        fontSize: '10px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        borderRadius: '3px',
                        background: priorityColors[exp.priority]?.bg || 'var(--v4-bg)',
                        color: priorityColors[exp.priority]?.color || 'var(--v4-text-muted)',
                      }}>
                        {exp.priority}
                      </span>
                      <span style={{
                        padding: '2px 8px',
                        fontSize: '10px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        borderRadius: '3px',
                        background: effortColors[exp.effort_level]?.bg || 'var(--v4-bg)',
                        color: effortColors[exp.effort_level]?.color || 'var(--v4-text-muted)',
                      }}>
                        {exp.effort_level} effort
                      </span>
                    </div>
                    {exp.hypothesis_claim_id && (
                      <span style={{ fontSize: '10px', color: 'var(--v4-text-muted)' }}>
                        Validates: {exp.hypothesis_claim_id}
                      </span>
                    )}
                  </div>
                  <h4 style={{ fontSize: '15px', fontWeight: 600, margin: 0 }}>{exp.experiment_name}</h4>
                </div>

                {/* Experiment Details */}
                <div style={{ padding: '14px 16px' }}>
                  {/* Target Profile */}
                  {exp.target_profile && (
                    <div style={{ marginBottom: '14px' }}>
                      <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Target Profile</h5>
                      <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{exp.target_profile}</p>
                    </div>
                  )}

                  {/* Instructions */}
                  {exp.specific_instructions && (
                    <div style={{ marginBottom: '14px' }}>
                      <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '6px' }}>Instructions</h5>
                      <p style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', margin: 0 }}>{exp.specific_instructions}</p>
                    </div>
                  )}

                  {/* Success / Failure Criteria */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '14px' }}>
                    {exp.success_criteria && (
                      <div style={{ padding: '10px 12px', background: 'var(--v4-success-bg)', borderRadius: 'var(--v4-radius)' }}>
                        <h5 style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-success)', marginBottom: '4px' }}>Success Criteria</h5>
                        <p style={{ fontSize: '12px', color: '#166534', margin: 0 }}>{exp.success_criteria}</p>
                      </div>
                    )}
                    {exp.failure_criteria && (
                      <div style={{ padding: '10px 12px', background: 'var(--v4-error-bg)', borderRadius: 'var(--v4-radius)' }}>
                        <h5 style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-error)', marginBottom: '4px' }}>Failure Criteria</h5>
                        <p style={{ fontSize: '12px', color: '#b91c1c', margin: 0 }}>{exp.failure_criteria}</p>
                      </div>
                    )}
                  </div>

                  {/* Meta Info */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '12px', color: 'var(--v4-text-muted)', marginBottom: '14px' }}>
                    {exp.sample_size && <span><strong>Sample Size:</strong> {exp.sample_size}</span>}
                    {exp.timeline && <span><strong>Timeline:</strong> {exp.timeline}</span>}
                    {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                    {(exp as any).cost_estimate && <span><strong>Cost:</strong> {(exp as any).cost_estimate}</span>}
                  </div>

                  {/* Upgrade Path */}
                  {exp.upgrade_path && exp.upgrade_path.length > 0 && (
                    <div>
                      <h5 style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--v4-text-muted)', marginBottom: '8px' }}>Upgrade Path</h5>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        {exp.upgrade_path.map((step, j) => (
                          <span key={j} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ padding: '4px 10px', fontSize: '11px', background: 'var(--v4-bg)', border: '1px solid var(--v4-border)', borderRadius: '4px', fontFamily: 'monospace' }}>{step}</span>
                            {j < exp.upgrade_path.length - 1 && <span style={{ color: 'var(--v4-text-muted)' }}>→</span>}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Empty State */}
      {experiments.length === 0 && !playbook.quick_wins && !playbook.critical_path && !playbook.prioritization_rationale && (
        <Card title="Validation Playbook">
          <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)' }}>No validation experiments defined.</p>
        </Card>
      )}
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
