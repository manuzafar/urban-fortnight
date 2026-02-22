import { Shield, AlertTriangle, CheckCircle, Users, Clock, Lightbulb } from 'lucide-react';
import './rendererStyles.css';

interface RealPerson {
  name: string;
  struggling_moment: string;
  how_you_know_them?: string;
}

interface TarpitCheck {
  is_tarpit: boolean;
  similarity_score: number;
  similar_to: string[];
  specific_concerns: string[];
  user_differentiation?: string;
}

interface ProblemLoveOutput {
  problem_statement: string;
  problem_statement_refined?: string;
  specificity_score: number;
  real_people: RealPerson[];
  real_people_count: number;
  frequency: string;
  frequency_analysis: string;
  current_alternatives: string[];
  alternatives_analysis: string;
  tarpit_check: TarpitCheck;
  overall_score: number;
  ai_coaching_notes: string[];
  proceed_recommendation: boolean;
}

interface ProblemLoveRendererProps {
  output: ProblemLoveOutput;
}

export function ProblemLoveRenderer({ output }: ProblemLoveRendererProps) {
  const displayStatement = output.problem_statement_refined || output.problem_statement;

  return (
    <div className="stage-renderer problem-love">
      {/* Problem Statement Section */}
      <section className="renderer-section">
        <h4>
          <Lightbulb size={16} />
          Problem Statement
        </h4>
        <div className="problem-statement">
          {displayStatement}
        </div>
        <div className="score-row">
          <div className="score-badge">
            Specificity: {output.specificity_score}/10
          </div>
        </div>
      </section>

      {/* Real People Section */}
      <section className="renderer-section">
        <h4>
          <Users size={16} />
          Real People ({output.real_people?.length || output.real_people_count || 0})
        </h4>
        {output.real_people && output.real_people.length > 0 ? (
          <ul className="people-list">
            {output.real_people.map((person, i) => (
              <li key={i} className="person-item">
                <strong>{person.name}</strong>
                <span className="struggling-moment">{person.struggling_moment}</span>
                {person.how_you_know_them && (
                  <span className="how-you-know">({person.how_you_know_them})</span>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-state">No real people identified yet. Consider talking to potential users.</p>
        )}
      </section>

      {/* Frequency Analysis */}
      <section className="renderer-section">
        <h4>
          <Clock size={16} />
          Problem Frequency
        </h4>
        <span className={`frequency-badge frequency-${output.frequency}`}>
          {output.frequency}
        </span>
        <p className="analysis-text">{output.frequency_analysis}</p>
      </section>

      {/* Current Alternatives */}
      {output.current_alternatives && output.current_alternatives.length > 0 && (
        <section className="renderer-section">
          <h4>Current Alternatives</h4>
          <ul className="alternatives-list">
            {output.current_alternatives.map((alt, i) => (
              <li key={i}>{alt}</li>
            ))}
          </ul>
          {output.alternatives_analysis && (
            <p className="analysis-text">{output.alternatives_analysis}</p>
          )}
        </section>
      )}

      {/* Tarpit Check */}
      <section className="renderer-section tarpit-section">
        <h4>
          <Shield size={16} />
          Tarpit Analysis
        </h4>
        <div className={`tarpit-status ${output.tarpit_check?.is_tarpit ? 'warning' : 'safe'}`}>
          {output.tarpit_check?.is_tarpit ? (
            <>
              <AlertTriangle size={18} />
              Potential Tarpit Detected
            </>
          ) : (
            <>
              <CheckCircle size={18} />
              Not a Known Tarpit
            </>
          )}
        </div>
        {output.tarpit_check?.similarity_score > 0 && (
          <p className="similarity-score">
            Similarity Score: {Math.round(output.tarpit_check.similarity_score * 100)}%
          </p>
        )}
        {output.tarpit_check?.similar_to && output.tarpit_check.similar_to.length > 0 && (
          <div className="similar-ideas">
            <strong>Similar to:</strong>
            <ul>
              {output.tarpit_check.similar_to.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        )}
        {output.tarpit_check?.specific_concerns && output.tarpit_check.specific_concerns.length > 0 && (
          <div className="concerns">
            <strong>Concerns:</strong>
            <ul className="concerns-list">
              {output.tarpit_check.specific_concerns.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        )}
        {output.tarpit_check?.user_differentiation && (
          <div className="differentiation">
            <strong>Your Differentiation:</strong>
            <p>{output.tarpit_check.user_differentiation}</p>
          </div>
        )}
      </section>

      {/* AI Coaching Notes */}
      {output.ai_coaching_notes && output.ai_coaching_notes.length > 0 && (
        <section className="renderer-section coaching-section">
          <h4>
            <Lightbulb size={16} />
            AI Coaching Notes
          </h4>
          <ul className="coaching-list">
            {output.ai_coaching_notes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Overall Score & Recommendation */}
      <div className="stage-summary">
        <div className="overall-score">
          Overall Score: <strong>{output.overall_score}/10</strong>
        </div>
        <div className={`recommendation ${output.proceed_recommendation ? 'proceed' : 'refine'}`}>
          {output.proceed_recommendation ? (
            <>
              <CheckCircle size={16} />
              Ready to proceed
            </>
          ) : (
            <>
              <AlertTriangle size={16} />
              Consider refining before continuing
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProblemLoveRenderer;
