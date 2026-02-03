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
} from 'lucide-react';
import type { InceptionPack, Epic, UserStory, AcceptanceCriteria } from '../types/api';

interface InceptionPackViewerProps {
  pack: InceptionPack;
  onNewDiscovery: () => void;
}

type TabId = 'summary' | 'research' | 'business' | 'prd' | 'architecture' | 'quality';

interface TabConfig {
  id: TabId;
  label: string;
  icon: typeof FileText;
}

const TABS: TabConfig[] = [
  { id: 'summary', label: 'Executive Summary', icon: FileText },
  { id: 'research', label: 'Customer Research', icon: Users },
  { id: 'business', label: 'Business Case', icon: TrendingUp },
  { id: 'prd', label: 'PRD', icon: Target },
  { id: 'architecture', label: 'Architecture', icon: Cpu },
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
      case 'quality':
        return <QualityTab quality={pack.quality_assessment} metadata={pack.metadata} />;
      default:
        return null;
    }
  };

  return (
    <div className="inception-pack-viewer">
      <div className="viewer-header">
        <div className="header-content">
          <h2>{pack.executive_summary.product_name}</h2>
          <p className="tagline">{pack.executive_summary.tagline}</p>
        </div>
        <div className="header-actions">
          <button className="download-button" onClick={handleDownload}>
            <Download size={18} />
            Download JSON
          </button>
          <button className="new-discovery-button" onClick={onNewDiscovery}>
            Start New Discovery
          </button>
        </div>
      </div>

      <div className="quality-badge">
        <Star size={16} />
        <span>Quality Score: {((pack.quality_assessment.overall_score || 0) * 100).toFixed(0)}%</span>
        {pack.quality_assessment.passed && <CheckCircle2 size={16} className="passed" />}
      </div>

      <nav className="tabs-nav">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon size={18} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="tab-content">{renderContent()}</div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Tab Components
// ═══════════════════════════════════════════════════════════════════════════════

function ExecutiveSummaryTab({ summary }: { summary: InceptionPack['executive_summary'] }) {
  return (
    <div className="tab-panel summary-panel">
      <section className="section">
        <h3>Problem Statement</h3>
        <p>{summary.problem_statement}</p>
      </section>

      <section className="section">
        <h3>Solution Overview</h3>
        <p>{summary.solution_overview}</p>
      </section>

      <section className="section">
        <h3>Value Proposition</h3>
        <p className="highlight">{summary.value_proposition}</p>
      </section>

      <div className="section-grid">
        <section className="section">
          <h3><Users size={18} /> Target Users</h3>
          <ul>
            {summary.target_users.map((user, i) => (
              <li key={i}>{user}</li>
            ))}
          </ul>
        </section>

        <section className="section">
          <h3><Zap size={18} /> Key Differentiators</h3>
          <ul>
            {summary.key_differentiators.map((diff, i) => (
              <li key={i}>{diff}</li>
            ))}
          </ul>
        </section>

        <section className="section">
          <h3><Target size={18} /> Success Metrics</h3>
          <ul>
            {summary.success_metrics.map((metric, i) => (
              <li key={i}>{metric}</li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

function CustomerResearchTab({ research }: { research: InceptionPack['customer_research'] }) {
  // Check if using new evidence-based format or legacy format
  const isNewFormat = research.research_scope || research.pain_signals;

  if (isNewFormat) {
    return (
      <div className="tab-panel research-panel">
        {/* Research Scope & Quality */}
        {research.research_scope && (
          <section className="section">
            <h3>Research Scope & Limitations</h3>
            <div className={`confidence-badge ${research.research_scope.confidence_level}`}>
              Confidence: {research.research_scope.confidence_level}
            </div>
            <p className="observation-context">{research.research_scope.observation_context}</p>
            <div className="scope-details">
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
                <ul className="gaps-list">
                  {research.research_scope.known_gaps.map((gap, i) => (
                    <li key={i}>{gap}</li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        )}

        {/* Job to Be Done */}
        {research.job_to_be_done && (
          <section className="section">
            <h3>Job-to-Be-Done</h3>
            <div className="jtbd-card">
              <div className="jtbd-item">
                <strong>Trigger:</strong>
                <p>{research.job_to_be_done.trigger_situation}</p>
              </div>
              <div className="jtbd-item">
                <strong>Goal:</strong>
                <p>{research.job_to_be_done.underlying_goal}</p>
              </div>
              <div className="jtbd-item">
                <strong>Success:</strong>
                <p>{research.job_to_be_done.success_definition}</p>
              </div>
            </div>
          </section>
        )}

        {/* Current Behaviour */}
        {research.current_behaviour && (
          <section className="section">
            <h3>Current Behaviour</h3>
            <div className="behaviour-grid">
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
                <ul className="friction-list">
                  {research.current_behaviour.friction_points.map((fp, i) => (
                    <li key={i}>{fp}</li>
                  ))}
                </ul>
              </div>
            </div>
            <p className="why-persists"><strong>Why This Problem Persists:</strong> {research.current_behaviour.why_problem_persists}</p>
          </section>
        )}

        {/* Pain Signals */}
        {research.pain_signals && research.pain_signals.length > 0 && (
          <section className="section">
            <h3>Pain Signals (Evidence-Tagged)</h3>
            <div className="pain-signals-list">
              {research.pain_signals.map((pain, i) => (
                <div key={i} className={`pain-signal severity-${pain.severity} ${pain.challenges_solution ? 'challenges-solution' : ''}`}>
                  <div className="pain-header">
                    <span className="severity-badge">{pain.severity}</span>
                    <span className="evidence-badge">{pain.evidence_tier}</span>
                    {pain.challenges_solution && <span className="challenges-badge">Challenges Solution</span>}
                  </div>
                  <p className="pain-description">{pain.description}</p>
                  <p className="evidence-detail"><em>Evidence:</em> {pain.evidence_detail}</p>
                  <p className="impact"><em>Impact:</em> {pain.impact}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Uncomfortable Insights */}
        {research.uncomfortable_insights && research.uncomfortable_insights.length > 0 && (
          <section className="section uncomfortable-section">
            <h3>Uncomfortable Insights</h3>
            <div className="insights-list">
              {research.uncomfortable_insights.map((insight, i) => (
                <div key={i} className="uncomfortable-insight">
                  <span className="evidence-badge">{insight.evidence_tier}</span>
                  <p className="insight-text">{insight.insight}</p>
                  <p className="implication"><em>Implication:</em> {insight.implication}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* What Customers Don't Care About */}
        {research.what_customers_dont_care_about && research.what_customers_dont_care_about.length > 0 && (
          <section className="section indifference-section">
            <h3>What Customers Don't Care About</h3>
            <div className="indifference-list">
              {research.what_customers_dont_care_about.map((item, i) => (
                <div key={i} className="indifference-item">
                  <span className="evidence-badge">{item.evidence_tier}</span>
                  <p><strong>Assumed:</strong> {item.assumed_need}</p>
                  <p><strong>Reality:</strong> {item.reality}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Open Questions */}
        {research.open_questions && research.open_questions.length > 0 && (
          <section className="section">
            <h3>Open Questions & Unknowns</h3>
            <div className="questions-list">
              {research.open_questions.map((q, i) => (
                <div key={i} className="open-question">
                  <p className="question"><strong>Q:</strong> {q.question}</p>
                  <p className="why-matters"><em>Why it matters:</em> {q.why_it_matters}</p>
                  <p className="validation"><em>Validation needed:</em> {q.validation_needed}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Competitive Landscape */}
        {research.competitive_landscape && (
          <section className="section">
            <h3>Competitive Reality Check</h3>
            <p className="market-position">{research.competitive_landscape.market_position}</p>
            <div className="competitors-grid">
              {research.competitive_landscape.competitors.map((comp, i) => (
                <div key={i} className="competitor-card">
                  <h4>{comp.name}</h4>
                  <p><strong>Their approach:</strong> {comp.how_they_solve_it}</p>
                  <p><strong>Why they haven't won:</strong> {comp.why_they_havent_won}</p>
                  <p className="barriers"><strong>Switching barriers:</strong> {comp.switching_barriers}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Market Context */}
        {research.market_context && (
          <section className="section">
            <h3>Market Context</h3>
            <div className="market-size-grid">
              <div className="market-card">
                <span className="label">TAM</span>
                <span className="value">{research.market_context.total_addressable_market}</span>
              </div>
              <div className="market-card">
                <span className="label">SAM</span>
                <span className="value">{research.market_context.serviceable_addressable_market}</span>
              </div>
              <div className="market-card">
                <span className="label">SOM</span>
                <span className="value">{research.market_context.serviceable_obtainable_market}</span>
              </div>
            </div>
            {research.market_context.uncertainty_factors.length > 0 && (
              <div className="uncertainty-section">
                <strong>Uncertainty Factors:</strong>
                <ul>
                  {research.market_context.uncertainty_factors.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {/* Research Quality Self-Check */}
        {research.research_quality_check && (
          <section className="section quality-check-section">
            <h3>Research Quality Self-Check</h3>
            <div className="quality-checks">
              <div className={`check-item ${research.research_quality_check.could_kill_idea ? 'pass' : 'fail'}`}>
                {research.research_quality_check.could_kill_idea ? '✓' : '✗'} Could kill the idea
              </div>
              <div className={`check-item ${research.research_quality_check.skeptic_would_trust ? 'pass' : 'fail'}`}>
                {research.research_quality_check.skeptic_would_trust ? '✓' : '✗'} Skeptic would trust
              </div>
              <div className={`check-item ${research.research_quality_check.assumptions_separated ? 'pass' : 'fail'}`}>
                {research.research_quality_check.assumptions_separated ? '✓' : '✗'} Assumptions separated
              </div>
            </div>
            <p className="self-critique"><em>Self-critique:</em> {research.research_quality_check.self_critique}</p>
          </section>
        )}
      </div>
    );
  }

  // Legacy format display
  return (
    <div className="tab-panel research-panel">
      <section className="section">
        <h3>Market Size</h3>
        <div className="market-size-grid">
          <div className="market-card">
            <span className="label">TAM</span>
            <span className="value">{research.total_addressable_market}</span>
          </div>
          <div className="market-card">
            <span className="label">SAM</span>
            <span className="value">{research.serviceable_addressable_market}</span>
          </div>
          <div className="market-card">
            <span className="label">SOM</span>
            <span className="value">{research.serviceable_obtainable_market}</span>
          </div>
        </div>
      </section>

      {research.user_personas && research.user_personas.length > 0 && (
        <section className="section">
          <h3>User Personas</h3>
          <div className="personas-grid">
            {research.user_personas.map((persona, i) => (
              <div key={i} className="persona-card">
                <div className="persona-header">
                  <h4>{persona.name}</h4>
                  <span className="role">{persona.role}</span>
                </div>
                <p className="quote">"{persona.quote}"</p>
                <div className="persona-details">
                  <div>
                    <strong>Goals:</strong>
                    <ul>
                      {persona.goals.slice(0, 3).map((goal, j) => (
                        <li key={j}>{goal}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong>Frustrations:</strong>
                    <ul>
                      {persona.frustrations.slice(0, 3).map((f, j) => (
                        <li key={j}>{f}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {research.pain_points && research.pain_points.length > 0 && (
        <section className="section">
          <h3>Pain Points</h3>
          <div className="pain-points-list">
            {research.pain_points.map((pain, i) => (
              <div key={i} className={`pain-point severity-${pain.severity}`}>
                <span className="severity-badge">{pain.severity}</span>
                <p>{pain.description}</p>
                {pain.current_workaround && (
                  <span className="workaround">Current workaround: {pain.current_workaround}</span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {research.competitors && research.competitors.length > 0 && (
        <section className="section">
          <h3>Competitive Landscape</h3>
          <div className="competitors-grid">
            {research.competitors.map((comp, i) => (
              <div key={i} className="competitor-card">
                <h4>{comp.name}</h4>
                <p className="position">{comp.market_position}</p>
                <div className="comp-details">
                  <div>
                    <strong>Strengths:</strong>
                    <ul>
                      {comp.strengths.slice(0, 3).map((s, j) => (
                        <li key={j}>{s}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong>Weaknesses:</strong>
                    <ul>
                      {comp.weaknesses.slice(0, 3).map((w, j) => (
                        <li key={j}>{w}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function BusinessCaseTab({ businessCase }: { businessCase: InceptionPack['business_case'] }) {
  const canvas = businessCase.lean_canvas;

  return (
    <div className="tab-panel business-panel">
      <section className="section">
        <h3>Lean Canvas</h3>
        <div className="lean-canvas">
          <div className="canvas-cell problem">
            <h4>Problem</h4>
            <ul>
              {canvas.problem.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
          <div className="canvas-cell solution">
            <h4>Solution</h4>
            <ul>
              {canvas.solution.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <div className="canvas-cell uvp">
            <h4>Unique Value Proposition</h4>
            <p>{canvas.unique_value_proposition}</p>
          </div>
          <div className="canvas-cell advantage">
            <h4>Unfair Advantage</h4>
            <p>{canvas.unfair_advantage}</p>
          </div>
          <div className="canvas-cell segments">
            <h4>Customer Segments</h4>
            <ul>
              {canvas.customer_segments.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <div className="canvas-cell metrics">
            <h4>Key Metrics</h4>
            <ul>
              {canvas.key_metrics.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          </div>
          <div className="canvas-cell channels">
            <h4>Channels</h4>
            <ul>
              {canvas.channels.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
          <div className="canvas-cell costs">
            <h4>Cost Structure</h4>
            <ul>
              {canvas.cost_structure.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
          <div className="canvas-cell revenue">
            <h4>Revenue Streams</h4>
            <ul>
              {canvas.revenue_streams.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <div className="section-grid">
        <section className="section">
          <h3><DollarSign size={18} /> Financial Projections</h3>
          <div className="financial-cards">
            <div className="fin-card">
              <span className="label">Year 1</span>
              <span className="value">{businessCase.year_1_projection}</span>
            </div>
            <div className="fin-card">
              <span className="label">Year 3</span>
              <span className="value">{businessCase.year_3_projection}</span>
            </div>
            <div className="fin-card">
              <span className="label">Break-even</span>
              <span className="value">{businessCase.break_even_analysis}</span>
            </div>
            <div className="fin-card">
              <span className="label">Funding Required</span>
              <span className="value">{businessCase.funding_requirement}</span>
            </div>
          </div>
        </section>
      </div>

      <section className="section">
        <h3>Go-to-Market Strategy</h3>
        <p>{businessCase.go_to_market_strategy}</p>
      </section>

      <section className="section">
        <h3>Revenue Streams</h3>
        <div className="revenue-streams">
          {businessCase.revenue_streams.map((stream, i) => (
            <div key={i} className="revenue-card">
              <h4>{stream.name}</h4>
              <p>{stream.description}</p>
              <div className="stream-details">
                <span>Model: {stream.pricing_model}</span>
                <span>Contribution: {stream.estimated_contribution}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
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
      <div className="tab-panel prd-panel">
        <div className="empty-state">
          <FileText size={48} />
          <h3>PRD Not Available</h3>
          <p>The Product Requirements Document was not generated for this session.</p>
        </div>
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
    <div className="tab-panel prd-panel">
      {/* Quality and Stats Banner */}
      {(stats || qualityScore !== undefined) && (
        <div className="prd-stats-banner">
          {qualityScore !== undefined && (
            <div className="stat-item">
              <span className="stat-value">{(qualityScore * 100).toFixed(0)}%</span>
              <span className="stat-label">Quality Score</span>
            </div>
          )}
          {stats && (
            <>
              <div className="stat-item">
                <span className="stat-value">{stats.total_epics}</span>
                <span className="stat-label">Epics</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{stats.total_stories}</span>
                <span className="stat-label">Stories</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{stats.total_story_points}</span>
                <span className="stat-label">Story Points</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{stats.total_functional_requirements}</span>
                <span className="stat-label">FRs</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{stats.total_non_functional_requirements}</span>
                <span className="stat-label">NFRs</span>
              </div>
            </>
          )}
        </div>
      )}

      <section className="section">
        <h3>{productName ? `${productName} - Overview` : 'Overview'}</h3>
        {problemStatement && <p className="problem-statement"><strong>Problem:</strong> {problemStatement}</p>}
        <p>{overview}</p>
      </section>

      {objectives.length > 0 && (
        <section className="section">
          <h3>Objectives</h3>
          <ul className="objectives-list">
            {objectives.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
        </section>
      )}

      {(scopeIn.length > 0 || scopeOut.length > 0) && (
        <div className="section-grid">
          {scopeIn.length > 0 && (
            <section className="section">
              <h3>In Scope</h3>
              <ul>
                {scopeIn.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </section>
          )}
          {scopeOut.length > 0 && (
            <section className="section">
              <h3>Out of Scope</h3>
              <ul>
                {scopeOut.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}

      {epics.length > 0 && (
        <section className="section epics-section">
          <h3>
            Epics & User Stories
            <span className="count">
              {epics.length} epics, {totalStories} stories
            </span>
          </h3>

          <div className="epics-list">
            {epics.map((epic) => (
              <EpicCard
                key={epic.id}
                epic={epic}
                isExpanded={expandedEpics.has(epic.id)}
                onToggle={() => toggleEpic(epic.id)}
              />
            ))}
          </div>
        </section>
      )}

      {releasePhases.length > 0 && (
        <section className="section">
          <h3>Release Plan</h3>
          <div className="release-timeline">
            {releasePhases.map((phase, i) => (
              <div key={i} className="release-phase">
                <div className="phase-header">
                  <span className="phase-name">{(phase as { phase?: string; name?: string }).phase || (phase as { name?: string }).name}</span>
                </div>
                <p>{phase.description}</p>
                {phase.features && phase.features.length > 0 && (
                  <div className="phase-features">
                    <strong>Features:</strong>
                    <ul>
                      {phase.features.map((f, j) => (
                        <li key={j}>{f}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
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
    <div className={`epic-card ${isExpanded ? 'expanded' : ''}`}>
      <button className="epic-header" onClick={onToggle}>
        {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
        <span className="epic-id">{epic.id}</span>
        <span className="epic-title">{epic.title}</span>
        {epic.priority && <span className={`priority-badge ${epic.priority}`}>{epic.priority}</span>}
        <span className="story-count">{stories.length} stories{totalPoints > 0 ? ` (${totalPoints} pts)` : ''}</span>
      </button>

      {isExpanded && (
        <div className="epic-content">
          <p className="epic-description">{epic.description}</p>
          {epic.business_value && (
            <p className="business-value">
              <strong>Business Value:</strong> {epic.business_value}
            </p>
          )}

          <div className="stories-list">
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
    <div className={`story-card ${isExpanded ? 'expanded' : ''}`}>
      <button className="story-header" onClick={() => setIsExpanded(!isExpanded)}>
        {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <span className="story-id">{story.id}</span>
        <span className="story-title">{story.title}</span>
        <span className={`priority-badge ${story.priority}`}>{story.priority}</span>
        {story.story_points && <span className="points-badge">{story.story_points} pts</span>}
        {story.size && <span className="size-badge">{story.size}</span>}
      </button>

      {isExpanded && (
        <div className="story-content">
          {/* New format: description contains the full user story */}
          {story.description && (
            <p className="story-description">{story.description}</p>
          )}

          {/* Old format: as_a / i_want / so_that */}
          {story.as_a && story.i_want && story.so_that && (
            <div className="user-story-format">
              <p>
                <strong>As a</strong> {story.as_a},
              </p>
              <p>
                <strong>I want</strong> {story.i_want},
              </p>
              <p>
                <strong>So that</strong> {story.so_that}.
              </p>
            </div>
          )}

          {story.acceptance_criteria && story.acceptance_criteria.length > 0 && (
            <div className="acceptance-criteria">
              <strong>Acceptance Criteria:</strong>
              {hasOldFormatAC ? (
                // Old format: Given/When/Then objects
                (story.acceptance_criteria as AcceptanceCriteria[]).map((ac, i) => (
                  <div key={i} className="ac-item">
                    <p>
                      <em>Given</em> {ac.given}
                    </p>
                    <p>
                      <em>When</em> {ac.when}
                    </p>
                    <p>
                      <em>Then</em> {ac.then}
                    </p>
                  </div>
                ))
              ) : (
                // New format: string array
                <ul className="ac-list">
                  {(story.acceptance_criteria as string[]).map((ac, i) => (
                    <li key={i}>{ac}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {story.notes && (
            <p className="notes">
              <strong>Notes:</strong> {story.notes}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function ArchitectureTab({ architecture }: { architecture: InceptionPack['technical_architecture'] }) {
  return (
    <div className="tab-panel architecture-panel">
      <section className="section">
        <h3>Architecture Style</h3>
        <p className="highlight">{architecture.architecture_style}</p>
        <p>{architecture.architecture_diagram_description}</p>
      </section>

      <section className="section">
        <h3>Technology Stack</h3>
        <div className="tech-stack-grid">
          {architecture.technology_stack.map((tech, i) => (
            <div key={i} className="tech-card">
              <span className="category">{tech.category}</span>
              <h4>{tech.technology}</h4>
              <p>{tech.rationale}</p>
              {tech.alternatives_considered.length > 0 && (
                <span className="alternatives">
                  Alternatives: {tech.alternatives_considered.join(', ')}
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h3>System Components</h3>
        <div className="components-grid">
          {architecture.system_components.map((comp, i) => (
            <div key={i} className="component-card">
              <h4>{comp.name}</h4>
              <p>{comp.description}</p>
              <div className="comp-details">
                <div>
                  <strong>Responsibilities:</strong>
                  <ul>
                    {comp.responsibilities.map((r, j) => (
                      <li key={j}>{r}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong>Technologies:</strong>
                  <span className="tech-tags">
                    {comp.technologies.map((t, j) => (
                      <span key={j} className="tag">
                        {t}
                      </span>
                    ))}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="section-grid">
        <section className="section">
          <h3><Shield size={18} /> Security</h3>
          <p>{architecture.security_architecture}</p>
        </section>
        <section className="section">
          <h3><TrendingUp size={18} /> Scalability</h3>
          <p>{architecture.scalability_approach}</p>
        </section>
      </div>

      <section className="section">
        <h3>Deployment Strategy</h3>
        <p>{architecture.deployment_strategy}</p>
      </section>

      <section className="section">
        <h3>Infrastructure Requirements</h3>
        <ul>
          {architecture.infrastructure_requirements.map((req, i) => (
            <li key={i}>{req}</li>
          ))}
        </ul>
      </section>
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
  return (
    <div className="tab-panel quality-panel">
      <section className="section">
        <h3>Overall Assessment</h3>
        <div className="quality-score-display">
          <div className="score-circle">
            <span className="score">{((quality.overall_score || 0) * 100).toFixed(0)}%</span>
            <span className="label">Quality Score</span>
          </div>
          <div className="score-status">
            {quality.passed ? (
              <span className="status passed">
                <CheckCircle2 size={20} />
                Quality Check Passed
              </span>
            ) : (
              <span className="status failed">
                <Shield size={20} />
                Below Threshold
              </span>
            )}
            <p>Iteration: {quality.iteration}</p>
            {quality.ready_for_delivery && (
              <span className="ready-badge">Ready for Delivery</span>
            )}
          </div>
        </div>
      </section>

      <section className="section">
        <h3>Section Scores</h3>
        <div className="section-scores">
          {quality.section_scores.map((section, i) => (
            <div key={i} className="score-item">
              <div className="score-header">
                <span className="section-name">{section.section}</span>
                <span className="section-score">{(section.score * 100).toFixed(0)}%</span>
              </div>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{ width: `${section.score * 100}%` }}
                />
              </div>
              <p className="feedback">{section.feedback}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="section-grid">
        <section className="section">
          <h3>Strengths</h3>
          <ul className="strengths-list">
            {quality.strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </section>

        {quality.weaknesses.length > 0 && (
          <section className="section">
            <h3>Areas for Improvement</h3>
            <ul className="weaknesses-list">
              {quality.weaknesses.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </section>
        )}
      </div>

      {quality.recommendations.length > 0 && (
        <section className="section">
          <h3>Recommendations</h3>
          <ul>
            {quality.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="section metadata-section">
        <h3><Clock size={18} /> Generation Metadata</h3>
        <div className="metadata-grid">
          <div className="meta-item">
            <span className="label">Session ID</span>
            <span className="value">{metadata.session_id}</span>
          </div>
          <div className="meta-item">
            <span className="label">Generated At</span>
            <span className="value">{new Date(metadata.generated_at).toLocaleString()}</span>
          </div>
          <div className="meta-item">
            <span className="label">Duration</span>
            <span className="value">{Math.round(metadata.total_duration_seconds)}s</span>
          </div>
          <div className="meta-item">
            <span className="label">Iterations</span>
            <span className="value">{metadata.iterations}</span>
          </div>
          <div className="meta-item">
            <span className="label">Tokens Used</span>
            <span className="value">{metadata.total_tokens_used.toLocaleString()}</span>
          </div>
        </div>
      </section>
    </div>
  );
}
