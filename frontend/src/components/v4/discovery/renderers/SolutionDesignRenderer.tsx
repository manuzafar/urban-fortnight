import { Sparkles, Shield, DollarSign, AlertTriangle, Eye, Ghost, CheckCircle } from 'lucide-react';
import './rendererStyles.css';

interface DHMScore {
  delight: number;
  delight_reasoning: string;
  hard_to_copy: number;
  hard_to_copy_reasoning: string;
  moat_type?: string;
  margin: number;
  margin_reasoning: string;
  total: number;
  passes_threshold: boolean;
}

interface PreMortemItem {
  description: string;
  mitigation?: string;
  early_warning?: string;
  owner?: string;
}

interface PreMortem {
  tigers: PreMortemItem[];
  paper_tigers: PreMortemItem[];
  elephants: PreMortemItem[];
}

interface SolutionDesignOutput {
  solution_concept: string;
  solution_description?: string;
  key_features?: string[];
  value_proposition?: string;
  dhm_score: DHMScore;
  pre_mortem: PreMortem;
}

interface SolutionDesignRendererProps {
  output: SolutionDesignOutput;
}

export function SolutionDesignRenderer({ output }: SolutionDesignRendererProps) {
  const dhm = output.dhm_score;
  const premortem = output.pre_mortem;

  return (
    <div className="stage-renderer solution-design">
      {/* Solution Concept */}
      <section className="renderer-section">
        <h4>
          <Sparkles size={16} />
          Solution Concept
        </h4>
        <div className="solution-concept">
          {output.solution_concept}
        </div>
        {output.solution_description && (
          <p className="analysis-text solution-description">
            {output.solution_description}
          </p>
        )}
      </section>

      {/* Key Features */}
      {output.key_features && output.key_features.length > 0 && (
        <section className="renderer-section">
          <h4>Key Features</h4>
          <ul className="alternatives-list">
            {output.key_features.map((feature, i) => (
              <li key={i}>{feature}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Value Proposition */}
      {output.value_proposition && (
        <section className="renderer-section">
          <h4>Value Proposition</h4>
          <div className="key-insight">
            <p>{output.value_proposition}</p>
          </div>
        </section>
      )}

      {/* DHM Score */}
      <section className="renderer-section">
        <h4>
          <Shield size={16} />
          DHM Analysis
        </h4>

        <div className="dhm-grid">
          {/* Delight */}
          <div className="dhm-card">
            <Sparkles size={24} className="dhm-icon dhm-icon-delight" />
            <div className="dhm-score">{dhm.delight}</div>
            <div className="dhm-label">Delight</div>
            <p className="dhm-reasoning">{dhm.delight_reasoning}</p>
          </div>

          {/* Hard to Copy */}
          <div className="dhm-card">
            <Shield size={24} className="dhm-icon dhm-icon-moat" />
            <div className="dhm-score">{dhm.hard_to_copy}</div>
            <div className="dhm-label">Hard to Copy</div>
            <p className="dhm-reasoning">{dhm.hard_to_copy_reasoning}</p>
            {dhm.moat_type && (
              <span className="score-badge moat-badge">
                {dhm.moat_type}
              </span>
            )}
          </div>

          {/* Margin */}
          <div className="dhm-card">
            <DollarSign size={24} className="dhm-icon dhm-icon-margin" />
            <div className="dhm-score">{dhm.margin}</div>
            <div className="dhm-label">Margin</div>
            <p className="dhm-reasoning">{dhm.margin_reasoning}</p>
          </div>
        </div>

        {/* Total */}
        <div className="dhm-total">
          <div className="dhm-score">{dhm.total}</div>
          <div className="dhm-label">Total DHM Score</div>
          <div className={`dhm-threshold ${dhm.passes_threshold ? 'passes' : 'fails'}`}>
            {dhm.passes_threshold ? (
              <>
                <CheckCircle size={16} className="threshold-icon" />
                Passes threshold (≥20)
              </>
            ) : (
              <>
                <AlertTriangle size={16} className="threshold-icon" />
                Below threshold (&lt;20)
              </>
            )}
          </div>
        </div>
      </section>

      {/* Pre-Mortem */}
      <section className="renderer-section">
        <h4>
          <Eye size={16} />
          Pre-Mortem Analysis
        </h4>

        {/* Tigers */}
        {premortem.tigers && premortem.tigers.length > 0 && (
          <div className="premortem-section tigers">
            <h5>
              <AlertTriangle size={16} className="premortem-icon-tigers" />
              Tigers (Real Threats)
            </h5>
            <div className="premortem-items">
              {premortem.tigers.map((item, i) => (
                <div key={i} className="premortem-item">
                  <p className="premortem-description">{item.description}</p>
                  {item.mitigation && (
                    <p className="premortem-mitigation">
                      <strong>Mitigation:</strong> {item.mitigation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Paper Tigers */}
        {premortem.paper_tigers && premortem.paper_tigers.length > 0 && (
          <div className="premortem-section paper-tigers">
            <h5>
              <Ghost size={16} className="premortem-icon-paper-tigers" />
              Paper Tigers (Seem Scary But Aren't)
            </h5>
            <div className="premortem-items">
              {premortem.paper_tigers.map((item, i) => (
                <div key={i} className="premortem-item">
                  <p className="premortem-description">{item.description}</p>
                  {item.mitigation && (
                    <p className="premortem-mitigation">
                      <strong>Why it's not a real threat:</strong> {item.mitigation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Elephants */}
        {premortem.elephants && premortem.elephants.length > 0 && (
          <div className="premortem-section elephants">
            <h5>
              <Eye size={16} className="premortem-icon-elephants" />
              Elephants (Things No One Talks About)
            </h5>
            <div className="premortem-items">
              {premortem.elephants.map((item, i) => (
                <div key={i} className="premortem-item">
                  <p className="premortem-description">{item.description}</p>
                  {item.mitigation && (
                    <p className="premortem-mitigation">
                      <strong>How to address:</strong> {item.mitigation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export default SolutionDesignRenderer;
