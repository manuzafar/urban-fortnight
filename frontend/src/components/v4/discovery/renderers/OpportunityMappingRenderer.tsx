import { ArrowUp, ArrowDown, Lightbulb, Target } from 'lucide-react';
import './rendererStyles.css';

interface Force {
  items: string[];
  evidence: Array<{ item: string; source_interview?: string; quote?: string }>;
  strength: number;
}

interface FourForces {
  push: Force;
  pull: Force;
  anxiety: Force;
  habit: Force;
  force_balance: number;
  change_likely: boolean;
  key_insight: string;
}

interface Opportunity {
  id: string;
  description: string;
  interview_count: number;
  evidence: Array<{ quote?: string }>;
  solutions: string[];
  priority: number;
}

interface OpportunityTree {
  outcome: string;
  opportunities: Opportunity[];
}

interface OpportunityMappingOutput {
  four_forces: FourForces;
  opportunity_tree: OpportunityTree;
  primary_opportunity: string;
}

interface OpportunityMappingRendererProps {
  output: OpportunityMappingOutput;
}

export function OpportunityMappingRenderer({ output }: OpportunityMappingRendererProps) {
  const forces = output.four_forces;
  const tree = output.opportunity_tree;

  return (
    <div className="stage-renderer opportunity-mapping">
      {/* Four Forces */}
      <section className="renderer-section">
        <h4>
          <Target size={16} />
          Four Forces of Change
        </h4>

        <div className="four-forces-grid">
          {/* Push */}
          <div className="force-card push">
            <div className="force-header">
              <h5>
                <ArrowUp size={16} className="force-icon-push" />
                Push (What's Broken)
              </h5>
              <span className="force-strength">{forces.push?.strength || 0}/10</span>
            </div>
            <ul className="force-items">
              {forces.push?.items?.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          {/* Pull */}
          <div className="force-card pull">
            <div className="force-header">
              <h5>
                <ArrowUp size={16} className="force-icon-pull" />
                Pull (What's Attractive)
              </h5>
              <span className="force-strength">{forces.pull?.strength || 0}/10</span>
            </div>
            <ul className="force-items">
              {forces.pull?.items?.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          {/* Anxiety */}
          <div className="force-card anxiety">
            <div className="force-header">
              <h5>
                <ArrowDown size={16} className="force-icon-anxiety" />
                Anxiety (What Scares Them)
              </h5>
              <span className="force-strength">{forces.anxiety?.strength || 0}/10</span>
            </div>
            <ul className="force-items">
              {forces.anxiety?.items?.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          {/* Habit */}
          <div className="force-card habit">
            <div className="force-header">
              <h5>
                <ArrowDown size={16} className="force-icon-habit" />
                Habit (What's Comfortable)
              </h5>
              <span className="force-strength">{forces.habit?.strength || 0}/10</span>
            </div>
            <ul className="force-items">
              {forces.habit?.items?.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Force Balance */}
        <div className="force-balance">
          <div className="force-balance-score">
            {forces.force_balance > 0 ? '+' : ''}{forces.force_balance || 0}
          </div>
          <div className="force-balance-label">
            Force Balance = (Push + Pull) - (Anxiety + Habit)
          </div>
          <div className={`recommendation ${forces.change_likely ? 'proceed' : 'refine'}`}>
            {forces.change_likely
              ? 'Change is likely - favorable conditions for adoption'
              : 'Change is uncertain - need to address friction'}
          </div>
        </div>

        {/* Key Insight */}
        {forces.key_insight && (
          <div className="key-insight">
            <h5 className="key-insight-title">Key Insight</h5>
            <p>{forces.key_insight}</p>
          </div>
        )}
      </section>

      {/* Opportunity Tree */}
      <section className="renderer-section">
        <h4>
          <Lightbulb size={16} />
          Opportunity Solution Tree
        </h4>

        <div className="opportunity-tree">
          {/* Outcome */}
          <div className="outcome-box">
            {tree?.outcome || 'Desired Outcome'}
          </div>

          {/* Opportunities */}
          <div className="opportunities-list">
            {tree?.opportunities?.map((opp, i) => (
              <div
                key={opp.id || i}
                className={`opportunity-card ${opp.description === output.primary_opportunity ? 'primary' : ''}`}
              >
                <div className="opportunity-header">
                  <div>
                    <span className="opportunity-name">{opp.description}</span>
                    {opp.interview_count > 0 && (
                      <span className="interview-evidence">
                        ({opp.interview_count} interviews)
                      </span>
                    )}
                  </div>
                  <span className="opportunity-priority">P{opp.priority}</span>
                </div>
                {opp.solutions && opp.solutions.length > 0 && (
                  <ul className="opportunity-solutions">
                    {opp.solutions.map((solution, j) => (
                      <li key={j}>{solution}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Primary Opportunity */}
      {output.primary_opportunity && (
        <div className="stage-summary">
          <div className="overall-score">
            Primary Opportunity:
          </div>
          <div className="recommendation proceed">
            <Target size={16} />
            {output.primary_opportunity}
          </div>
        </div>
      )}
    </div>
  );
}

export default OpportunityMappingRenderer;
