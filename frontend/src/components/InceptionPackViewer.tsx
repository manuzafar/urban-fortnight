import { useState } from 'react';
import {
  FileText,
  Users,
  TrendingUp,
  Cpu,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Target,
  Zap,
  DollarSign,
  Shield,
  Clock,
  Download,
  Star,
  Scale,
  AlertTriangle,
  Rocket,
} from 'lucide-react';
import type { InceptionPack, Epic, UserStory, AcceptanceCriteria, LegalRegulatoryReview } from '../types/api';
import { MermaidDiagram } from './MermaidDiagram';

interface InceptionPackViewerProps {
  pack: InceptionPack;
  onNewDiscovery: () => void;
}

type TabId = 'summary' | 'research' | 'business' | 'prd' | 'architecture' | 'legal' | 'quality';

interface TabConfig {
  id: TabId;
  label: string;
  icon: typeof FileText;
}

const TABS: TabConfig[] = [
  { id: 'summary', label: 'Executive Summary', icon: FileText },
  { id: 'research', label: 'Market Hypotheses', icon: Users },
  { id: 'business', label: 'Business Case', icon: TrendingUp },
  { id: 'prd', label: 'PRD', icon: Target },
  { id: 'architecture', label: 'Architecture', icon: Cpu },
  { id: 'legal', label: 'Legal & Regulatory', icon: Scale },
  { id: 'quality', label: 'Quality', icon: CheckCircle2 },
];

