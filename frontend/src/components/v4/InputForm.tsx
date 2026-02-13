/**
 * V4 Input Form Component
 * Two-column layout with form sections and output preview sidebar
 */

import { useState, type FormEvent, type ChangeEvent } from 'react';
import { ChipInput, ChipSelect } from './ChipInput';
import '../../styles/theme-v4.css';
import type { DiscoveryRequest } from '../../types/api';

interface InputFormV4Props {
  onSubmit: (request: DiscoveryRequest) => void;
  onBack: () => void;
  isLoading?: boolean;
}

// Output sections for the sidebar
const OUTPUT_SECTIONS = [
  { category: 'Overview', title: 'Executive Summary' },
  { category: 'Discovery', title: 'Customer Research' },
  { category: 'Discovery', title: 'Competitive Analysis' },
  { category: 'Discovery', title: 'Personas' },
  { category: 'Strategy', title: 'Business Case' },
  { category: 'Strategy', title: 'Go-to-Market' },
  { category: 'Strategy', title: 'Financial Model' },
  { category: 'Delivery', title: 'Product Requirements' },
  { category: 'Delivery', title: 'Technical Architecture' },
  { category: 'Delivery', title: 'Legal & Regulatory' },
  { category: 'Delivery', title: 'Risk Assessment' },
  { category: 'Design', title: 'Wireframes' },
  { category: 'Design', title: 'Prototype' },
  { category: 'Synthesis', title: 'Stakeholder Views' },
  { category: 'Synthesis', title: 'Validation Playbook' },
  { category: 'Quality', title: 'Quality Assessment' },
];

const MARKET_TYPES = ['B2B Enterprise', 'B2B Mid-Market', 'B2B SMB', 'B2C Consumer', 'Marketplace'];
const GEOGRAPHIES = ['North America', 'Europe', 'Asia-Pacific', 'Global'];
const INDUSTRIES = ['Financial Services', 'Healthcare', 'Technology', 'Manufacturing', 'Retail', 'Other'];
const COMPANY_SIZES = ['1-50', '51-200', '201-1000', '1001-5000', '5000+'];
const BUDGETS = ['< $100K', '$100K - $500K', '$500K - $1M', '$1M - $5M', '> $5M'];
const TIMELINES = ['< 3 months', '3-6 months', '6-12 months', '> 12 months'];
const FUNDING_STAGES = ['Bootstrapped', 'Pre-seed', 'Seed', 'Series A+', 'Corporate'];
const REGULATIONS = ['GDPR', 'HIPAA', 'SOC 2', 'PCI-DSS', 'ISO 27001'];
const TECH_STACK = ['AWS', 'Azure', 'GCP', 'Kubernetes', 'React', 'Python'];
const STAKEHOLDERS = ['CEO', 'CFO', 'CTO', 'CISO', 'VP Product', 'Legal', 'Board'];

