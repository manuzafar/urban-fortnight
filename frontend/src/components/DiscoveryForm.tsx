import { useState } from 'react';
import type { DiscoveryRequest } from '../types/api';

interface DiscoveryFormProps {
  onSubmit: (request: DiscoveryRequest) => void;
  isLoading: boolean;
  onBack?: () => void;
}

export function DiscoveryForm({ onSubmit, isLoading, onBack }: DiscoveryFormProps) {
  const [productIdea, setProductIdea] = useState('');
  const [industry, setIndustry] = useState('');
  const [targetMarket, setTargetMarket] = useState('');
  const [constraints, setConstraints] = useState('');
  const [additionalContext, setAdditionalContext] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const request: DiscoveryRequest = {
      product_idea: productIdea,
      industry: industry || undefined,
      target_market: targetMarket || undefined,
      constraints: constraints ? constraints.split('\n').filter(c => c.trim()) : undefined,
      additional_context: additionalContext || undefined,
    };

    onSubmit(request);
  };

  const isValid = productIdea.length >= 10;

  return (
    <div className="discovery-page-premium">
      {/* Back Navigation */}
      {onBack && (
        <div className="discovery-nav-container">
          <button className="back-btn-premium" onClick={onBack}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 5L7 10l5 5"/>
            </svg>
            <span>Back to home</span>
          </button>
        </div>
      )}

      <div className="discovery-container-premium">
        {/* Header Section */}
        <div className="discovery-header-premium">
          <div className="header-badge-premium">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10 2L2 7l8 5 8-5-8-5z"/>
              <path d="M2 12l8 5 8-5"/>
            </svg>
            <span>Discovery Session</span>
          </div>
          <h1 className="discovery-title-premium">Tell us about your idea</h1>
          <p className="discovery-subtitle-premium">
            Describe your product vision. Our AI agents will compress weeks of discovery into a comprehensive, decision-ready pack in under 12 minutes.
          </p>
        </div>

        <div className="discovery-grid-premium">
          {/* Form Section */}
          <div className="form-section-premium">
            <div className="form-card-premium">

              <form onSubmit={handleSubmit} className="discovery-form-premium">
                {/* Product Idea */}
                <div className="form-group-premium">
                  <label className="label-premium">
                    <span className="label-text">Product Idea</span>
                    <span className="label-badge">Required</span>
                  </label>
                  <div className="input-wrapper-premium">
                    <textarea
                      className="textarea-premium"
                      value={productIdea}
                      onChange={(e) => setProductIdea(e.target.value)}
                      placeholder="Describe your product vision. What problem does it solve? Who is it for? Be specific about the core value proposition..."
                      maxLength={2000}
                      required
                      disabled={isLoading}
                      rows={6}
                    />
                    <div className="input-footer">
                      <span className="input-hint">
                        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="8" cy="8" r="7"/>
                          <path d="M8 12v-4M8 5h.01"/>
                        </svg>
                        {productIdea.length > 0 && productIdea.length < 10
                          ? `${10 - productIdea.length} more characters needed`
                          : 'Be specific about the problem and who you\'re solving it for'}
                      </span>
                      <span className="char-count-premium">
                        {productIdea.length}<span className="char-total">/2000</span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* Industry & Target Market */}
                <div className="form-row-premium">
                  <div className="form-group-premium">
                    <label className="label-premium">
                      <span className="label-text">Industry</span>
                      <span className="label-badge optional">Optional</span>
                    </label>
                    <input
                      className="input-premium"
                      type="text"
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      placeholder="e.g., Healthcare, FinTech, SaaS"
                      disabled={isLoading}
                    />
                  </div>
                  <div className="form-group-premium">
                    <label className="label-premium">
                      <span className="label-text">Target Market</span>
                      <span className="label-badge optional">Optional</span>
                    </label>
                    <input
                      className="input-premium"
                      type="text"
                      value={targetMarket}
                      onChange={(e) => setTargetMarket(e.target.value)}
                      placeholder="e.g., Small businesses, Enterprises"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                {/* Advanced Options */}
                <details className="advanced-details-premium" open={showAdvanced} onToggle={(e) => setShowAdvanced(e.currentTarget.open)}>
                  <summary className="advanced-summary-premium">
                    <div className="advanced-title">
                      <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="2" y="2" width="12" height="12" rx="2"/>
                        <path d="M8 5v6M5 8h6"/>
                      </svg>
                      <span>Advanced options</span>
                    </div>
                    <span className="advanced-hint-premium">
                      {showAdvanced ? 'Hide' : 'Show'} additional fields
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" style={{ transform: showAdvanced ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s ease' }}>
                        <path d="M4 6l4 4 4-4"/>
                      </svg>
                    </span>
                  </summary>
                  <div className="advanced-content-premium">
                    <div className="form-group-premium">
                      <label className="label-premium">
                        <span className="label-text">Constraints</span>
                        <span className="label-badge optional">Optional</span>
                      </label>
                      <textarea
                        className="textarea-premium small"
                        value={constraints}
                        onChange={(e) => setConstraints(e.target.value)}
                        placeholder="Time, budget, technical, or regulatory constraints (e.g., PCI compliant, 6-month timeline, AWS only, $500K budget)"
                        disabled={isLoading}
                        rows={3}
                      />
                    </div>
                    <div className="form-group-premium">
                      <label className="label-premium">
                        <span className="label-text">Additional Context</span>
                        <span className="label-badge optional">Optional</span>
                      </label>
                      <textarea
                        className="textarea-premium small"
                        value={additionalContext}
                        onChange={(e) => setAdditionalContext(e.target.value)}
                        placeholder="Links, meeting notes, research data, or any additional context..."
                        disabled={isLoading}
                        rows={3}
                      />
                    </div>
                  </div>
                </details>

                {/* Submit Section */}
                <div className="submit-section-premium">
                  <div className="submit-info-premium">
                    <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M8 1l2 5h5l-4 3 2 5-5-4-5 4 2-5-4-3h5z" fill="currentColor" opacity="0.2"/>
                    </svg>
                    <span>Tip: Be concise. Our AI agents will gather additional insights automatically.</span>
                  </div>
                  <button type="submit" className="btn-submit-premium" disabled={!isValid || isLoading}>
                    {isLoading ? (
                      <>
                        <span className="spinner-premium"></span>
                        <span>Analyzing your idea...</span>
                      </>
                    ) : !isValid ? (
                      <>
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{ marginRight: '10px' }}>
                          <path d="M10 3l7 4v6l-7 4-7-4V7l7-4z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                          <circle cx="10" cy="10" r="3" fill="currentColor"/>
                        </svg>
                        <span>{productIdea.length === 0 ? 'Describe your product idea above' : `${10 - productIdea.length} more characters needed`}</span>
                      </>
                    ) : (
                      <>
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style={{ marginRight: '10px' }}>
                          <path d="M10 3l7 4v6l-7 4-7-4V7l7-4z" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                          <circle cx="10" cy="10" r="3" fill="currentColor"/>
                        </svg>
                        <span>Start Discovery</span>
                        <svg width="20" height="20" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ marginLeft: '10px' }}>
                          <path d="M6 12l4-4-4-4"/>
                        </svg>
                      </>
                    )}
                  </button>
                  <div className="submit-note-premium">
                    <span className="kbd-premium">⌘</span>
                    <span className="kbd-premium">↵</span>
                    <span>to submit</span>
                  </div>
                </div>
              </form>
            </div>
          </div>

          {/* Sidebar */}
          <aside className="sidebar-premium">
            <div className="sidebar-card-premium">
              <div className="sidebar-header-premium">
                <div className="sidebar-icon-premium">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                    <line x1="12" y1="22.08" x2="12" y2="12"/>
                  </svg>
                </div>
                <h3 className="sidebar-title-premium">Your Decision Pack</h3>
              </div>
              <p className="sidebar-text-premium">
                A complete inception pack generated by <strong>6 specialized AI agents</strong> in approximately <strong>8–12 minutes</strong>.
              </p>

              <div className="deliverables-list-premium">
                <DeliverableItem number="01" name="Executive Summary" description="High-level overview & next steps" />
                <DeliverableItem number="02" name="Customer Research" description="Evidence-based market analysis" />
                <DeliverableItem number="03" name="Business Strategy" description="Lean Canvas & financials" />
                <DeliverableItem number="04" name="Product Requirements" description="Epics, stories & criteria" />
                <DeliverableItem number="05" name="Technical Architecture" description="System design & tech stack" />
                <DeliverableItem number="06" name="Legal & Regulatory" description="Compliance & legal risks" />
                <DeliverableItem number="07" name="Quality Assessment" description="Cross-validation & critique" />
              </div>

              <div className="sidebar-footer-premium">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                <span>100% AI-powered. Evidence-based. Audit-ready.</span>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

interface DeliverableItemProps {
  number: string;
  name: string;
  description: string;
}

function DeliverableItem({ number, name, description }: DeliverableItemProps) {
  return (
    <div className="deliverable-item-premium">
      <div className="deliverable-number-premium">{number}</div>
      <div className="deliverable-content-premium">
        <div className="deliverable-name-premium">{name}</div>
        <div className="deliverable-desc-premium">{description}</div>
      </div>
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" className="deliverable-check">
        <path d="M13 4L6 11 3 8"/>
      </svg>
    </div>
  );
}