export function InceptionPackViewer({ pack, onNewDiscovery }: InceptionPackViewerProps) {
  const [activeTab, setActiveTab] = useState<TabId>('summary');
  const [expandedEpics, setExpandedEpics] = useState<Set<string>>(new Set());

  const toggleEpic = (epicId: string) => {
    const newExpanded = new Set(expandedEpics);
    if (newExpanded.has(epicId)) {
      newExpanded.delete(epicId);
    } else {
      newExpanded.add(epicId);
    }
    setExpandedEpics(newExpanded);
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(pack, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inception-pack-${pack.metadata.session_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'summary':
        return <ExecutiveSummaryTab summary={pack.executive_summary} />;
      case 'research':
        return <CustomerResearchTab research={pack.customer_research} />;
      case 'business':
        return <BusinessCaseTab businessCase={pack.business_case} />;
      case 'prd':
        return (
          <PRDTab
            prd={pack.product_requirements_document}
            expandedEpics={expandedEpics}
            toggleEpic={toggleEpic}
          />
        );
      case 'architecture':
        return <ArchitectureTab architecture={pack.technical_architecture} />;
      case 'legal':
        return <LegalReviewTab legalReview={pack.legal_regulatory_review} />;
      case 'quality':
        return <QualityTab quality={pack.quality_assessment} metadata={pack.metadata} />;
      default:
        return null;
    }
  };

  return (
    <div className="results-container">
      {/* Top Bar */}
      <div className="results-top-bar">
        <div className="results-top-inner">
          <div className="results-brand">
            <div className="logo"></div>
            <span>{pack.executive_summary.product_name}</span>
          </div>
          <div className="results-actions">
            <button className="action-btn" onClick={handleDownload}>
              <Download size={18} />
              Download JSON
            </button>
            <button className="action-btn primary" onClick={onNewDiscovery}>
              Start New Discovery
            </button>
          </div>
        </div>
      </div>

      {/* Main Layout */}
      <div className="results-layout">
        {/* Sidebar Navigation */}
        <aside className="results-sidebar">
          <nav className="results-nav">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  className={`results-nav-item ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <div className="nav-item-icon">
                    <Icon size={18} />
                  </div>
                  <span className="nav-item-label">{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Quality Badge in Sidebar */}
          <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.7)' }}>
              <Star size={16} style={{ color: '#ffcf5a' }} />
              <span>Quality: {((pack.quality_assessment?.overall_score || 0) * 100).toFixed(0)}%</span>
              {pack.quality_assessment?.passed && <CheckCircle2 size={16} style={{ color: '#44d17b' }} />}
            </div>
          </div>
        </aside>

        {/* Content Area */}
        <div className="results-content">
          <div className="results-content-inner">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tab Components
// ═══════════════════════════════════════════════════════════════════════════════

function StatCard({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div style={{
      padding: '1rem',
      background: accent ? 'rgba(68, 209, 123, 0.08)' : 'rgba(255, 255, 255, 0.03)',
      borderRadius: '8px',
      border: accent ? '1px solid rgba(68, 209, 123, 0.2)' : '1px solid rgba(255, 255, 255, 0.06)'
    }}>
      <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</div>
      <div style={{ fontSize: '0.95rem', color: accent ? '#44d17b' : 'var(--color-text)', fontWeight: 500 }}>{value}</div>
    </div>
  );
}

function ExecutiveSummaryTab({ summary }: { summary: InceptionPack['executive_summary'] }) {
  return (
    <div>
      {/* Recommendation Banner */}
      {summary.recommendation && (
        <div style={{
          padding: '1.25rem',
          marginBottom: '1.5rem',
          background: summary.recommendation.toLowerCase().includes('proceed') && !summary.recommendation.toLowerCase().includes('not')
            ? 'rgba(68, 209, 123, 0.1)'
            : summary.recommendation.toLowerCase().includes('pivot')
              ? 'rgba(255, 207, 90, 0.1)'
              : 'rgba(255, 90, 90, 0.1)',
          borderRadius: '12px',
          border: summary.recommendation.toLowerCase().includes('proceed') && !summary.recommendation.toLowerCase().includes('not')
            ? '1px solid rgba(68, 209, 123, 0.3)'
            : summary.recommendation.toLowerCase().includes('pivot')
              ? '1px solid rgba(255, 207, 90, 0.3)'
              : '1px solid rgba(255, 90, 90, 0.3)'
        }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Recommendation</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{summary.recommendation}</div>
        </div>
      )}

      {/* Problem & Solution */}
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Problem Statement</h3>
        </div>
        <div className="section-content">
          <p>{summary.problem_statement}</p>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Solution Overview</h3>
        </div>
        <div className="section-content">
          <p>{summary.solution_overview}</p>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Value Proposition</h3>
        </div>
        <div className="section-content">
          <p style={{ color: 'var(--color-accent-2)', fontWeight: 600 }}>{summary.value_proposition}</p>
        </div>
      </div>

      {/* Financial Summary - Key Numbers */}
      {(summary.funding_required || summary.expected_roi || summary.financial_projections) && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <DollarSign size={18} /> Financial Summary
            </h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              {summary.funding_required && <StatCard label="Funding Required" value={summary.funding_required} accent />}
              {summary.expected_roi && <StatCard label="Expected ROI" value={summary.expected_roi} accent />}
              {summary.break_even_timeline && <StatCard label="Break Even" value={summary.break_even_timeline} />}
            </div>
            {summary.revenue_model && (
              <div style={{ marginBottom: '1rem' }}>
                <strong>Revenue Model:</strong> {summary.revenue_model}
              </div>
            )}
            {summary.financial_projections && (
              <div>
                <strong>Projections:</strong> {summary.financial_projections}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Market Opportunity */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Users size={18} /> Target Market
            </h3>
          </div>
          <div className="section-content">
            {summary.target_market_size && (
              <div style={{
                padding: '0.75rem',
                background: 'rgba(100, 150, 255, 0.1)',
                borderRadius: '8px',
                marginBottom: '1rem',
                border: '1px solid rgba(100, 150, 255, 0.2)'
              }}>
                <strong>Market Size:</strong> {summary.target_market_size}
              </div>
            )}
            <ul>
              {summary.target_users?.map((user, i) => (
                <li key={i}>{user}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Zap size={18} /> Competitive Position
            </h3>
          </div>
          <div className="section-content">
            {summary.competitive_landscape && (
              <p style={{ marginBottom: '1rem', color: 'var(--color-muted)' }}>{summary.competitive_landscape}</p>
            )}
            <strong>Key Differentiators:</strong>
            <ul>
              {summary.key_differentiators?.map((diff, i) => (
                <li key={i}>{diff}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Risk & Compliance */}
      {(summary.top_risks || summary.regulatory_summary) && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {summary.top_risks && summary.top_risks.length > 0 && (
            <div className="pack-section content-section">
              <div className="section-header">
                <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <AlertTriangle size={18} /> Top Risks
                </h3>
              </div>
              <div className="section-content">
                <ul>
                  {summary.top_risks.map((risk, i) => (
                    <li key={i} style={{ marginBottom: '0.5rem' }}>{risk}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {summary.regulatory_summary && (
            <div className="pack-section content-section">
              <div className="section-header">
                <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Shield size={18} /> Regulatory Summary
                </h3>
              </div>
              <div className="section-content">
                <p>{summary.regulatory_summary}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Go-to-Market */}
      {(summary.gtm_strategy || (summary.key_milestones && summary.key_milestones.length > 0)) && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Rocket size={18} /> Go-to-Market Strategy
            </h3>
          </div>
          <div className="section-content">
            {summary.gtm_strategy && (
              <p style={{ marginBottom: '1rem' }}>{summary.gtm_strategy}</p>
            )}
            {summary.key_milestones && summary.key_milestones.length > 0 && (
              <>
                <strong>Key Milestones:</strong>
                <ul>
                  {summary.key_milestones.map((milestone, i) => (
                    <li key={i}>{milestone}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </div>
      )}

      {/* Success Metrics */}
      {summary.success_metrics && summary.success_metrics.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Target size={18} /> Success Metrics
            </h3>
          </div>
          <div className="section-content">
            <ul>
              {summary.success_metrics.map((metric, i) => (
                <li key={i}>{metric}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

function CustomerResearchTab({ research }: { research: InceptionPack['customer_research'] }) {
  // Check if using new evidence-based format or legacy format
  const isNewFormat = research.research_scope || research.pain_signals;

  if (isNewFormat) {
    return (
      <div>
        {/* Validation Reminder Banner */}
        <div style={{
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem',
          background: 'rgba(255, 207, 90, 0.1)',
          borderRadius: '10px',
          border: '1px solid rgba(255, 207, 90, 0.3)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.75rem'
        }}>
          <AlertTriangle size={20} style={{ color: '#ffcf5a', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontWeight: 600, color: '#ffcf5a', marginBottom: '0.25rem' }}>These are hypotheses, not validated research</div>
            <div style={{ fontSize: '0.9rem', color: 'var(--color-muted)' }}>
              {research.validation_reminder || 'Schedule 5+ customer interviews to validate these assumptions before making product decisions.'}
            </div>
          </div>
        </div>

        {/* Research Scope & Quality */}
        {research.research_scope && (
          <div className="pack-section content-section">
            <div className="section-header">
              <h3 className="section-title">Research Scope & Limitations</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'inline-block', padding: '0.5rem 1rem', borderRadius: '6px', background: 'rgba(68, 209, 123, 0.1)', border: '1px solid rgba(68, 209, 123, 0.3)', color: '#44d17b', fontWeight: 600, marginBottom: '1rem' }}>
                Confidence: {research.research_scope.confidence_level}
              </div>
              <p style={{ marginBottom: '1.5rem', color: 'var(--color-muted)' }}>{research.research_scope.observation_context}</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                <div>
                  <strong>Segments Examined:</strong>
                  <ul>
                    {research.research_scope.segments_examined.map((seg, i) => (
                      <li key={i}>{seg}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong>Known Gaps:</strong>
                  <ul style={{ color: 'var(--color-warn)' }}>
                    {research.research_scope.known_gaps.map((gap, i) => (
                      <li key={i}>{gap}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Job to Be Done */}
        {research.job_to_be_done && (
          <div className="pack-section content-section">
            <div className="section-header">
              <h3 className="section-title">Job-to-Be-Done</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'grid', gap: '1.5rem' }}>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', borderLeft: '3px solid var(--color-accent)' }}>
                  <strong style={{ color: 'var(--color-accent-2)' }}>Trigger:</strong>
                  <p>{research.job_to_be_done.trigger_situation}</p>
                </div>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', borderLeft: '3px solid var(--color-good)' }}>
                  <strong style={{ color: 'var(--color-good)' }}>Goal:</strong>
                  <p>{research.job_to_be_done.underlying_goal}</p>
                </div>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', borderLeft: '3px solid var(--color-accent-2)' }}>
                  <strong style={{ color: 'var(--color-accent-2)' }}>Success:</strong>
                  <p>{research.job_to_be_done.success_definition}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Current Behaviour */}
        {research.current_behaviour && (
          <div className="pack-section content-section">
            <div className="section-header">
              <h3 className="section-title">Current Behaviour</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
                <div>
                  <strong>Existing Solutions:</strong>
                  <ul>
                    {research.current_behaviour.existing_solutions.map((sol, i) => (
                      <li key={i}>{sol}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong>Tools & Workarounds:</strong>
                  <ul>
                    {research.current_behaviour.tools_and_workarounds.map((tool, i) => (
                      <li key={i}>{tool}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong>Friction Points:</strong>
                  <ul style={{ color: 'var(--color-error)' }}>
                    {research.current_behaviour.friction_points.map((fp, i) => (
                      <li key={i}>{fp}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(255, 207, 90, 0.08)', border: '1px solid rgba(255, 207, 90, 0.2)', borderRadius: '8px' }}>
                <strong style={{ color: 'var(--color-warn)' }}>Why This Problem Persists:</strong> {research.current_behaviour.why_problem_persists}
              </div>
            </div>
          </div>
        )}

        {/* Pain Signals */}
        {research.pain_signals && research.pain_signals.length > 0 && (
          <div className="pack-section content-section">
            <div className="section-header">
              <h3 className="section-title">Pain Signals (Evidence-Tagged)</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {research.pain_signals.map((pain, i) => (
                  <div key={i} style={{
                    padding: '1.25rem',
                    background: pain.severity === 'high' ? 'rgba(239, 68, 68, 0.08)' : pain.severity === 'medium' ? 'rgba(255, 207, 90, 0.08)' : 'rgba(255, 255, 255, 0.03)',
                    border: `1px solid ${pain.severity === 'high' ? 'rgba(239, 68, 68, 0.3)' : pain.severity === 'medium' ? 'rgba(255, 207, 90, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                    borderRadius: '8px',
                    borderLeft: `4px solid ${pain.severity === 'high' ? 'var(--color-error)' : pain.severity === 'medium' ? 'var(--color-warn)' : 'var(--color-muted)'}`,
                  }}>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                      <span style={{ padding: '0.25rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700, background: pain.severity === 'high' ? 'var(--color-error)' : pain.severity === 'medium' ? 'var(--color-warn)' : 'var(--color-muted)', color: 'white', textTransform: 'uppercase' }}>
                        {pain.severity}
                      </span>
                      <span style={{ padding: '0.25rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600, background: 'rgba(109, 94, 252, 0.2)', border: '1px solid rgba(109, 94, 252, 0.4)', color: 'var(--color-accent-2)' }}>
                        {pain.evidence_tier}
                      </span>
                      {pain.challenges_solution && (
                        <span style={{ padding: '0.25rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600, background: 'rgba(255, 207, 90, 0.2)', border: '1px solid rgba(255, 207, 90, 0.4)', color: 'var(--color-warn)' }}>
                          Challenges Solution
                        </span>
                      )}
                    </div>
                    <p style={{ marginBottom: '0.75rem', fontWeight: 600, color: 'var(--color-text)' }}>{pain.description}</p>
                    <p style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}><em style={{ color: 'var(--color-muted)' }}>Evidence:</em> {pain.evidence_detail}</p>
                    <p style={{ fontSize: '0.875rem' }}><em style={{ color: 'var(--color-muted)' }}>Impact:</em> {pain.impact}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Uncomfortable Insights */}
        {research.uncomfortable_insights && research.uncomfortable_insights.length > 0 && (
          <div className="pack-section content-section" style={{ background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <div className="section-header">
              <h3 className="section-title" style={{ color: 'var(--color-error)' }}>Uncomfortable Insights</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {research.uncomfortable_insights.map((insight, i) => (
                  <div key={i} style={{ padding: '1rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px', borderLeft: '3px solid var(--color-error)' }}>
                    <span style={{ display: 'inline-block', padding: '0.25rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600, background: 'rgba(109, 94, 252, 0.2)', border: '1px solid rgba(109, 94, 252, 0.4)', color: 'var(--color-accent-2)', marginBottom: '0.75rem' }}>
                      {insight.evidence_tier}
                    </span>
                    <p style={{ fontWeight: 600, color: 'var(--color-text)', marginBottom: '0.5rem' }}>{insight.insight}</p>
                    <p style={{ fontSize: '0.875rem' }}><em style={{ color: 'var(--color-muted)' }}>Implication:</em> {insight.implication}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* What Customers Don't Care About */}
        {research.what_customers_dont_care_about && research.what_customers_dont_care_about.length > 0 && (
          <div className="pack-section content-section" style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <div className="section-header">
              <h3 className="section-title">What Customers Don't Care About</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {research.what_customers_dont_care_about.map((item, i) => (
                  <div key={i} style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px' }}>
                    <span style={{ display: 'inline-block', padding: '0.25rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600, background: 'rgba(109, 94, 252, 0.2)', border: '1px solid rgba(109, 94, 252, 0.4)', color: 'var(--color-accent-2)', marginBottom: '0.75rem' }}>
                      {item.evidence_tier}
                    </span>
                    <p style={{ marginBottom: '0.5rem' }}><strong>Assumed:</strong> {item.assumed_need}</p>
                    <p><strong style={{ color: 'var(--color-warn)' }}>Reality:</strong> {item.reality}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Open Questions */}
        {research.open_questions && research.open_questions.length > 0 && (
          <div className="pack-section content-section">
            <div className="section-header">
              <h3 className="section-title">Open Questions & Unknowns</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {research.open_questions.map((q, i) => (
                  <div key={i} style={{ padding: '1rem', background: 'rgba(255, 207, 90, 0.06)', border: '1px solid rgba(255, 207, 90, 0.2)', borderRadius: '8px', borderLeft: '3px solid var(--color-warn)' }}>
                    <p style={{ marginBottom: '0.5rem', fontWeight: 600, color: 'var(--color-text)' }}><strong style={{ color: 'var(--color-warn)' }}>Q:</strong> {q.question}</p>
                    <p style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}><em style={{ color: 'var(--color-muted)' }}>Why it matters:</em> {q.why_it_matters}</p>
                    <p style={{ fontSize: '0.875rem' }}><em style={{ color: 'var(--color-muted)' }}>Validation needed:</em> {q.validation_needed}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Competitive Landscape */}
        {research.competitive_landscape && (
          <div className="pack-section content-section">
            <div className="section-header">
              <h3 className="section-title">Competitive Reality Check</h3>
            </div>
            <div className="section-content">
              <p style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(109, 94, 252, 0.08)', border: '1px solid rgba(109, 94, 252, 0.2)', borderRadius: '8px', fontWeight: 600 }}>{research.competitive_landscape.market_position}</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                {research.competitive_landscape.competitors.map((comp, i) => (
                  <div key={i} style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
                    <h4 style={{ marginBottom: '1rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1.125rem' }}>{comp.name}</h4>
                    <p style={{ marginBottom: '0.75rem', fontSize: '0.875rem' }}><strong>Their approach:</strong> {comp.how_they_solve_it}</p>
                    <p style={{ marginBottom: '0.75rem', fontSize: '0.875rem' }}><strong style={{ color: 'var(--color-warn)' }}>Why they haven't won:</strong> {comp.why_they_havent_won}</p>
                    <p style={{ fontSize: '0.875rem', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '6px' }}><strong style={{ color: 'var(--color-error)' }}>Switching barriers:</strong> {comp.switching_barriers}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Market Context */}
        {research.market_context && (
          <div className="pack-section content-section">
            <div className="section-header">
              <h3 className="section-title">Market Context</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(109, 94, 252, 0.15), rgba(109, 94, 252, 0.05))', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
                  <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-2)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>TAM</span>
                  <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{research.market_context.total_addressable_market}</span>
                </div>
                <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(68, 209, 123, 0.15), rgba(68, 209, 123, 0.05))', border: '1px solid rgba(68, 209, 123, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
                  <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-good)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>SAM</span>
                  <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{research.market_context.serviceable_addressable_market}</span>
                </div>
                <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(139, 124, 255, 0.15), rgba(139, 124, 255, 0.05))', border: '1px solid rgba(139, 124, 255, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
                  <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-2)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>SOM</span>
                  <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{research.market_context.serviceable_obtainable_market}</span>
                </div>
              </div>
              {research.market_context.uncertainty_factors.length > 0 && (
                <div style={{ padding: '1rem', background: 'rgba(255, 207, 90, 0.08)', border: '1px solid rgba(255, 207, 90, 0.2)', borderRadius: '8px' }}>
                  <strong style={{ color: 'var(--color-warn)' }}>Uncertainty Factors:</strong>
                  <ul style={{ marginTop: '0.5rem' }}>
                    {research.market_context.uncertainty_factors.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Research Quality Self-Check */}
        {research.research_quality_check && (
          <div className="pack-section content-section" style={{ background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.2)' }}>
            <div className="section-header">
              <h3 className="section-title" style={{ color: 'var(--color-good)' }}>Research Quality Self-Check</h3>
            </div>
            <div className="section-content">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{
                  padding: '1rem',
                  background: research.research_quality_check.could_kill_idea ? 'rgba(68, 209, 123, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${research.research_quality_check.could_kill_idea ? 'rgba(68, 209, 123, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: '8px',
                  color: research.research_quality_check.could_kill_idea ? 'var(--color-good)' : 'var(--color-error)',
                  fontWeight: 600
                }}>
                  {research.research_quality_check.could_kill_idea ? '✓' : '✗'} Could kill the idea
                </div>
                <div style={{
                  padding: '1rem',
                  background: research.research_quality_check.skeptic_would_trust ? 'rgba(68, 209, 123, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${research.research_quality_check.skeptic_would_trust ? 'rgba(68, 209, 123, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: '8px',
                  color: research.research_quality_check.skeptic_would_trust ? 'var(--color-good)' : 'var(--color-error)',
                  fontWeight: 600
                }}>
                  {research.research_quality_check.skeptic_would_trust ? '✓' : '✗'} Skeptic would trust
                </div>
                <div style={{
                  padding: '1rem',
                  background: research.research_quality_check.assumptions_separated ? 'rgba(68, 209, 123, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${research.research_quality_check.assumptions_separated ? 'rgba(68, 209, 123, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: '8px',
                  color: research.research_quality_check.assumptions_separated ? 'var(--color-good)' : 'var(--color-error)',
                  fontWeight: 600
                }}>
                  {research.research_quality_check.assumptions_separated ? '✓' : '✗'} Assumptions separated
                </div>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px', borderLeft: '3px solid var(--color-good)' }}>
                <em style={{ color: 'var(--color-muted)' }}>Self-critique:</em> {research.research_quality_check.self_critique}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Legacy format display
  return (
    <div>
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Market Size</h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(109, 94, 252, 0.15), rgba(109, 94, 252, 0.05))', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-2)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>TAM</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{research.total_addressable_market}</span>
            </div>
            <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(68, 209, 123, 0.15), rgba(68, 209, 123, 0.05))', border: '1px solid rgba(68, 209, 123, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-good)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>SAM</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{research.serviceable_addressable_market}</span>
            </div>
            <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(139, 124, 255, 0.15), rgba(139, 124, 255, 0.05))', border: '1px solid rgba(139, 124, 255, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-2)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>SOM</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{research.serviceable_obtainable_market}</span>
            </div>
          </div>
        </div>
      </div>

      {research.user_personas && research.user_personas.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">User Personas</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
              {research.user_personas.map((persona, i) => (
                <div key={i} style={{ padding: '1.5rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px' }}>
                  <div style={{ marginBottom: '1rem' }}>
                    <h4 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: '0.25rem' }}>{persona.name}</h4>
                    <span style={{ display: 'inline-block', padding: '0.25rem 0.75rem', borderRadius: '6px', background: 'rgba(109, 94, 252, 0.2)', border: '1px solid rgba(109, 94, 252, 0.3)', color: 'var(--color-accent-2)', fontSize: '0.75rem', fontWeight: 600 }}>{persona.role}</span>
                  </div>
                  <p style={{ fontStyle: 'italic', color: 'var(--color-muted)', marginBottom: '1rem', padding: '0.75rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px', borderLeft: '3px solid var(--color-accent)' }}>"{persona.quote}"</p>
                  <div style={{ display: 'grid', gap: '1rem' }}>
                    <div>
                      <strong style={{ color: 'var(--color-good)' }}>Goals:</strong>
                      <ul style={{ marginTop: '0.5rem' }}>
                        {persona.goals.slice(0, 3).map((goal, j) => (
                          <li key={j}>{goal}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <strong style={{ color: 'var(--color-error)' }}>Frustrations:</strong>
                      <ul style={{ marginTop: '0.5rem' }}>
                        {persona.frustrations.slice(0, 3).map((f, j) => (
                          <li key={j}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {research.pain_points && research.pain_points.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Pain Points</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {research.pain_points.map((pain, i) => (
                <div key={i} style={{
                  padding: '1.25rem',
                  background: pain.severity === 'high' ? 'rgba(239, 68, 68, 0.08)' : pain.severity === 'medium' ? 'rgba(255, 207, 90, 0.08)' : 'rgba(255, 255, 255, 0.03)',
                  border: `1px solid ${pain.severity === 'high' ? 'rgba(239, 68, 68, 0.3)' : pain.severity === 'medium' ? 'rgba(255, 207, 90, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                  borderRadius: '8px',
                  borderLeft: `4px solid ${pain.severity === 'high' ? 'var(--color-error)' : pain.severity === 'medium' ? 'var(--color-warn)' : 'var(--color-muted)'}`,
                }}>
                  <span style={{ display: 'inline-block', padding: '0.25rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700, background: pain.severity === 'high' ? 'var(--color-error)' : pain.severity === 'medium' ? 'var(--color-warn)' : 'var(--color-muted)', color: 'white', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
                    {pain.severity}
                  </span>
                  <p style={{ marginBottom: pain.current_workaround ? '0.75rem' : '0' }}>{pain.description}</p>
                  {pain.current_workaround && (
                    <span style={{ display: 'block', padding: '0.5rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', fontSize: '0.875rem', color: 'var(--color-muted)' }}>
                      <strong>Current workaround:</strong> {pain.current_workaround}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {research.competitors && research.competitors.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Competitive Landscape</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
              {research.competitors.map((comp, i) => (
                <div key={i} style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
                  <h4 style={{ marginBottom: '0.5rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1.125rem' }}>{comp.name}</h4>
                  <p style={{ marginBottom: '1rem', color: 'var(--color-accent-2)', fontSize: '0.875rem', fontStyle: 'italic' }}>{comp.market_position}</p>
                  <div style={{ display: 'grid', gap: '1rem' }}>
                    <div>
                      <strong style={{ color: 'var(--color-good)' }}>Strengths:</strong>
                      <ul style={{ marginTop: '0.5rem' }}>
                        {comp.strengths.slice(0, 3).map((s, j) => (
                          <li key={j}>{s}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <strong style={{ color: 'var(--color-error)' }}>Weaknesses:</strong>
                      <ul style={{ marginTop: '0.5rem' }}>
                        {comp.weaknesses.slice(0, 3).map((w, j) => (
                          <li key={j}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function BusinessCaseTab({ businessCase }: { businessCase: InceptionPack['business_case'] }) {
  const canvas = businessCase.lean_canvas;

  return (
    <div>
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Lean Canvas</h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1.25rem', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-error)', fontWeight: 700, fontSize: '1rem' }}>Problem</h4>
              <ul>
                {canvas.problem.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(68, 209, 123, 0.08)', border: '1px solid rgba(68, 209, 123, 0.2)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-good)', fontWeight: 700, fontSize: '1rem' }}>Solution</h4>
              <ul>
                {canvas.solution.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(109, 94, 252, 0.12)', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-accent-2)', fontWeight: 700, fontSize: '1rem' }}>Unique Value Proposition</h4>
              <p>{canvas.unique_value_proposition}</p>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(255, 207, 90, 0.08)', border: '1px solid rgba(255, 207, 90, 0.2)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-warn)', fontWeight: 700, fontSize: '1rem' }}>Unfair Advantage</h4>
              <p>{canvas.unfair_advantage}</p>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1rem' }}>Customer Segments</h4>
              <ul>
                {canvas.customer_segments.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1rem' }}>Key Metrics</h4>
              <ul>
                {canvas.key_metrics.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1rem' }}>Channels</h4>
              <ul>
                {canvas.channels.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.15)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-error)', fontWeight: 700, fontSize: '1rem' }}>Cost Structure</h4>
              <ul>
                {canvas.cost_structure.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
            <div style={{ padding: '1.25rem', background: 'rgba(68, 209, 123, 0.08)', border: '1px solid rgba(68, 209, 123, 0.2)', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-good)', fontWeight: 700, fontSize: '1rem' }}>Revenue Streams</h4>
              <ul>
                {canvas.revenue_streams.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <DollarSign size={18} /> Financial Projections
          </h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(68, 209, 123, 0.15), rgba(68, 209, 123, 0.05))', border: '1px solid rgba(68, 209, 123, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-good)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Year 1</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{businessCase.year_1_projection}</span>
            </div>
            <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(109, 94, 252, 0.15), rgba(109, 94, 252, 0.05))', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-2)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Year 3</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{businessCase.year_3_projection}</span>
            </div>
            <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(255, 207, 90, 0.15), rgba(255, 207, 90, 0.05))', border: '1px solid rgba(255, 207, 90, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-warn)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Break-even</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{businessCase.break_even_analysis}</span>
            </div>
            <div style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(139, 124, 255, 0.15), rgba(139, 124, 255, 0.05))', border: '1px solid rgba(139, 124, 255, 0.3)', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-2)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Funding Required</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text)' }}>{businessCase.funding_requirement}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Go-to-Market Strategy</h3>
        </div>
        <div className="section-content">
          <p>{businessCase.go_to_market_strategy}</p>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Revenue Streams</h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {businessCase.revenue_streams.map((stream, i) => (
              <div key={i} style={{ padding: '1.25rem', background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.2)', borderRadius: '8px', borderLeft: '3px solid var(--color-good)' }}>
                <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1.125rem' }}>{stream.name}</h4>
                <p style={{ marginBottom: '1rem', color: 'var(--color-muted)' }}>{stream.description}</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
                  <span style={{ padding: '0.5rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px' }}><strong>Model:</strong> {stream.pricing_model}</span>
                  <span style={{ padding: '0.5rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px' }}><strong>Contribution:</strong> {stream.estimated_contribution}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function PRDTab({
  prd,
  expandedEpics,
  toggleEpic,
}: {
  prd: InceptionPack['product_requirements_document'];
  expandedEpics: Set<string>;
  toggleEpic: (id: string) => void;
}) {
  if (!prd) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--color-muted)' }}>
        <FileText size={48} style={{ marginBottom: '1rem', color: 'var(--color-muted-2)' }} />
        <h3 style={{ marginBottom: '0.5rem', color: 'var(--color-text)', fontSize: '1.5rem', fontWeight: 700 }}>PRD Not Available</h3>
        <p>The Product Requirements Document was not generated for this session.</p>
      </div>
    );
  }

  // Handle both new and old PRD formats
  const epics = prd.epics || [];
  const totalStories = epics.reduce((sum, epic) => sum + (epic.stories?.length || 0), 0);

  // Get overview - handle both formats
  const overview = prd.product_overview?.vision || prd.overview || '';
  const productName = prd.product_overview?.name || '';
  const problemStatement = prd.product_overview?.problem_statement || '';

  // Get objectives - handle both formats
  const objectives = prd.product_overview?.objectives || prd.objectives || [];

  // Get scope - handle both formats
  const scopeIn = prd.scope?.in_scope || prd.scope_in || [];
  const scopeOut = prd.scope?.out_of_scope || prd.scope_out || [];

  // Get release plan - handle both formats
  const releasePhases = Array.isArray(prd.release_plan)
    ? prd.release_plan
    : (prd.release_plan as { phases?: Array<{ name: string; description: string; features: string[]; success_criteria: string[] }> })?.phases || [];

  // Get statistics if available
  const stats = prd.statistics;
  const qualityScore = prd.quality_score;

  return (
    <div>
      {/* Quality and Stats Banner */}
      {(stats || qualityScore !== undefined) && (
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', padding: '1.5rem', background: 'linear-gradient(135deg, rgba(109, 94, 252, 0.15), rgba(109, 94, 252, 0.05))', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
          {qualityScore !== undefined && (
            <div style={{ textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '2rem', fontWeight: 700, color: 'var(--color-text)' }}>{(qualityScore * 100).toFixed(0)}%</span>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Quality Score</span>
            </div>
          )}
          {stats && (
            <>
              <div style={{ textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '2rem', fontWeight: 700, color: 'var(--color-accent-2)' }}>{stats.total_epics}</span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Epics</span>
              </div>
              <div style={{ textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '2rem', fontWeight: 700, color: 'var(--color-good)' }}>{stats.total_stories}</span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Stories</span>
              </div>
              <div style={{ textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '2rem', fontWeight: 700, color: 'var(--color-text)' }}>{stats.total_story_points}</span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Story Points</span>
              </div>
              <div style={{ textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '2rem', fontWeight: 700, color: 'var(--color-accent-2)' }}>{stats.total_functional_requirements}</span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>FRs</span>
              </div>
              <div style={{ textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '2rem', fontWeight: 700, color: 'var(--color-warn)' }}>{stats.total_non_functional_requirements}</span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>NFRs</span>
              </div>
            </>
          )}
        </div>
      )}

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">{productName ? `${productName} - Overview` : 'Overview'}</h3>
        </div>
        <div className="section-content">
          {problemStatement && <p style={{ marginBottom: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', borderLeft: '3px solid var(--color-error)' }}><strong style={{ color: 'var(--color-error)' }}>Problem:</strong> {problemStatement}</p>}
          <p>{overview}</p>
        </div>
      </div>

      {objectives.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Objectives</h3>
          </div>
          <div className="section-content">
            <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {objectives.map((obj, i) => (
                <li key={i} style={{ padding: '0.75rem 0.75rem 0.75rem 1rem', background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.2)', borderRadius: '6px', borderLeft: '3px solid var(--color-good)' }}>{obj}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {(scopeIn.length > 0 || scopeOut.length > 0) && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {scopeIn.length > 0 && (
            <div className="pack-section content-section" style={{ background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.2)' }}>
              <div className="section-header">
                <h3 className="section-title" style={{ color: 'var(--color-good)' }}>In Scope</h3>
              </div>
              <div className="section-content">
                <ul>
                  {scopeIn.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
          {scopeOut.length > 0 && (
            <div className="pack-section content-section" style={{ background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <div className="section-header">
                <h3 className="section-title" style={{ color: 'var(--color-error)' }}>Out of Scope</h3>
              </div>
              <div className="section-content">
                <ul>
                  {scopeOut.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {epics.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">
              Epics & User Stories
              <span style={{ marginLeft: '1rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-muted)' }}>
                {epics.length} epics, {totalStories} stories
              </span>
            </h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {epics.map((epic) => (
                <EpicCard
                  key={epic.id}
                  epic={epic}
                  isExpanded={expandedEpics.has(epic.id)}
                  onToggle={() => toggleEpic(epic.id)}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {releasePhases.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Release Plan</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {releasePhases.map((phase, i) => (
                <div key={i} style={{ padding: '1.5rem', background: 'rgba(109, 94, 252, 0.08)', border: '1px solid rgba(109, 94, 252, 0.2)', borderRadius: '10px', borderLeft: '4px solid var(--color-accent)' }}>
                  <div style={{ marginBottom: '1rem' }}>
                    <span style={{ display: 'inline-block', padding: '0.5rem 1rem', borderRadius: '8px', background: 'var(--color-accent)', color: 'white', fontWeight: 700, fontSize: '1rem' }}>
                      {(phase as { phase?: string; name?: string }).phase || (phase as { name?: string }).name}
                    </span>
                  </div>
                  <p style={{ marginBottom: '1rem' }}>{phase.description}</p>
                  {phase.features && phase.features.length > 0 && (
                    <div>
                      <strong style={{ color: 'var(--color-accent-2)' }}>Features:</strong>
                      <ul style={{ marginTop: '0.5rem' }}>
                        {phase.features.map((f, j) => (
                          <li key={j}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function EpicCard({
  epic,
  isExpanded,
  onToggle,
}: {
  epic: Epic;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const stories = epic.stories || [];
  const totalPoints = stories.reduce((sum, s) => sum + (s.story_points || 0), 0);

  return (
    <div style={{ border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', overflow: 'hidden' }}>
      <button
        onClick={onToggle}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '1rem 1.25rem',
          background: 'transparent',
          border: 'none',
          color: 'var(--color-text)',
          cursor: 'pointer',
          fontSize: '1rem',
          textAlign: 'left',
          transition: 'background 0.2s'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
      >
        {isExpanded ? <ChevronDown size={20} style={{ color: 'var(--color-accent)' }} /> : <ChevronRight size={20} style={{ color: 'var(--color-muted)' }} />}
        <span style={{ padding: '0.25rem 0.75rem', borderRadius: '6px', background: 'rgba(109, 94, 252, 0.2)', border: '1px solid rgba(109, 94, 252, 0.4)', color: 'var(--color-accent-2)', fontSize: '0.75rem', fontWeight: 700 }}>{epic.id}</span>
        <span style={{ flex: 1, fontWeight: 600 }}>{epic.title}</span>
        {epic.priority && (
          <span style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '6px',
            fontSize: '0.75rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            background: epic.priority === 'high' ? 'var(--color-error)' : epic.priority === 'medium' ? 'var(--color-warn)' : 'var(--color-muted)',
            color: 'white'
          }}>
            {epic.priority}
          </span>
        )}
        <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>{stories.length} stories{totalPoints > 0 ? ` (${totalPoints} pts)` : ''}</span>
      </button>

      {isExpanded && (
        <div style={{ padding: '0 1.25rem 1.25rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
          <p style={{ marginTop: '1rem', marginBottom: '1rem', color: 'var(--color-muted)' }}>{epic.description}</p>
          {epic.business_value && (
            <p style={{ marginBottom: '1rem', padding: '0.75rem', background: 'rgba(68, 209, 123, 0.08)', border: '1px solid rgba(68, 209, 123, 0.2)', borderRadius: '6px', borderLeft: '3px solid var(--color-good)' }}>
              <strong style={{ color: 'var(--color-good)' }}>Business Value:</strong> {epic.business_value}
            </p>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
            {stories.map((story) => (
              <StoryCard key={story.id} story={story} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StoryCard({ story }: { story: UserStory }) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Check if acceptance criteria are in old format (objects with given/when/then) or new format (strings)
  const hasOldFormatAC = story.acceptance_criteria?.length > 0 &&
    typeof story.acceptance_criteria[0] === 'object' &&
    'given' in (story.acceptance_criteria[0] as AcceptanceCriteria);

  return (
    <div style={{ border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.02)' }}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.75rem 1rem',
          background: 'transparent',
          border: 'none',
          color: 'var(--color-text)',
          cursor: 'pointer',
          fontSize: '0.9375rem',
          textAlign: 'left',
          transition: 'background 0.2s'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
      >
        {isExpanded ? <ChevronDown size={16} style={{ color: 'var(--color-accent)' }} /> : <ChevronRight size={16} style={{ color: 'var(--color-muted)' }} />}
        <span style={{ padding: '0.25rem 0.5rem', borderRadius: '4px', background: 'rgba(255, 255, 255, 0.08)', fontSize: '0.6875rem', fontWeight: 700, fontFamily: 'monospace' }}>{story.id}</span>
        <span style={{ flex: 1 }}>{story.title}</span>
        <span style={{
          padding: '0.125rem 0.5rem',
          borderRadius: '4px',
          fontSize: '0.6875rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          background: story.priority === 'high' ? 'rgba(239, 68, 68, 0.2)' : story.priority === 'medium' ? 'rgba(255, 207, 90, 0.2)' : 'rgba(255, 255, 255, 0.1)',
          color: story.priority === 'high' ? 'var(--color-error)' : story.priority === 'medium' ? 'var(--color-warn)' : 'var(--color-muted)'
        }}>
          {story.priority}
        </span>
        {story.story_points && <span style={{ padding: '0.125rem 0.5rem', borderRadius: '4px', fontSize: '0.6875rem', fontWeight: 700, background: 'rgba(109, 94, 252, 0.2)', color: 'var(--color-accent-2)' }}>{story.story_points} pts</span>}
        {story.size && <span style={{ padding: '0.125rem 0.5rem', borderRadius: '4px', fontSize: '0.6875rem', fontWeight: 600, background: 'rgba(255, 255, 255, 0.08)', color: 'var(--color-muted)' }}>{story.size}</span>}
      </button>

      {isExpanded && (
        <div style={{ padding: '0 1rem 1rem', fontSize: '0.875rem' }}>
          {/* New format: description contains the full user story */}
          {story.description && (
            <p style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>{story.description}</p>
          )}

          {/* Old format: as_a / i_want / so_that */}
          {story.as_a && story.i_want && story.so_that && (
            <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(109, 94, 252, 0.06)', border: '1px solid rgba(109, 94, 252, 0.15)', borderRadius: '6px' }}>
              <p style={{ marginBottom: '0.5rem' }}>
                <strong style={{ color: 'var(--color-accent-2)' }}>As a</strong> {story.as_a},
              </p>
              <p style={{ marginBottom: '0.5rem' }}>
                <strong style={{ color: 'var(--color-accent-2)' }}>I want</strong> {story.i_want},
              </p>
              <p>
                <strong style={{ color: 'var(--color-accent-2)' }}>So that</strong> {story.so_that}.
              </p>
            </div>
          )}

          {story.acceptance_criteria && story.acceptance_criteria.length > 0 && (
            <div style={{ marginTop: '0.75rem' }}>
              <strong style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--color-good)' }}>Acceptance Criteria:</strong>
              {hasOldFormatAC ? (
                // Old format: Given/When/Then objects
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {(story.acceptance_criteria as AcceptanceCriteria[]).map((ac, i) => (
                    <div key={i} style={{ padding: '0.75rem', background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.15)', borderRadius: '6px' }}>
                      <p style={{ marginBottom: '0.25rem' }}>
                        <em style={{ color: 'var(--color-good)' }}>Given</em> {ac.given}
                      </p>
                      <p style={{ marginBottom: '0.25rem' }}>
                        <em style={{ color: 'var(--color-good)' }}>When</em> {ac.when}
                      </p>
                      <p>
                        <em style={{ color: 'var(--color-good)' }}>Then</em> {ac.then}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                // New format: string array
                <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {(story.acceptance_criteria as string[]).map((ac, i) => (
                    <li key={i} style={{ padding: '0.5rem 0.5rem 0.5rem 0.75rem', background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.15)', borderRadius: '6px', borderLeft: '3px solid var(--color-good)' }}>{ac}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {story.notes && (
            <p style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(255, 207, 90, 0.08)', border: '1px solid rgba(255, 207, 90, 0.2)', borderRadius: '6px' }}>
              <strong style={{ color: 'var(--color-warn)' }}>Notes:</strong> {story.notes}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function ArchitectureTab({ architecture }: { architecture: InceptionPack['technical_architecture'] }) {
  return (
    <div>
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Architecture Style</h3>
        </div>
        <div className="section-content">
          <p style={{ padding: '1rem', background: 'rgba(109, 94, 252, 0.12)', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '8px', color: 'var(--color-accent-2)', fontWeight: 700, fontSize: '1.125rem', marginBottom: '1rem' }}>{architecture.architecture_style}</p>
          <p>{architecture.architecture_diagram_description}</p>
        </div>
      </div>

      {architecture.architecture_diagram_mermaid && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Cpu size={18} /> System Architecture Diagram
            </h3>
          </div>
          <div className="section-content">
            <MermaidDiagram chart={architecture.architecture_diagram_mermaid} />
          </div>
        </div>
      )}

      {architecture.sequence_diagram_mermaid && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Cpu size={18} /> Sequence Diagram — Primary User Flow
            </h3>
          </div>
          <div className="section-content">
            <MermaidDiagram chart={architecture.sequence_diagram_mermaid} />
          </div>
        </div>
      )}

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Technology Stack</h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
            {architecture.technology_stack.map((tech, i) => (
              <div key={i} style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
                <span style={{ display: 'inline-block', padding: '0.25rem 0.75rem', borderRadius: '6px', background: 'rgba(109, 94, 252, 0.2)', border: '1px solid rgba(109, 94, 252, 0.4)', color: 'var(--color-accent-2)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.75rem' }}>{tech.category}</span>
                <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1.125rem' }}>{tech.technology}</h4>
                <p style={{ marginBottom: '0.75rem', color: 'var(--color-muted)' }}>{tech.rationale}</p>
                {tech.alternatives_considered.length > 0 && (
                  <span style={{ display: 'block', padding: '0.5rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', fontSize: '0.75rem', color: 'var(--color-muted-2)' }}>
                    <strong>Alternatives:</strong> {tech.alternatives_considered.join(', ')}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">System Components</h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {architecture.system_components.map((comp, i) => (
              <div key={i} style={{ padding: '1.25rem', background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.2)', borderRadius: '8px', borderLeft: '3px solid var(--color-good)' }}>
                <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-text)', fontWeight: 700, fontSize: '1.125rem' }}>{comp.name}</h4>
                <p style={{ marginBottom: '1rem', color: 'var(--color-muted)' }}>{comp.description}</p>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  <div>
                    <strong style={{ color: 'var(--color-good)' }}>Responsibilities:</strong>
                    <ul style={{ marginTop: '0.5rem' }}>
                      {comp.responsibilities.map((r, j) => (
                        <li key={j}>{r}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--color-accent-2)' }}>Technologies:</strong>
                    <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {comp.technologies.map((t, j) => (
                        <span key={j} style={{ padding: '0.25rem 0.75rem', borderRadius: '6px', background: 'rgba(109, 94, 252, 0.2)', border: '1px solid rgba(109, 94, 252, 0.3)', color: 'var(--color-accent-2)', fontSize: '0.75rem', fontWeight: 600 }}>
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div className="pack-section content-section" style={{ background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-error)' }}>
              <Shield size={18} /> Security
            </h3>
          </div>
          <div className="section-content">
            <p>{architecture.security_architecture}</p>
          </div>
        </div>
        <div className="pack-section content-section" style={{ background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.2)' }}>
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-good)' }}>
              <TrendingUp size={18} /> Scalability
            </h3>
          </div>
          <div className="section-content">
            <p>{architecture.scalability_approach}</p>
          </div>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Deployment Strategy</h3>
        </div>
        <div className="section-content">
          <p>{architecture.deployment_strategy}</p>
        </div>
      </div>

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Infrastructure Requirements</h3>
        </div>
        <div className="section-content">
          <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {architecture.infrastructure_requirements.map((req, i) => (
              <li key={i} style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '6px', borderLeft: '3px solid var(--color-accent)' }}>{req}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function QualityTab({
  quality,
  metadata,
}: {
  quality: InceptionPack['quality_assessment'];
  metadata: InceptionPack['metadata'];
}) {
  const overallScore = quality?.overall_score || 0;
  const passed = quality?.passed ?? false;
  const iteration = quality?.iteration ?? 1;
  const readyForDelivery = quality?.ready_for_delivery ?? false;
  const sectionScores = quality?.section_scores || [];
  const strengths = quality?.strengths || [];
  const weaknesses = quality?.weaknesses || [];
  const recommendations = quality?.recommendations || [];
  const criticalGaps = quality?.critical_gaps || [];

  return (
    <div>
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Overall Assessment</h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{
              width: '140px',
              height: '140px',
              borderRadius: '50%',
              background: `conic-gradient(var(--color-accent) ${overallScore * 360}deg, rgba(255, 255, 255, 0.1) 0deg)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative'
            }}>
              <div style={{
                width: '110px',
                height: '110px',
                borderRadius: '50%',
                background: 'var(--color-bg-1)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-text)' }}>{(overallScore * 100).toFixed(0)}%</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Quality</span>
              </div>
            </div>
            <div style={{ flex: 1 }}>
              {passed ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', background: 'rgba(68, 209, 123, 0.1)', border: '1px solid rgba(68, 209, 123, 0.3)', borderRadius: '8px', marginBottom: '1rem' }}>
                  <CheckCircle2 size={24} style={{ color: 'var(--color-good)' }} />
                  <span style={{ fontWeight: 700, fontSize: '1.125rem', color: 'var(--color-good)' }}>Quality Check Passed</span>
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', marginBottom: '1rem' }}>
                  <Shield size={24} style={{ color: 'var(--color-error)' }} />
                  <span style={{ fontWeight: 700, fontSize: '1.125rem', color: 'var(--color-error)' }}>Below Threshold</span>
                </div>
              )}
              <p style={{ marginBottom: '0.5rem', color: 'var(--color-muted)' }}>Iteration: <strong style={{ color: 'var(--color-text)' }}>{iteration}</strong></p>
              {readyForDelivery && (
                <span style={{ display: 'inline-block', padding: '0.5rem 1rem', borderRadius: '8px', background: 'var(--color-accent)', color: 'white', fontWeight: 700, fontSize: '0.875rem' }}>Ready for Delivery</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {sectionScores.length > 0 && (
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Section Scores</h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {sectionScores.map((section, i) => (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--color-text)' }}>{section.section}</span>
                  <span style={{ fontWeight: 700, color: (section.score || 0) >= 0.8 ? 'var(--color-good)' : (section.score || 0) >= 0.6 ? 'var(--color-warn)' : 'var(--color-error)' }}>{((section.score || 0) * 100).toFixed(0)}%</span>
                </div>
                <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden', marginBottom: '0.5rem' }}>
                  <div
                    style={{
                      width: `${(section.score || 0) * 100}%`,
                      height: '100%',
                      background: (section.score || 0) >= 0.8 ? 'var(--color-good)' : (section.score || 0) >= 0.6 ? 'var(--color-warn)' : 'var(--color-error)',
                      transition: 'width 0.3s ease'
                    }}
                  />
                </div>
                <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}>{section.feedback}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {strengths.length > 0 && (
        <div className="pack-section content-section" style={{ background: 'rgba(68, 209, 123, 0.06)', border: '1px solid rgba(68, 209, 123, 0.2)' }}>
          <div className="section-header">
            <h3 className="section-title" style={{ color: 'var(--color-good)' }}>Strengths</h3>
          </div>
          <div className="section-content">
            <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {strengths.map((s, i) => (
                <li key={i} style={{ padding: '0.75rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px', borderLeft: '3px solid var(--color-good)' }}>{s}</li>
              ))}
            </ul>
          </div>
        </div>
        )}

        {weaknesses.length > 0 && (
          <div className="pack-section content-section" style={{ background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <div className="section-header">
              <h3 className="section-title" style={{ color: 'var(--color-error)' }}>Areas for Improvement</h3>
            </div>
            <div className="section-content">
              <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {weaknesses.map((w, i) => (
                  <li key={i} style={{ padding: '0.75rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px', borderLeft: '3px solid var(--color-error)' }}>{w}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {criticalGaps.length > 0 && (
        <div className="pack-section content-section" style={{ background: 'rgba(239, 168, 68, 0.06)', border: '1px solid rgba(239, 168, 68, 0.2)' }}>
          <div className="section-header">
            <h3 className="section-title" style={{ color: 'var(--color-warn)' }}>Critical Gaps</h3>
          </div>
          <div className="section-content">
            <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {criticalGaps.map((g, i) => (
                <li key={i} style={{ padding: '0.75rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px', borderLeft: '3px solid var(--color-warn)' }}>{g}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Recommendations</h3>
          </div>
          <div className="section-content">
            <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {recommendations.map((r, i) => (
                <li key={i} style={{ padding: '0.75rem 0.75rem 0.75rem 1rem', background: 'rgba(109, 94, 252, 0.08)', border: '1px solid rgba(109, 94, 252, 0.2)', borderRadius: '6px', borderLeft: '3px solid var(--color-accent)' }}>{r}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={18} /> Generation Metadata
          </h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Session ID</span>
              <span style={{ display: 'block', fontWeight: 600, color: 'var(--color-text)', fontFamily: 'monospace', fontSize: '0.875rem' }}>{metadata?.session_id || 'N/A'}</span>
            </div>
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Generated At</span>
              <span style={{ display: 'block', fontWeight: 600, color: 'var(--color-text)', fontSize: '0.875rem' }}>{metadata?.generated_at ? new Date(metadata.generated_at).toLocaleString() : 'N/A'}</span>
            </div>
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Duration</span>
              <span style={{ display: 'block', fontWeight: 700, color: 'var(--color-text)', fontSize: '1.5rem' }}>{Math.round(metadata?.total_duration_seconds || 0)}s</span>
            </div>
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Iterations</span>
              <span style={{ display: 'block', fontWeight: 700, color: 'var(--color-accent-2)', fontSize: '1.5rem' }}>{metadata?.iterations || 1}</span>
            </div>
            <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', textAlign: 'center' }}>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Tokens Used</span>
              <span style={{ display: 'block', fontWeight: 700, color: 'var(--color-good)', fontSize: '1.5rem' }}>{(metadata?.total_tokens_used || 0).toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LegalReviewTab({ legalReview }: { legalReview: LegalRegulatoryReview }) {
  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'var(--color-error)';
      case 'medium': return 'var(--color-warn)';
      case 'low': return 'var(--color-good)';
      default: return 'var(--color-muted)';
    }
  };

  const getRiskBg = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'rgba(239, 68, 68, 0.1)';
      case 'medium': return 'rgba(255, 207, 90, 0.1)';
      case 'low': return 'rgba(68, 209, 123, 0.1)';
      default: return 'rgba(255, 255, 255, 0.05)';
    }
  };

  return (
    <div>
      {/* Executive Summary */}
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Legal & Regulatory Overview</h3>
        </div>
        <div className="section-content">
          <p style={{ lineHeight: 1.8, color: 'var(--color-muted)' }}>{legalReview.executive_summary}</p>
        </div>
      </div>

      {/* Overall Risk Assessment */}
      <div className="pack-section content-section" style={{
        background: getRiskBg(legalReview.overall_risk_assessment.risk_level),
        border: `1px solid ${getRiskColor(legalReview.overall_risk_assessment.risk_level)}40`
      }}>
        <div className="section-header">
          <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={18} style={{ color: getRiskColor(legalReview.overall_risk_assessment.risk_level) }} />
            Overall Risk Assessment
          </h3>
        </div>
        <div className="section-content">
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <div style={{
              padding: '1.5rem 2rem',
              borderRadius: '12px',
              background: getRiskBg(legalReview.overall_risk_assessment.risk_level),
              border: `2px solid ${getRiskColor(legalReview.overall_risk_assessment.risk_level)}`,
              textAlign: 'center'
            }}>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Risk Level</span>
              <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 700, color: getRiskColor(legalReview.overall_risk_assessment.risk_level), textTransform: 'uppercase' }}>
                {legalReview.overall_risk_assessment.risk_level}
              </span>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ color: 'var(--color-text)' }}>Timeline Buffer:</strong>
                <span style={{ marginLeft: '0.5rem', color: 'var(--color-muted)' }}>{legalReview.overall_risk_assessment.recommended_timeline_buffer}</span>
              </div>
              <div>
                <strong style={{ color: 'var(--color-text)' }}>Budget Allocation:</strong>
                <span style={{ marginLeft: '0.5rem', color: 'var(--color-muted)' }}>{legalReview.overall_risk_assessment.recommended_budget_allocation}</span>
              </div>
            </div>
          </div>

          {legalReview.overall_risk_assessment.key_concerns.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-text)', fontSize: '1rem' }}>Key Concerns</h4>
              <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {legalReview.overall_risk_assessment.key_concerns.map((concern, i) => (
                  <li key={i} style={{ padding: '0.75rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px', borderLeft: `3px solid ${getRiskColor(legalReview.overall_risk_assessment.risk_level)}` }}>{concern}</li>
                ))}
              </ul>
            </div>
          )}

          {legalReview.overall_risk_assessment.blocking_issues.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ marginBottom: '0.75rem', color: 'var(--color-error)', fontSize: '1rem' }}>⚠️ Blocking Issues</h4>
              <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {legalReview.overall_risk_assessment.blocking_issues.map((issue, i) => (
                  <li key={i} style={{ padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px' }}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Applicable Regulations */}
      {legalReview.applicable_regulations.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Applicable Regulations ({legalReview.applicable_regulations.length})</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {legalReview.applicable_regulations.map((reg, i) => (
                <div key={i} style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <h4 style={{ margin: 0, color: 'var(--color-text)', fontSize: '1.1rem' }}>{reg.name}</h4>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      borderRadius: '100px',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      background: getRiskBg(reg.impact_level),
                      color: getRiskColor(reg.impact_level),
                      border: `1px solid ${getRiskColor(reg.impact_level)}40`
                    }}>
                      {reg.impact_level} Impact
                    </span>
                  </div>
                  <p style={{ color: 'var(--color-muted)', marginBottom: '0.75rem', lineHeight: 1.6 }}>{reg.description}</p>
                  <p style={{ color: 'var(--color-muted)', marginBottom: '0.75rem', fontSize: '0.875rem' }}>
                    <strong style={{ color: 'var(--color-text)' }}>Why it applies:</strong> {reg.applicability}
                  </p>
                  <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
                      <strong style={{ color: 'var(--color-text)' }}>Timeline:</strong> {reg.estimated_compliance_timeline}
                    </span>
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
                      <strong style={{ color: 'var(--color-text)' }}>Cost:</strong> {reg.estimated_compliance_cost}
                    </span>
                  </div>
                  {reg.compliance_requirements.length > 0 && (
                    <div style={{ marginTop: '0.75rem' }}>
                      <strong style={{ fontSize: '0.875rem', color: 'var(--color-text)', display: 'block', marginBottom: '0.5rem' }}>Compliance Requirements:</strong>
                      <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--color-muted)', fontSize: '0.875rem' }}>
                        {reg.compliance_requirements.map((req, j) => (
                          <li key={j} style={{ marginBottom: '0.25rem' }}>{req}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Legal Risks */}
      {legalReview.legal_risks.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Legal Risks ({legalReview.legal_risks.length})</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {legalReview.legal_risks.map((risk, i) => (
                <div key={i} style={{
                  padding: '1.25rem',
                  background: getRiskBg(risk.severity),
                  border: `1px solid ${getRiskColor(risk.severity)}30`,
                  borderRadius: '8px',
                  borderLeft: `4px solid ${getRiskColor(risk.severity)}`
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <h4 style={{ margin: 0, color: 'var(--color-text)', fontSize: '1rem' }}>{risk.risk_category}</h4>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        background: getRiskBg(risk.severity),
                        color: getRiskColor(risk.severity)
                      }}>
                        Severity: {risk.severity}
                      </span>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        background: 'rgba(255, 255, 255, 0.05)',
                        color: 'var(--color-muted)'
                      }}>
                        Likelihood: {risk.likelihood}
                      </span>
                    </div>
                  </div>
                  <p style={{ color: 'var(--color-muted)', marginBottom: '0.75rem', lineHeight: 1.6 }}>{risk.description}</p>
                  {risk.mitigation_strategies.length > 0 && (
                    <div>
                      <strong style={{ fontSize: '0.875rem', color: 'var(--color-text)', display: 'block', marginBottom: '0.5rem' }}>Mitigation Strategies:</strong>
                      <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--color-muted)', fontSize: '0.875rem' }}>
                        {risk.mitigation_strategies.map((strategy, j) => (
                          <li key={j} style={{ marginBottom: '0.25rem' }}>{strategy}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {risk.legal_counsel_recommended && (
                    <div style={{ marginTop: '0.75rem', padding: '0.5rem 0.75rem', background: 'rgba(109, 94, 252, 0.1)', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '4px', fontSize: '0.875rem' }}>
                      ⚖️ <strong>Legal counsel recommended</strong> for this risk
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Data Protection Requirements */}
      {legalReview.data_protection_requirements.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={18} /> Data Protection Requirements
            </h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {legalReview.data_protection_requirements.map((dp, i) => (
                <div key={i} style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
                  <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--color-accent-2)', fontSize: '1.1rem' }}>{dp.regulation}</h4>
                  <div style={{ marginBottom: '0.75rem' }}>
                    <strong style={{ fontSize: '0.875rem', color: 'var(--color-text)' }}>Data Types Covered:</strong>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                      {dp.data_types_covered.map((type, j) => (
                        <span key={j} style={{ padding: '0.25rem 0.75rem', background: 'rgba(109, 94, 252, 0.1)', border: '1px solid rgba(109, 94, 252, 0.3)', borderRadius: '100px', fontSize: '0.8rem' }}>{type}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{ marginBottom: '0.75rem' }}>
                    <strong style={{ fontSize: '0.875rem', color: 'var(--color-text)' }}>User Rights:</strong>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                      {dp.user_rights.map((right, j) => (
                        <span key={j} style={{ padding: '0.25rem 0.75rem', background: 'rgba(68, 209, 123, 0.1)', border: '1px solid rgba(68, 209, 123, 0.3)', borderRadius: '100px', fontSize: '0.8rem' }}>{right}</span>
                      ))}
                    </div>
                  </div>
                  <p style={{ color: 'var(--color-error)', fontSize: '0.875rem', marginTop: '0.75rem' }}>
                    <strong>Penalties:</strong> {dp.penalties_for_non_compliance}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Licensing Requirements */}
      {legalReview.licensing_requirements.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Licensing Requirements</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
              {legalReview.licensing_requirements.map((lic, i) => (
                <div key={i} style={{ padding: '1.25rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--color-text)', fontSize: '1rem' }}>{lic.license_type}</h4>
                  <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem', marginBottom: '0.75rem' }}>Issued by: {lic.issuing_authority}</p>
                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.75rem', fontSize: '0.875rem' }}>
                    <span style={{ color: 'var(--color-muted)' }}><strong>Timeline:</strong> {lic.timeline}</span>
                    <span style={{ color: 'var(--color-muted)' }}><strong>Cost:</strong> {lic.cost}</span>
                  </div>
                  <p style={{ color: 'var(--color-muted)', fontSize: '0.8rem' }}><strong>Renewal:</strong> {lic.renewal_requirements}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Intellectual Property */}
      {legalReview.intellectual_property.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Intellectual Property Considerations</h3>
          </div>
          <div className="section-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {legalReview.intellectual_property.map((ip, i) => (
                <div key={i} style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', borderLeft: '3px solid var(--color-accent)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <h4 style={{ margin: 0, color: 'var(--color-text)', fontSize: '1rem' }}>{ip.ip_type}</h4>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      background: ip.priority === 'critical' ? 'rgba(239, 68, 68, 0.2)' : ip.priority === 'high' ? 'rgba(255, 207, 90, 0.2)' : 'rgba(68, 209, 123, 0.2)',
                      color: ip.priority === 'critical' ? 'var(--color-error)' : ip.priority === 'high' ? 'var(--color-warn)' : 'var(--color-good)'
                    }}>
                      {ip.priority}
                    </span>
                  </div>
                  <p style={{ color: 'var(--color-muted)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>{ip.description}</p>
                  <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}><strong>Action:</strong> {ip.action_required}</p>
                  <p style={{ color: 'var(--color-muted)', fontSize: '0.875rem' }}><strong>Est. Cost:</strong> {ip.estimated_cost}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recommended Legal Structure */}
      <div className="pack-section content-section">
        <div className="section-header">
          <h3 className="section-title">Recommended Legal Structure</h3>
        </div>
        <div className="section-content">
          <p style={{ lineHeight: 1.8, color: 'var(--color-muted)' }}>{legalReview.recommended_legal_structure}</p>
        </div>
      </div>

      {/* Next Steps */}
      {legalReview.next_steps.length > 0 && (
        <div className="pack-section content-section" style={{ background: 'rgba(109, 94, 252, 0.06)', border: '1px solid rgba(109, 94, 252, 0.2)' }}>
          <div className="section-header">
            <h3 className="section-title" style={{ color: 'var(--color-accent-2)' }}>Recommended Next Steps</h3>
          </div>
          <div className="section-content">
            <ol style={{ margin: 0, paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {legalReview.next_steps.map((step, i) => (
                <li key={i} style={{ padding: '0.75rem', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '6px', color: 'var(--color-text)' }}>{step}</li>
              ))}
            </ol>
          </div>
        </div>
      )}

      {/* Ongoing Compliance Requirements */}
      {legalReview.ongoing_compliance_requirements.length > 0 && (
        <div className="pack-section content-section">
          <div className="section-header">
            <h3 className="section-title">Ongoing Compliance Requirements</h3>
          </div>
          <div className="section-content">
            <ul style={{ listStyleType: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {legalReview.ongoing_compliance_requirements.map((req, i) => (
                <li key={i} style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '6px', borderLeft: '3px solid var(--color-accent)' }}>{req}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