export function InputFormV4({ onSubmit, onBack, isLoading = false }: InputFormV4Props) {
  const [formData, setFormData] = useState({
    productName: '',
    productDescription: '',
    marketType: '',
    geography: '',
    targetCustomer: '',
    competitors: [] as string[],
    industry: '',
    companySize: '',
    regulations: [] as string[],
    techStack: [] as string[],
    technicalConstraints: '',
    budget: '',
    timeline: '',
    fundingStage: '',
    stakeholders: [] as string[],
    knownConcerns: '',
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    const constraintsList = [
      formData.technicalConstraints,
      formData.knownConcerns,
      formData.budget ? `Budget: ${formData.budget}` : '',
      formData.timeline ? `Timeline: ${formData.timeline}` : '',
      ...formData.competitors.map((c) => `Competitor: ${c}`),
      ...formData.regulations.map((r) => `Regulation: ${r}`),
      ...formData.techStack.map((t) => `Tech: ${t}`),
      ...formData.stakeholders.map((s) => `Stakeholder: ${s}`),
    ].filter(Boolean);

    const additionalContext = [
      formData.companySize ? `Company size: ${formData.companySize}` : '',
      formData.fundingStage ? `Funding stage: ${formData.fundingStage}` : '',
    ]
      .filter(Boolean)
      .join('. ');

    const request: DiscoveryRequest = {
      product_idea: `${formData.productName}\n\n${formData.productDescription}`,
      target_market: formData.targetCustomer || `${formData.marketType} - ${formData.geography}`,
      constraints: constraintsList,
      industry: formData.industry,
      additional_context: additionalContext || undefined,
    };

    onSubmit(request);
  };

  return (
    <div className="v4-root" style={{ minHeight: '100vh' }}>
      {/* Navigation */}
      <nav
        style={{
          padding: '16px 24px',
          borderBottom: '1px solid var(--v4-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'var(--v4-surface)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--v4-text-muted)' }}>
          <ProgressStep label="Start" status="done" />
          <ProgressLine />
          <ProgressStep label="Define" status="active" />
          <ProgressLine />
          <ProgressStep label="Generate" status="pending" />
          <ProgressLine />
          <ProgressStep label="Review" status="pending" />
        </div>
      </nav>

      {/* Main Layout */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '260px 1fr',
          minHeight: 'calc(100vh - 57px)',
        }}
      >
        {/* Sidebar */}
        <aside
          style={{
            padding: '32px 24px',
            borderRight: '1px solid var(--v4-border)',
            background: 'var(--v4-surface)',
          }}
        >
          <div
            style={{
              fontSize: '11px',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              color: 'var(--v4-text-muted)',
              marginBottom: '20px',
            }}
          >
            Output Sections
          </div>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {OUTPUT_SECTIONS.map((section, i) => (
              <li
                key={i}
                style={{
                  fontSize: '13px',
                  color: 'var(--v4-text-secondary)',
                  padding: '8px 0',
                  borderBottom: i < OUTPUT_SECTIONS.length - 1 ? '1px solid var(--v4-border)' : 'none',
                }}
              >
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    color: 'var(--v4-text-muted)',
                    display: 'block',
                    marginBottom: '2px',
                  }}
                >
                  {section.category}
                </span>
                {section.title}
              </li>
            ))}
          </ul>
        </aside>

        {/* Main Form */}
        <main style={{ padding: '48px 64px 140px', maxWidth: '680px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 600, letterSpacing: '-0.02em', marginBottom: '8px' }}>
            Define your initiative
          </h1>
          <p style={{ fontSize: '15px', color: 'var(--v4-text-secondary)', marginBottom: '48px' }}>
            The more context you provide, the more grounded your inception pack will be.
          </p>

          <form onSubmit={handleSubmit}>
            {/* Section 1: Product Idea */}
            <FormSection label="Required" title="Product Idea">
              <Field label="Initiative name">
                <input
                  type="text"
                  name="productName"
                  value={formData.productName}
                  onChange={handleChange}
                  placeholder="e.g., Enterprise Customer Portal 2.0"
                  className="v4-input"
                  required
                />
              </Field>
              <Field label="Description">
                <textarea
                  name="productDescription"
                  value={formData.productDescription}
                  onChange={handleChange}
                  placeholder="What problem does it solve? Who is the target customer? What makes this approach unique?"
                  className="v4-textarea"
                  style={{ minHeight: '160px' }}
                  required
                />
              </Field>
            </FormSection>

            <div className="v4-divider" />

            {/* Section 2: Target Market */}
            <FormSection label="Discovery" title="Target Market">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
                <Field label="Market type">
                  <select name="marketType" value={formData.marketType} onChange={handleChange} className="v4-select">
                    <option value="">Select</option>
                    {MARKET_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Geography">
                  <select name="geography" value={formData.geography} onChange={handleChange} className="v4-select">
                    <option value="">Select</option>
                    {GEOGRAPHIES.map((geo) => (
                      <option key={geo} value={geo}>
                        {geo}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
              <Field label="Target customer" optional>
                <textarea
                  name="targetCustomer"
                  value={formData.targetCustomer}
                  onChange={handleChange}
                  placeholder="Role, industry, company size, pain points..."
                  className="v4-textarea"
                />
              </Field>
              <Field label="Known competitors" optional>
                <ChipInput
                  value={formData.competitors}
                  onChange={(competitors) => setFormData((prev) => ({ ...prev, competitors }))}
                  placeholder="Add competitors..."
                />
              </Field>
            </FormSection>

            <div className="v4-divider" />

            {/* Section 3: Enterprise Context */}
            <FormSection label="Strategy" title="Enterprise Context">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
                <Field label="Your industry">
                  <select name="industry" value={formData.industry} onChange={handleChange} className="v4-select">
                    <option value="">Select</option>
                    {INDUSTRIES.map((ind) => (
                      <option key={ind} value={ind}>
                        {ind}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Company size">
                  <select name="companySize" value={formData.companySize} onChange={handleChange} className="v4-select">
                    <option value="">Select</option>
                    {COMPANY_SIZES.map((size) => (
                      <option key={size} value={size}>
                        {size}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
              <Field label="Regulatory requirements">
                <ChipInput
                  value={formData.regulations}
                  onChange={(regulations) => setFormData((prev) => ({ ...prev, regulations }))}
                  placeholder="Add..."
                  suggestions={REGULATIONS}
                />
              </Field>
            </FormSection>

            <div className="v4-divider" />

            {/* Section 4: Technical Context */}
            <FormSection label="Delivery" title="Technical Context">
              <Field label="Current tech stack" optional>
                <ChipInput
                  value={formData.techStack}
                  onChange={(techStack) => setFormData((prev) => ({ ...prev, techStack }))}
                  placeholder="Add technologies..."
                  suggestions={TECH_STACK}
                />
              </Field>
              <Field label="Technical constraints" optional>
                <textarea
                  name="technicalConstraints"
                  value={formData.technicalConstraints}
                  onChange={handleChange}
                  placeholder="Integration requirements, security needs, performance expectations..."
                  className="v4-textarea"
                />
              </Field>
            </FormSection>

            <div className="v4-divider" />

            {/* Section 5: Business Constraints */}
            <FormSection label="Strategy" title="Business Constraints">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                <Field label="Budget range">
                  <select name="budget" value={formData.budget} onChange={handleChange} className="v4-select">
                    <option value="">Select</option>
                    {BUDGETS.map((b) => (
                      <option key={b} value={b}>
                        {b}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Timeline">
                  <select name="timeline" value={formData.timeline} onChange={handleChange} className="v4-select">
                    <option value="">Select</option>
                    {TIMELINES.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Funding stage">
                  <select name="fundingStage" value={formData.fundingStage} onChange={handleChange} className="v4-select">
                    <option value="">Select</option>
                    {FUNDING_STAGES.map((f) => (
                      <option key={f} value={f}>
                        {f}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
            </FormSection>

            <div className="v4-divider" />

            {/* Section 6: Stakeholders */}
            <FormSection label="Synthesis" title="Stakeholders">
              <Field label="Who needs to approve?">
                <ChipSelect
                  options={STAKEHOLDERS}
                  selected={formData.stakeholders}
                  onChange={(stakeholders) => setFormData((prev) => ({ ...prev, stakeholders }))}
                />
              </Field>
              <Field label="Known concerns" optional>
                <textarea
                  name="knownConcerns"
                  value={formData.knownConcerns}
                  onChange={handleChange}
                  placeholder="Budget concerns, technical feasibility doubts, competitive threats..."
                  className="v4-textarea"
                />
              </Field>
            </FormSection>
          </form>
        </main>
      </div>

      {/* Footer */}
      <footer
        style={{
          position: 'fixed',
          bottom: 0,
          left: '260px',
          right: 0,
          padding: '16px 64px',
          background: 'var(--v4-surface)',
          borderTop: '1px solid var(--v4-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', gap: '24px', fontSize: '13px', color: 'var(--v4-text-muted)' }}>
          <span>16 sections</span>
          <span>12+ agents</span>
          <span>~12-15 min</span>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button type="button" className="v4-btn v4-btn-secondary">
            Save Draft
          </button>
          <button
            type="submit"
            className="v4-btn v4-btn-primary"
            onClick={handleSubmit}
            disabled={isLoading || !formData.productName || !formData.productDescription}
          >
            {isLoading ? 'Generating...' : 'Generate Inception Pack'}
          </button>
        </div>
      </footer>

      {/* Responsive styles */}
      <style>{`
        @media (max-width: 900px) {
          .v4-root > div {
            grid-template-columns: 1fr !important;
          }
          .v4-root aside {
            display: none !important;
          }
          .v4-root main {
            padding: 32px 24px 140px !important;
          }
          .v4-root footer {
            left: 0 !important;
            padding: 16px 24px !important;
          }
          .v4-root [style*="grid-template-columns: repeat(2"] {
            grid-template-columns: 1fr !important;
          }
          .v4-root [style*="grid-template-columns: repeat(3"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

function FormSection({ label, title, children }: { label: string; title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: '40px' }}>
      <div style={{ marginBottom: '24px' }}>
        <div className="v4-eyebrow" style={{ marginBottom: '8px' }}>
          {label}
        </div>
        <h2 style={{ fontSize: '17px', fontWeight: 600, letterSpacing: '-0.01em' }}>{title}</h2>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>{children}</div>
    </section>
  );
}

function Field({ label, optional, children }: { label: string; optional?: boolean; children: React.ReactNode }) {
  return (
    <div>
      <label className="v4-label">
        {label}
        {optional && <span className="v4-label-optional"> — optional</span>}
      </label>
      {children}
    </div>
  );
}

function ProgressStep({ label, status }: { label: string; status: 'done' | 'active' | 'pending' }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        color: status === 'active' ? 'var(--v4-text)' : 'var(--v4-text-muted)',
        fontWeight: status === 'active' ? 500 : 400,
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background:
            status === 'done' ? 'var(--v4-success)' : status === 'active' ? 'var(--v4-accent)' : 'var(--v4-text-muted)',
        }}
      />
      {label}
    </div>
  );
}

function ProgressLine() {
  return <div style={{ width: '24px', height: '1px', background: 'var(--v4-border)' }} />;
}

export default InputFormV4;
