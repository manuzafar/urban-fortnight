import { MermaidDiagram } from './MermaidDiagram';
import type {
  ExecutiveSummary,
  CustomerResearch,
  BusinessCase,
  ProductRequirementsDocument,
  TechnicalArchitecture,
  LegalRegulatoryReview,
  QualityAssessment,
} from '../types/api';

interface SlideProps {
  index: number;
  total: number;
  title: string;
  icon: string;
  accentColor: string;
  data: unknown;
  sectionKey: string;
}

export function Slide({ index, total, title, icon, accentColor, data, sectionKey }: SlideProps) {
  if (!data) {
    return (
      <div className="slide">
        <div className="slide-inner">
          <p className="slide-empty">This section is not available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="slide" style={{ '--accent-color': accentColor } as React.CSSProperties}>
      <div className="slide-inner">
        <div className="slide-section-header">
          <span className="slide-number">{index + 1} / {total}</span>
          <span className="slide-icon">{icon}</span>
          <h2 className="slide-section-title">{title}</h2>
        </div>

        <div className="slide-body">
          {renderSectionContent(sectionKey, data)}
        </div>

        {index < total - 1 && (
          <div className="slide-footer">
            <span className="slide-scroll-hint">↓ Scroll for next section</span>
          </div>
        )}
      </div>
    </div>
  );
}

function renderSectionContent(sectionKey: string, data: unknown) {
  switch (sectionKey) {
    case 'executive_summary':
      return <ExecutiveSummarySlide data={data as ExecutiveSummary} />;
    case 'customer_research':
      return <CustomerResearchSlide data={data as CustomerResearch} />;
    case 'business_case':
      return <BusinessCaseSlide data={data as BusinessCase} />;
    case 'product_requirements_document':
      return <ProductRequirementsSlide data={data as ProductRequirementsDocument} />;
    case 'technical_architecture':
      return <TechnicalArchitectureSlide data={data as TechnicalArchitecture} />;
    case 'legal_regulatory_review':
      return <LegalRegulatorySlide data={data as LegalRegulatoryReview} />;
    case 'quality_assessment':
      return <QualityAssessmentSlide data={data as QualityAssessment} />;
    default:
      return <GenericSlide data={data} />;
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Section-specific Slide Components
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function ExecutiveSummarySlide({ data }: { data: ExecutiveSummary }) {
  return (
    <div className="slide-section executive-summary">
      <div className="slide-hero">
        <h1 className="slide-product-name">{data.product_name}</h1>
        {data.tagline && <p className="slide-tagline">{data.tagline}</p>}
      </div>

      <div className="slide-grid two-col">
        <div className="slide-card">
          <h3>Problem</h3>
          <p>{data.problem_statement}</p>
        </div>
        <div className="slide-card">
          <h3>Solution</h3>
          <p>{data.solution_overview}</p>
        </div>
      </div>

      {data.value_proposition && (
        <div className="slide-card highlight">
          <h3>Value Proposition</h3>
          <p>{data.value_proposition}</p>
        </div>
      )}

      {data.key_differentiators && data.key_differentiators.length > 0 && (
        <div className="slide-card">
          <h3>Key Differentiators</h3>
          <ul>
            {data.key_differentiators.map((diff, i) => (
              <li key={i}>{diff}</li>
            ))}
          </ul>
        </div>
      )}

      {data.success_metrics && data.success_metrics.length > 0 && (
        <div className="slide-metrics">
          {data.success_metrics.slice(0, 4).map((metric, i) => (
            <div key={i} className="slide-metric-card">
              <span className="slide-metric-value">{i + 1}</span>
              <span className="slide-metric-label">{metric}</span>
            </div>
          ))}
        </div>
      )}

      {data.top_risks && data.top_risks.length > 0 && (
        <div className="slide-card warning">
          <h3>Top Risks</h3>
          <ul>
            {data.top_risks.slice(0, 3).map((risk, i) => (
              <li key={i}>{risk}</li>
            ))}
          </ul>
        </div>
      )}

      {data.recommendation && (
        <div className="slide-card highlight">
          <h3>Recommendation</h3>
          <p>{data.recommendation}</p>
        </div>
      )}
    </div>
  );
}

function CustomerResearchSlide({ data }: { data: CustomerResearch }) {
  return (
    <div className="slide-section customer-research">
      {data.job_to_be_done && (
        <div className="slide-card highlight">
          <h3>Job to be Done</h3>
          <p><strong>Trigger:</strong> {data.job_to_be_done.trigger_situation}</p>
          <p><strong>Goal:</strong> {data.job_to_be_done.underlying_goal}</p>
          <p><strong>Success:</strong> {data.job_to_be_done.success_definition}</p>
        </div>
      )}

      {data.pain_signals && data.pain_signals.length > 0 && (
        <div className="slide-card">
          <h3>Pain Signals</h3>
          <ul className="evidence-list">
            {data.pain_signals.slice(0, 5).map((signal, i) => (
              <li key={i}>
                <span className="evidence-tier-badge">{signal.evidence_tier}</span>
                <span>{signal.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.uncomfortable_insights && data.uncomfortable_insights.length > 0 && (
        <div className="slide-card warning">
          <h3>Uncomfortable Insights</h3>
          <ul>
            {data.uncomfortable_insights.slice(0, 3).map((insight, i) => (
              <li key={i}>
                <strong>[{insight.evidence_tier}]</strong> {insight.insight}
                {insight.implication && <><br /><em>→ {insight.implication}</em></>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.competitive_landscape && (
        <div className="slide-card">
          <h3>Competitive Landscape</h3>
          <p>{data.competitive_landscape.market_position}</p>
          {data.competitive_landscape.competitors && data.competitive_landscape.competitors.length > 0 && (
            <ul>
              {data.competitive_landscape.competitors.slice(0, 3).map((comp, i) => (
                <li key={i}><strong>{comp.name}:</strong> {comp.how_they_solve_it}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {data.market_context && (
        <div className="slide-card">
          <h3>Market Context</h3>
          <div className="slide-metrics">
            {data.market_context.total_addressable_market && (
              <div className="slide-metric-card">
                <span className="slide-metric-value">{data.market_context.total_addressable_market}</span>
                <span className="slide-metric-label">TAM</span>
              </div>
            )}
            {data.market_context.serviceable_addressable_market && (
              <div className="slide-metric-card">
                <span className="slide-metric-value">{data.market_context.serviceable_addressable_market}</span>
                <span className="slide-metric-label">SAM</span>
              </div>
            )}
            {data.market_context.serviceable_obtainable_market && (
              <div className="slide-metric-card">
                <span className="slide-metric-value">{data.market_context.serviceable_obtainable_market}</span>
                <span className="slide-metric-label">SOM</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function BusinessCaseSlide({ data }: { data: BusinessCase }) {
  return (
    <div className="slide-section business-case">
      {data.lean_canvas && (
        <>
          <h3 style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>Lean Canvas</h3>
          <div className="lean-canvas-grid">
            {data.lean_canvas.problem && data.lean_canvas.problem.length > 0 && (
              <div className="canvas-cell">
                <h4>Problem</h4>
                <p>{data.lean_canvas.problem.join('; ')}</p>
              </div>
            )}
            {data.lean_canvas.solution && data.lean_canvas.solution.length > 0 && (
              <div className="canvas-cell">
                <h4>Solution</h4>
                <p>{data.lean_canvas.solution.join('; ')}</p>
              </div>
            )}
            {data.lean_canvas.unique_value_proposition && (
              <div className="canvas-cell">
                <h4>Unique Value</h4>
                <p>{data.lean_canvas.unique_value_proposition}</p>
              </div>
            )}
            {data.lean_canvas.customer_segments && data.lean_canvas.customer_segments.length > 0 && (
              <div className="canvas-cell">
                <h4>Customers</h4>
                <p>{data.lean_canvas.customer_segments.join('; ')}</p>
              </div>
            )}
            {data.lean_canvas.channels && data.lean_canvas.channels.length > 0 && (
              <div className="canvas-cell">
                <h4>Channels</h4>
                <p>{data.lean_canvas.channels.join('; ')}</p>
              </div>
            )}
            {data.lean_canvas.revenue_streams && data.lean_canvas.revenue_streams.length > 0 && (
              <div className="canvas-cell">
                <h4>Revenue</h4>
                <p>{data.lean_canvas.revenue_streams.join('; ')}</p>
              </div>
            )}
          </div>
        </>
      )}

      {data.revenue_streams && data.revenue_streams.length > 0 && (
        <div className="slide-card">
          <h3>Revenue Streams</h3>
          <ul>
            {data.revenue_streams.map((stream, i) => (
              <li key={i}>
                <strong>{stream.name}:</strong> {stream.description} ({stream.pricing_model})
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.go_to_market_strategy && (
        <div className="slide-card">
          <h3>Go-to-Market Strategy</h3>
          <p>{data.go_to_market_strategy}</p>
        </div>
      )}

      {data.risks_and_mitigations && data.risks_and_mitigations.length > 0 && (
        <div className="slide-card warning">
          <h3>Risks & Mitigations</h3>
          <ul>
            {data.risks_and_mitigations.slice(0, 4).map((item, i) => (
              <li key={i}>
                <strong>{item.risk}:</strong> {item.mitigation}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ProductRequirementsSlide({ data }: { data: ProductRequirementsDocument }) {
  return (
    <div className="slide-section product-requirements">
      {data.product_overview?.vision && (
        <div className="slide-card highlight">
          <h3>Product Vision</h3>
          <p>{data.product_overview.vision}</p>
        </div>
      )}

      {data.product_overview?.objectives && data.product_overview.objectives.length > 0 && (
        <div className="slide-card">
          <h3>Objectives</h3>
          <ul>
            {data.product_overview.objectives.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
        </div>
      )}

      {data.epics && data.epics.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>Epics</h3>
          {data.epics.slice(0, 4).map((epic, i) => (
            <div key={i} className="epic-card">
              <div className="epic-header">
                <span className="epic-id">{epic.id}</span>
                <h4>{epic.title}</h4>
              </div>
              <p>{epic.description}</p>
              {epic.stories && (
                <div className="epic-meta">
                  {epic.stories.length} user stories
                  {epic.priority && <> · Priority: {epic.priority}</>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {data.scope && (
        <div className="slide-grid two-col">
          {data.scope.in_scope && data.scope.in_scope.length > 0 && (
            <div className="slide-card">
              <h3>In Scope</h3>
              <ul>
                {data.scope.in_scope.slice(0, 5).map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {data.scope.out_of_scope && data.scope.out_of_scope.length > 0 && (
            <div className="slide-card warning">
              <h3>Out of Scope</h3>
              <ul>
                {data.scope.out_of_scope.slice(0, 5).map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TechnicalArchitectureSlide({ data }: { data: TechnicalArchitecture }) {
  return (
    <div className="slide-section technical-architecture">
      {data.architecture_style && (
        <div className="slide-card highlight">
          <h3>Architecture Style</h3>
          <p>{data.architecture_style}</p>
        </div>
      )}

      {data.architecture_diagram_description && (
        <div className="slide-card">
          <h3>Architecture Overview</h3>
          <p>{data.architecture_diagram_description}</p>
        </div>
      )}

      {data.technology_stack && data.technology_stack.length > 0 && (
        <>
          <h3 style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>Technology Stack</h3>
          <div className="tech-stack-grid">
            {data.technology_stack.map((choice, i) => (
              <div key={i} className="tech-category">
                <h4>{choice.category}</h4>
                <div className="tech-tags">
                  <span className="tech-tag">{choice.technology}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {data.architecture_diagram_mermaid && (
        <div className="slide-card">
          <h3>System Diagram</h3>
          <MermaidDiagram chart={data.architecture_diagram_mermaid} />
        </div>
      )}

      {data.security_architecture && (
        <div className="slide-card">
          <h3>Security Architecture</h3>
          <p>{data.security_architecture}</p>
        </div>
      )}

      {data.scalability_approach && (
        <div className="slide-card">
          <h3>Scalability Approach</h3>
          <p>{data.scalability_approach}</p>
        </div>
      )}
    </div>
  );
}

function LegalRegulatorySlide({ data }: { data: LegalRegulatoryReview }) {
  return (
    <div className="slide-section legal-regulatory">
      {data.executive_summary && (
        <div className="slide-card highlight">
          <h3>Executive Summary</h3>
          <p>{data.executive_summary}</p>
        </div>
      )}

      {data.applicable_regulations && data.applicable_regulations.length > 0 && (
        <div className="slide-card">
          <h3>Applicable Regulations</h3>
          <div className="tech-tags" style={{ marginTop: '0.5rem' }}>
            {data.applicable_regulations.map((reg, i) => (
              <span key={i} className="tech-tag">{reg.name}</span>
            ))}
          </div>
        </div>
      )}

      {data.data_protection_requirements && data.data_protection_requirements.length > 0 && (
        <div className="slide-card">
          <h3>Data Protection</h3>
          <ul>
            {data.data_protection_requirements.slice(0, 3).map((req, i) => (
              <li key={i}>
                <strong>{req.regulation}:</strong> {req.key_obligations.slice(0, 2).join('; ')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.legal_risks && data.legal_risks.length > 0 && (
        <div className="slide-card warning">
          <h3>Legal Risks</h3>
          <ul>
            {data.legal_risks.slice(0, 4).map((risk, i) => (
              <li key={i}>
                <strong>{risk.risk_category} ({risk.severity}):</strong> {risk.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.intellectual_property && data.intellectual_property.length > 0 && (
        <div className="slide-card">
          <h3>IP Considerations</h3>
          <ul>
            {data.intellectual_property.slice(0, 3).map((ip, i) => (
              <li key={i}>
                <strong>{ip.ip_type}:</strong> {ip.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.overall_risk_assessment && (
        <div className="slide-card">
          <h3>Overall Risk Assessment</h3>
          <p><strong>Risk Level:</strong> {data.overall_risk_assessment.risk_level}</p>
          {data.overall_risk_assessment.key_concerns.length > 0 && (
            <ul>
              {data.overall_risk_assessment.key_concerns.map((concern, i) => (
                <li key={i}>{concern}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function QualityAssessmentSlide({ data }: { data: QualityAssessment }) {
  const overallScore = data.overall_score !== undefined ? data.overall_score : 0;

  return (
    <div className="slide-section quality-assessment">
      <div className="slide-score-hero">
        <div
          className="slide-score-circle"
          style={{
            background: `conic-gradient(var(--color-accent) ${overallScore * 100}%, rgba(255,255,255,0.1) 0)`,
          }}
        >
          <span className="score-value">{Math.round(overallScore * 100)}%</span>
        </div>
        <p className="slide-score-label">Overall Quality Score</p>
        <p style={{ color: data.passed ? 'var(--color-good)' : 'var(--color-error)', marginTop: '0.5rem' }}>
          {data.passed ? '✓ Passed' : '✗ Not Passed'}
        </p>
      </div>

      {data.section_scores && data.section_scores.length > 0 && (
        <div className="section-scores-list">
          {data.section_scores.map((sectionScore) => (
            <div key={sectionScore.section} className="section-score-row">
              <span className="section-score-name">{sectionScore.section.replace(/_/g, ' ')}</span>
              <div className="section-score-bar">
                <div
                  className="section-score-fill"
                  style={{ width: `${sectionScore.score * 100}%` }}
                />
              </div>
              <span className="section-score-value">{Math.round(sectionScore.score * 100)}%</span>
            </div>
          ))}
        </div>
      )}

      {data.strengths && data.strengths.length > 0 && (
        <div className="slide-card" style={{ marginTop: '2rem' }}>
          <h3>Strengths</h3>
          <ul>
            {data.strengths.map((strength, i) => (
              <li key={i}>{strength}</li>
            ))}
          </ul>
        </div>
      )}

      {data.critical_gaps && data.critical_gaps.length > 0 && (
        <div className="slide-card warning">
          <h3>Critical Gaps</h3>
          <ul>
            {data.critical_gaps.map((gap, i) => (
              <li key={i}>{gap}</li>
            ))}
          </ul>
        </div>
      )}

      {data.recommendations && data.recommendations.length > 0 && (
        <div className="slide-card">
          <h3>Recommendations</h3>
          <ul>
            {data.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function GenericSlide({ data }: { data: unknown }) {
  return (
    <div className="slide-section generic">
      <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', color: 'var(--color-muted)' }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
