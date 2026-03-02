/**
 * V4 Landing Page Component
 * Light theme, typography-forward design with terracotta accent
 */

import { History, LogOut } from 'lucide-react';
import '../../styles/theme-v4.css';

interface User {
  email?: string;
  user_metadata?: {
    full_name?: string;
    avatar_url?: string;
  };
}

interface LandingPageV4Props {
  onStart: () => void;
  user?: User | null;
  onSessionsClick?: () => void;
  onSignOut?: () => void;
}

export function LandingPageV4({ onStart, user, onSessionsClick, onSignOut }: LandingPageV4Props) {
  return (
    <div className="v4-root">
      {/* Navigation */}
      <nav
        style={{
          padding: '20px 0',
          borderBottom: '1px solid var(--v4-border)',
        }}
      >
        <div className="v4-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <a
            href="#"
            style={{
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--v4-text)',
              textDecoration: 'none',
              letterSpacing: '-0.02em',
            }}
          >
            Seedcraft
          </a>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {user && onSessionsClick && (
              <button
                onClick={onSessionsClick}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: 'var(--v4-text-secondary)',
                  background: 'transparent',
                  padding: '8px 14px',
                  borderRadius: 'var(--v4-radius)',
                  border: '1px solid var(--v4-border)',
                  cursor: 'pointer',
                }}
              >
                <History size={14} />
                My Sessions
              </button>
            )}
            {user && onSignOut && (
              <button
                onClick={onSignOut}
                title="Sign out"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '36px',
                  height: '36px',
                  color: 'var(--v4-text-secondary)',
                  background: 'transparent',
                  borderRadius: 'var(--v4-radius)',
                  border: '1px solid var(--v4-border)',
                  cursor: 'pointer',
                }}
              >
                <LogOut size={14} />
              </button>
            )}
            <button
              onClick={onStart}
              className="btn-start"
              style={{
                fontSize: '14px',
                fontWeight: 500,
                color: 'white',
                background: 'var(--v4-text)',
                padding: '10px 20px',
                borderRadius: 'var(--v4-radius)',
                border: 'none',
                cursor: 'pointer',
                transition: 'background 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--v4-text-secondary)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--v4-text)')}
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{ padding: '120px 0 100px', textAlign: 'center' }}>
        <div className="v4-container">
          <h1
            style={{
              fontFamily: 'var(--v4-font-display)',
              fontSize: 'var(--v4-font-size-hero)',
              fontWeight: 600,
              letterSpacing: '-0.035em',
              lineHeight: 1.1,
              marginBottom: '24px',
              maxWidth: '720px',
              marginLeft: 'auto',
              marginRight: 'auto',
            }}
          >
            Accelerate your enterprise from idea to outcome.
          </h1>
          <p
            style={{
              fontSize: '18px',
              color: 'var(--v4-text-secondary)',
              maxWidth: '560px',
              margin: '0 auto 40px',
              lineHeight: 1.7,
            }}
          >
            Seedcraft compresses the entire discovery-to-delivery lifecycle. Decision-ready inception packs in minutes, not months.
          </p>
          <button
            onClick={onStart}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '15px',
              fontWeight: 500,
              color: 'white',
              background: 'var(--v4-accent)',
              padding: '14px 28px',
              borderRadius: 'var(--v4-radius)',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--v4-accent-hover)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--v4-accent)')}
          >
            Accelerate Your Next Initiative
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </button>
          <div
            style={{
              marginTop: '48px',
              display: 'flex',
              justifyContent: 'center',
              gap: '40px',
              fontSize: '14px',
              color: 'var(--v4-text-muted)',
            }}
          >
            <span>16 sections</span>
            <span>12+ AI agents</span>
            <span>~12 minutes</span>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section style={{ padding: '100px 0', borderTop: '1px solid var(--v4-border)' }}>
        <div className="v4-container">
          <div style={{ maxWidth: '640px', marginBottom: '64px' }}>
            <p className="v4-eyebrow" style={{ marginBottom: '16px' }}>
              The Problem
            </p>
            <h2
              style={{
                fontFamily: 'var(--v4-font-display)',
                fontSize: '36px',
                fontWeight: 600,
                letterSpacing: '-0.025em',
                lineHeight: 1.2,
                marginBottom: '20px',
              }}
            >
              Your ideas aren't slow. Your process is.
            </h2>
            <p style={{ fontSize: '17px', color: 'var(--v4-text-secondary)', lineHeight: 1.7 }}>
              Discovery takes months. Alignment takes longer. By the time you have a business case, competitors have shipped.
            </p>
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '1px',
              background: 'var(--v4-border)',
              border: '1px solid var(--v4-border)',
              borderRadius: 'var(--v4-radius)',
              overflow: 'hidden',
            }}
          >
            <ProblemItem
              title="Months of discovery"
              description="Stakeholder interviews, market research, endless alignment meetings that still end in misalignment."
            />
            <ProblemItem
              title="Siloed artifacts"
              description="PRDs that don't match financial models. Architecture that ignores legal constraints. No single source of truth."
            />
            <ProblemItem
              title="80% never used"
              description="Most features ship to indifference. Not because ideas were bad—because discovery couldn't validate fast enough."
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section style={{ padding: '100px 0', borderTop: '1px solid var(--v4-border)' }}>
        <div className="v4-container">
          <h2
            style={{
              fontFamily: 'var(--v4-font-display)',
              fontSize: '36px',
              fontWeight: 600,
              letterSpacing: '-0.025em',
              marginBottom: '64px',
            }}
          >
            How it works
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '48px' }}>
            <HowStep
              number="01"
              title="Input your context"
              description="Describe your initiative. Add your enterprise constraints—industry, regulations, tech stack, budget, stakeholders."
            />
            <HowStep
              number="02"
              title="Agents execute"
              description="Three coordinated swarms—Discovery, Strategy, Delivery—research, model, and validate in parallel."
            />
            <HowStep
              number="03"
              title="Review and decide"
              description="Get a 16-section inception pack. Cross-validated, evidence-tiered, ready for stakeholder review."
            />
          </div>
        </div>
      </section>

      {/* Sections Grid */}
      <section style={{ padding: '100px 0', borderTop: '1px solid var(--v4-border)', background: 'var(--v4-bg-alt)' }}>
        <div className="v4-container">
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-end',
              marginBottom: '48px',
            }}
          >
            <h2 style={{ fontFamily: 'var(--v4-font-display)', fontSize: '36px', fontWeight: 600, letterSpacing: '-0.025em' }}>What you get</h2>
            <p style={{ fontSize: '15px', color: 'var(--v4-text-secondary)' }}>16 sections, validated and cross-referenced</p>
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '1px',
              background: 'var(--v4-border)',
              border: '1px solid var(--v4-border)',
              borderRadius: 'var(--v4-radius)',
              overflow: 'hidden',
            }}
          >
            <SectionItem category="Overview" title="Executive Summary" />
            <SectionItem category="Discovery" title="Customer Research" />
            <SectionItem category="Discovery" title="Competitive Analysis" />
            <SectionItem category="Discovery" title="Personas" />
            <SectionItem category="Strategy" title="Business Case" />
            <SectionItem category="Strategy" title="Go-to-Market" />
            <SectionItem category="Strategy" title="Financial Model" />
            <SectionItem category="Delivery" title="Product Requirements" />
            <SectionItem category="Delivery" title="Technical Architecture" />
            <SectionItem category="Delivery" title="Legal & Regulatory" />
            <SectionItem category="Delivery" title="Risk Assessment" />
            <SectionItem category="Design" title="Wireframes" />
            <SectionItem category="Design" title="Prototype" />
            <SectionItem category="Synthesis" title="Stakeholder Views" />
            <SectionItem category="Synthesis" title="Validation Playbook" />
            <SectionItem category="Quality" title="Quality Assessment" />
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section style={{ padding: '100px 0', borderTop: '1px solid var(--v4-border)' }}>
        <div className="v4-container">
          <h2 style={{ fontFamily: 'var(--v4-font-display)', fontSize: '36px', fontWeight: 600, letterSpacing: '-0.025em', marginBottom: '48px' }}>
            Built for scrutiny
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '32px' }}>
            <TrustItem
              title="Evidence-tiered claims"
              description="Every claim tagged E1–E4. You know exactly what's validated versus what needs customer interviews."
            />
            <TrustItem
              title="Critique-validated"
              description="AI agents cross-check each other. Contradictions are flagged before you see the output."
            />
            <TrustItem
              title="Stakeholder-ready"
              description="Tailored views for CFO, CTO, Legal. Each stakeholder gets relevant sections surfaced."
            />
            <TrustItem
              title="Context-aware"
              description="Works with your constraints. Your industry, your regulations, your tech stack—not generic assumptions."
            />
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section style={{ padding: '100px 0', borderTop: '1px solid var(--v4-border)', textAlign: 'center' }}>
        <div className="v4-container">
          <h2 style={{ fontFamily: 'var(--v4-font-display)', fontSize: '40px', fontWeight: 600, letterSpacing: '-0.025em', marginBottom: '16px' }}>
            Stop waiting for discovery.
          </h2>
          <p style={{ fontSize: '17px', color: 'var(--v4-text-secondary)', marginBottom: '32px' }}>
            Generate a decision-ready inception pack for your next initiative.
          </p>
          <button
            onClick={onStart}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '15px',
              fontWeight: 500,
              color: 'white',
              background: 'var(--v4-accent)',
              padding: '16px 32px',
              borderRadius: 'var(--v4-radius)',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--v4-accent-hover)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--v4-accent)')}
          >
            Get Started
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '32px 0', borderTop: '1px solid var(--v4-border)' }}>
        <div className="v4-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <p style={{ fontSize: '13px', color: 'var(--v4-text-muted)' }}>&copy; 2026 Seedcraft</p>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: '13px', color: 'var(--v4-text-secondary)', textDecoration: 'none' }}
          >
            GitHub
          </a>
        </div>
      </footer>

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 900px) {
          .v4-container h1 {
            font-size: 40px !important;
          }
          .v4-container [style*="grid-template-columns: repeat(3"] {
            grid-template-columns: 1fr !important;
          }
          .v4-container [style*="grid-template-columns: repeat(4"] {
            grid-template-columns: 1fr !important;
          }
          .v4-container [style*="grid-template-columns: repeat(2"] {
            grid-template-columns: 1fr !important;
          }
          .v4-container [style*="flex-direction"] {
            flex-direction: column !important;
            gap: 8px !important;
          }
        }
      `}</style>
    </div>
  );
}

function ProblemItem({ title, description }: { title: string; description: string }) {
  return (
    <div style={{ background: 'var(--v4-bg)', padding: '32px' }}>
      <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>{title}</h3>
      <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.6 }}>{description}</p>
    </div>
  );
}

function HowStep({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div>
      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--v4-text-muted)', marginBottom: '16px' }}>{number}</div>
      <h3 style={{ fontFamily: 'var(--v4-font-display)', fontSize: '18px', fontWeight: 600, marginBottom: '12px', letterSpacing: '-0.01em' }}>{title}</h3>
      <p style={{ fontSize: '15px', color: 'var(--v4-text-secondary)', lineHeight: 1.65 }}>{description}</p>
    </div>
  );
}

function SectionItem({ category, title }: { category: string; title: string }) {
  return (
    <div style={{ background: 'var(--v4-bg)', padding: '24px' }}>
      <span
        style={{
          fontSize: '11px',
          fontWeight: 600,
          color: 'var(--v4-text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
        }}
      >
        {category}
      </span>
      <h4 style={{ fontSize: '14px', fontWeight: 500, marginTop: '8px' }}>{title}</h4>
    </div>
  );
}

function TrustItem({ title, description }: { title: string; description: string }) {
  return (
    <div>
      <h3 style={{ fontFamily: 'var(--v4-font-display)', fontSize: '15px', fontWeight: 600, marginBottom: '8px' }}>{title}</h3>
      <p style={{ fontSize: '14px', color: 'var(--v4-text-secondary)', lineHeight: 1.6 }}>{description}</p>
    </div>
  );
}

export default LandingPageV4;
