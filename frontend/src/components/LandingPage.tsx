import type { ReactNode } from 'react';

interface LandingPageProps {
  onStartDiscovery: () => void;
}

// Professional SVG Icons
const Icons = {
  // Trust bar
  layers: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 2 7 12 12 22 7 12 2"/>
      <polyline points="2 17 12 22 22 17"/>
      <polyline points="2 12 12 17 22 12"/>
    </svg>
  ),
  clock: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </svg>
  ),
  shield: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <path d="M9 12l2 2 4-4"/>
    </svg>
  ),
  target: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="6"/>
      <circle cx="12" cy="12" r="2"/>
    </svg>
  ),
  // Deliverable cards
  barChart: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="20" x2="12" y2="10"/>
      <line x1="18" y1="20" x2="18" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  ),
  microscope: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 18h8"/>
      <path d="M3 22h18"/>
      <path d="M14 22a7 7 0 1 0 0-14h-1"/>
      <path d="M9 14h2"/>
      <path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"/>
      <path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/>
    </svg>
  ),
  briefcase: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
    </svg>
  ),
  clipboard: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
      <path d="M9 14h6"/>
      <path d="M9 18h6"/>
      <path d="M9 10h6"/>
    </svg>
  ),
  cpu: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
      <rect x="9" y="9" width="6" height="6"/>
      <line x1="9" y1="1" x2="9" y2="4"/>
      <line x1="15" y1="1" x2="15" y2="4"/>
      <line x1="9" y1="20" x2="9" y2="23"/>
      <line x1="15" y1="20" x2="15" y2="23"/>
      <line x1="20" y1="9" x2="23" y2="9"/>
      <line x1="20" y1="14" x2="23" y2="14"/>
      <line x1="1" y1="9" x2="4" y2="9"/>
      <line x1="1" y1="14" x2="4" y2="14"/>
    </svg>
  ),
  scale: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3v18"/>
      <path d="M5 6l7-3 7 3"/>
      <path d="M2 12l3-6 3 6"/>
      <path d="M16 12l3-6 3 6"/>
      <path d="M2 12h6"/>
      <path d="M16 12h6"/>
    </svg>
  ),
  checkCircle: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
      <polyline points="22 4 12 14.01 9 11.01"/>
    </svg>
  ),
  shieldCheck: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  ),
};

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
              Start Discovery
            </span>
          </button>
          <a href="#what-you-get" className="btn-cta-secondary">
            See what you get
          </a>
        </div>

        {/* Trust Indicators */}
        <div className="trust-bar">
          <div className="trust-item">
            {Icons.layers}
            <span>Multi-Agent AI</span>
          </div>
          <div className="trust-item">
            {Icons.clock}
            <span>8-12 Minutes</span>
          </div>
          <div className="trust-item">
            {Icons.shield}
            <span>Audit-Ready</span>
          </div>
          <div className="trust-item">
            {Icons.target}
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
            icon={Icons.barChart}
          />

          <DeliverableCard
            number="02"
            title="Market Hypotheses"
            description="AI-generated market hypotheses with uncomfortable questions. Tiered confidence system (E1-E4) indicates certainty level. Ready for customer interview validation."
            icon={Icons.microscope}
          />

          <DeliverableCard
            number="03"
            title="Business Strategy"
            description="Complete business case with Lean Canvas, financial projections, revenue models, and go-to-market strategy. Ready for stakeholder review."
            icon={Icons.briefcase}
          />

          <DeliverableCard
            number="04"
            title="Product Requirements"
            description="Comprehensive PRD with epics, user stories, acceptance criteria, and release planning. Quality-assured through automated critic loop."
            icon={Icons.clipboard}
          />

          <DeliverableCard
            number="05"
            title="Technical Architecture"
            description="System design and tech stack recommendations. Component diagrams, scalability considerations, security patterns — engineering-ready documentation."
            icon={Icons.cpu}
          />

          <DeliverableCard
            number="06"
            title="Legal & Regulatory Review"
            description="Comprehensive compliance analysis. Industry regulations, licensing requirements, data protection obligations, and legal risks — stress tested for your industry."
            icon={Icons.scale}
          />

          <DeliverableCard
            number="07"
            title="Quality Assessment"
            description="Cross-validation and critique across all sections. Identifies gaps, inconsistencies, and risks — ensuring the pack is decision-ready."
            icon={Icons.checkCircle}
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
                Get Your Inception Pack Now
              </span>
            </button>

            <div className="cta-guarantee">
              {Icons.shieldCheck}
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
  icon: ReactNode;
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
