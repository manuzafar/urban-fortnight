import { useState } from 'react';
import { Send, Building2, Users, ChevronDown, ChevronUp } from 'lucide-react';
import type { DiscoveryRequest } from '../types/api';

interface DiscoveryFormProps {
  onSubmit: (request: DiscoveryRequest) => void;
  isLoading: boolean;
}

export function DiscoveryForm({ onSubmit, isLoading }: DiscoveryFormProps) {
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
    <form onSubmit={handleSubmit} className="discovery-form">
      {/* Main textarea - like Claude's chat input */}
      <div className="form-group">
        <textarea
          id="product-idea"
          value={productIdea}
          onChange={(e) => setProductIdea(e.target.value)}
          placeholder="Describe your product idea... What problem does it solve? Who is it for?"
          rows={3}
          required
          minLength={10}
          maxLength={2000}
        />
      </div>

      {/* Quick options row */}
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="industry">
            <Building2 size={14} />
            Industry
          </label>
          <input
            id="industry"
            type="text"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g., Healthcare, FinTech"
            maxLength={100}
          />
        </div>

        <div className="form-group">
          <label htmlFor="target-market">
            <Users size={14} />
            Target Market
          </label>
          <input
            id="target-market"
            type="text"
            value={targetMarket}
            onChange={(e) => setTargetMarket(e.target.value)}
            placeholder="e.g., SMBs, Enterprise"
            maxLength={200}
          />
        </div>
      </div>

      {/* Advanced toggle */}
      <button
        type="button"
        className="toggle-advanced"
        onClick={() => setShowAdvanced(!showAdvanced)}
      >
        {showAdvanced ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {showAdvanced ? 'Less options' : 'More options'}
      </button>

      {showAdvanced && (
        <div className="advanced-options">
          <div className="form-group">
            <label htmlFor="constraints">Constraints</label>
            <textarea
              id="constraints"
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder="Budget limits, timeline, technical requirements (one per line)"
              rows={2}
            />
          </div>

          <div className="form-group">
            <label htmlFor="context">Additional Context</label>
            <textarea
              id="context"
              value={additionalContext}
              onChange={(e) => setAdditionalContext(e.target.value)}
              placeholder="Any other information that would help..."
              rows={2}
              maxLength={1000}
            />
          </div>
        </div>
      )}

      {/* Submit row */}
      <div className="form-actions">
        <div className="char-count">
          {productIdea.length}/2000
        </div>
        <button
          type="submit"
          className="submit-button"
          disabled={!isValid || isLoading}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Generating...
            </>
          ) : (
            <>
              <Send size={16} />
              Generate
            </>
          )}
        </button>
      </div>
    </form>
  );
}
