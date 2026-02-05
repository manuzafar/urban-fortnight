interface LandingPageProps {
  onStartDiscovery: () => void;
}

export function LandingPage({ onStartDiscovery }: LandingPageProps) {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-badge-premium">
          <div className="badge-glow"></div>
          <span className="status-dot-premium"></span>
          <span>6 AI Agents • Live & Ready</span>
          <div className="badge-shimmer"></div>
        </div>

        <h1 className="hero-title-premium">
          Turn weeks of discovery
          <br />
          into <span className="gradient-text-premium">hours of clarity</span>
        </h1>

        <p className="hero-subtitle-premium">
          Get a decision-ready inception pack in <strong style={{ color: '#8b7cff' }}>under 12 minutes</strong>.
          <br />
          AI-generated hypotheses for research, business strategy, and architecture. Ready for customer validation.
        </p>

        <div className="hero-cta-premium">
          <button className="btn-cta-primary" onClick={onStartDiscovery}>
            <span className="btn-inner">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{ marginRight: '8px' }}>
                <path d="M10 3l7 4v6l-7 4-7-4V7l7-4z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                <circle cx="10" cy="10" r="3" fill="currentColor"/>
              </svg>
              Start Discovery
              <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ marginLeft: '8px' }}>
                <path d="M6 12l4-4-4-4"/>
              </svg>
            </span>
            <div className="btn-glow"></div>
          </button>
          <a href="#what-you-get" className="btn-cta-secondary">
            <span>See what you get</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M8 4v8M4 8h8"/>
            </svg>
          </a>
        </div>

        {/* Trust Indicators */}
        <div className="trust-bar">
          <div className="trust-item">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <span>Multi-Agent AI</span>
          </div>
          <div className="trust-item">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <span>8-12 Minutes</span>
          </div>
          <div className="trust-item">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span>Audit-Ready</span>
          </div>
          <div className="trust-item">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>Hypothesis-First</span>
          </div>
        </div>
      </section>

      {/* What You Get Section */}
      <section className="what-you-get-premium" id="what-you-get">
        <div className="section-header-premium">
          <div className="section-eyebrow-premium">
            <div className="eyebrow-glow"></div>
            Complete Inception Pack
          </div>
          <h2 className="section-title-premium">
            Everything you need to
            <span className="gradient-text-accent"> decide and ship</span>
          </h2>
          <p className="section-subtitle-premium">
            Six specialized AI agents collaborate to deliver a structured, decision-ready pack with legal compliance analysis your team can review, debate, and approve with confidence.
          </p>
        </div>

        <div className="deliverables-grid-premium">
          <DeliverableCard
            number="01"
            title="Executive Summary"
            description="High-level overview of the entire inception pack. Problem, solution, key insights, and recommended next steps — everything leadership needs to make informed decisions."
            icon="📊"
          />

          <DeliverableCard
            number="02"
            title="Market Hypotheses"
            description="AI-generated market hypotheses with uncomfortable questions. Tiered confidence system (E1-E4) indicates certainty level. Ready for customer interview validation."
            icon="🔬"
          />

          <DeliverableCard
            number="03"
            title="Business Strategy"
            description="Complete business case with Lean Canvas, financial projections, revenue models, and go-to-market strategy. Ready for stakeholder review."
            icon="💼"
          />

          <DeliverableCard
            number="04"
            title="Product Requirements"
            description="Comprehensive PRD with epics, user stories, acceptance criteria, and release planning. Quality-assured through automated critic loop."
            icon="📋"
          />

          <DeliverableCard
            number="05"
            title="Technical Architecture"
            description="System design and tech stack recommendations. Component diagrams, scalability considerations, security patterns — engineering-ready documentation."
            icon="⚙️"
          />

          <DeliverableCard
            number="06"
            title="Legal & Regulatory Review"
            description="Comprehensive compliance analysis. Industry regulations, licensing requirements, data protection obligations, and legal risks — stress tested for your industry."
            icon="⚖️"
          />

          <DeliverableCard
            number="07"
            title="Quality Assessment"
            description="Cross-validation and critique across all sections. Identifies gaps, inconsistencies, and risks — ensuring the pack is decision-ready."
            icon="✓"
          />
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="final-cta-section">
        <div className="cta-card-premium">
          <div className="cta-glow-orb"></div>
          <div className="cta-content">
            <h3 className="cta-headline">
              Ready to compress your discovery?
            </h3>
            <p className="cta-subtext">
              Join teams who ship faster with AI-powered inception packs.
              <br />
              <strong>No credit card required.</strong> Start free in 30 seconds.
            </p>

            <div className="cta-stats-inline">
              <div className="inline-stat">
                <div className="stat-number">8-12</div>
                <div className="stat-text">Minutes</div>
              </div>
              <div className="stat-divider"></div>
              <div className="inline-stat">
                <div className="stat-number">6</div>
                <div className="stat-text">AI Agents</div>
              </div>
              <div className="stat-divider"></div>
              <div className="inline-stat">
                <div className="stat-number">7</div>
                <div className="stat-text">Deliverables</div>
              </div>
            </div>

            <button className="btn-cta-final" onClick={onStartDiscovery}>
              <span className="btn-final-inner">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{ marginRight: '10px' }}>
                  <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                  <path d="M7 10l2 2 4-4" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Get Your Inception Pack Now
                <svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ marginLeft: '10px' }}>
                  <path d="M6 12l4-4-4-4"/>
                </svg>
              </span>
              <div className="btn-final-glow"></div>
            </button>

            <div className="cta-guarantee">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
              <span>100% free. No strings attached.</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

interface DeliverableCardProps {
  number: string;
  title: string;
  description: string;
  icon: string;
}

function DeliverableCard({ number, title, description, icon }: DeliverableCardProps) {
  return (
    <div
      className="deliverable-card-premium"
      onMouseMove={(e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        e.currentTarget.style.setProperty('--mouse-x', `${x}px`);
        e.currentTarget.style.setProperty('--mouse-y', `${y}px`);
      }}
    >
      <div className="card-glow-effect"></div>
      <div className="card-header-premium">
        <div className="card-icon-premium">{icon}</div>
        <div className="card-number-premium">{number}</div>
      </div>
      <h3 className="card-title-premium">{title}</h3>
      <p className="card-description-premium">{description}</p>
      <div className="card-shine"></div>
    </div>
  );
}
